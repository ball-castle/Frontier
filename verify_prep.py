from pathlib import Path
import json,hashlib,re,sys,subprocess,concurrent.futures,urllib.parse,html
from pypdf import PdfReader
from reportlab.pdfbase.ttfonts import TTFont
from prep_content import MANUAL,ALGORITHMS,CHEAT
BASE=Path(r'C:\Users\CAI BIN\Desktop\1'); OUT=BASE/'美赛建模面试备考包_20261105'; QA=BASE/'_work/qa';QA.mkdir(exist_ok=True)
checks=[]
for name,expected in [('01_临场速记',2),('02_面试完整准备',13),('03_常见算法通俗速记',5)]:
    p=OUT/(name+'.pdf');r=PdfReader(p);texts=[x.extract_text() or '' for x in r.pages]
    assert len(r.pages)==expected,(name,len(r.pages))
    assert all(len(t)>80 for t in texts),(name,'empty page')
    assert not any('\ufffd' in t or '\u25a0' in t for t in texts),(name,'glyph replacement')
    (QA/(name+'.txt')).write_text('\n\n'.join(texts),encoding='utf8')
    checks.append({'file':name,'pages':len(r.pages),'chars_per_page':[len(t) for t in texts]})
    (QA/name).mkdir(exist_ok=True)
font=TTFont('Check',r'C:\Windows\Fonts\simsun.ttc',subfontIndex=0)
s=str(MANUAL)+str(ALGORITHMS)+str(CHEAT)
missing=sorted(set(c for c in s if not c.isspace() and ord(c) not in font.face.charToGlyph))
assert not missing,('missing glyphs',missing)
manifest=json.loads((OUT/'资料索引/精选资料来源与SHA256.json').read_text(encoding='utf8'))
for m in manifest:assert hashlib.sha256((OUT/m['copy']).read_bytes()).hexdigest()==m['sha256']
ex=PdfReader(OUT/'原始资料/国赛B题_面试阅读节选_第1至27页.pdf');src=PdfReader(r'D:\ball_castle\数模论文\B题.pdf')
assert len(ex.pages)==27
for i in range(27):assert ex.pages[i].extract_text()==src.pages[i].extract_text()
nav=(OUT/'00_资料导航.html').read_text(encoding='utf8')
broken=[]
for url in re.findall(r'<a href="([^"]+)"',nav):
    url=html.unescape(url)
    if url.startswith('http'):continue
    if url.startswith('file:'):
        s=urllib.parse.unquote(urllib.parse.urlparse(url).path).lstrip('/');p=Path(s)
    else:p=OUT/urllib.parse.unquote(url)
    if not p.exists():broken.append(str(p))
assert not broken,broken
print(json.dumps({'pdf_checks':checks,'copied_files_verified':len(manifest),'excerpt_pages_verified':27,'broken_local_links':broken,'missing_glyphs':missing},ensure_ascii=False),flush=True)
(QA/'verification.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf8')

def render(name):
    before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (QA/name).glob('*.png')}
    cmd=['pdftoppm','-r','110','-png',str(OUT/(name+'.pdf')),str(QA/name/'page')]
    r=subprocess.run(cmd,capture_output=True,timeout=180)
    if r.returncode:raise RuntimeError(r.stderr.decode(errors='replace'))
    changed=[p.name for p in (QA/name).glob('*.png') if before.get(p.name)!=hashlib.sha256(p.read_bytes()).hexdigest()]
    print('RENDERED',name,len(list((QA/name).glob('*.png'))),'CHANGED',changed,flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
    list(pool.map(render,['01_临场速记','02_面试完整准备','03_常见算法通俗速记']))
