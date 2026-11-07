# -*- coding: utf-8 -*-
import json, os, shutil, html
from pathlib import Path
from urllib.parse import quote

root = Path(r'C:\Users\CAI BIN\Desktop\1\paper')
def load_json(rel): return json.loads((root / rel).read_text(encoding='utf-8'))
def href_for(path, base=root): return quote(os.path.relpath(str(path), str(base)).replace('\\', '/'), safe='/')
def esc(value): return html.escape(str(value or ''), quote=True)
def local_path(value):
    if not value: return None
    p=Path(str(value))
    return p if p.is_absolute() else root/p
def link(label, href, cls='link', external=False):
    attrs=' target="_blank" rel="noopener"' if external else ''
    return f'<a class="{cls}" href="{esc(href)}"{attrs}>{esc(label)}</a>'

main_data=load_json('paper_manifest.json')['papers']
main_papers={x['id']:x for x in main_data if x.get('local_file') and x['id']!='W06'}
graph_data=load_json('W06_GNN_Transformer专题/selected_papers.json')
supp_data=load_json('补充对照论文/supplement_manifest.json')
topic_groups=[
 ('01','注意力与高效 Transformer 结构','关注稀疏注意力、空间先验、局部与全局计算，以及递归和循环结构。',['W01','W02','W09','W10','W11','B01','B05','B06','B07','B22']),
 ('02','视觉生成、视频与潜在世界模型','覆盖动态场景重建、视频生成、预测式潜空间和视觉信号离散表示。',['B02','B08','B09','B10','B16']),
 ('03','视觉任务与多模态感知','按主要应用归入医学影像、异常检测、点云和地球观测。',['W03','W05','W08','W14','B03','B20']),
 ('04','Agent、科学发现与长程记忆','包括科研 Agent、交互视觉推理、测试时记忆和研究系统。',['W04','W13','B11','B12','B15','B18']),
 ('05','专家混合、剪枝与模型压缩','聚焦专家粒度、跨层共享与输出空间剪枝。',['W12','B19']),
 ('06','校准、强化学习与训练目标','整理个体校准、信用分配、奖励设计、自蒸馏和表征几何。',['W07','B04','B13','B14','B17']),
]
assigned=[pid for _,_,_,ids in topic_groups for pid in ids]
missing=sorted(set(main_papers)-set(assigned)); unmatched=sorted(set(assigned)-set(main_papers))
if missing or unmatched: raise RuntimeError(f'分类映射不一致: 未分类={missing}; 清单中不存在={unmatched}')
supp_groups=[('长程记忆与流式视频',['S01','S03','S04','S05','S06']),('证据获取、验证与具身导航',['S02','S07','S08'])]
css='''
:root{--ink:#172435;--muted:#607080;--line:#dce5ec;--paper:#fff;--wash:#f3f7fa;--blue:#145b83;--teal:#0f766e;--shadow:0 8px 24px rgba(22,49,70,.07)}
*{box-sizing:border-box}body{margin:0;background:var(--wash);color:var(--ink);font:16px/1.65 "Segoe UI","Microsoft YaHei",sans-serif}a{color:var(--blue);text-decoration:none}a:hover{text-decoration:underline}.wrap{max-width:1160px;margin:auto;padding:28px 22px 64px}.hero{background:linear-gradient(120deg,#123c5a,#176c79);color:white;padding:30px 34px;border-radius:20px;box-shadow:var(--shadow)}.hero h1{font-size:30px;line-height:1.25;margin:0 0 10px}.hero p{margin:0;max-width:850px;color:#e6f3f5}.eyebrow{text-transform:uppercase;letter-spacing:.12em;font-size:12px;font-weight:700;color:#a8d9da;margin-bottom:8px}.stats{display:flex;flex-wrap:wrap;gap:10px;margin-top:20px}.stat{min-width:128px;padding:10px 14px;border-radius:12px;background:rgba(255,255,255,.12)}.stat strong{display:block;font-size:21px}.stat span{font-size:12px;color:#d5e9ed}.actions{display:flex;flex-wrap:wrap;gap:10px;margin:18px 0 26px}.button{display:inline-block;padding:10px 15px;border-radius:10px;background:var(--blue);color:#fff;font-weight:700}.button.secondary{background:#fff;color:var(--blue);border:1px solid var(--line)}.button:hover{text-decoration:none;filter:brightness(1.06)}.section{margin:30px 0}.section h2{font-size:22px;margin:0 0 5px}.lede{margin:0 0 16px;color:var(--muted)}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:14px}.card,.paper-card{background:var(--paper);border:1px solid var(--line);border-radius:14px;padding:17px 18px;box-shadow:var(--shadow)}.card h3,.paper-card h3{font-size:17px;line-height:1.4;margin:4px 0 8px}.card p,.paper-card p{color:#4d5c68;margin:0 0 12px}.card .count{color:var(--teal);font-size:13px;font-weight:700}.pill{display:inline-block;padding:3px 9px;border-radius:999px;background:#eaf3f7;color:#305468;font-size:12px;margin:2px 5px 2px 0}.kicker{font-size:12px;color:var(--muted);font-weight:700;letter-spacing:.03em}.links{display:flex;flex-wrap:wrap;gap:8px;margin-top:8px}.links a{font-size:13px;font-weight:700}.group{margin:22px 0}.group-head{display:flex;align-items:baseline;gap:10px;flex-wrap:wrap;margin-bottom:10px}.group-head h2{margin:0;font-size:21px}.group-head .n{font-size:13px;color:var(--teal);font-weight:700}.searchbar{position:sticky;top:8px;z-index:5;background:rgba(243,247,250,.95);padding:10px 0 12px;backdrop-filter:blur(8px)}input[type=search]{width:100%;max-width:620px;padding:12px 14px;border:1px solid #b8c9d6;border-radius:10px;font-size:16px;background:#fff}.paper-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(310px,1fr));gap:12px}.paper-card .id{font-weight:800;color:var(--teal);margin-right:8px}.paper-card h3{font-size:15px}.paper-card .idea{font-size:14px}.paper-card[hidden],.group[hidden]{display:none}.note{padding:14px 17px;background:#edf5f7;border-left:4px solid #3d8790;border-radius:8px;color:#405760}.subtle{font-size:13px;color:var(--muted)}.footer{border-top:1px solid var(--line);margin-top:35px;padding-top:16px;color:var(--muted);font-size:13px}.empty{display:none;color:var(--muted);padding:14px}.empty.show{display:block}.tableish{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:10px}.mini{background:#fff;border:1px solid var(--line);border-radius:12px;padding:12px 14px}.mini strong{display:block}.mini span{color:var(--muted);font-size:13px}
@media(max-width:600px){.wrap{padding:14px 12px 40px}.hero{padding:22px 19px}.hero h1{font-size:25px}.stat{min-width:100px}.paper-grid{grid-template-columns:1fr}}
'''
script='''<script>const q=document.querySelector('#paperSearch');if(q){q.addEventListener('input',()=>{const term=q.value.trim().toLowerCase();let shown=0;document.querySelectorAll('.paper-card[data-search]').forEach(card=>{const ok=!term||card.dataset.search.includes(term);card.hidden=!ok;if(ok)shown++;});document.querySelectorAll('.group[data-group]').forEach(group=>{group.hidden=!group.querySelector('.paper-card:not([hidden])');});const empty=document.querySelector('#emptyResults');if(empty)empty.classList.toggle('show',shown===0);});}</script>'''

