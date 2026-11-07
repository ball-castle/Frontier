# -*- coding: utf-8 -*-
from pathlib import Path
import json, html, re, hashlib
from urllib.parse import quote
from pypdf import PdfReader
from bs4 import BeautifulSoup
from build_library import ROOT, page, read, dump, esc

groups=read('十组精读/任务分配.json')['groups']
manifest=read('paper_manifest.json')['papers']; by_id={x['id']:x for x in manifest}
labels={'screenshot_check':'截图身份核对','problem':'研究问题','mechanism':'核心机制与公式','evidence':'原文证据','compute':'算力、数据与复现','limits':'边界与核查意见','transfer_hypothesis':'迁移假设（研究建议）','pilot':'最小验证与对照','priority':'精读与投入优先级'}
def render(v):
 if isinstance(v,str): return '<p>'+esc(v).replace('\n','<br>')+'</p>'
 if isinstance(v,list): return '<ul>'+''.join('<li>'+render(x)+'</li>' for x in v)+'</ul>'
 if isinstance(v,dict): return '<dl>'+''.join('<dt><b>'+esc(k)+'</b></dt><dd>'+render(x)+'</dd>' for k,x in v.items())+'</dl>'
 return esc(v)

done=[]; cards=[]; combined=[]; missing=[]
for g in groups:
 p=ROOT/'十组精读'/(g['id']+'.json')
 if not p.exists(): missing.append(g['id']);continue
 d=json.loads(p.read_text(encoding='utf-8-sig'))
 if isinstance(d,dict):
  for key in ['papers','items','entries','reviews']:
   if key in d and isinstance(d[key],list): d=d[key];break
 if not isinstance(d,list): raise ValueError(f'Unexpected schema {p}')
 ids=[e.get('id') for e in d]
 if set(ids)!=set(g['paper_ids']):raise ValueError((g['id'],ids,g['paper_ids']))
 done.append(g['id']);combined.extend(d)
 cards.append('<h2 id="group'+g['id']+'">第 '+g['id']+' 组 · '+esc(g['title'])+'</h2><p><a href="'+quote('十组精读/'+g['id']+'.txt')+'">本组完整文本</a> · <a href="'+quote('十组精读/'+g['id']+'.json')+'">结构化提取</a></p>')
 for e in d:
  if e['id']=='W06':
   e['screenshot_check']='截图3是GNN＋Transformer融合方法汇总。根据用户后续要求，已围绕主题独立选取并下载11篇代表论文，详见专题；不再追溯原公众号名单。'
   e['topic_followup']='11篇专题已完成下载与全文提取：Graphormer、GraphGPS、GraphTrans、TokenGT、NodeFormer、NAGphormer、Exphormer、SGFormer、Polynormer、HubGT、GTLM。'
  m=by_id[e['id']]; link='<a href="'+quote(m['local_file'])+'">本地 PDF</a> · ' if m['local_file'] else ''
  if m.get('topic_file'):link+='<a href="'+quote(m['topic_file'])+'">11篇专题精读与PDF</a> · '
  if m.get('source_url'):link+='<a href="'+esc(m['source_url'])+'">论文来源</a>'
  raw=ROOT/'全文提取'/(e['id']+'_全文.txt')
  if raw.exists():link+=' · <a href="'+quote(raw.relative_to(ROOT).as_posix())+'">逐页原文 TXT</a>'
  extra_files={'B02':('十组精读/05_work/B02_supplement.pdf','官方补充材料'), 'B03':('十组精读/06/B03_supplemental.pdf','官方补充材料'), 'B07':('十组精读/07/B07_arxiv.pdf','arXiv含附录版')}
  if e['id'] in extra_files:
   ep,label=extra_files[e['id']]
   link+=' · <a href="'+quote(ep)+'">'+label+'</a>'
  if e['id']=='W10':link+=' · <a href="'+quote('十组精读/04_version_correction.json')+'">2026扩展版核查</a>'
  parts=['<details open id="'+e['id']+'"><summary>'+e['id']+' · '+esc(e.get('title',m['title']))+'</summary><p>'+link+'</p>']
  for key,label in labels.items():
   if key in e:parts.append('<h3>'+label+'</h3>'+render(e[key]))
  rest={k:v for k,v in e.items() if k not in labels and k not in ['id','title','source_url']}
  if rest:parts.append(render(rest))
  parts.append('</details>'); cards.extend(parts)
