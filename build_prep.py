from pathlib import Path
import os,json,re,shutil,hashlib,collections,html,zipfile,subprocess
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,KeepTogether
from pypdf import PdfReader,PdfWriter
from prep_content import MANUAL,ALGORITHMS,CHEAT,INTRO

BASE=Path(r'C:\Users\CAI BIN\Desktop\1')
WORK=BASE/'_work'
OUT=BASE/'美赛建模面试备考包_20261105'
OUT.mkdir(exist_ok=True)
for d in ['原始资料','训练论文','资料索引']:(OUT/d).mkdir(exist_ok=True)
pdfmetrics.registerFont(TTFont('Chinese',r'C:\Windows\Fonts\simsun.ttc',subfontIndex=0))
pdfmetrics.registerFont(TTFont('ChineseBold',r'C:\Windows\Fonts\simhei.ttf'))
pdfmetrics.registerFontFamily('Chinese',normal='Chinese',bold='ChineseBold',italic='Chinese',boldItalic='ChineseBold')
W,H=A4
WIDTH=W-102
styles={
 'title':ParagraphStyle('title',fontName='ChineseBold',fontSize=20,leading=28,spaceAfter=14,textColor=colors.black,wordWrap='CJK',keepWithNext=True),
 'lead':ParagraphStyle('lead',fontName='ChineseBold',fontSize=11.3,leading=18,spaceAfter=11,textColor=colors.HexColor('#183b56'),wordWrap='CJK',keepWithNext=True),
 'h':ParagraphStyle('h',fontName='ChineseBold',fontSize=12.4,leading=18.5,spaceBefore=8,spaceAfter=5,textColor=colors.black,wordWrap='CJK',keepWithNext=True),
 'p':ParagraphStyle('p',fontName='Chinese',fontSize=11,leading=17.8,spaceAfter=7.5,textColor=colors.black,wordWrap='CJK'),
 'english':ParagraphStyle('english',fontName='Times-Roman',fontSize=11.5,leading=16,spaceAfter=10),
 'cell':ParagraphStyle('cell',fontName='Chinese',fontSize=10,leading=15.2,spaceAfter=0,wordWrap='CJK'),
 'headcell':ParagraphStyle('headcell',fontName='ChineseBold',fontSize=10,leading=15.2,textColor=colors.white,wordWrap='CJK'),
 'src':ParagraphStyle('src',fontName='Chinese',fontSize=8.2,leading=12.3,spaceBefore=10,spaceAfter=3,textColor=colors.HexColor('#555555'),wordWrap='CJK',splitLongWords=True),
 'formula':ParagraphStyle('formula',fontName='Times-Roman',fontSize=14,leading=22,spaceBefore=4,spaceAfter=10,leftIndent=20),
}

def para(s,sty='p'):
    s=str(s)
    if s.startswith('“') and s.endswith('”'):s=s[1:-1]
    return Paragraph(html.escape(s).replace('\n','<br/>'),styles[sty])

def make_table(headers,rows):
    n=len(headers)
    if n==2: ratios=[.24,.76]
    elif n==3: ratios=[.20,.34,.46]
    else: ratios=[.27,.23,.18,.32]
    if headers==['证据层','Q3','Q4']:ratios=[.24,.38,.38]
    if headers==['材料','记住的方法','一句话理解']:ratios=[.23,.29,.48]
    data=[[para(x,'headcell') for x in headers]]+[[para(x,'cell') for x in r] for r in rows]
    t=Table(data,colWidths=[WIDTH*v for v in ratios],repeatRows=1,hAlign='LEFT')
    cmd=[('BACKGROUND',(0,0),(-1,0),colors.HexColor('#24465c')),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('GRID',(0,0),(-1,-1),.45,colors.HexColor('#d9d9d9')),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]
    for i in range(2,len(data),2):cmd.append(('BACKGROUND',(0,i),(-1,i),colors.HexColor('#f2f5f7')))
    t.setStyle(TableStyle(cmd));return t

def footer(c,d):
    c.setFont('Chinese',8);c.setFillColor(colors.HexColor('#666666'))
    c.drawString(51,30,'美赛建模方向面试准备  2026年11月5日')
    c.drawRightString(W-51,30,str(d.page))