def card_html(item, base=root, idea=None, tag=None, local=None, extra_links=None, search_extra=''):
    title=item.get('title',''); pid=item.get('id','')
    if local is None: local=local_path(item.get('local_file'))
    tags=[tag] if tag else []
    if item.get('theme'):
        th=item['theme']; tags.extend([str(z) for z in th[:2]] if isinstance(th,list) else [str(th)])
    tag_html=''.join(f'<span class="pill">{esc(x)}</span>' for x in tags if x)
    links=[]
    if local and local.exists(): links.append(link('本地 PDF',href_for(local,base)))
    elif item.get('pdf_url'): links.append(link('公开 PDF',item['pdf_url'],external=True))
    src=item.get('source_url') or item.get('landing_url')
    if src: links.append(link('论文来源',src,external=True))
    for label,href,external in (extra_links or []):
        if href: links.append(link(label,href,external=external))
    meta=' · '.join(str(x) for x in (item.get('year'),item.get('venue')) if x)
    search=' '.join([pid,title,idea or '',tag or '',search_extra,meta,' '.join(str(x) for x in tags)]).lower()
    return f'<article class="paper-card" data-search="{esc(search)}"><div class="kicker"><span class="id">{esc(pid)}</span>{esc(meta)}</div><h3>{esc(title)}</h3>{tag_html}<p class="idea">{esc(idea or "")}</p><div class="links">{" ".join(links)}</div></article>'

