# -*- coding: utf-8 -*-
"""Acquire public PDFs from the three added research collections and record identity checks."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
import hashlib
import json
import re
import time

import fitz
import requests
from difflib import SequenceMatcher

ROOT = Path(__file__).resolve().parent
MANIFESTS = [
    ROOT / '专题文献' / '何恺明' / 'manifest.json',
    ROOT / '专题文献' / '赖思邈' / 'manifest.json',
    ROOT / '专题文献' / '武汉理工AI_CCF-A' / 'manifest.json',
]
REPORT = ROOT / '专题文献' / 'download_verification.json'


def normalize(value):
    return re.sub(r'[^a-z0-9]+', '', value.casefold())


def read_manifest(path):
    data = json.loads(path.read_text(encoding='utf-8-sig'))
    if isinstance(data, dict):
        entries = data.get('papers', data.get('entries'))
        if not isinstance(entries, list):
            raise ValueError(f'No papers/entries array in {path}')
    elif isinstance(data, list):
        entries = data
    else:
        raise ValueError(f'Unexpected manifest format in {path}')
    return entries


def default_local_file(collection, entry):
    """Choose a stable, readable archive path for linked papers without one."""
    paper_id = re.sub(r'[^A-Za-z0-9._-]+', '_', entry.get('id') or 'paper').strip('._-')
    label = re.sub(r'[^A-Za-z0-9._-]+', '_', entry.get('short_name') or '').strip('._-')
    if not label:
        label = re.sub(r'[^A-Za-z0-9._-]+', '_', entry.get('title') or '').strip('._-')[:72]
    filename = f'{paper_id}_{label}.pdf' if label else f'{paper_id}.pdf'
    return (Path('专题文献') / collection / filename).as_posix()


def pdf_candidates(entry):
    urls = entry.get('pdf_urls') or []
    for key in ('pdf_url', 'fallback_pdf_url', 'author_pdf_url'):
        value = entry.get(key)
        if value:
            urls.append(value)
    seen = set()
    for url in urls:
        if url and url not in seen:
            seen.add(url)
            yield url


def check_pdf(path, entry):
    raw = path.read_bytes()
    if not raw.startswith(b'%PDF-'):
        raise ValueError('response is not a PDF')
    with fitz.open(path) as doc:
        if not len(doc):
            raise ValueError('PDF has no pages')
        first = doc[0].get_text(sort=True).replace('\x00', '')
        title = entry.get('title', '')
        title_n = normalize(title)
        first_n = normalize(first)
        # PDF line breaks and ligatures can split the title. Compare the longest title
        # prefix as a fallback, but keep any ambiguous file in manual review.
        title_ok = bool(title_n and title_n in first_n)
        ratio = SequenceMatcher(None, title_n[:100], first_n[:220]).ratio() if title_n else 0.0
        title_ok = title_ok or ratio >= 0.72
        author_list = entry.get('authors') or []
        first_author = author_list[0] if author_list else ''
        author_ok = not first_author or normalize(first_author) in first_n
        return {
            'pdf_magic_verified': True,
            'title_verified': title_ok,
            'first_author_verified': author_ok,
            'pages': len(doc),
            'bytes': len(raw),
            'sha256': hashlib.sha256(raw).hexdigest(),
            'first_page_excerpt': first[:1100],
        }


def verify_identity(entry, checks):
    """Accept text checks, or a hash-bound manual visual review."""
    manual = entry.get('manual_identity_review') or {}
    if (manual.get('method') == 'visual_first_page'
            and manual.get('sha256') == checks.get('sha256')):
        return True, 'manual_visual_inspection'
    if checks.get('title_verified') and checks.get('first_author_verified'):
        return True, 'pdf_text'
    return False, 'pdf_text_unconfirmed'


def fetch_one(collection, entry):
    record = {
        'collection': collection,
        'id': entry.get('id'),
        'title': entry.get('title'),
        'source_url': entry.get('source_url'),
        'attempted_pdf_urls': list(pdf_candidates(entry)),
    }
    local = entry.get('local_file')
    urls = record['attempted_pdf_urls']
    if not local or not urls:
        record.update(status='public_fulltext_unavailable', local_file=local)
        return record
    dest = (ROOT / local).resolve()
    try:
        dest.relative_to(ROOT.resolve())
    except ValueError:
        record.update(status='unsafe_local_path_rejected', local_file=local)
        return record
    dest.parent.mkdir(parents=True, exist_ok=True)
    errors = []
    if dest.is_file():
        try:
            checks = check_pdf(dest, entry)
            identity_ok, method = verify_identity(entry, checks)
            record.update(checks)
            record.update(identity_verified=identity_ok, identity_verification_method=method,
                          status='existing_pdf_checked' if identity_ok else 'existing_pdf_identity_review_needed',
                          local_file=local)
            return record
        except Exception as exc:
            errors.append(f'existing file: {type(exc).__name__}: {exc}')
            dest.unlink()
    for url in urls:
        for attempt in range(3):
            tmp = dest.with_suffix(dest.suffix + '.part')
            try:
                response = requests.get(
                    url, timeout=(20, 120), stream=True,
                    headers={'User-Agent': 'Mozilla/5.0 (compatible; research-library/1.0)'},
                )
                response.raise_for_status()
                content_type = response.headers.get('Content-Type', '').casefold()
                with tmp.open('wb') as output:
                    for block in response.iter_content(chunk_size=1024 * 256):
                        if block:
                            output.write(block)
                response.close()
                if not tmp.read_bytes().startswith(b'%PDF-'):
                    raise ValueError(f'not a PDF response ({content_type})')
                tmp.replace(dest)
                checks = check_pdf(dest, entry)
                identity_ok, method = verify_identity(entry, checks)
                status = 'downloaded_verified' if identity_ok else 'downloaded_identity_review_needed'
                record.update(checks)
                record.update(identity_verified=identity_ok, identity_verification_method=method,
                              status=status, local_file=local, successful_pdf_url=url)
                return record
            except Exception as exc:
                errors.append(f'{url} attempt {attempt + 1}: {type(exc).__name__}: {exc}')
                if tmp.exists():
                    tmp.unlink()
                if attempt < 2:
                    time.sleep(1.5 * (attempt + 1))
    record.update(status='download_failed', local_file=local, errors=errors)
    return record


def main():
    collections = []
    jobs = []
    for path in MANIFESTS:
        if not path.is_file():
            continue
        name = path.parent.name
        entries = read_manifest(path)
        for entry in entries:
            if not entry.get('local_file') and list(pdf_candidates(entry)):
                entry['local_file'] = default_local_file(name, entry)
        collections.append((name, path, entries))
        jobs.extend((name, entry) for entry in entries)

    report_by_key = {}
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(fetch_one, name, entry): (name, entry) for name, entry in jobs}
        for future in as_completed(futures):
            name, entry = futures[future]
            report = future.result()
            report_by_key[(name, entry.get('id'))] = report
            print(json.dumps({'collection': name, 'id': entry.get('id'), 'status': report['status']}, ensure_ascii=False), flush=True)

    all_records = []
    for name, path, entries in collections:
        for entry in entries:
            record = report_by_key[(name, entry.get('id'))]
            # Avoid embedding long excerpts and retry logs in the paper manifest.
            entry['download_status'] = record['status']
            if record.get('local_file'):
                entry['local_file'] = record['local_file']
            if record.get('sha256'):
                entry['sha256'] = record['sha256']
                entry['pages'] = record['pages']
                entry['bytes'] = record['bytes']
            if record.get('identity_verification_method'):
                entry['pdf_identity_verified'] = record['identity_verified']
                entry['pdf_identity_verification_method'] = record['identity_verification_method']
            if record.get('successful_pdf_url'):
                entry['successful_pdf_url'] = record['successful_pdf_url']
            all_records.append(record)
        path.write_text(json.dumps(entries, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    summary = {
        'generated_utc': datetime.now(timezone.utc).isoformat(),
        'collections': {name: sum(x['collection'] == name for x in all_records) for name, _, _ in collections},
        'record_count': len(all_records),
        'downloaded_verified': sum(x['status'] in ('downloaded_verified', 'existing_pdf_checked') and x.get('identity_verified') for x in all_records),
        'identity_review_needed': sum(x['status'] in ('downloaded_identity_review_needed', 'existing_pdf_identity_review_needed') for x in all_records),
        'public_fulltext_unavailable': sum(x['status'] == 'public_fulltext_unavailable' for x in all_records),
        'download_failed': sum(x['status'] == 'download_failed' for x in all_records),
        'files': all_records,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in summary.items() if k != 'files'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
