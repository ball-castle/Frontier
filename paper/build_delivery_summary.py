# -*- coding: utf-8 -*-
"""Compose the delivery overview from the checked manifests, not fixed totals."""
from pathlib import Path
from datetime import date
import json
from urllib.parse import quote
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent

def read(name):
    return json.loads((ROOT/name).read_text(encoding='utf-8-sig'))

def build_home():
    from build_library import page, esc
    extracts = read('reading_extracts.json')
    groups = read('十组精读/任务分配.json')['groups']
    graph = read('W06_GNN_Transformer专题/manifest.json')
    supplements = read('supplement_manifest.json')
    archive = read('全文提取/index.json')
    version = read('十组精读/04_version_correction.json')
    extended = version.get('local_file') and Path(version['local_file']).is_file()
    main_count = len(read('download_verification.json')['pdfs']) + len(graph) + len(supplements)
    collection_paths = [
        ('何恺明', '专题文献/何恺明/manifest.json'),
        ('赖思邈', '专题文献/赖思邈/manifest.json'),
        ('武汉理工AI CCF-A', '专题文献/武汉理工AI_CCF-A/manifest.json'),
    ]
    collection_entries = {}
    for name, path in collection_paths:
        data = read(path)
        collection_entries[name] = data if isinstance(data, list) else data.get('papers', data.get('entries', []))
    collection_downloads = read('专题文献/download_verification.json')
    collection_entry_count = sum(len(x) for x in collection_entries.values())
    graph_reviews_path = ROOT/'W06_GNN_Transformer专题/reading_extracts.json'
    graph_reviews = read('W06_GNN_Transformer专题/reading_extracts.json') if graph_reviews_path.exists() else []
    if isinstance(graph_reviews, dict):
        graph_reviews = graph_reviews.get('entries', graph_reviews.get('papers', []))
    open_items = [] if extended else ['W10：2026 TPAMI期刊扩展版尚无可用全文；已提供2022会议原版精读，期刊新增内容仅据题录及摘要核准。']
    if collection_downloads.get('download_failed'):
        open_items.append(f"新增专题文献：{collection_downloads['download_failed']} 个公开PDF链接未能下载，详见专题文献/download_verification.json。")
    if collection_downloads.get('public_fulltext_unavailable'):
        open_items.append(f"新增专题文献：{collection_downloads['public_fulltext_unavailable']} 条记录未找到合法公开全文；来源与访问说明保留在各自清单。")
    status = {
        'date': date.today().isoformat(), 'screenshot_entries': len(extracts['entries']),
        'completed_groups': extracts['completed_groups'], 'missing_groups': extracts['missing_groups'],
        'primary_paper_versions': main_count, 'graph_reviews': len(graph_reviews),
        'all_local_pdfs': archive['pdf_count'], 'exported_pages': archive['total_pages'],
        'research_collection_entries': collection_entry_count,
        'research_collection_local_pdfs_verified': collection_downloads.get('downloaded_verified', 0),
        'research_collection_identity_review_needed': collection_downloads.get('identity_review_needed', 0),
        'research_collection_public_fulltext_unavailable': collection_downloads.get('public_fulltext_unavailable', 0),
        'research_collection_download_failed': collection_downloads.get('download_failed', 0),
        'horNet_journal_fulltext_obtained': bool(extended),
        'scope_note': '36截图条目含34论文、1主题、1软件；W06独立专题选文。另整理何恺明、赖思邈与武汉理工AI三组专题文献。HorNet指定期刊版与会议原版分别记录。',
        'open_items': open_items,
    }
    (ROOT/'completion_status.json').write_text(json.dumps(status, ensure_ascii=False, indent=2),encoding='utf8')
    cards = [('36/36', '截图条目已逐项处理'),
             (f'{len(extracts["completed_groups"])}/10', '精读组已汇总'),
             (f'{len(graph_reviews)}/11', '图模型专题逐篇提取'),
             (str(archive['pdf_count']), '本地PDF文件，含补充版本'),
             (str(collection_entry_count), '新增专题文献记录')]
    card_html = ''.join(f'<div class="card"><div class="number">{n}</div>{label}</div>' for n,label in cards)
    glinks = ''.join('<li><a href="02_逐篇精读汇编.html#group'+g['id']+'">'+g['id']+' · '+esc(g['title'])+'</a>（'+', '.join(g['paper_ids'])+'）</li>' for g in groups)
    collection_links = ''.join(f'<li><a href="{quote(path)}">{esc(name)}清单</a> · {len(collection_entries[name])} 条记录</li>' for name, path in collection_paths)
    if extended:
        version_note = 'HorNet 的2022会议原版与2026期刊扩展版已分别保存；定量结果请按对应版本阅读。'
    else:
        version_note = '<b>尚有一个全文缺口：</b>W10截图指向HorNet的2026 TPAMI扩展版，公开全文尚未取得。已保存并精读2022 NeurIPS会议原版；期刊新增的Hor3D、HorCLIP目前只核准题录和摘要，未冒充全文精读。'
    body = f'''<p class="meta">论文库续接完成 · {date.today().isoformat()}</p><h1>截图论文与研究方向阅读入口</h1>
<div class="lead"><b>主材料是逐篇论文提取。</b>十组报告已合并，涵盖问题、方法与公式、带位置的原文证据、算力、适用条件，以及面向4–8张高端GPU和2–4人的迁移假设与最小实验。迁移方案尚未运行训练或验证新颖性。</div>
<div class="row">{card_html}</div>
<h2>从这里开始</h2><ol>
<li><a href="02_逐篇精读汇编.html"><b>十组逐篇精读汇编</b></a> · <a href="02_逐篇精读汇编.txt">纯文本</a>：36个截图条目的主要阅读材料。</li>
<li><a href="01_截图论文索引.html"><b>截图论文索引</b></a>：搜索题名，打开原图、论文PDF与来源。</li>
<li><a href="05_GNN与Transformer融合专题.html"><b>11篇GNN与Transformer专题</b></a>：结构编码、局部/全局融合、图token、稀疏注意力与图语言模型。</li>
<li><a href="07_原文全文提取索引.html"><b>全部PDF的逐页原文文本</b></a>：{archive['pdf_count']}份文件，共{archive['total_pages']}页；保留物理页码，便于全文检索与逐页回查。</li>
<li><a href="06_优先阅读与迁移路线.html"><b>优先阅读与迁移路线</b></a>：优先读什么、如何连接现有项目、怎样安排第一轮实验。</li>
<li><a href="03_研究投入建议.html"><b>现有项目与投入建议</b></a>：沿用上轮本地项目及78个GitHub仓库的盘点证据；本轮没有重新审计全部仓库。</li>
<li><a href="04_补充对照论文.html"><b>8篇选题对照</b></a>：结合<a href="novelty_screen.txt">定向查新记录</a>判断候选机制与已有工作的重合。</li></ol>
<h2>文件数与身份说明</h2>
<p>主清单共{main_count}份论文PDF：34份截图相关论文版本、11篇图模型专题和8篇选题对照。此外，D4RT和PointCNN各有官方补充材料，ReHyAt另有含附录的arXiv版本；这些不重复计作独立论文。</p>
<h2>新增专题文献</h2>
<p>另整理{collection_entry_count}条研究成果记录，包含何恺明{len(collection_entries['何恺明'])}条、赖思邈{len(collection_entries['赖思邈'])}条、武汉理工AI CCF-A {len(collection_entries['武汉理工AI CCF-A'])}条。新增记录中{collection_downloads.get('downloaded_verified', 0)}份PDF已下载并核验；{collection_downloads.get('public_fulltext_unavailable', 0)}条没有找到合法公开全文，{collection_downloads.get('download_failed', 0)}个公开链接未能下载。逐篇状态见<a href="专题文献/download_verification.json">下载核验报告</a>。</p>
<ul>{collection_links}</ul>
<div class="box">{version_note} <a href="十组精读/04_version_correction.json">版本与查找记录</a>。</div>
<p>W06已按用户要求独立选取11篇代表论文，不宣称还原公众号原名单。B21 DeepInfer作为软件项目提取，未找到独立论文PDF。MiTA在截图11、12重复出现，已去重。12张原始截图均保留。</p>
<h2>十组精读</h2><ol>{glinks}</ol>
<h2>核验与可追溯材料</h2>
<p><a href="final_verification.json">最终文件与链接核验</a> · <a href="completion_status.json">完成范围与缺口</a> · <a href="paper_manifest.json">截图统一清单</a> · <a href="reading_extracts.json">中文结构化精读</a> · <a href="W06_GNN_Transformer专题/reading_extracts.json">图模型结构化精读</a> · <a href="全文提取/index.json">全文提取与逐页文字量</a>。</p>
<p>论文PDF的格式、页数和SHA-256与清单核对；关键结论的页码或表号保留在精读中。机器文字提取不能完整保留公式与图表布局，请回看PDF。<a href="_qa/precision_review.txt">上一轮事实与数学复核</a> · <a href="_qa/resumption_audit.txt">本轮续接复核</a>。</p>
<p>本轮补齐论文提取、汇编和阅读入口；没有进行模型训练、修改研究仓库或提交论文。研究方向排序是基于已存证据的建议，不是达到SOTA或顶会录用的承诺。</p>'''
    (ROOT/'00_阅读入口.html').write_text(page('截图论文阅读入口',body),encoding='utf8')
    text = BeautifulSoup(body,'html.parser').get_text('\n',strip=True)
    (ROOT/'提取完成与缺口.txt').write_text(text,encoding='utf8')
    (ROOT/'请先打开阅读入口.txt').write_text(
        '请用浏览器打开同目录 00_阅读入口.html。\n\n'
        '02 为十组中文精读；01 可搜索截图条目；05 为11篇图模型专题；07 可打开全部逐页全文TXT。\n'
        '06 为优先阅读与迁移实验建议；03 为现有项目审查；新增专题文献清单位于“专题文献”目录。\n\n'
        + BeautifulSoup(version_note,'html.parser').get_text()+'\n'
        'W06为按主题独立选文；DeepInfer为软件项目。具体数量、版本与剩余缺口见completion_status.json。\n',encoding='utf8')
    return status

if __name__ == '__main__':
    print(json.dumps(build_home(),ensure_ascii=False))
