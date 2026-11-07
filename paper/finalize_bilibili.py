import json, re, unicodedata
from pathlib import Path
import fitz
root=Path(__file__).resolve().parent
path=root/'bilibili_manifest.json'
entries=json.loads(path.read_text(encoding='utf-8'))
pub={
'B02':('CVPR 2026','https://openaccess.thecvf.com/content/CVPR2026/html/Zhang_Efficiently_Reconstructing_Dynamic_Scenes_One_D4RT_at_a_Time_CVPR_2026_paper.html'),
'B03':('CVPR 2026','https://openaccess.thecvf.com/content/CVPR2026/html/Li_PointCNN_Performant_Convolution_on_Native_Points_CVPR_2026_paper.html'),
'B04':('ACL 2026','https://aclanthology.org/2026.acl-long.1132/'),
'B05':('ICML 2023','https://proceedings.mlr.press/v202/giannou23a.html'),
'B06':('AAAI 2026','https://ojs.aaai.org/index.php/AAAI/article/view/39303'),
'B07':('CVPR 2026','https://openaccess.thecvf.com/content/CVPR2026/html/Ghafoorian_ReHyAt_Recurrent_Hybrid_Attention_for_Video_Diffusion_Transformers_CVPR_2026_paper.html'),
'B08':('ECCV 2026','https://eccv.ecva.net/Conferences/2026/AcceptedPapers'),
'B10':('ECCV 2026','https://doi.org/10.1007/978-3-032-37324-3_17'),
'B17':('ICML 2026','https://proceedings.mlr.press/v306/karkada26a.html'),
'B20':('NeurIPS 2026 accepted','https://neurips.cc/Downloads/2026'),
'B22':('NeurIPS 2026 accepted','https://neurips.cc/Downloads/2026')}
shots={9:'461148f8-d675-4901-9d70-4c5f329a38f2',10:'c529a870-0e68-4c28-ad51-547035974893',11:'32c7651c-39dd-49a4-a26c-752e20d4c960',12:'896a400d-308c-422f-a70c-d5957e2fdad6'}
for e in entries:
    e['verified_on']='2026-11-05'
    if e['id'] in pub:
        e['venue'],e['publication_url']=pub[e['id']]
        e['publication_verified']=True
    else:
        e['venue']='arXiv preprint; conference acceptance not verified' if e['pdf_url'] else 'software project'
        e['publication_url']=None
    if e['screenshot'] in shots: e['screenshot_file']='C:/Users/CAI BIN/AppData/Local/Temp/codex-clipboard-'+shots[e['screenshot']]+'.png'
    e['screenshot_occurrences']=[e['screenshot']]
    if e['id']=='B08': e['notes']='ECCV2026官方AcceptedPapers核验，Poster Session 2 #150；下载arXiv公开版。'
    if e['id']=='B20': e['notes']='NeurIPS2026官方Downloads列表收录；作者主页和模型卡也确认录用。当前为会议前录用状态，下载arXiv公开版。'
    if e['id']=='B22':
        e['notes']='NeurIPS2026官方Downloads列表收录（会议题名末段为Efficient Attention as Scalable Fast Weights；arXiv为via）；官方仓库与arXiv均确认录用。“注意力层不存在”为夸张视频标题。'
        e['screenshot_occurrences']=[11,12]
    if e['local_file']:
        with fitz.open(e['local_file']) as doc:
            text=doc[0].get_text()
            normalize=lambda x:re.sub('[^a-z0-9]','',unicodedata.normalize('NFKD',x).lower())
            e['exact_normalized_title_match']=normalize(e['title']) in normalize(text)
        assert Path(e['local_file']).read_bytes()[:5]==b'%PDF-'
        print(e['id'],e['exact_normalized_title_match'])
    e.pop('download_error',None)
path.write_text(json.dumps(entries,ensure_ascii=False,indent=2),encoding='utf-8')
print('VERIFIED',sum(e['download_status']=='verified' for e in entries),'PDFs;',sum(e['publication_verified'] for e in entries),'conference records')
