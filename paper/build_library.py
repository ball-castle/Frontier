# -*- coding: utf-8 -*-
from pathlib import Path
import json, hashlib, html, shutil, re
from urllib.parse import quote
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent
def esc(v): return html.escape(str(v if v is not None else ''))
def dump(name, data): (ROOT/name).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
def read(name): return json.loads((ROOT/name).read_text(encoding='utf-8'))
CSS = '''body{font:16px/1.8 system-ui,"Microsoft YaHei",sans-serif;color:#1d2b3a;background:#f5f7fa;margin:0}main{max-width:1180px;margin:auto;padding:38px 30px;background:white}h1{font-size:32px;line-height:1.35}h2{margin-top:2.5em;border-bottom:2px solid #dbe7e8;padding-bottom:.3em}h3{margin-top:1.8em}a{color:#116b81;text-decoration:none}a:hover{text-decoration:underline}.meta,small{color:#627587}.lead{padding:22px;background:#eaf4f3;border-left:5px solid #168579;border-radius:4px}.row{display:flex;gap:16px;flex-wrap:wrap}.card{flex:1;min-width:180px;border:1px solid #dbe4ea;padding:18px;border-radius:8px}.number{font-size:30px;font-weight:bold;color:#087d70}table{width:100%;border-collapse:collapse;font-size:14px}th,td{padding:13px 12px;border-bottom:1px solid #dbe3e8;text-align:left;vertical-align:top}th{background:#edf2f5}tr:hover{background:#f8fafb}.scroll{overflow:auto}input,select{padding:10px 12px;border:1px solid #bccbd3;border-radius:6px;font:inherit}input{width:min(620px,90%)}.tag{display:inline-block;font-size:12px;padding:2px 7px;border-radius:4px;background:#eaf4f3;color:#086f64}.warn{background:#fff4df;color:#8b5903}.box{padding:18px 24px;margin:20px 0;background:#f5f7fa;border:1px solid #dae3e9}nav{display:flex;gap:18px;flex-wrap:wrap;margin:20px 0}details{border:1px solid #dbe4ea;padding:16px;margin:12px 0;border-radius:8px}summary{font-weight:600;cursor:pointer}.paper-title{font-weight:650}code{background:#f1f4f6;padding:1px 4px}li{margin:6px 0}figure{margin:20px 0}img{max-width:100%;height:auto}footer{margin-top:45px;font-size:13px;color:#627587}@media print{body{background:white}main{padding:0}input,select,button{display:none}a{color:inherit}details{break-inside:avoid}h2,h3{break-after:avoid}}'''
def page(title, body): return '<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+esc(title)+'</title><style>'+CSS+'main{overflow-wrap:anywhere}dd{margin-inline-start:20px}</style><main>'+body+'</main></html>'

assignment=read('十组精读/任务分配.json')
group_by_id={p:g for g in assignment['groups'] for p in g['paper_ids']}
ideas={
'W01':'以局部感受野与充电—发放—重置动态近似脉冲注意力，减少显式注意力矩阵存储。',
'W02':'利用时空注意力能量随距离衰减构造 O(n log n) 稀疏模式。',
'W03':'把临床文本意图落到解剖结构，将成功推理轨迹提炼为可复用技能。',
'W04':'结合局部/全局注意力、训练系统优化、上下文课程与工具使用训练的开放模型。',
'W05':'由图像选择正常/异常提示专家，用稀疏混合提高未见类别异常检测。',
'W06':'按用户追加要求整理11篇代表论文：结构偏置、局部/全局融合、图token化、稀疏通信和图语言模型。',
'W07':'ALD 概率参数化与双流优化，在声明的条件下研究个体校准保证。',
'W08':'通过反事实证据核验、概念定位和干预，检验胸片推理的视觉归因。',
'W09':'以欧氏距离衰减为空间先验，并用空间独立分组提高注意力效率。',
'W10':'递归门控卷积实现自适应高阶空间交互。',
'W11':'多尺度卷积分别建模时序的局部变化和全局上下文。',
'W12':'以输出空间二阶重要性剪除原子专家子单元，减少 Hessian 存储。',
'W13':'用科学家定义的开放问题和证据链接评分，核查科研 Agent 的实际完成度。',
'W14':'先用问题无关的低倍扫描构建切片记忆，再按问题检索和高倍取证。'}
papers=[]; checks=[]
for fn in ['wechat_manifest.json','bilibili_manifest.json']:
 for e in read(fn):
  p=Path(e['local_file']) if e.get('local_file') else None
  if p and not p.exists(): raise FileNotFoundError(p)
  check=None
  if p:
   data=p.read_bytes(); pdf=PdfReader(str(p)); digest=hashlib.sha256(data).hexdigest()
   expected=e.get('sha256') or e.get('pdf_validation',{}).get('sha256')
   check={'id':e['id'],'file':p.name,'pages':len(pdf.pages),'size_bytes':len(data),'sha256':digest,'magic_ok':data.startswith(b'%PDF-'),'parse_ok':True,'manifest_hash_matches':expected==digest}
   assert check['magic_ok'] and check['manifest_hash_matches'],check
   checks.append(check)
  status=e.get('venue') or e.get('publication_verified') or '发表状态待核实'
  papers.append({'id':e['id'],'title':e['title'],'screenshots':e.get('screenshot_occurrences') or [e['screenshot']], 'reading_group':group_by_id[e['id']]['id'],'source_url':e.get('source_url'),'publication_url':e.get('publication_url'),'publication_status':status,'local_file':p.name if p else None,'download_status':'已下载并核验' if p else ('软件项目，无独立论文PDF' if e['id']=='B21' else '尚不能唯一识别'),'key_idea':ideas.get(e['id'],e.get('key_idea')),'notes':e.get('notes'),'verification':check})
