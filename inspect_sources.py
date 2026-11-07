from pathlib import Path
import json,subprocess,hashlib,re,collections
from pypdf import PdfReader
from docx import Document
b=Path(r'C:\Users\CAI BIN\Desktop\1\_work'); b.mkdir(exist_ok=True)
root=Path(r'D:\Project\shuxuejianmo')
paths={
'B_final':root/'B/output/pdf/B题研究稿.pdf',
'B_submission':Path(r'D:\ball_castle\数模论文\B题.pdf'),
'B_print':Path(r'D:\Software\Wechat\xwechat_files\wxid_w6hshsa9tghs22_af19\msg\file\2026-09\2026数学建模B题纸质论文_打印版_9月29日.pdf'),
'B_problem':root/'B/B题/B题.pdf',
'train2':root/'7.25/output/pdf/第2题_大型展销会临时工招聘与排班优化.pdf',
'train5':root/'8.11/FINAL_DELIVERY/paper.pdf',
'train9':root/'8.19/Q9_FINAL_PROJECT/FINAL_DELIVERY/第9题_算电协同_最终论文.pdf',
'train11':root/'8.24/outputs/problem11_final/方形材料切割加工优化论文.pdf',
'train14':root/'8.28/outputs/problem14_final/物流分拣中心排班优化论文.pdf',
'stat_certificate':Path(r'C:\Users\CAI BIN\Downloads\第十二届统计建模大赛省赛证书.pdf'),
'stat_paper':Path(r'C:\Users\CAI BIN\Downloads\数据赋能与圈层优化-翔宇杯原有成果整合终稿-Round5.pdf'),
}
meta={}
for k,p in paths.items():
    if not p.exists(): continue
    r=PdfReader(str(p)); count=len(r.pages)
    res=subprocess.run(['pdftotext','-f','1','-l',str(min(count,26) if k.startswith('B_') else min(count,3)),'-layout',str(p),str(b/(k+'.txt'))],capture_output=True)
    meta[k]={'path':str(p),'pages':count,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
    print(k,json.dumps(meta[k],ensure_ascii=False))
    if not k.startswith('B_'): print((b/(k+'.txt')).read_text(encoding='utf8')[:2600])
(b/'source_meta.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf8')
for k,p in [('stat_qa',Path(r'D:\Software\Wechat\xwechat_files\wxid_w6hshsa9tghs22_af19\msg\file\2026-06\ST_RAO_统计建模答辩问答完整版.docx'))]:
    if p.exists():
        d=Document(p); s='\n'.join(x.text for x in d.paragraphs)+'\n'+'\n'.join(' | '.join(c.text for c in row.cells) for t in d.tables for row in t.rows)
        (b/(k+'.txt')).write_text(s,encoding='utf8'); print(k,s[:3000])
