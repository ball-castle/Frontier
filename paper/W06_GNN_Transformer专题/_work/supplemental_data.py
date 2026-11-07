"""Evidence checked against local PDFs; suggestions are not executed experiments."""

PROBLEMS = {
 'G01':'普通Transformer缺少图结构归纳偏置，怎样仅通过输入编码与注意力偏置改善分子图预测？',
 'G02':'怎样把位置编码、局部传播和全局注意力拆成可替换、可消融且能扩展的通用图架构？',
 'G03':'局部GNN很难把远距离关系传入图级读出，能否用后接的全局注意力补上这一环？',
 'G04':'无需专用图算子时，标准Transformer怎样从节点和边token识别关联关系，并获得较强的图表达能力？',
 'G05':'观测图可能异配、不完整或不存在；怎样可微地学习潜在全对连接，同时摆脱节点数的二次成本？',
 'G06':'怎样把大图节点分类转成可用mini-batch训练的短序列问题，并保留不同跳数的邻域信息？',
 'G07':'稠密全局注意力受显存限制，怎样用线性数量的通信边保留远距离传播能力？',
 'G08':'大图学习是否一定需要复杂深层全局注意力，还是一次简化全局传播已能取得竞争结果？',
 'G09':'怎样在可扩展成本内显式构造高阶多项式交互，并同时处理同配与异配图？',
 'G10':'图操作、采样与距离计算阻碍GPU利用率；怎样通过可复用索引将图处理与Transformer训练解耦？',
 'G11':'将节点文本压缩为一个向量会损失细节，怎样让预训练LLM直接同时利用完整文本和图拓扑？',
}