main_sections=[]
for num,title,desc,ids in topic_groups:
    cards=[card_html(main_papers[pid],idea=main_papers[pid].get('key_idea'),tag=title,local=local_path(main_papers[pid].get('local_file'))) for pid in ids]
    main_sections.append(f'<section class="group" data-group><div class="group-head"><h2>{num} · {esc(title)}</h2><span class="n">{len(ids)} 篇</span></div><p class="lede">{esc(desc)}</p><div class="paper-grid">{"".join(cards)}</div></section>')
graph_cards=[]
for item in graph_data:
    matches=sorted((root/'W06_GNN_Transformer专题').glob(f"{item['id']}_*.pdf"))
    graph_cards.append(card_html(item,idea=item.get('key_idea'),tag=item.get('mechanism_family') or '图 Transformer',local=matches[0] if matches else None,extra_links=[('专题精读',href_for(root/'05_GNN与Transformer融合专题.html'),False)]))
main_sections.append(f'<section class="group" data-group><div class="group-head"><h2>07 · GNN 与 Transformer 融合</h2><span class="n">{len(graph_cards)} 篇</span></div><p class="lede">按结构偏置、局部/全局融合、图 token、稀疏通信和图语言模型整理；逐篇机制与对照见专题精读。</p><div class="paper-grid">{"".join(graph_cards)}</div></section>')
supp_map={x['id']:x for x in supp_data}; supp_sections=[]
for title,ids in supp_groups:
    cards=[card_html(supp_map[pid],tag=title,local=local_path(supp_map[pid].get('local_file'))) for pid in ids]
    supp_sections.append(f'<section class="group" data-group><div class="group-head"><h3>{esc(title)}</h3><span class="n">{len(cards)} 篇</span></div><div class="paper-grid">{"".join(cards)}</div></section>')
