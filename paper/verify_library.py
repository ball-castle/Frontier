# -*- coding: utf-8 -*-
from pathlib import Path
from urllib.parse import unquote,urlsplit
import json, hashlib, re, logging
from bs4 import BeautifulSoup
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parent
issues=[]; links=0; htmls=[]
for p in sorted(ROOT.glob('0*.html')):
 soup=BeautifulSoup(p.read_text(encoding='utf8'),'html.parser'); htmls.append(p.name)
 if '\ufffd' in soup.get_text():issues.append('Unicode replacement character: '+p.name)
 for a in soup.select('[href], [src]'):
  href=a.get('href') or a.get('src'); u=urlsplit(href)
  if u.scheme or u.netloc or not u.path:continue
  dest=(p.parent/unquote(u.path)).resolve();links+=1
  if not dest.exists():issues.append(f'{p.name}: missing {href}')
  elif u.fragment and dest.suffix=='.html':
   target=BeautifulSoup(dest.read_text(encoding='utf8'),'html.parser')
   if not target.find(id=unquote(u.fragment)):issues.append(f'{p.name}: missing anchor {href}')
a=json.loads((ROOT/'十组精读/任务分配.json').read_text(encoding='utf8'))
r=json.loads((ROOT/'reading_extracts.json').read_text(encoding='utf8'))
expected=[i for g in a['groups'] for i in g['paper_ids']]
actual=[e['id'] for e in r['entries']]
if sorted(actual)!=sorted(expected):issues.append(f'Entry mismatch {len(actual)} vs {len(expected)}')
if len(actual)!=len(set(actual)):issues.append('Duplicate screenshot entry IDs')
if r['missing_groups'] or len(r['completed_groups'])!=10:issues.append('Incomplete reading groups')
required_html=['00_阅读入口.html','01_截图论文索引.html','02_逐篇精读汇编.html','03_研究投入建议.html','04_补充对照论文.html','05_GNN与Transformer融合专题.html','06_优先阅读与迁移路线.html','07_原文全文提取索引.html']
for name in required_html:
 if not (ROOT/name).is_file():issues.append('Missing required page: '+name)
for e in r['entries']:
 for key in ['problem','mechanism','evidence','compute','limits','transfer_hypothesis','pilot','priority']:
  if not e.get(key):issues.append(f'{e["id"]}: empty {key}')
 if len(e.get('evidence',[]))<2:issues.append(f'{e["id"]}: fewer than 2 evidence records')
graph_manifest=json.loads((ROOT/'W06_GNN_Transformer专题/manifest.json').read_text(encoding='utf8'))
graph_reading=json.loads((ROOT/'W06_GNN_Transformer专题/reading_extracts.json').read_text(encoding='utf-8-sig'))
if isinstance(graph_reading,dict):graph_reading=graph_reading.get('entries',graph_reading.get('papers',[]))
if sorted(x['id'] for x in graph_reading)!=sorted(x['id'] for x in graph_manifest):issues.append('Graph topic coverage mismatch')
for e in graph_reading:
 if len(e.get('evidence',[]))<2:issues.append(f'{e["id"]}: fewer than 2 evidence records')
 g=next(x for x in graph_manifest if x['id']==e['id'])
 if e.get('source_sha256')!=g['sha256']:issues.append(f'{e["id"]}: report/PDF version mismatch')
 for ev in e.get('evidence',[]):
  if isinstance(ev.get('page'),int) and not 1<=ev['page']<=g['pages']:issues.append(f'{e["id"]}: evidence page out of bounds')
checks=[]; parser_warnings=[]
class WarningCapture(logging.Handler):
 def emit(self,record):parser_warnings.append({'file':p.relative_to(ROOT).as_posix(),'message':record.getMessage()})
logger=logging.getLogger('pypdf');logger.handlers.clear();logger.propagate=False;logger.addHandler(WarningCapture())
for p in sorted(ROOT.rglob('*.pdf')):
 b=p.read_bytes()
 try:
  pdf=PdfReader(str(p));pages=len(pdf.pages)
  if not b.startswith(b'%PDF-') or pages<1:raise ValueError('Bad PDF')
  checks.append({'file':p.relative_to(ROOT).as_posix(),'pages':pages,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
 except Exception as ex:issues.append(f'{p.name}: {ex}')
archive=json.loads((ROOT/'全文提取/index.json').read_text(encoding='utf8'))
pdf_by_file={e['file']:e for e in checks}
if set(pdf_by_file)!=set(e['pdf_file'] for e in archive['files']):issues.append('Raw text / PDF coverage mismatch')
for e in archive['files']:
 p=ROOT/e['text_file'];pdf=pdf_by_file.get(e['pdf_file'])
 if not p.is_file():issues.append('Missing raw text: '+e['text_file']);continue
 text=p.read_text(encoding='utf8')
 if len(re.findall(r'={24} PDF 第 \d+ 页 ={24}',text))!=e['pages']:issues.append('Raw text page markers mismatch: '+e['id'])
 if not pdf or e['sha256']!=pdf['sha256'] or e['pages']!=pdf['pages']:issues.append('Raw text provenance mismatch: '+e['id'])
 if e['characters']<100:issues.append('Very low text extraction: '+e['id'])
for name in ['download_verification.json','supplement_verification.json','graph_topic_verification.json']:
 for e in json.loads((ROOT/name).read_text(encoding='utf8'))['pdfs']:
  pdf=pdf_by_file.get(e['file'])
  if not pdf or e['sha256']!=pdf['sha256']:issues.append('Manifest hash mismatch: '+e['file'])
for p in list((ROOT/'十组精读').glob('*.json'))+[ROOT/'reading_extracts.json',ROOT/'W06_GNN_Transformer专题/reading_extracts.json']:
 if '\ufffd' in p.read_text(encoding='utf-8-sig'):issues.append('Unicode replacement character: '+str(p.relative_to(ROOT)))
status=json.loads((ROOT/'completion_status.json').read_text(encoding='utf8'))
rendered_warning_files=[]
if parser_warnings:
 import fitz
 for name in sorted(set(x['file'] for x in parser_warnings)):
  try:
   with fitz.open(ROOT/name) as document:
    for page in document:page.get_pixmap(matrix=fitz.Matrix(.25,.25))
    rendered_warning_files.append({'file':name,'all_pages_rendered_with_second_parser':True,'pages':len(document)})
  except Exception as ex:issues.append('Secondary render failed: '+name+': '+str(ex))
result={'date':'2026-11-05','html_pages':htmls,'checked_local_links':links,'groups':r['completed_groups'],'screenshot_entries':len(actual),'graph_topic_entries':len(graph_reading),'all_pdf_count':len(checks),'all_pdf_bytes':sum(e['bytes'] for e in checks),'exported_text_files':len(archive['files']),'exported_pages':archive['total_pages'],'open_items':status['open_items'],'parser_warnings':parser_warnings,'warning_file_crosschecks':rendered_warning_files,'issues':issues,'passed':not issues,'pdfs':checks}
(ROOT/'final_verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in result.items() if k!='pdfs'},ensure_ascii=False))
raise SystemExit(0 if not issues else 1)