EXPERIMENTS = {
 'G01': [
  (7,'表1，PCQM4M-LSC验证集','Graphormer验证MAE为0.1234，GraphormerSMALL为0.1264，GIN-VN为0.1395；参数量分别47.1M、12.5M、6.7M。参数规模不一致，不能把全部差距单独归因于一种编码。'),
  (9,'表5，编码消融；训练协议见第8页','无结构编码验证MAE为0.2276；加空间编码为0.1427，再加中心性为0.1396，采用路径边attention bias后为0.1304。表5是12层模型训练100K步，不能直接和表1完整训练数值同比。'),
 ],
 'G02': [
  (20,'表B.1，ZINC；4个随机种子','GINE＋Transformer＋RWSE-20测试MAE为0.070±0.002、总时长7.56h；去掉全局注意力为0.070±0.004、3.90h；仅保留全局注意力为0.217±0.008。此任务的主要收益不能归于全局分支。'),
  (20,'表B.2，PCQM4Mv2的10%子集；3个随机种子','GatedGCN＋Transformer＋RWSE-16测试MAE为0.1159±0.0004，去掉全局分支为0.1213±0.0002，去掉局部分支为0.3294±0.0137。全局分支在此有增益，其必要性应按任务验证。'),
 ],
 'G03': [
  (8,'表3，ogbg-code2；5次运行','GCN-Virtual测试F1为0.1595±0.0018，GraphTrans（GCN-Virtual）为0.1830±0.0024；DAGNN为0.1751±0.0049。这支持串联读出在该程序图任务的有效性。'),
  (8,'表4，冻结/微调GNN消融','预训练GCN-Virtual测试F1为0.1574；冻结GNN、只训练后接Transformer为0.1616；联合微调为0.1733。表4不使用输入嵌入拼接，不能与表3最优配置直接等同。'),
 ],
 'G04': [
  (9,'表2，PCQM4Mv2验证MAE','普通Transformer为0.2340，TokenGT（ORF）为0.0962，TokenGT（Lap）为0.0910，Graphormer为0.0864。图标识显著改善该实验，但TokenGT在此没有超过Graphormer。'),
  (8,'表1，合成等变基拟合；3次运行','稀疏输入测试L2误差：无节点/类型标识34.70±1.167，ORF端点＋类型标识0.011±0.002，Lap端点＋类型标识0.019±0.007。这是直接监督注意力拟合等变基的合成实验，不是一般下游任务保证。'),
  (9,'表2，Performer变体','TokenGT（Lap）＋Performer验证MAE为0.0935，稠密TokenGT（Lap）为0.0910。第24页说明前者从稠密模型检查点微调，不能解释为完全从零训练的等预算比较。'),
 ],
 'G05': [
  (7,'表2与表3；5次不同初始化','OGB-Proteins上NodeFormer ROC-AUC为77.45±1.15%，训练显存3.2GB；GraphSAINT-GAT为74.63±1.24%、5.2GB。Amazon2M上NodeFormer准确率87.85±0.24%、4.0GB；GCN为83.90±0.10%、5.7GB。两数据集batch分别10K和100K。'),
  (24,'表6，边正则与关系偏置消融','Cora准确率：完整88.69±0.46%，去边正则81.98±0.46%，去关系偏置88.06±0.59%；Deezer ROC-AUC则分别71.24±0.32、71.22±0.32、71.10±0.36。观测图约束的收益取决于图和任务。'),
 ],
 'G06': [
  (8,'表2，大图节点分类','Amazon2M准确率77.43±0.24%，对照GRAND+为75.49±0.11%、GraphSAINT为75.21±0.15%；Reddit为93.58±0.05%，对照GRAND+为92.81±0.03%。该文数据划分不同于NodeFormer，Amazon2M数值不能跨论文直接排高低。'),
  (8,'表3，结构编码消融','CoraFull加入结构编码后准确率从70.42%升至71.51%，Amazon2M从76.98%升至77.43%，Reddit从93.47%升至93.58%。增益大小随数据变化。'),
  (18,'附录G表6，排除预处理的成本','Amazon2M报告NAGphormer显存2035MB、运行时间58.66s，PPRGo为1097MB、152.62s。原文比较训练/推理阶段，排除不同框架的预处理；不能将58.66s解释为从原图开始的端到端训练总耗时。'),
 ],
 'G07': [
  (7,'表2，GraphGPS内注意力机制比较','CIFAR10准确率：Exphormer 74.69±0.125%，GPS-Transformer 72.305±0.344%，GPS-Performer 70.670±0.338%；Peptides-Func AP分别0.6527±0.0043、0.6535±0.0041、0.6475±0.0056。稀疏版本有竞争力，但并非处处更优。'),
  (8,'表5，组件消融','MalNet-Tiny全组件准确率92.06±0.18%，去扩展图边为94.02±0.21%；PascalVOC-SP全组件F1为0.3682±0.0042，去全局节点为0.3975±0.0037。主结果使用按任务选择的组件组合。'),
 ],
 'G08': [
  (7,'表3，大图测试集','SGFormer在ogbn-proteins的ROC-AUC为79.53±0.38%，NodeFormer为77.45±1.15%；Amazon2M准确率分别89.09±0.10%和87.85±0.24%；papers100M上SGFormer为66.01±0.37%，SIGN为65.11±0.14%。'),
  (7,'表4，Tesla T4计时与显存','Amazon2M上SGFormer训练2481.4ms/epoch、推理382.5ms、显存2.7GB；NodeFormer为5369.5ms/epoch、1410.0ms、4.6GB。不能与其他论文不同硬件/批量的表格混算加速比。'),
 ],
 'G09': [
  (7,'表1，同配图；10次运行','Computer准确率：Polynormer-r 93.68±0.21%，Polynormer 93.18±0.18%，OrderedGNN 92.03±0.13%；CS上Polynormer-r为95.53±0.16%，NAGphormer为95.75±0.09%。收益存在任务差异。'),
  (8,'表3，大图与ReLU对照','ogbn-arxiv准确率从Polynormer的71.82±0.23%变为Polynormer-r的73.46±0.16%；ogbn-products从82.97±0.28%变为83.82±0.11%。非线性本身也是性能来源。'),
  (23,'附录J.2表6，真实大图成本','ogbn-arxiv上Polynormer训练0.31s/epoch、显存16.09GB；GraphGPS为1.32s/epoch、38.91GB；GAT为0.16s/epoch、10.64GB。Polynormer并非所有比较模型中同时最省时省显存。'),
 ],
 'G10': [
  (9,'表2，GENIUS；时间单位秒','HubGT准确率89.68±0.48%，预计算125s、训练23s/epoch、推理2.5s；SGFormer准确率85.01±0.25%，训练0.72s/epoch、推理2.4s。带星号的SGFormer推理在CPU全批执行；该表不支持HubGT所有阶段都更快。'),
  (10,'表3，模块消融','CiteSeer完整模型准确率75.47%，去SPD bias为68.55%，去全局hub为71.15%；Chameleon完整模型43.63%，对应去除后36.52%和37.08%。结构距离和hub在这两个设定均有贡献。'),
 ],
 'G11': [
  (8,'表6；评测协议见第20页','Needle-in-a-graph在N=128、每节点T=512 token、k=4跳时，GTLM准确率98.0%，扁平LLM为8.5%；该单元约65k token且超出训练长度分布。每单元200图，表6采用3个seed中验证准确率居中的seed，不是3次均值。'),
  (8,'表7，GraphQA偏置消融','边数统计：完整GTLM 57.2±2.7%，去Magnetic bias后8.9±0.5%；最短路为92.7±1.7%到87.5±3.9%。去SPD后最短路为93.5±0.5%，作者说明SPD效果在seed噪声范围内，并非三类偏置都获独立有效性证明。'),
  (24,'表20，H100 80GB、bf16、batch=1、LoRA、梯度检查点','ogbn-arxiv平均1065 token时，单训练步eager/Flex/无图偏置Flash分别2006.2/208.3/103.7ms。Flex解决显式偏置存储和实现开销，仍约为无图偏置LLM耗时的2.01倍。'),
 ],
}