def build(name,pages):
    story=[];txt=[]
    for num,(title,blocks) in enumerate(pages):
        if num:story.append(PageBreak())
        story.append(para(title,'title')); txt+=['\n'+'='*24,title,'='*24]
        for kind,data in blocks:
            if kind=='table':
                story += [make_table(*data),Spacer(1,9)]
                txt+=[' | '.join(data[0])]+[' | '.join(row) for row in data[1]]
            elif kind=='steps':
                for i,v in enumerate(data,1):story.append(para(f'{i}. {v}'));txt.append(f'{i}. {v}')
            elif kind=='qa':
                story += [para(data[0],'h'),para(data[1])];txt += [data[0],data[1]]
            else:
                story.append(para(data,kind));txt.append(data)
    doc=SimpleDocTemplate(str(OUT/(name+'.pdf')),pagesize=A4,rightMargin=51,leftMargin=51,topMargin=45,bottomMargin=48,title=name,author='蔡斌',pageCompression=1)
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
    (OUT/(name+'.txt')).write_text('\n\n'.join(txt),encoding='utf-8-sig')
    print(name,'pages',len(PdfReader(str(OUT/(name+'.pdf'))).pages))

build('01_临场速记',CHEAT)
build('02_面试完整准备',MANUAL)
build('03_常见算法通俗速记',ALGORITHMS)
(OUT/'04_三分钟自我介绍.txt').write_text('\n\n'.join(INTRO),encoding='utf-8-sig')
print('Intro Chinese characters',sum(len(re.findall(r'[\u4e00-\u9fff]',p)) for p in INTRO))

meta=json.loads((WORK/'source_meta.json').read_text(encoding='utf8'))
copylist=[
('B_submission','原始资料/国赛B题_最终提交版_完整103页.pdf'),
('B_problem','原始资料/2026国赛B题_原题.pdf'),
('stat_certificate','原始资料/统计建模_湖北赛区一等奖证书.pdf'),
('train2','训练论文/01_临时工招聘与排班.pdf'),('train5','训练论文/02_芯片微通道热管理.pdf'),
('train9','训练论文/03_算电协同调度.pdf'),('train11','训练论文/04_材料切割加工.pdf'),('train14','训练论文/05_物流分拣排班.pdf')]
manifest=[]
def copy(src,dest,label=''):
    src=Path(src);dest=OUT/dest
    if not src.is_file():raise FileNotFoundError(src)
    dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists():
        assert hashlib.sha256(dest.read_bytes()).hexdigest()==hashlib.sha256(src.read_bytes()).hexdigest(),('copy differs',str(dest))
    else:
        shutil.copy2(src,dest)
    sh=hashlib.sha256(dest.read_bytes()).hexdigest()
    assert sh==hashlib.sha256(src.read_bytes()).hexdigest()
    manifest.append({'label':label or dest.stem,'source':str(src),'copy':str(dest.relative_to(OUT)),'sha256':sh,'bytes':dest.stat().st_size})

for key,dest in copylist:copy(meta[key]['path'],dest)
B=Path(r'D:\Project\shuxuejianmo\B')
for src,dest in [
 (B/'FACT_TABLE.md','原始资料/B题_最终事实表.md'),(B/'FINAL_STATUS.md','原始资料/B题_最终状态.md'),
 (B/'research/OFFICIAL_RESULTS.csv','原始资料/B题_六局正式测试台账.csv'),
 (B/'output/runners/q3_q4_final_round_20260913.zip','原始资料/B题_Final程序包.zip'),
 (Path(r'C:\Users\CAIBIN~1\AppData\Local\Temp\codex-clipboard-f307af4c-72cd-4d88-b5b9-9bf8a3259fa2.png'),'原始资料/面试安排_原截图.png'),
 (Path(r'D:\ball_castle\数模论文\支撑材料.zip'),'原始资料/B题_提交支撑材料.zip'),
 (Path(r'D:\Software\Wechat\xwechat_files\wxid_w6hshsa9tghs22_af19\msg\file\2026-06\ST_RAO_统计建模答辩问答完整版.docx'),'原始资料/统计建模_原有答辩问答.docx')]:copy(src,dest)

reader=PdfReader(meta['B_submission']['path']);writer=PdfWriter()
for page in reader.pages[:27]:writer.add_page(page)
writer.add_metadata({'/Title':'国赛B题面试阅读节选 第1至27页','/Author':'原论文节选'})
with (OUT/'原始资料/国赛B题_面试阅读节选_第1至27页.pdf').open('wb') as f:writer.write(f)

