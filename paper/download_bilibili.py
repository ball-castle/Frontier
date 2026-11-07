import concurrent.futures, hashlib, json, re, time, urllib.request, sys, unicodedata
from pathlib import Path
import fitz

ROOT = Path(__file__).resolve().parent
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
# Entries identified against primary source records, 2026-11-05.
DATA = [
(1,8,'Look Only When Needed: Certificate-Guided Visual Routing for Efficient Diffusion VLMs','2610.36671','',False,'arXiv预印本；截图线索Only visit并非正式标题。','按无图预测与最近有图预测的一致性认证复用视觉，并自适应确定解掩码数量；训练免费。'),
(2,8,'Efficiently Reconstructing Dynamic Scenes One D4RT at a Time','','https://openaccess.thecvf.com/content/CVPR2026/papers/Zhang_Efficiently_Reconstructing_Dynamic_Scenes_One_D4RT_at_a_Time_CVPR_2026_paper.pdf',True,'CVPR 2026, pp.7382–7392，CVF会议记录核验。','单一视频编码和统一查询解码接口，按任意时空点查询3D位置，避免逐帧密集解码。'),
(3,8,'PointCNN++: Performant Convolution on Native Points','2511.23227','https://openaccess.thecvf.com/content/CVPR2026/papers/Li_PointCNN_Performant_Convolution_on_Native_Points_CVPR_2026_paper.pdf',True,'CVPR 2026, pp.24151–24161，CVF会议记录核验。','保留原始点坐标精度，以矩阵向量乘法和归约定制GPU算子，在点上直接卷积。'),
(4,8,'Outcome-Grounded Advantage Reshaping for Fine-Grained Credit Assignment in Mathematical Reasoning','2601.07408','https://aclanthology.org/2026.acl-long.1132.pdf',True,'ACL 2026会议论文由ACL Anthology核验。','用反事实扰动或输入梯度度量token对最终答案的敏感性，保总优势质量地重分配GRPO优势。'),
(5,8,'Looped Transformers as Programmable Computers','2301.13196','https://proceedings.mlr.press/v202/giannou23a/giannou23a.pdf',True,'ICML 2023, PMLR202:11398–11442。','常数深度共享权重Transformer循环执行指令，实现条件分支、程序计数器及反向传播。'),
(6,9,'Vision Transformers are Circulant Attention Learners','2512.21542','',True,'AAAI 2026 40(26):21549–21557；https://ojs.aaai.org/index.php/AAAI/article/view/39303。','视觉attention近似块循环矩阵，显式BCCB参数化以O(N log N)计算。'),
(7,9,'ReHyAt: Recurrent Hybrid Attention for Video Diffusion Transformers','2601.04342','https://openaccess.thecvf.com/content/CVPR2026/papers/Ghafoorian_ReHyAt_Recurrent_Hybrid_Attention_for_Video_Diffusion_Transformers_CVPR_2026_paper.pdf',True,'CVPR 2026, pp.40674–40684。官方项目称Wan2.1 1.3B蒸馏约160GPU小时。','局部关键token保留softmax、全局使用线性attention；块递归可恒定内存，利用预训练模型蒸馏。'),
(8,9,'Recurrent Autoregressive Diffusion: Global Memory Meets Local Attention','2511.12940','',False,'作者项目页标注ECCV2026；待确认正式会议条目，勿将项目页声明等同会议记录。','LSTM全局记忆与局部重叠窗口attention结合；clean-frame memory及训练推理一致的逐帧递归。'),
(9,9,'Latent-Foresight: End-to-End Learning Predictable Representations for Latent World Models','2610.01942','',False,'2026-10 arXiv预印本。','联合优化latent tokenizer与flow动态预测器，让压缩空间同时可重建和可预测，防止latent坍缩。'),
(10,9,'ELT: Elastic Looped Transformers for Visual Generation','2604.09168','',True,'ECCV2026 Springer DOI 10.1007/978-3-032-37324-3_17。','共享Transformer跨loop迭代，最大循环教师对中间循环自蒸馏，支持可变推理计算量。'),
(11,9,'How Far Can Coding Agents Go in Visual Generation?','2610.19025','',False,'2026-10 arXiv预印本；200-prompt AgentDrawBench，结构质量与感知质量分开衡量。','以可执行视觉程序作为外部视觉思维表征，研究代码绘图能力、测试时扩展及跨接口一致性。'),
(12,9,'VISTA: A Visual Harness for Reasoning in an Interactive World','2610.02200','',False,'2026-10 arXiv预印本；MIT作者和https://github.com/joshhhhan/VISTA与截图吻合。','保留原始视觉观察的无损外部记忆，模型主动检索和重组视觉输入以完成长程交互任务。'),
(13,9,'Eat Your Precision: Precision Objective Mitigates Reward Hacking in Rubric-based RL','2610.33512','',False,'2026-10 arXiv预印本。','FORK同时优化rubric召回和必要性、事实准确性精度，抑制冗长答案的奖励投机。'),
(14,10,'Function-Space Temporal Self-Distillation for Policy Optimization','2610.19687','',False,'2026-10 arXiv预印本；Aryan Das, Arnab Bhattacharya, Vinay Kumar Verma。','以稀疏历史next-token分布保存时序教师目标；单策略结合特权反馈适应，避免额外常驻EMA模型。'),
(15,10,'Can Test-Time Memory Evolution Outperform Test-Time Training for Scientific Discovery?','2610.32046','',False,'2026-10 arXiv预印本；实验限论文考察的数学发现任务，不可外推所有任务。','固定权重，执行反馈更新指导记忆与成功策略记忆；同框架对照TTT并比较FLOPs和时间。'),
(16,10,'Can Discrete Tokens Serve as Semantically Lossless Representations of Visual Signals?','2610.37662','',False,'2026-10 arXiv预印本；semantically lossless是下游理解代理指标结论，不是信息论无损。','FVQ对互补固定维度视图使用并行码本；有效比特预算比量化MSE更能解释语义质量。'),
(17,10,'Symmetry in language statistics shapes the geometry of model representations','','https://raw.githubusercontent.com/mlresearch/v306/main/assets/karkada26a/karkada26a.pdf',True,'ICML2026, PMLR306:56137–56172；正式会议记录核验。','语言共现统计的平移对称性决定低维表征几何，潜在连续变量使几何对统计扰动稳健。'),
(18,10,'Building AI Research Teams for Autonomous Discovery of Linear Attention Architectures','2610.28887','',False,'2026-10 arXiv预印本。','不同学科研究代理、私有持久历史、共享实验证据与自适应算力分配协同搜索线性attention架构。'),
(19,11,'Meta Expert: Cross-Layer Expert Sharing for Storage- and Retrieval-Efficient MoE','2610.27598','',False,'2026-10 arXiv预印本。','跨层共享专家池减少参数冗余，给隐状态更灵活的残差检索路径；对照固定激活量和专家粒度。'),
(20,11,'UniverSat: Resolution- and Modality-Agnostic Transformers for Earth Observation','2606.23503','',False,'作者项目页及官方模型卡标注NeurIPS2026录用；会议正式记录待核验。','Universal Patch Encoder用同套权重接收任意空间、光谱和时间分辨率，多传感器自监督学习。'),
(21,11,'DeepInfer','','',False,'开源软件项目，非已确认的独立论文。官方README未提供专属PDF，故不伪造论文。','推理系统含并行调度、稀疏/滑窗优化、置信度调度验证、batch不变推理；适合作工程基线。'),
(22,12,'Mixture-of-Top-k Attention: Efficient Attention via Scalable Fast Weights','2602.01219','',False,'作者官方代码库标注NeurIPS2026录用；视频标题“注意力层不存在”是夸张转述。','把attention视为输入诱导的快权重MLP；少量landmark query形成可复用top-k专家，加共享压缩专家。'),
]