PILOTS = {
 'G01':'建议先在ZINC比较无偏置、真实结构偏置、打乱结构偏置，控制层数和近似参数量，3个seed，报告MAE/显存/预处理。再固定事件证据集合，只换时间或关系偏置；打乱关系若同样增益，先检查额外容量。',
 'G02':'建议在ZINC和Peptides-func分别跑local-only、global-only、并行融合，固定编码与训练步数，3个seed，报告MAE/AP与GPU小时。迁移时冻结视觉编码和保留集合，只换读出器，检验远程证据交互的真实增益。',
 'G03':'建议复现Code2表4的预训练GNN、冻结GNN后接Transformer、联合微调，3个seed，记录F1/参数/迭代耗时。迁移再交叉比较原始或摘要证据、均值或注意力读出，定位信息损失阶段。',
 'G04':'建议先复现小型等变基拟合，控制节点数，比较无标识、端点标识、端点＋类型标识。迁移用同字节节点token与节点＋关系token，3个seed，测关系组合任务和节点重编号稳定性。',
 'G05':'建议从Cora和Actor固定划分起步，比较有无Gumbel、有无边正则，3个seed，记录随机特征数与batch。迁移时限制为已见历史，扫描两档特征维度/采样数，对照确定性线性注意力，并报告方差和耗时。',
 'G06':'建议先在Pubmed及Reddit的预算内设定比较K=4/8/12和有无结构编码，3个seed，分计预计算/CPU缓存/GPU训练。迁移固定总字节比较原始证据与多尺度摘要，并加入恢复被删关键事件的干预。',
 'G07':'建议在MalNet-Tiny和Peptides-func比较局部、局部＋扩展图、局部＋虚拟节点、全部组件，控制层数和近似参数量，3个模型seed并记录扩展图seed。迁移固定保留集合和读取边数，测成功率随传播层数的变化。',
 'G08':'建议在ogbn-arxiv比较单层线性全局＋GCN、仅GCN、同预算多层全局，3个seed，报告准确率/耗时/显存。迁移固定存储和读取量，复杂模型增益若落在seed波动内，先不扩大模块开发。',
 'G09':'建议在Computer和roman-empire分别去乘法、改local/global次序、去ReLU，3个seed，报告指标和参数/时间。迁移加入可控二证据合取任务，并保留自然样本复核，避免仅用构造任务宣称普适收益。',
 'G10':'建议在CiteSeer与ogbn-arxiv比较完整、无SPD、无hub，3个seed，分计冷索引/CPU RAM/热查询/GPU训练与推理。动态图迁移用固定频率增删节点，测索引维护摊销；完整索引超总状态预算则不符合有限记忆设定。',
 'G11':'建议以1B底座和1k–4k token比较扁平文本、节点内位置重置、结构偏置及两者组合，固定内容/LoRA预算，3个seed，报告准确率/token/时延。再独立施加历史字节限制测试保留策略；先做单卡显存试跑，单层70k内核测试不能证明完整模型可训练。',
}

def enrich(rows, manifest):
    for r in rows:
        pid = r['id']
        r['problem'] = PROBLEMS[pid]
        r['minimum_validation'] = PILOTS[pid]
        r['suggestion_status'] = '迁移方向与最小验证均为研究建议；本次未训练模型，也未证实新颖性。'
        for e in r['original_evidence']:
            e['evidence_type'] = 'method_or_interpretation'
        r['experimental_evidence'] = [
            {'page':p, 'locator':loc, 'quote':'', 'supports':s, 'evidence_type':'experiment'}
            for p,loc,s in EXPERIMENTS[pid]
        ]
        r['original_evidence'].extend(r['experimental_evidence'])
        r['evidence'] = r['experimental_evidence']
        r['record_type'] = '人工结构化精读摘要；不是机器全文导出'
        r['page_numbering'] = '本地PDF文件第1页起计数。'
        r['source_sha256'] = manifest[pid]['sha256']
        r['local_pages'] = manifest[pid]['pages']
    by_id = {r['id']:r for r in rows}
    by_id['G03']['cost']['reported'] = '第10页表7报告迭代计时：NCI1上GraphTrans前向/反向15.01/12.04ms，Code2为34.93/31.14ms（均值）。本地正文未找到明确GPU型号、卡数与完整GPU小时，不能由此估算全量训练预算。'
    by_id['G04']['cost']['reported'] = by_id['G04']['cost']['reported'].replace('第9、25页','第9、24页')
    by_id['G05']['cost']['reported'] += ' §4（第7页）明确全部实验采用单张16GB NVIDIA V100。'
    by_id['G11']['cost']['reported'] += ' 附录N（第25页）称可用单张A100/H100 80GB；部分实测使用B200/B300。1B GraphQA任务10–40分钟，TAG在H100约6–8小时，ogbn-arxiv约20小时；这些分别对应不同任务。'
    by_id['G11']['claim_boundary'] += ' 表6使用验证中位seed而非多seed平均；第20页另给扁平LLM的跨seed均值，比较应保留区别。'