b21=next((x for x in main_data if x['id']=='B21'),None)
b21_html=''
if b21: b21_html=f'<section class="section"><h2>配套研究软件</h2><div class="paper-card"><div class="kicker"><span class="id">B21</span>GitHub 项目 · 非 PDF</div><h3>{esc(b21.get("title"))}</h3><p class="idea">{esc(b21.get("key_idea"))}</p><div class="links">{link("项目主页",b21.get("source_url",""),external=True)}</div></div></section>'
catalog=f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>论文主题分类</title><style>{css}</style></head><body><main class="wrap"><header class="hero"><div class="eyebrow">Research Paper Map · 2026</div><h1>论文主题分类</h1><p>主线论文按主要研究问题归入一个主题；GNN/Transformer 与补充对照单列。搜索框可按编号、标题和机制要点检索。作者/机构收藏论文保留独立入口。</p><div class="stats"><div class="stat"><strong>34</strong><span>主线论文 PDF</span></div><div class="stat"><strong>11</strong><span>GNN / Transformer</span></div><div class="stat"><strong>8</strong><span>补充对照 PDF</span></div><div class="stat"><strong>119</strong><span>作者/机构记录</span></div></div></header><div class="actions"><a class="button" href="00_阅读入口.html">回到阅读入口</a><a class="button secondary" href="专题文献/00_作者机构文献索引.html">打开作者/机构文献库</a><a class="button secondary" href="06_优先阅读与迁移路线.html">阅读路线</a></div><div class="searchbar"><input id="paperSearch" type="search" placeholder="搜索编号、英文标题或中文要点，例如 W14 / memory / 医学"></div><div id="emptyResults" class="empty">没有找到匹配的论文。</div><section class="section"><h2>主线论文</h2><p class="lede">每篇只出现一次，按主要贡献归类；交叉主题可以通过搜索标题和要点定位。</p>{''.join(main_sections)}</section><section class="section"><div class="group-head"><h2>08 · 补充对照论文</h2><span class="n">8 篇</span></div><p class="lede">与主线相关的记忆机制、证据获取和具身验证工作。</p>{''.join(supp_sections)}</section>{b21_html}<section class="section"><div class="note">主线论文链接回原始 PDF 位置；作者/机构文献库按来源独立检索。这样可以按研究主题找论文，同时保留原始收集脉络。</div></section><section class="section"><details><summary>版本说明</summary><p>W10 本地全文为 2022 NeurIPS 原版；截图指向 2026 TPAMI 扩展版，后者全文尚未取得。状态详见 completion_status.json。</p></details></section><footer class="footer">资料来自本地清单与已整理的精读记录。此页按研究主题组织阅读入口，不替代论文原文与版本记录。<br><a href="01_截图论文索引.html">截图论文索引</a> · <a href="02_逐篇精读汇编.html">逐篇精读</a> · <a href="05_GNN与Transformer融合专题.html">GNN专题精读</a> · <a href="07_原文全文提取索引.html">全文提取索引</a></footer></main>{script}</body></html>'''
(root/'08_论文主题分类.html').write_text(catalog,encoding='utf-8')

collections=[('何恺明','专题文献/何恺明/manifest.json','CV / 视觉学习研究记录'),('武汉理工 AI CCF-A','专题文献/武汉理工AI_CCF-A/manifest.json','机构论文清单'),('赖思邈','专题文献/赖思邈/manifest.json','作者论文清单')]
collection_sections=[]; summary=[]; collection_records=0; local_count=0
for name,manifest_rel,desc in collections:
    records=load_json(manifest_rel); collection_records+=len(records)
    present=sum(1 for x in records if local_path(x.get('local_file')) and local_path(x.get('local_file')).exists()); local_count+=present; summary.append((name,len(records),present))
    records=sorted(records,key=lambda x:(-(x.get('year') or 0),str(x.get('title') or ''))); cards=[]
    for item in records:
        p=local_path(item.get('local_file'))
        if p and p.exists(): availability='本地 PDF'
        elif item.get('pdf_url'): availability='公开 PDF 链接'
        else: availability='仅目录/题录'
        extras=[]; src=item.get('source_url') or item.get('landing_url')
        if src: extras.append(('题录/来源',src,True))
        if not (p and p.exists()) and item.get('pdf_url'): extras.insert(0,('公开 PDF',item['pdf_url'],True))
        search_extra=' '.join(str(x) for x in (item.get('authors',[]) or []))
        cards.append(card_html(item,base=root/'专题文献',tag=availability,local=p if p and p.exists() else None,extra_links=extras,search_extra=search_extra))
    collection_sections.append(f'<section class="group" data-group><div class="group-head"><h2>{esc(name)}</h2><span class="n">{len(records)} 条 · {present} 份本地 PDF</span></div><p class="lede">{esc(desc)}；按年份倒序，来源脉络保持独立。</p><div class="paper-grid">{"".join(cards)}</div></section>')
profile_page=f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>作者与机构文献库</title><style>{css}</style></head><body><main class="wrap"><header class="hero"><div class="eyebrow">Author & Institution Collections</div><h1>作者与机构文献库</h1><p>按原始收集来源分别展示，不与主线主题目录混排。可以搜索论文编号、作者、标题、年份或会议；本地 PDF 与公开来源分别标出。</p><div class="stats"><div class="stat"><strong>{collection_records}</strong><span>条文献记录</span></div><div class="stat"><strong>{local_count}</strong><span>份本地 PDF</span></div><div class="stat"><strong>{len(collections)}</strong><span>来源分组</span></div></div></header><div class="actions"><a class="button" href="../00_阅读入口.html">回到阅读入口</a><a class="button secondary" href="../08_论文主题分类.html">主线主题目录</a></div><div class="tableish">{"".join(f'<div class="mini"><strong>{esc(n)}</strong><span>{c} 条记录 · {p} 份本地 PDF</span></div>' for n,c,p in summary)}</div><div class="searchbar"><input id="paperSearch" type="search" placeholder="搜索论文编号、标题、作者、年份或会议"></div><div id="emptyResults" class="empty">没有找到匹配的论文。</div>{''.join(collection_sections)}<section class="section"><div class="note">来源集合按作者/机构保留。主线目录会与这里存在少量主题重合；两边分别服务于按研究方向查找和按来源追溯。</div></section><footer class="footer"><a href="../00_阅读入口.html">阅读入口</a> · <a href="../08_论文主题分类.html">主题分类</a> · 原始清单：<a href="何恺明/manifest.json">何恺明</a> · <a href="武汉理工AI_CCF-A/manifest.json">武汉理工</a> · <a href="赖思邈/manifest.json">赖思邈</a></footer></main>{script}</body></html>'''
(root/'专题文献'/'00_作者机构文献索引.html').write_text(profile_page,encoding='utf-8')