def entry(row):
    i,shot,title,arxiv,pdf,pub,note,idea=row
    if arxiv: source='https://arxiv.org/abs/'+arxiv
    elif i==2: source=pdf.replace('/papers/','/html/').replace('.pdf','.html')
    elif i==17: source='https://proceedings.mlr.press/v306/karkada26a.html'
    else: source='https://github.com/deepseek-ai/DeepInfer'
    name=re.sub(r'[^A-Za-z0-9]+','_',title).strip('_')[:125]
    return dict(id='B%02d'%i,title=title,screenshot=shot,confidence='high',source_url=source,pdf_url=pdf or ('https://arxiv.org/pdf/'+arxiv if arxiv else None),local_file=None,publication_verified=pub,notes=note,key_idea=idea,arxiv_id=arxiv or None,download_status='pending' if i!=21 else 'not_a_paper',filename='B%02d_%s.pdf'%(i,name))

entries=[entry(x) for x in DATA]

def download(e):
    if not e['pdf_url']: return e
    path=ROOT/e['filename']
    candidates=[e['pdf_url']]
    if e['arxiv_id'] and 'arxiv.org/pdf/' not in e['pdf_url']: candidates.append('https://arxiv.org/pdf/'+e['arxiv_id'])
    for url in candidates:
        try:
            if path.exists() and path.read_bytes()[:5]==b'%PDF-': data=path.read_bytes()
            else:
                req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 (Academic bibliography download)'})
                with urllib.request.urlopen(req,timeout=100) as r: data=r.read()
            if not data.startswith(b'%PDF-'): raise ValueError('not PDF magic: '+repr(data[:80]))
            doc=fitz.open(stream=data,filetype='pdf')
            first=doc[0].get_text()
            normalized=lambda s: re.sub('[^a-z0-9]','',unicodedata.normalize('NFKD',s).lower())
            titleok=normalized(e['title']) in normalized(first)
            if not titleok:
                words=[w.lower() for w in re.findall('[A-Za-z]+',e['title']) if len(w)>3]
                titleok=sum(w in first.lower() for w in words)>=max(3,len(words)*.85)
            if not titleok: raise ValueError('first-page title mismatch: '+first[:400])
            path.write_bytes(data)
            e.update(local_file=str(path).replace('\\','/'),download_status='verified',download_url=url,pdf_magic_verified=True,title_verified=True,pages=len(doc),size_bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),first_page_excerpt=first[:1000])
            (ROOT/'_checks').mkdir(exist_ok=True)
            doc[0].get_pixmap(matrix=fitz.Matrix(.8,.8)).save(str(ROOT/'_checks'/(e['id']+'_first.png')))
            print(e['id']+' OK '+str(len(doc))+' pages '+e['title'],flush=True)
            return e
        except Exception as ex: e['download_error']=str(ex)
    e['download_status']='failed'
    print(e['id']+' FAILED '+e.get('download_error',''),flush=True)
    return e

if __name__=='__main__':
    ROOT.mkdir(parents=True,exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool: entries=list(pool.map(download,entries))
    (ROOT/'bilibili_manifest.json').write_text(json.dumps(entries,ensure_ascii=False,indent=2),encoding='utf-8')
    print('DONE '+str(sum(e['download_status']=='verified' for e in entries))+'/'+str(len(entries)),flush=True)