assert len(papers)==36 and len(checks)==34
for p in papers:
 if p['id']=='W06':
  p['download_status']='已补齐11篇代表论文专题'
  p['topic_file']='05_GNN与Transformer融合专题.html'
  p['notes']='按用户要求围绕主题独立选取11篇代表论文；不再追溯公众号，不宣称与原汇总逐篇一致。'
 if p['id']=='W10':
  p['download_status']='2022会议原版已下载；2026期刊扩展版见版本核查'
  p['version_record']='十组精读/04_version_correction.json'
dump('paper_manifest.json',{'date':'2026-11-05','scope':'12张截图，36个去重条目：34篇论文、1软件项目、1汇总主题；汇总主题另补11篇代表论文','papers':papers})
dump('download_verification.json',{'date':'2026-11-05','pdf_count':len(checks),'total_bytes':sum(c['size_bytes'] for c in checks),'all_pass':True,'pdfs':checks})

sd=ROOT/'截图原图'; sd.mkdir(exist_ok=True)
for s in assignment['screenshot_paths']:
 dest=sd/f"截图{s['number']:02d}.png"
 if Path(s['path']).exists(): shutil.copy2(s['path'],dest)
 elif not dest.exists(): raise FileNotFoundError(s['path'])

rows=[]
for p in papers:
 loc='<a href="'+quote(p['local_file'])+'">打开 PDF</a>' if p['local_file'] else '<span class="tag warn">'+esc(p['download_status'])+'</span>'
 if p.get('topic_file'): loc='<a href="'+quote(p['topic_file'])+'">打开11篇专题与PDF</a>'
 if p.get('version_record'): loc+='<br><a href="'+quote(p['version_record'])+'">期刊扩展版取得情况</a>'
 links=[]
 if p['source_url']:links.append('<a href="'+esc(p['source_url'])+'">原始来源</a>')
 if p['publication_url'] and p['publication_url']!=p['source_url']:links.append('<a href="'+esc(p['publication_url'])+'">发表记录</a>')
 pics='、'.join('<a href="'+quote('截图原图/截图%02d.png'%i)+'">'+str(i)+'</a>' for i in p['screenshots'])
 verify=p.get('verification'); footprint=f"{verify['pages']} 页 · {verify['size_bytes']/1048576:.1f} MiB" if verify else ''
 row=f'''<tr data-search="{esc((p['id']+' '+p['title']+' '+str(p['key_idea'])+' '+str(p['publication_status'])).lower())}"><td>{p['id']}<br><small>截图 {pics}<br>精读第{p['reading_group']}组</small></td><td class="paper-title">{esc(p['title'])}<br><small>{esc(p['key_idea'])}</small></td><td>{esc(p['publication_status'])}<br><small>{esc(p['notes'])}</small></td><td>{loc}<br>{' · '.join(links)}<br><small>{footprint}</small></td></tr>'''
 rows.append(row)
body='''<p class="meta">截图原文核对 · 截至 2026-11-05</p><h1>截图论文索引</h1><nav><a href="00_阅读入口.html">阅读入口</a><a href="02_逐篇精读汇编.html">十组逐篇精读</a><a href="03_研究投入建议.html">项目与投入建议</a></nav><div class="lead">12 张截图，36 个去重条目：<b>34 份截图相关论文 PDF 已下载（HorNet 为会议原版）</b>，另有 DeepInfer 软件项目，以及“GNN＋Transformer”汇总主题（已另补 11 篇代表论文专题）。MiTA 在截图 11、12 重复出现，只计一次。</div><p>文件名 W 对应前七张截图，B 对应后五张。每篇论文的 PDF 格式、页数解析、首页身份和 SHA-256 均有核验记录；会议发表状态与预印本分别标注。原始截图已随库保存。</p><label for="search">搜索题名、方法、会议或编号：</label><p><input id="search" placeholder="例如：memory / ICML / W07 / 注意力" autocomplete="off"></p><p id="count"></p><div class="scroll"><table><thead><tr><th>定位</th><th>论文与核心思想</th><th>发表状态与核对说明</th><th>全文与来源</th></tr></thead><tbody id="papers">'''+''.join(rows)+'''</tbody></table></div><footer>原始结构化清单：<a href="wechat_manifest.json">W 清单</a>、<a href="bilibili_manifest.json">B 清单</a>；统一清单：<a href="paper_manifest.json">paper_manifest.json</a>；下载验证：<a href="download_verification.json">download_verification.json</a>。</footer><script>const q=document.getElementById('search'),rs=[...document.querySelectorAll('#papers tr')];function filter(){let n=0;for(const r of rs){let show=r.dataset.search.includes(q.value.toLowerCase());r.hidden=!show;n+=show;}document.getElementById('count').textContent='显示 '+n+' / '+rs.length+' 个条目';}q.addEventListener('input',filter);filter();</script>'''
(ROOT/'01_截图论文索引.html').write_text(page('截图论文索引',body),encoding='utf-8')
print(json.dumps({'screenshot_entries':len(papers),'verified_screenshot_pdfs':len(checks),'size_mib':round(sum(c['size_bytes'] for c in checks)/1048576,2),'copied_screenshots':len(assignment['screenshot_paths'])},ensure_ascii=False))
