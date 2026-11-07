# -*- coding: utf-8 -*-
"""Export every locally held PDF, retaining physical PDF page boundaries."""
from pathlib import Path
from datetime import date
import hashlib
import html
import json
from urllib.parse import quote
import fitz

ROOT = Path(__file__).resolve().parent
OUT = ROOT / '全文提取'
OUT.mkdir(exist_ok=True)
MAX_RAW_PAGE_CHARS = 1_000_000
PRESERVE_PREFIX_CHARS = 8_000
INDEX_PATH = OUT / 'index.json'
previous_records = {}
if INDEX_PATH.is_file():
    try:
        previous_records = {x['id']: x for x in json.loads(INDEX_PATH.read_text(encoding='utf-8-sig')).get('files', [])}
    except (OSError, ValueError, TypeError):
        previous_records = {}

def read(name):
    return json.loads((ROOT / name).read_text(encoding='utf-8-sig'))

sources = {}
for name, category in [('wechat_manifest.json', '截图相关'),
                       ('bilibili_manifest.json', '截图相关'),
                       ('W06_GNN_Transformer专题/manifest.json', '图模型专题'),
                       ('supplement_manifest.json', '选题对照'),
                       ('专题文献/何恺明/manifest.json', '何恺明论文'),
                       ('专题文献/赖思邈/manifest.json', '赖思邈论文'),
                       ('专题文献/武汉理工AI_CCF-A/manifest.json', '武汉理工AI CCF-A论文')]:
    if not (ROOT / name).is_file():
        continue
    for e in read(name):
        if e.get('local_file'):
            source_path = Path(e['local_file'])
            if not source_path.is_absolute():
                source_path = ROOT / source_path
            sources[source_path.resolve()] = {**e, 'category': category}

extra = {
    'B02_supplement.pdf': ('B02-S', 'D4RT 官方补充材料', 'B02'),
    'B03_supplemental.pdf': ('B03-S', 'PointCNN 官方补充材料', 'B03'),
    'B07_arxiv.pdf': ('B07-A', 'ReHyAt arXiv 含附录版本', 'B07'),
}
for p in ROOT.rglob('*.pdf'):
    if p.name in extra:
        pid, title, main = extra[p.name]
        parent = next(e for e in sources.values() if e['id'] == main)
        sources[p.resolve()] = {'id': pid, 'title': title, 'source_url': parent['source_url'],
                                'category': '补充材料或另一版本', 'parent_id': main}
correction = read('十组精读/04_version_correction.json')
correction_path = Path(correction['local_file']) if correction.get('local_file') else None
if correction_path and not correction_path.is_absolute():
    correction_path = ROOT / correction_path
if correction_path and correction_path.is_file():
    sources[correction_path.resolve()] = {
        'id': 'W10-J', 'title': correction['corrected_title'],
        'source_url': correction['source_url'], 'category': '期刊扩展版', 'parent_id': 'W10'}

records = []
for p in sorted(ROOT.rglob('*.pdf')):
    e = sources.get(p.resolve())
    if not e:
        raise ValueError(f'Unclassified PDF: {p}')
    digest = hashlib.sha256(p.read_bytes()).hexdigest()
    pages = []
    raw_page_characters = []
    truncated_text_pages = []
    previous = previous_records.get(e['id'], {})
    previous_raw_counts = previous.get('raw_page_characters') or previous.get('page_characters') or []
    with fitz.open(p) as doc:
        for i, page in enumerate(doc, 1):
            previous_count = previous_raw_counts[i - 1] if i <= len(previous_raw_counts) else 0
            if previous_count > MAX_RAW_PAGE_CHARS:
                raw_count = previous_count
                text = (f'[Text extraction skipped on PDF page {i}: a previous extraction produced '
                        f'{raw_count:,} characters from the embedded text layer. See this page in the PDF.]')
                truncated_text_pages.append({'pdf_page': i, 'raw_characters': raw_count,
                                             'reason': 'previous extraction exceeded the safe text limit'})
            else:
                raw_text = page.get_text(sort=True).replace('\x00', '')
                raw_count = len(raw_text.strip())
                if raw_count > MAX_RAW_PAGE_CHARS:
                    text = (raw_text[:PRESERVE_PREFIX_CHARS]
                            + f'\n\n[Text truncated: embedded text layer yielded {raw_count:,} characters. '
                            + f'See PDF page {i} for the complete page.]')
                    truncated_text_pages.append({'pdf_page': i, 'raw_characters': raw_count,
                                                 'reason': 'embedded text exceeded the safe text limit'})
                else:
                    text = raw_text
            raw_page_characters.append(raw_count)
            pages.append({'pdf_page': i, 'characters': len(text.strip()), 'text': text})
    txt_path = OUT / (e['id'] + '_全文.txt')
    header = (f"{e['id']} | {e['title']}\n来源：{e.get('source_url', '')}\n"
              f"本地PDF：{p.relative_to(ROOT).as_posix()}\nSHA-256：{digest}\n"
              "页码为PDF文件页序，不一定等于论文印刷页码。此文件为机器文字提取；"
              "多栏阅读顺序、数学符号和图表必须回看PDF。空文本页不等于空白页。\n")
    txt_path.write_text(header + ''.join(
        f"\n{'=' * 24} PDF 第 {x['pdf_page']} 页 {'=' * 24}\n{x['text']}\n"
        for x in pages), encoding='utf8')
    records.append({'id': e['id'], 'title': e['title'], 'short_name': e.get('short_name', ''), 'category': e['category'],
                    'parent_id': e.get('parent_id'), 'source_url': e.get('source_url'),
                    'pdf_file': p.relative_to(ROOT).as_posix(),
                    'text_file': txt_path.relative_to(ROOT).as_posix(),
                    'pages': len(pages), 'sha256': digest, 'pdf_bytes': p.stat().st_size,
                    'characters': sum(x['characters'] for x in pages),
                    'low_text_pages': [x['pdf_page'] for x in pages if x['characters'] < 40],
                    'page_characters': [x['characters'] for x in pages],
                    'raw_page_characters': raw_page_characters,
                    'truncated_text_pages': truncated_text_pages})