toc=' · '.join('<a href="#group'+g['id']+'">第 '+g['id']+' 组</a>' for g in groups if g['id'] in done)
body='<p class="meta">10 个独立分工 · 原图核对与正文提取</p><h1>截图论文逐篇精读汇编</h1><nav><a href="00_阅读入口.html">阅读入口</a><a href="01_截图论文索引.html">论文索引</a><a href="03_研究投入建议.html">项目与投入建议</a></nav><div class="lead">正文提取 '+str(len(done))+'/10 组，覆盖 '+str(len(combined))+'/36 个截图条目。论文证据、我们的推导检查和迁移建议分开标注。数值是对原文的提取，本次未复现训练实验。W10的定量精读来自2022会议原版，截图所指2026期刊扩展版尚未取得全文；W06与B21分别按专题和软件处理。</div><p>'+toc+'</p>'+''.join(cards)
(ROOT/'02_逐篇精读汇编.html').write_text(page('截图论文逐篇精读汇编',body),encoding='utf8')
dump('reading_extracts.json',{'date':'2026-11-05','completed_groups':done,'missing_groups':missing,'entries':combined})

supp=read('supplement_manifest.json');srows=[];schecks=[]
for s in supp:
 p=Path(s['local_file']);b=p.read_bytes();digest=hashlib.sha256(b).hexdigest();pdf=PdfReader(str(p))
 assert b.startswith(b'%PDF-') and digest==s['sha256']
 rel=p.relative_to(ROOT).as_posix();schecks.append({'id':s['id'],'file':rel,'pages':len(pdf.pages),'sha256':digest,'size_bytes':len(b),'verified':True})
 srows.append('<tr><td>'+esc(s['short_name'])+'</td><td>'+esc(s['title'])+'</td><td><a href="'+quote(rel)+'">PDF</a> · <a href="'+esc(s['source_url'])+'">原文</a></td></tr>')
dump('supplement_verification.json',{'count':len(schecks),'all_pass':True,'pdfs':schecks})
suppbody='<h1>为选题追加的直接对照论文</h1><p><a href="00_阅读入口.html">返回入口</a> · <a href="novelty_screen.txt">完整碰撞审查</a></p><p>以下 '+str(len(supp))+' 篇用于检验候选方向与已有工作的重合，不计入截图的 34 篇。</p><table><thead><tr><th>简称</th><th>论文</th><th>来源</th></tr></thead><tbody>'+''.join(srows)+'</tbody></table>'
(ROOT/'04_补充对照论文.html').write_text(page('补充对照论文',suppbody),encoding='utf8')

graph=read('W06_GNN_Transformer专题/manifest.json');gchecks=[]
for s in graph:
 p=Path(s['local_file']);b=p.read_bytes();digest=hashlib.sha256(b).hexdigest();pdf=PdfReader(str(p))
 assert b.startswith(b'%PDF-') and digest==s['sha256']
 gchecks.append({'id':s['id'],'file':p.relative_to(ROOT).as_posix(),'pages':len(pdf.pages),'sha256':digest,'size_bytes':len(b),'verified':True})
dump('graph_topic_verification.json',{'count':len(gchecks),'all_pass':True,'pdfs':gchecks})
if (ROOT/'graph_topic_body.html').exists():
 (ROOT/'05_GNN与Transformer融合专题.html').write_text(page('GNN与Transformer融合专题',(ROOT/'graph_topic_body.html').read_text(encoding='utf8')),encoding='utf8')

