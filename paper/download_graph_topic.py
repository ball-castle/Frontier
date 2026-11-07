# -*- coding: utf-8 -*-
from pathlib import Path
import json,re,hashlib,requests,concurrent.futures
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parent/'W06_GNN_Transformer专题'
items=json.loads((ROOT/'selected_papers.json').read_text(encoding='utf8'))
def norm(s):return re.sub('[^a-z0-9]','',s.lower())
def one(e):
 p=ROOT/(e['id']+'_'+e['short_name']+'.pdf')
 try:
  if not p.exists():
   r=requests.get(e['pdf_url'],timeout=(15,60));r.raise_for_status();assert r.content.startswith(b'%PDF-');p.write_bytes(r.content)
  b=p.read_bytes();r=PdfReader(str(p));text=r.pages[0].extract_text() or ''
  exact=norm(e['title']) in norm(text)
  terms=[x for x in re.findall('[a-zA-Z0-9]+',e['title'].lower()) if len(x)>2]
  ratio=sum(norm(w) in norm(text) for w in terms)/len(terms)
  assert ratio>.95,(e['id'],ratio)
  e.update(local_file=str(p),status='downloaded_verified',pages=len(r.pages),bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),exact_normalized_title_match=exact,title_word_match_ratio=ratio,first_page_excerpt=text[:1400])
  print(e['id'],e['short_name'],len(r.pages),'pages',round(len(b)/1048576,2),'MiB',flush=True)
 except Exception as ex:e.update(status='failed',error=str(ex));print(e['id'],'FAILED',str(ex),flush=True)
 return e
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:result=list(pool.map(one,items))
(ROOT/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
print('SUCCESS',sum(x['status']=='downloaded_verified' for x in result),'OF',len(result))