result = {'date': date.today().isoformat(), 'method': 'PyMuPDF page.get_text(sort=True), physical PDF page markers; pathological pages are truncated with PDF-page references',
          'pdf_count': len(records), 'total_pages': sum(x['pages'] for x in records),
          'total_characters': sum(x['characters'] for x in records), 'files': records}
(OUT / 'index.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf8')

# Import after extraction, as the existing library module also rebuilds its index.
from build_library import page
esc = html.escape
rows = []
for e in sorted(records, key=lambda x: x['id']):
    low = ('；少量文本页：' + ', '.join(map(str, e['low_text_pages']))) if e['low_text_pages'] else ''
    truncated = ('；文本层异常页：' + ', '.join(str(x['pdf_page']) for x in e['truncated_text_pages']) + '（请查看 PDF）') if e['truncated_text_pages'] else ''
    alias = '<b>'+esc(e['short_name'])+'</b><br>' if e.get('short_name') else ''
    rows.append(f'<tr><td>{e["id"]}<br>{e["category"]}</td><td>{alias}{esc(e["title"])}</td>'
                f'<td><a href="{quote(e["pdf_file"])}">PDF</a> · '
                f'<a href="{quote(e["text_file"])}">逐页全文 TXT</a><br>'
                f'{e["pages"]} 页 · {e["characters"]:,} 字符{low}{truncated}</td></tr>')
body = ('<h1>原文全文提取索引</h1><nav><a href="00_阅读入口.html">阅读入口</a>'
        '<a href="02_逐篇精读汇编.html">中文精读汇编</a></nav>'
        f'<div class="lead">已从 {len(records)} 份本地 PDF 导出全部 {result["total_pages"]} 页的文本，'
        '包含主论文、补充材料和另存版本。每页保留物理页码，方便定位原文。'
        '本页搜索题名；打开 TXT 后可用 Ctrl+F 搜索正文。中文精读和英文全文分别保存。</div>'
        '<p>文本抽取不替代PDF：公式、图像、图表及复杂排版应回看原页。'
        '补充材料和同论文的另一版本不增加独立论文数量。HorNet的版本取得情况见阅读入口。</p>'
        '<p><input id="q" placeholder="搜索编号、题名或类别"></p><p id="count"></p>'
        '<table><thead><tr><th>编号与类别</th><th>题名</th><th>文件</th></tr></thead><tbody>'
        + ''.join(rows) + '</tbody></table>'
        '<p><a href="全文提取/index.json">逐页文字量、哈希和机器可读清单</a></p>'
        '<script>const q=document.querySelector("#q"),rs=[...document.querySelectorAll("tbody tr")];'
        'function f(){let n=0;for(const r of rs){r.hidden=!r.textContent.toLowerCase().includes(q.value.toLowerCase());'
        'n+=!r.hidden;}document.querySelector("#count").textContent=`显示 ${n} / ${rs.length} 份文件`;}'
        'q.addEventListener("input",f);f();</script>')
(ROOT / '07_原文全文提取索引.html').write_text(page('原文全文提取索引', body), encoding='utf8')
print(json.dumps({k: v for k, v in result.items() if k != 'files'}, ensure_ascii=False))