group_links=''.join('<li><a href="'+quote('十组精读/'+g['id']+'.txt')+'">'+g['id']+' · '+esc(g['title'])+'</a>（'+', '.join(g['paper_ids'])+'）</li>' for g in groups if g['id'] in done)
home='''<p class="meta">论文提取与科研方向审查 · 2026-11-05</p><h1>从截图论文到下一项研究</h1><div class="lead"><b>主材料是十组逐篇论文提取。</b>从准确题名、方法与公式到实验、算力和迁移假设，都可追溯到本地 PDF 与原始来源。</div><div class="row"><div class="card"><div class="number">34</div>截图论文 PDF</div><div class="card"><div class="number">10</div>独立精读分工</div><div class="card"><div class="number">12</div>原始截图</div><div class="card"><div class="number">8</div>补充对照论文</div></div><h2>从这里开始</h2><ol><li><a href="02_逐篇精读汇编.html"><b>逐篇精读汇编</b></a>：问题、机制、原文证据、算力、边界、迁移与最小实验。</li><li><a href="01_截图论文索引.html"><b>截图论文索引</b></a>：可搜索，逐项打开 PDF、原图及发表记录。</li><li><a href="03_研究投入建议.html"><b>现有项目与投入建议</b></a>：先完成 ESN 证书成果；以严格有限记忆下的事件/状态保真作为第一优先验证的新候选。</li><li><a href="04_补充对照论文.html"><b>补充对照论文</b></a>：检查候选思路是否已被 GEM、MemEvo、BEACON 等覆盖。</li></ol><h2>十组分工</h2><ol>'''+group_links+'''</ol><h2>两项身份边界</h2><p>W06 是“GNN＋Transformer 11 种融合方法”的二次汇总，截图缺少具体论文题名与作者，尚未还原这 11 篇；已保留检索记录。B21 DeepInfer 是开源推理软件项目，未找到独立论文 PDF。MiTA 在截图 11、12 重复出现，去重后计一篇。</p><h2>核验与出处</h2><p>34 篇截图论文约 200.8 MiB；另有 8 篇补充论文约 29.4 MiB。各文件经过 PDF 格式、页数解析、题名与哈希核查。<a href="download_verification.json">下载验证</a>、<a href="supplement_verification.json">补充文件验证</a>、<a href="paper_manifest.json">统一论文清单</a>、<a href="reading_extracts.json">全文提取数据</a>。</p><p>项目审查依据保存在 <a href="project_inventory.json">仓库清单</a>、<a href="project_evidence.json">项目证据</a>、<a href="portfolio_independent_review.txt">独立项目复核</a>与<a href="novelty_screen.txt">定向查新</a>。本次没有执行模型训练、修改研究仓库或提交论文。</p>'''
home=home.replace('<div class="number">8</div>补充对照论文','<div class="number">19</div>追加论文（11专题＋8对照）')
home=home.replace('<h2>十组分工</h2>','<h2>专题与阅读路线</h2><p><a href="05_GNN与Transformer融合专题.html"><b>11篇GNN与Transformer融合专题</b></a> · <a href="06_优先阅读与迁移路线.html"><b>优先阅读与迁移路线</b></a></p><h2>十组分工</h2>')
home=home.replace('W06 是“GNN＋Transformer 11 种融合方法”的二次汇总，截图缺少具体论文题名与作者，尚未还原这 11 篇；已保留检索记录。','W06 已按用户要求整理为 11 篇代表论文专题，覆盖结构编码、串并联融合、图token、稀疏注意力和图语言模型；选文不宣称与原公众号名单一致。')
home=home.replace('34 篇截图论文约 200.8 MiB；另有 8 篇补充论文约 29.4 MiB。','合计 53 篇 PDF：34 篇截图论文、11 篇图模型专题、8 篇选题对照。')
home=home.replace('<a href="download_verification.json">下载验证</a>','<a href="graph_topic_verification.json">专题文件验证</a>、<a href="download_verification.json">截图文件验证</a>')
home=home.replace('10 个独立分工','10 个独立分工')
(ROOT/'00_阅读入口.html').write_text(page('截图论文阅读入口',home),encoding='utf8')
for name in ['02_逐篇精读汇编','03_研究投入建议']:
 p=ROOT/(name+'.html')
 if p.exists():
  soup=BeautifulSoup(p.read_text(encoding='utf8'),'html.parser')
  for el in soup(['style','script','nav']):el.decompose()
  (ROOT/(name+'.txt')).write_text(soup.get_text('\n',strip=True),encoding='utf8')
print(json.dumps({'completed_groups':done,'missing_groups':missing,'extracted_entries':len(combined),'supplement_verified':len(schecks)},ensure_ascii=False))
