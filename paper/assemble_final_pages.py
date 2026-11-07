# -*- coding: utf-8 -*-
from pathlib import Path
from build_library import page, ROOT
from bs4 import BeautifulSoup
for body_name,out_name,title in [('portfolio_body.html','03_研究投入建议','研究投入建议'),('graph_topic_body.html','05_GNN与Transformer融合专题','GNN与Transformer融合专题'),('reading_route_body.html','06_优先阅读与迁移路线','优先阅读与迁移路线')]:
 p=ROOT/body_name
 if not p.exists():continue
 body=p.read_text(encoding='utf-8-sig')
 (ROOT/(out_name+'.html')).write_text(page(title,body),encoding='utf8')
 soup=BeautifulSoup(body,'html.parser')
 (ROOT/(out_name+'.txt')).write_text(soup.get_text('\n',strip=True),encoding='utf8')
(ROOT/'请先打开阅读入口.txt').write_text('请用浏览器打开同目录 00_阅读入口.html。\n\n02_逐篇精读汇编.html 是十组主材料；01_截图论文索引.html 可搜索；05 是11篇GNN与Transformer专题；06 是优先阅读和实验路线；03 是现有项目审查。\n\nPDF、截图、精读文本与结构化JSON均可离线打开。来源网页链接需联网。\n\nW06按主题独立补齐11篇，不再追溯公众号名单。W10 HorNet已保存2022会议原版，截图所指2026 TPAMI扩展版仅核准正式身份，未取得全文。DeepInfer为软件项目。\n',encoding='utf8')

from build_delivery_summary import build_home
build_home()
