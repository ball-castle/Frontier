from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests, fitz, hashlib, json, re, time

ROOT = Path(__file__).resolve().parent
OUT = ROOT / '补充对照论文'
OUT.mkdir(exist_ok=True)
CHECK = OUT / '_checks'
CHECK.mkdir(exist_ok=True)
PAPERS = [
    ('S01', 'GEM', '2609.27332', 'Stable Geometry with Divergent Task Evidence for Efficient Long-Horizon Agent Compression'),
    ('S02', 'BEACON', '2608.05757', 'Beyond Relevance: Bayesian Evidence Acquisition for Agentic Whole-Slide Image Reasoning'),
    ('S03', 'MemEvo', '2609.36581', 'MemEvo: Automatic Discovery of Streaming Video Memory Mechanisms'),
    ('S04', 'DeltaStreamer', '2610.19849', 'DeltaStreamer: Towards Human-Like Agentic Streaming Video Understanding'),
    ('S05', 'FOLIO', '2607.13298', 'FOLIO: Focused Semantic Memory for Streaming Video Understanding'),
    ('S06', 'MoM', '2609.25054', 'Memory of Memory'),
    ('S07', 'REVEAL', '2608.08612', 'REVEAL: A Rubric-Guided Agent for Explicit Evidence Sufficiency Verification in Long-Video Question Answering'),
    ('S08', 'CLOSER', '2610.28476', 'CLOSER: Evidence-Aware Active Visual Verification for Embodied Object-Goal Navigation'),
]

def normal(s):
    return re.sub('[^a-z0-9]', '', s.lower())

def fetch(row):
    num, short, aid, title = row
    p = OUT / f'{num}_{short}_{aid}.pdf'
    url = f'https://arxiv.org/pdf/{aid}'
    item = dict(id=num, short_name=short, arxiv_id=aid, title=title,
                source_url=f'https://arxiv.org/abs/{aid}', pdf_url=url,
                local_file=str(p), inclusion='supplement_only_not_screenshot_collection',
                verified_on='2026-11-05', status='pending')
    try:
        if not p.exists():
            error = None
            for attempt in range(3):
                try:
                    r = requests.get(url, timeout=100, headers={'User-Agent': 'Mozilla/5.0'})
                    r.raise_for_status()
                    if not r.content.startswith(b'%PDF-'):
                        raise ValueError('Response is not a PDF')
                    p.write_bytes(r.content)
                    error = None
                    break
                except Exception as exc:
                    error = exc
                    if attempt < 2:
                        time.sleep(2 + attempt)
            if error:
                raise error
        raw = p.read_bytes()
        if not raw.startswith(b'%PDF-'):
            raise ValueError('Local file is not PDF')
        with fitz.open(p) as doc:
            first = doc[0].get_text()
            # Ligatures and line-break hyphenation are removed by normalization.
            identity = normal(title) in normal(first)
            if not identity and short == 'MoM':
                identity = 'memoryofmemory' in normal(first)
            doc[0].get_pixmap(matrix=fitz.Matrix(0.8, 0.8)).save(CHECK / f'{num}_first.png')
            item.update(status='verified' if identity else 'downloaded_title_review_needed',
                        pdf_magic_verified=True, title_verified=identity,
                        pages=len(doc), bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest(),
                        first_page_excerpt=first[:1700], render_path=str(CHECK / f'{num}_first.png'))
    except Exception as exc:
        item.update(status='failed', error=f'{type(exc).__name__}: {exc}')
    return item

results=[]
with ThreadPoolExecutor(max_workers=4) as pool:
    for future in as_completed([pool.submit(fetch, p) for p in PAPERS]):
        item=future.result()
        results.append(item)
        print(json.dumps({k:item[k] for k in ('id','short_name','status')}, ensure_ascii=False), flush=True)
results.sort(key=lambda x:x['id'])
(ROOT / 'supplement_manifest.json').write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
(OUT / 'supplement_manifest.json').write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'total':len(results), 'verified':sum(x['status']=='verified' for x in results)}, ensure_ascii=False))