entry_path=root/'00_阅读入口.html'; backup_dir=root/'_work'/'archive'; backup_dir.mkdir(parents=True,exist_ok=True); backup_path=backup_dir/'00_阅读入口_改版前_2026-11-06.html'
if not backup_path.exists() and entry_path.exists(): shutil.copy2(entry_path,backup_path)
entry=f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>论文阅读入口</title><style>{css}</style></head><body><main class="wrap"><header class="hero"><div class="eyebrow">Research Library · Navigation</div><h1>论文阅读入口</h1><p>先按研究主题找主线论文；作者与机构收藏保持单独检索。精读、迁移路线和全文文本放在辅助材料区，入口只保留常用路径。</p><div class="stats"><div class="stat"><strong>34</strong><span>主线论文全文</span></div><div class="stat"><strong>11</strong><span>GNN / Transformer 专题</span></div><div class="stat"><strong>8</strong><span>补充对照论文</span></div><div class="stat"><strong>119</strong><span>作者/机构文献记录</span></div></div></header><section class="section"><h2>从这里开始</h2><p class="lede">按你现在要做的事选一个入口，不需要先翻清单或工作文件。</p><div class="grid"><article class="card"><div class="count">主线 + 关联专题</div><h3>按研究主题浏览</h3><p>34 篇主线论文、11 篇 GNN/Transformer 专题和 8 篇补充对照，附关键机制与 PDF 链接。</p>{link('打开主题分类','08_论文主题分类.html','button')}</article><article class="card"><div class="count">单独来源库</div><h3>按作者或机构查找</h3><p>119 条来源记录，按何恺明、武汉理工 AI CCF-A、赖思邈分组；显示本地 PDF 与公开来源。</p>{link('打开作者/机构文献库','专题文献/00_作者机构文献索引.html','button')}</article><article class="card"><div class="count">建议阅读次序</div><h3>优先阅读与迁移路线</h3><p>从代表机制到可验证的小规模实验，说明先读什么、要比较什么。</p>{link('查看阅读路线','06_优先阅读与迁移路线.html','button secondary')}</article></div></section><section class="section"><h2>精读与检索</h2><div class="tableish"><div class="mini"><strong>36 篇截图条目</strong><span>{link('截图论文索引','01_截图论文索引.html')} · {link('逐篇精读汇编','02_逐篇精读汇编.html')}</span></div><div class="mini"><strong>GNN / Transformer</strong><span>{link('11 篇专题精读','05_GNN与Transformer融合专题.html')}</span></div><div class="mini"><strong>原文逐页文本</strong><span>{link('全文提取索引','07_原文全文提取索引.html')}</span></div><div class="mini"><strong>研究方向与项目判断</strong><span>{link('研究投入建议','03_研究投入建议.html')} · {link('8 篇补充对照','04_补充对照论文.html')}</span></div></div></section><section class="section"><h2>目录说明</h2><div class="note">分类页只新增主题导航，论文仍链接到现有 PDF 路径；作者/机构索引保留来源分组。清单、精读和原文提取文件都保留原位，避免重复存放同一份论文。</div></section><footer class="footer">先看 <a href="08_论文主题分类.html">主题分类</a>，再按需要进入 <a href="02_逐篇精读汇编.html">精读</a>、<a href="06_优先阅读与迁移路线.html">阅读路线</a> 或 <a href="07_原文全文提取索引.html">全文文本</a>。<br>核验记录和构建脚本仍在工作资料目录，不放在阅读入口。</footer></main></body></html>'''
entry_path.write_text(entry,encoding='utf-8')
readme='''请用浏览器打开同目录的 00_阅读入口.html。\n\n按主题找论文：08_论文主题分类.html（34 篇主线 + 11 篇 GNN/Transformer + 8 篇补充对照）。\n按作者/机构找论文：专题文献/00_作者机构文献索引.html（119 条记录；本地 PDF 和公开来源分开标注）。\n\n精读与原文：01_截图论文索引.html、02_逐篇精读汇编.html、05_GNN与Transformer融合专题.html、07_原文全文提取索引.html。\n研究路线：06_优先阅读与迁移路线.html；方向审查：03_研究投入建议.html；补充对照：04_补充对照论文.html。\n\n主题索引只提供分类和原文链接，不移动原 PDF；作者/机构索引保留原收集来源。\n'''
(root/'请先打开阅读入口.txt').write_text(readme,encoding='utf-8')
print('Generated:')
print('  08_论文主题分类.html | core PDFs:',len(main_papers),'| graph papers:',len(graph_data),'| supplements:',len(supp_data))
print('  专题文献/00_作者机构文献索引.html | records:',collection_records,'| local PDFs:',local_count,'| groups:',summary)
print('  00_阅读入口.html | previous copy:',backup_path.exists())