# Expand the filename search with the known project and nearby, relevant training material.
paths=(WORK/'all_paths.txt').read_text(encoding='utf8').splitlines()
pattern=re.compile(r'数学建模|数模|统计建模|美赛|国赛|建模竞赛|建模比赛|CUMCM|MCM.?ICM|shuxuejianmo|翔宇杯|ST.?RAO|GP2SFCA|RVS.?MCLP|数学工具',re.I)
related=sorted(set(p for p in paths if pattern.search(p) and 'quark-agent' not in p))
documents=[p for p in related if Path(p).suffix.lower() in ['.pdf','.docx','.doc','.pptx','.ppt','.tex','.md','.txt','.zip','.rar','.7z']]
(OUT/'资料索引/全部相关文件路径.txt').write_text('\n'.join(related),encoding='utf-8-sig')
(OUT/'资料索引/论文文档与压缩包路径.txt').write_text('\n'.join(documents),encoding='utf-8-sig')
(OUT/'资料索引/精选资料来源与SHA256.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
stats=json.loads((WORK/'scan_stats.json').read_text(encoding='utf8'))
stats['related_paths']=len(related);stats['document_archive_paths']=len(documents)
stats['notes']='C、D盘可访问非系统路径检索；退出码2表示存在未能访问的路径。文件名与目录匹配后重点阅读，未逐一读取全部文件正文。路径包含重复、历史记录、实验数据。'
(OUT/'资料索引/检索范围.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2),encoding='utf8')

rootgroups=collections.Counter()
for p in related:
    if 'D:\\Project\\shuxuejianmo\\' in p:rootgroups['数模项目 / '+p.split('shuxuejianmo\\',1)[1].split('\\',1)[0]]+=1
    elif '\\Wechat\\' in p:rootgroups['微信已下载附件']+=1
    elif '\\Downloads\\' in p:rootgroups['下载目录']+=1
    elif '\\OneDrive\\' in p:rootgroups['OneDrive本地备份']+=1
    else:rootgroups['其他匹配资料']+=1

def link(path,label=None):
    p=Path(path)
    return f'<a href="{html.escape(p.as_uri(),quote=True)}">{html.escape(label or p.name)}</a>'

cards=[]
for name,desc in [('01_临场速记.pdf','2页：进场前只看这一份'),('02_面试完整准备.pdf','自我介绍、国赛四问、追问、数据和模拟面试'),('03_常见算法通俗速记.pdf','5页：算法的用途、直觉与适用条件'),('04_三分钟自我介绍.txt','可直接修改和朗读')]:
    cards.append(f'<article><h3><a href="{name}">{name}</a></h3><p>{desc}</p></article>')
rows=''.join('<tr><td>'+html.escape(m['label'])+'</td><td><a href="'+html.escape(m['copy'].replace('\\','/'),quote=True)+'">打开副本</a></td><td>'+link(m['source'],'原始位置')+'</td></tr>' for m in manifest)
extra=[
(r'D:\Project\shuxuejianmo','完整数模项目与暑期训练'),
(r'D:\Project\shuxuejianmo\B\src\radioclear','B题几何、覆盖、策略与路线源代码'),
(r'D:\Project\shuxuejianmo\B\tests','B题原有测试资料'),
(r'D:\Project\shuxuejianmo\B\research','B题推导、对照实验与验证记录'),
(r'D:\Project\shuxuejianmo\example','往届国一参考论文'),
(r'D:\Project\shuxuejianmo\A','A题药材烘干材料'),
(r'C:\Users\CAI BIN\Downloads\数学工具.pdf','数学工具 PDF'),
(meta['stat_paper']['path'],'翔宇杯案例材料'),
(meta['B_print']['path'],'B题9月29日纸质打印版'),
(r'D:\ball_castle\learn\数据分析','数据分析学习目录'),
(r'D:\OneDrive\Документы\CUMCM\backup','国赛提交本地备份')]
extrahtml=''.join('<li>'+link(p,l)+'</li>' for p,l in extra if Path(p).exists())
source_links=[('COMAP 2027规则','https://www.contest.comap.com/undergraduate/contests/mcm/instructions.html'),('COMAP AI政策','https://www.contest.comap.com/undergraduate/contests/mcm/flyer/Contest_AI_Policy.pdf'),('SciPy整数规划','https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.milp.html'),('scikit-learn交叉验证','https://scikit-learn.org/stable/modules/cross_validation.html'),('scikit-learn高斯过程','https://scikit-learn.org/stable/modules/gaussian_process.html')]
webhtml=''.join(f'<li><a href="{u}">{t}</a></li>' for t,u in source_links)
summary='、'.join(f'{html.escape(k)} {v}项' for k,v in rootgroups.most_common())
page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>蔡斌 美赛建模面试资料导航</title><style>
body{font-family:Arial,"Microsoft YaHei",sans-serif;max-width:1100px;margin:40px auto;padding:0 24px;color:#172c3a;line-height:1.7;background:#f6f8fa}h1{font-size:32px}h2{margin-top:38px}a{color:#145c8a;text-underline-offset:3px}.meta{font-size:18px}.cards{display:grid;grid-template-columns:repeat(2,1fr);gap:14px}article{background:white;border:1px solid #d9e1e7;border-radius:10px;padding:16px}h3{margin:0 0 8px}article p{margin:0}table{width:100%;border-collapse:collapse;background:white}td,th{padding:11px;border:1px solid #d9e1e7;text-align:left}th{background:#24465c;color:white}.notice{background:#eaf1f5;padding:16px;border-radius:8px}small{color:#526776}.filter{padding:12px;width:100%;box-sizing:border-box;font:inherit;border:1px solid #aabcc9;border-radius:6px;margin:12px 0}@media(max-width:650px){.cards{grid-template-columns:1fr}body{padding:0 12px;margin:18px auto}td{padding:7px}h1{font-size:26px}}@media print{body{background:white}.filter{display:none}}
</style><h1>美赛建模面试资料导航</h1><p class="meta">蔡斌 · 建模方向 · 2026年11月5日 14:00</p><p>南湖校区数学与统计楼，具体教室与顺序查QQ群。先练3分钟介绍，再练7分钟追问。</p><div class="cards">'''+''.join(cards)+'''</div><h2>主讲定位</h2><div class="notice">国赛B题全部建模：带误差的几何定位 → 连续覆盖与停止判断 → 路线和探测顺序优化。获奖状态表述为“已获推荐参加全国评阅”；统计建模另有湖北赛区本科生组一等奖证书。</div><h2>精选原件与训练资料</h2><p><a href="原始资料/国赛B题_面试阅读节选_第1至27页.pdf">先读B题第1至27页节选</a>。完整103页版保留代码与附录。下列“副本”均由原文件复制并核对哈希。</p><input class="filter" id="filter" placeholder="筛选，例如：B题、排班、芯片、证书"><table><thead><tr><th>资料</th><th>本包副本</th><th>来源</th></tr></thead><tbody id="files">'''+rows+'''</tbody></table><h2>继续查原始资料</h2><ul>'''+extrahtml+'''</ul><h2>全盘相关路径索引</h2><p>检索C、D盘可访问非系统资料，共枚举'''+str(sum(x['paths'] for x in stats['scanned'].values()))+'''条文件路径。依关键词与已确认的数模项目目录整理出'''+str(len(related))+'''条相关路径，其中论文、文档、源码说明与压缩包类'''+str(len(documents))+'''条。路径数包含重复副本、历史版本、实验数据，不能等同于独立成果数。</p><p>'''+summary+'''。</p><ul><li><a href="资料索引/全部相关文件路径.txt">全部相关文件路径</a></li><li><a href="资料索引/论文文档与压缩包路径.txt">论文文档与压缩包路径</a></li><li><a href="资料索引/精选资料来源与SHA256.json">精选资料来源及哈希</a></li><li><a href="资料索引/检索范围.json">检索范围及限制</a></li></ul><small>检索未强行访问受限区域，未扫描系统和软件依赖内容；未逐一读取所有历史文件正文。原文件保持原样。</small><h2>核对过的官方资料</h2><ul>'''+webhtml+'''</ul><p><small>规则核对日期：2026年11月5日。算法文件是口语复习资料，具体参数与成绩请回看对应原始论文。网页在本机即可使用，无需联网；官方链接除外。</small></p><script>document.getElementById('filter').addEventListener('input',e=>{const q=e.target.value.trim().toLowerCase();document.querySelectorAll('#files tr').forEach(r=>r.hidden=!r.textContent.toLowerCase().includes(q))})</script></html>'''
(OUT/'00_资料导航.html').write_text(page,encoding='utf8')
(OUT/'00_先看这里.txt').write_text('美赛建模方向面试备考包\n\n面试：2026年11月5日14:00，南湖校区数学与统计楼，教室与顺序查QQ群。\n\n建议顺序：\n1. 双击00_资料导航.html。\n2. 练04_三分钟自我介绍.txt。\n3. 读02_面试完整准备.pdf的国赛四问与追问。\n4. 读03_常见算法通俗速记.pdf。\n5. 进场前只看01_临场速记.pdf。\n\nPDF均有同名TXT，可修改、复制或在手机上查看。原始资料中保留最终论文、原题、证书、程序和提交支撑材料，训练论文单列。全部相关路径在资料索引中。\n\n国赛状态：推国奖，表述为已获推荐参加全国评阅。\n个人分工：全部建模，已由本人确认。\n最终Q4为21站。较早25站稿件不用于面试。\n',encoding='utf-8-sig')
(WORK/'package_stats.json').write_text(json.dumps({'related':len(related),'documents':len(documents),'groups':rootgroups,'copied':len(manifest),'out':str(OUT)},ensure_ascii=False,indent=2),encoding='utf8')
print('PACKAGE',json.dumps({'related':len(related),'documents':len(documents),'groups':rootgroups,'copied':len(manifest)},ensure_ascii=False))
