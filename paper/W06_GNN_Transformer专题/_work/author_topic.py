from pathlib import Path
import json, html, re

BASE = Path(__file__).resolve().parents[1]
PAPER = BASE.parent
selected = {x['id']: x for x in json.loads((BASE/'selected_papers.json').read_text('utf-8-sig'))}
manifest = {x['id']: x for x in json.loads((BASE/'manifest.json').read_text('utf-8-sig'))}
rows = []

def add(pid, venue, task, fusion, mechanism, cost, evidence, transfer, experiment, boundary, priority):
    meta = selected[pid]
    rows.append({
        'id': pid, 'short_name': meta['short_name'], 'title': meta['title'],
        'venue_or_version': venue, 'task_scope': task,
        'source_url': meta['source_url'], 'local_pdf': 'W06_GNN_Transformer专题/'+Path(manifest[pid]['local_file']).name,
        'local_text': 'W06_GNN_Transformer专题/'+pid+'_全文.txt',
        'selection_basis': '按GNN与Transformer融合主题自主选择的代表论文；不主张与公众号原清单逐篇对应。',
        'fusion_position': fusion, 'core_mechanism': mechanism,
        'cost': cost, 'original_evidence': evidence,
        'transfer_to_current_projects': transfer, 'suggested_control': experiment,
        'claim_boundary': boundary, 'reading_priority': priority,
        'assessment_basis': '本地已下载PDF的方法、实验和附录；迁移方案为本专题判断，未执行复现。',
    })

add('G01', 'NeurIPS 2021；本地 arXiv v5', '以分子图等图级预测为主',
    '输入节点特征＋注意力分数偏置',
    '节点的入度、出度嵌入加到输入；节点对的最短路径距离映射为标量偏置；路径上的边特征经位置相关投影后平均，再加到注意力 logits。全局注意力仍读取所有节点，最终用特殊 [VNode] 表示整图。图结构在输入和路由权重中进入模型，不需要先堆一个独立GNN。',
    {'asymptotic':'普通稠密注意力的交互项为 O(N²d)，通常还需 O(N²) 节点对结构信息；最短路径预计算单独计费。不能把稀疏原图的 O(E) 传播成本套到这里。',
     'reported':'§4.1（PDF第6页）：PCQM4M设定训练100万步、batch 1024，报告8张V100训练约2天。论文同时给出12层/768维与6层/512维配置。',
     'resource_fit':'4–8张高端GPU可承接缩小模型或子集复现；全量训练应先复测吞吐，不直接按GPU代际换算天数。'},
    [{'page':5,'locator':'§3.1.3，式(7)','quote':'The proposed edge encoding incorporates edge features via a bias term to the attention module.',
      'supports':'原文把最短路径边编码 cij 与距离偏置一起加在注意力分数上，支持“结构偏置融合”的分类。'}],
    '对有限记忆事件决策，最可迁移的是给事件、对象与关系明确的相对结构，而不是任意序列化。可在保留的证据集合上加入时间间隔或关系类型偏置，但这只改变已保留信息的读取方式。对ESN证书方向，可借鉴其“指定参数构造覆盖某模型”的证明组织，不能由可表示直接推出可训练。',
    '相同保留集合和总字节下，比较无结构偏置、真实关系偏置、打乱关系偏置；再固定结构单独改变保留策略。',
    '式(7)和§3.3给出架构与表达能力论证；不证明模型能恢复被压缩掉的事件，也不证明任何图任务都需要全局注意力。',
    '基础必读：先理解结构如何进入注意力')

add('G02', 'NeurIPS 2022；本地 arXiv v4', '图、节点与边任务的通用模块化框架',
    '每层局部消息传递与全局注意力并行，随后相加并经MLP混合',
    '输入先接入位置/结构编码；同一层从相同节点状态出发，一路由MPNN沿真实边传播并处理边特征，另一路做全局注意力。两路结果相加后进入MLP。其价值是把编码、局部算子、全局算子拆成可替换部件，使融合位置与具体算子能够分别比较。',
    {'asymptotic':'仅当全局模块采用线性或相应可扩展注意力、且固定宽度等因素时，传播阶段才可写成 O(N+E)。普通Transformer实例仍有 O(N²) 交互；拉普拉斯分解等PE预计算不包含在线性声明中。',
     'reported':'附录B表B.1（PDF第20页），单A100：ZINC的GINE＋Transformer＋RWSE为MAE 0.070±0.002、总时长7.56h；去掉全局模块为0.070±0.004、3.90h。表B.2中PCQM4Mv2的10%子集又显示全局模块有收益。',
     'resource_fit':'很适合4–8 GPU并行跑模块消融与多seed；资源优先用于同协议对照，而非同时搜索所有编码与算子。'},
    [{'page':5,'locator':'§3.3，式(2)–(4)','quote':'the edge features are only passed to the MPNN layer',
      'supports':'局部与全局路径有明确职责分工；边特征经局部分支进入节点状态。'},
     {'page':20,'locator':'附录B，表B.1与B.2','quote':'','supports':'ZINC表中去除全局注意力未改变平均MAE；PCQM4Mv2子集则有差异。这组消融支持“模块是否必要依赖任务”，不是全局融合必胜。'}],
    '作为新候选的实验骨架最有用：固定视觉编码、局部事件关系与可访问历史，分别换全局读取和写入保留规则。与Dynamics_Learnability_Frontier的资源匹配习惯相接，可以把状态、接口和读取预算写成可复核协议。',
    '必须包含local-only、global-only、并行融合和同参数量局部模型；先证明任务确实需要跨远程证据交互，再开发新融合模块。',
    '其通用逼近论证使用足够丰富的谱编码与模型条件；不可自动等同于任意固定小模型、任意线性近似都拥有同样保证。',
    '最高优先：作为融合与成本消融的主框架')

add('G03', 'NeurIPS 2021；本地 arXiv v1发表于2022年', '图级分类与图级读出',
    'GNN在前、无序集合Transformer在后',
    '先用常规GNN得到含局部结构的节点向量，经投影后整体送入不使用序列位置编码的Transformer。后段允许所有节点对交互，并用可学习的 <CLS> token读出整图表示。前段负责局部归纳偏置，后段负责长程关系与汇总。',
    {'asymptotic':'常规GNN传播成本之外，还要承担后段稠密注意力 O(N²d) 的交互成本；这是由§4的全节点注意力计算推出的量级。论文提到可替换高效Transformer，并不等于原实现已具备线性成本。',
     'reported':'§4（PDF第4–5页）给出串联结构和CLS读出；本专题未找到可统一比较的整套GPU小时报告，因此不补造数字。',
     'resource_fit':'适合小图或预算内小型证据集合，是低工程成本的串联基线；不宜直接当百万节点图的全局读出方案。'},
    [{'page':4,'locator':'§4开头','quote':'a GNN subnetwork followed by a Transformer subnetwork',
      'supports':'原文直接给出串联顺序；§4后续说明Transformer不加入位置编码并使用CLS读出。'}],
    '可迁移为“先局部摘要，再统一读出”的基线，帮助定位信息损失发生在写入还是读取。对延迟事件任务，若前段聚合丢掉瞬时证据，后段注意力无从重建。对视频任务仍应保留时间戳或时序关系；图节点编号无关，不代表事件先后次序无关。',
    '固定后段读出器，比较原始证据token与局部摘要token；然后固定摘要器，比较均值池化与Transformer，分开测量压缩和读出的贡献。',
    '节点顺序置换不变是图级表示的性质；原文注意力热图展示远程关注，不构成事件级因果解释。',
    '基础必读：与GraphGPS一起理解串联和逐层并行的区别')

add('G04', 'NeurIPS 2022；本地 arXiv v2', '图表达能力与图级预测，附录含节点分类',
    '把图连接关系编码进节点token和边token',
    '每个节点与每条边都独立成为token。节点token携带两份同一节点标识，边token携带两个端点标识，再加节点/边类型标识。端点标识的内积让标准Transformer识别关联关系。理论使用正交标识；实现考察随机正交特征或拉普拉斯特征。',
    {'asymptotic':'token总数为 N+E，普通注意力为 O((N+E)²)；使用Performer的实例可线性化交互，但要另计特征维度及标识生成。完整正交标识要求足够维度，大图固定维实现采用近似并非原理论假设原样成立。',
     'reported':'§5.2及附录A.3.3（PDF第9、25页）：PCQM4Mv2主训练报告8张24GB RTX3090约3天；Performer变体微调另报告约12小时。',
     'resource_fit':'4–8 GPU可做小规模机制复现；边密集图会显著增加token数，需先核算关系token占用。'},
    [{'page':4,'locator':'Inductive Bias段与§3','quote':'treats input nodes and edges as independent tokens',
      'supports':'图结构由输入标识进入标准Transformer；PDF第3页明确端点标识的拼接方式。'}],
    '对事件记忆，启发是显式保存“关系本身”：同样节点摘要可能遗漏谁先接触谁、哪条关系改变等信息。可比较节点摘要与节点＋关系token的预算交换。对ESN/可训练性理论，需继续区分构造性的表达能力、实际正交近似和训练可达性。',
    '在同字节预算下，给节点更多维度与分配部分预算给关系token作对照；更换节点编号并同步更换标识，验证模型没有利用任意编号捷径。',
    '§3的k-IGN表达论证基于规定的张量表示、标识及容量条件；不能把附录中大图近似实现或任意稀疏删边版本直接视为无条件继承全部理论结论。',
    '选读重点：关系如何以token形式保留下来')

add('G05', 'NeurIPS 2022；本地 arXiv:2306.08385 v1', '单张大图的节点分类，可无输入图',
    '每层学习潜在连接；输入图作为可选关系偏置和边正则',
    '先把softmax相似度核用随机特征近似，使所有节点共享可复用的汇总量；再结合Gumbel-Softmax连续松弛，学习偏向离散邻接选择的全对传播。若有观测图，额外强化真实边传播并加入边似然正则。温度、随机特征维度和采样次数共同控制精度与成本。',
    {'asymptotic':'固定随机特征维度、头数与Gumbel采样数时，全对传播相对N为线性；加入原图偏置/正则后为 O(N+E)。更低温度对近似维度提出更高要求，因此“更离散”并非零成本。',
     'reported':'§4.2（PDF第8页）：Amazon2M中batch 100000报告约4GB训练显存。附录C.2（第23页）说明大图训练采用随机分批，测试在CPU上全批传播。',
     'resource_fit':'适合单卡复现加多卡并行seed；必须把CPU测试时间、批内关系范围和近似方差纳入评估。'},
    [{'page':6,'locator':'图1图注与§3.3–3.4','quote':'These two components require O(E) complexity.',
      'supports':'所指两个组件是观测图关系偏置与边正则；全局潜在图模块本身为O(N)。'},
     {'page':5,'locator':'§3.2，Theorem 1及Remark','quote':'','supports':'原文误差界依赖温度τ和随机特征维度m；Remark明确小τ需要更大m保证近似精度。'}],
    '可借鉴为记忆条目之间的学习路由或连接选择，而非预设所有相关性都等于视觉相似度。未知未来查询的在线写入必须只访问当时已见历史，不能把离线全图结构学习当作因果流式策略。',
    '真实边固定时比较确定性线性注意力、随机特征注意力、加入Gumbel选择的版本；同时扫描采样次数与特征维度，报告收益是否来自额外计算。',
    '全对表达指当前参与计算的节点集合；大图训练的随机mini-batch并不让每步访问全图所有节点。',
    '选读重点：学习连接、近似误差与成本交换')

add('G06', 'ICLR 2023；本地 arXiv v4', '单张大图的节点分类',
    '先离线多跳聚合，再把每个hop当一个token',
    'Hop2Token预计算 X、ÂX、…、ÂᴷX，将每个节点的0至K跳表示组织成长度K+1的序列；Transformer只在该节点的hop序列之间注意。输入还拼接拉普拉斯结构特征，最后用以0-hop表示为中心的注意力读出，决定各hop贡献。它处理的是多尺度摘要，不是所有原始节点两两交互。',
    {'asymptotic':'论文给出的注意力主项为 O(N(K+1)²d)，固定K时相对N线性。完整账目还包括稀疏传播约 O(KEd)、缓存约 O(N(K+1)d) 及谱编码预计算；这些项不能随GPU mini-batch缩小而消失。',
     'reported':'附录D（PDF第17页）实验设备为RTX2080Ti和64GB RAM。附录G表6（第18页）Amazon2M报告2035MB GPU内存、58.66s运行时间，正文说明时间包含训练与推理阶段，但不包含不同框架的预处理；不能读成从原图开始的端到端总耗时。',
     'resource_fit':'GPU门槛低，适合复现；大图的离线缓存、RAM及图变更后的重算比卡数更需要提前估算。'},
    [{'page':5,'locator':'§3.1，式(6)与Algorithm 1','quote':'Hop2Token is a non-parametric method.',
      'supports':'原文说明可在训练前离线执行，并通过其输出支持mini-batch；每个hop使用归一化邻接的幂作用于特征。'}],
    '对有限记忆候选，可作为多时间尺度摘要的参照：近期细节与较久历史的聚合token并存，但摘要内部丢掉的差异不保证可恢复。此类多尺度读取有成熟先例，仅把hop换成时间窗不足以构成新贡献。',
    '固定缓存字节，比较单尺度摘要、多尺度摘要和同字节原始证据；对短暂决定性事件做“恢复被删证据能否修复”的配对检验。',
    '输入节点的K跳摘要可以整合较远邻域，但不等于保留邻域所有成员、关系与顺序。论文的低GPU显存也不等于总存储恒定。',
    '高优先：理解预计算摘要与真实记忆预算')

add('G07', 'ICML 2023；本地 arXiv v2', '图级、节点级及长程图任务',
    '用稀疏交互图替换GraphGPS的全局注意力路径',
    '注意力边来自三部分：原图局部边、常数度随机扩展图边、少量连接所有节点的虚拟节点。扩展图提供短通信路径，虚拟节点提供全局汇总；组件可以按层选择。原文沿用GraphGPS架构，把其中Transformer部分换成Exphormer稀疏注意力。',
    {'asymptotic':'扩展图度数和虚拟节点个数固定时，交互边数与传播成本为 O(N+E)。若扩展为所有K跳邻居，边数可能超线性；稀疏化后远端信息通常需跨多层通信。',
     'reported':'§5.2（PDF第7页）：MalNet-Tiny上，稠密GraphGPS在40GB A100、batch 16时OOM，Exphormer可用batch 256。该对比属于论文设定，不能外推为任何图均能16倍扩批。',
     'resource_fit':'适合单卡实验和多seed并行；稀疏算子真实吞吐、通信层数、扩展图采样seed应与准确率一起报告。'},
    [{'page':4,'locator':'§3.2，Expander graph attention','quote':'we use a regular expander graph of constant degree',
      'supports':'常数度是附加边数O(N)的关键条件；同页逐项定义局部边和全局虚拟节点。'}],
    '最贴近预算内通信设计：在相同已存证据上限制可读取的关系数，检验少量长程连接是否足够。它帮助区分“存了但读不到”与“根本未保存”；对事件任务应保留时间和因果约束，不能任意重连后忽略语义。',
    '固定总状态与每步访问边数，比较局部连接、局部＋随机长边、局部＋扩展图、局部＋虚拟节点；再比较同成本多层传播与少层稠密读取。',
    '稀疏通信没有缩减已保存节点内容本身；好的扩展性或谱性质不自动保证指定事件证据能在给定层数内被正确使用。',
    '高优先：研究访问预算和长程通信的强基线')

add('G08', 'NeurIPS 2023；本地 arXiv v5', '大规模节点分类',
    '单层全局线性注意力与GNN分支在输出处加权融合',
    '先映射输入节点特征，再通过规范化Q、K及可重排的KᵀV计算一次全局交互，配合自环和残差保留本节点信息。最终把全局表示与GNN传播结果按α加权。这里的“全局”是一种简化线性注意力函数，不是对任意softmax矩阵的精确复现。',
    {'asymptotic':'固定特征宽度时，全局模块对N线性、图传播对E线性，总体 O(N+E)；宽度展开仍有 O(Nd²) 等项。更大图随机分批训练，每批的全对交互范围受批大小限制。',
     'reported':'§5.2（PDF第8页）：ogbn-papers100M报告单GPU约3.5小时、23.0GB显存、66.0准确率。PDF第7页表4还给出T4上小图/大图的时间与显存。论文这些数值不能当本机复现承诺。',
     'resource_fit':'最适合作为低成本起步基线；4–8 GPU用于重复、预算曲线及协议对照，往往比加深网络更有信息量。'},
    [{'page':3,'locator':'§3，Simple Global Attention','quote':'a single-layer global attention is sufficient.',
      'supports':'这是作者对其研究任务的经验判断；PDF第4页式(3)给线性计算，式(4)给GNN分支融合。'}],
    '对记忆读出，先测试“一次全局汇总＋局部缓存”能否覆盖收益，避免把复杂模块的增益混同于基本全局访问能力。其与线性状态汇总的联系可启发ESN/SSM比较，但静态全图分类与在线固定状态不属于相同访问条件。',
    '将单层线性读取、深层softmax读取和无全局读取放在同一存储/读取预算下；以第二模型和自然样本检验复杂设计是否仍有稳定增益。',
    '单层足够是所测任务上的经验，不是所有图推理或长程事件组合的一般定理；单GPU训练也不意味着全图常驻同一小型在线状态。',
    '最高优先：所有新融合模块都应先胜过的简单基线')

add('G09', 'ICLR 2024；本地 arXiv v3', '同配与异配图的节点分类',
    '带乘法交互的局部注意力堆栈，随后接全局线性注意力堆栈',
    '以 (WV)⊙(H+β) 的乘法更新显式构造高阶特征交互；局部部分用基于邻接的GAT型稀疏权重，全局部分用sigmoid特征核和归一化重排计算。先汇集不同局部层输出，再输入全局层；带ReLU的变体记为Polynormer-r。核心差异同时包含乘法结构和local-to-global次序。',
    {'asymptotic':'§3.2（PDF第5页）明确局部 O(Ed+Nd²)，全局 O(Nd²)，均以d远小于N为条件；无需显式枚举所有高阶单项式。大图仍通过随机分批缓解显存。',
     'reported':'附录F（PDF第19页）：实验机器有4张48GB RTX A6000，但Polynormer单次训练只用1张，其余用于并行基线。不能把“4张机器配置”误写成每次训练需求。',
     'resource_fit':'适合4–8 GPU做乘法、次序和非线性三类独立消融。较大隐维度的二次成本应与层数一起核算。'},
    [{'page':6,'locator':'图2与§3.3','quote':'local and global attention modules are applied sequentially',
      'supports':'图注区分其local-to-global次序与逐层同时使用local/global的框架；式(7)(8)保留Hadamard乘法。'}],
    '对事件决策，关系组合往往涉及多个证据同时成立，可把乘法交互作为普通注意力之外的候选读出。与Succinct-but-Unlearnable及ESN资产相接时，应沿用“能表示某个交互”与“给定数据能学到”分开的标准。',
    '在有明确真值的事件合取任务上，分别去掉乘法、交换局部/全局次序、去掉ReLU；再到自然样本验证，避免只在自造多项式任务获胜。',
    '定理3.3是规定的多项式表达能力定义下，L层基础模型达到2^L阶；不意味着学习任意高阶函数没有容量、优化或数据代价，也不能替代视觉任务证据。',
    '选读重点：高阶交互的理论主张如何落到受控消融')

add('G10', 'NeurIPS 2025；会议正式PDF', '大规模图节点分类与系统效率',
    '图索引预计算与Transformer训练解耦；索引供给邻居token和距离偏置',
    '为图构建分层hub标签：H-2全局hub、H-1局部hub、H-0补充的2-hop距离缓存。训练时从标签邻域采样固定长度子图，并查询子图节点对最短路距离，将其映射成注意力偏置。CPU查询与GPU训练流水并行；全局hub还可采用可学习特征。核心贡献在图结构查询与输入生成的成本组织。',
    {'asymptotic':'§4.3（PDF第6页）以标签/采样规模s给出索引时间 O(Ns²+Es)、索引内存 O(Ns²)，每轮距离查询 O(Ns²)。所以“线性”要求s受控。小批GPU占用受batch控制，整图索引与特征仍占RAM；常规Transformer对每个s-token子图的注意力交互仍含s²。',
     'reported':'§6.1（PDF第8页）评测服务器为32核Xeon、单张24GB A30、512GB RAM。512GB是机器配置，不等于每个实验都耗满，但说明不能只按24GB显存评价部署门槛。',
     'resource_fit':'4–8 GPU不是主要障碍；应先确认CPU、RAM、索引构建时间、查询吞吐和动态图更新代价，再选百万节点规模。'},
    [{'page':7,'locator':'§5开头与图3','quote':'it remains static in the RAM throughout GT training iterations.',
      'supports':'所指预计算索引常驻系统内存；图3明确CPU查询与GPU训练并行。'}],
    '对有限记忆课题最有价值的是成本账本：GPU外的索引也是记忆，全历史检索也有查询费用。它可以启发“结构索引＋按需读取”的基线，但在线视频图随时间变化，静态图预计算并不自动转成低成本在线更新。',
    '同时报告冷启动索引成本、RAM峰值、热查询延迟、GPU训练/推理时间；若迁移到流式事件，测每次增删节点后的索引维护和摊销成本。',
    '题名已按首页核准为HubGT: Fast Graph Transformer with Decoupled Hierarchy Labeling。其“训练中移除图计算”针对原图级算子；训练依然读取图派生索引，不能解读为不再使用图结构或全图存储。',
    '高优先：预算核算与系统边界，特别适合反查“恒定内存”说法')

add('G11', '2026预印本；本地 arXiv:2605.10247 v2，2026-10-02', '文本属性图、图问答、GraphRAG与分子文本任务',
    '直接改预训练LLM的注意力偏置、节点内位置编号与前缀mask',
    '保留每个节点的完整文本token，把节点对最短路、相对随机游走概率和磁拉普拉斯结构映射到每层每头的注意力偏置；节点内RoPE位置从零重置，图上下文用双向前缀注意力，目标节点文本仍自回归。结构参数与LoRA一起训练，避免先把整段节点文本压成单一向量。',
    {'asymptotic':'节点数N与总文本token数T需分开：结构偏置按节点对存储，但文本交互仍是密集注意力，计算量没有因参数少而变为线性。FlexAttention通过内核查询节点偏置，避免显式构建T×T偏置矩阵。',
     'reported':'PDF第9页：173056个结构参数约占1B底座的0.015%，rank 32 LoRA另约2%。TAG设定的前向＋反向约为同token序列FlashAttention LLM的2倍时间，峰值显存相同；相对eager版本快2–10倍。这些是原文特定实现和输入上的报告。',
     'resource_fit':'论文主底座为Llama-3.2-1B，可先做短上下文LoRA复现；4–8 GPU并不保证64k长上下文可直接复现，需先校验bias内核、序列长度与显存。'},
    [{'page':9,'locator':'Efficiency / Implementation','quote':'it only instantiates the node-level bias matrix',
      'supports':'原文使用FlexAttention score_mod按token所属节点查询偏置，避免显式token级偏置矩阵。'},
     {'page':4,'locator':'§3.2，Modified Attention','quote':'','supports':'方法公式把SPD、RRWP、Magnetic Laplacian三类偏置加到LLM注意力分数，前缀双向可见、目标生成保持因果。'}],
    '对新记忆方向是直接相关的读取侧先例：保留细粒度内容与结构可提高信息访问，但GTLM没有解决未知未来查询下应删掉哪些历史。可把它作为有文本事件图时的读出基线；直接用于视觉事件还需固定可复现的图构造，不能默认为它已验证视觉效果。',
    '相同内容与token数下比较扁平文本、节点内位置重置、结构偏置及其组合；之后再固定读出器比较存储预算，防止把读取收益归因保留策略。',
    '节点置换等变要求同步置换结构并保留节点内顺序。单目标节点退化回标准注意力是相同权重下的架构兼容性质，不保证LoRA微调后仍保持所有原预训练能力。该文为预印本，结果是作者报告，尚未由本专题独立复现。',
    '高优先：2026桥接工作，重点看全文保留、结构读取与写入问题的边界')

from supplemental_data import enrich
enrich(rows, manifest)

assert len(rows) == 11
for r in rows:
    assert (PAPER/r['local_pdf']).exists(), r['local_pdf']
    text = (PAPER/r['local_text']).read_text('utf-8-sig')
    chunks = re.split(r'\[PDF PAGE (\d+)\]\s*', text)
    page_map = {int(chunks[i]):chunks[i+1] for i in range(1,len(chunks),2)}
    for e in r['original_evidence']:
        assert e['page'] in page_map
        if e['quote']:
            normalize = lambda s: re.sub(r'\s+', ' ', s).strip()
            assert normalize(e['quote']) in normalize(page_map[e['page']]), (r['id'], e['quote'])

(BASE/'专题精读.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
(BASE/'reading_extracts.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')

E = html.escape
def ref(r, page=None, label='原文PDF'):
    return '<a href="'+E(r['local_pdf'])+('#page='+str(page) if page else '')+'">'+E(label)+'</a>'

body = '''<h1>W06｜GNN与Transformer如何融合</h1>
<p class="lead">11篇代表论文，从结构偏置、局部与全局交互，到图token、稀疏通信、预计算和预训练LLM。重点看结构放在哪里、计算花在哪里，以及哪些思路能进入现有研究。</p>
<div class="card"><p><strong>阅读定位：</strong>本专题按用户授权自主选编11篇原始论文，补齐GNN＋Transformer主题；不宣称还原公众号原来的11篇清单。以下机制、表格和实验数字均对应本地已下载原文；迁移建议是本专题分析，未运行复现。版本截至2026年11月5日本地保存资料。</p>
<p><strong>先看结论：</strong>“把GNN和Transformer放在一起”已经形成成熟方法谱系。最值得带走的是可检验的接口：局部结构如何编码、全局信息如何读取、预计算存储由谁承担。对当前团队，GraphGPS、SGFormer、NAGphormer、Exphormer、HubGT和GTLM比再增加一个通用融合模块更能帮助明确实验边界。</p></div>
<h2>一张表读懂11种实现</h2>
<p>N为节点数、E为边数、d为隐维度，K为hop数，s为每个查询节点的采样/标签规模。表中的“线性”只相对于图规模；各方法的维度、预计算与访问条件见逐篇精读。</p>
<table><thead><tr><th>论文</th><th>融合位置</th><th>核心成本问题</th></tr></thead><tbody>'''

cost_short = [
    '稠密节点对注意力与最短路结构信息',
    '全局算子是否线性；PE预计算另计',
    'GNN之后仍有全节点二次交互',
    '节点＋边使token数变成N+E',
    '随机特征、温度、采样数及大图分批',
    'GPU短序列计算之外还有整图hop缓存',
    '固定扩展度/虚拟节点数，另看传播层数',
    '单层O(N+E)，大图每步访问范围受分批限制',
    'O(Ed+Nd²)，隐维度与乘法交互不可省略',
    'GPU变轻；CPU索引与RAM仍随图规模增长',
    '少量可训练结构参数≠低文本注意力成本',
]
for r, c in zip(rows,cost_short):
    body += '<tr><td><a href="#'+r['id']+'">'+r['id']+' '+E(r['short_name'])+'</a></td><td>'+E(r['fusion_position'])+'</td><td>'+E(c)+'</td></tr>'
body += '''</tbody></table>
<h2>真正要区分的四件事</h2>
<div class="card"><p><strong>表示什么：</strong>Graphormer把结构变成偏置，TokenGT把节点与边变成token，NAGphormer把每个hop压成一个摘要。三者的输入信息不同，不能只按最终参数量声称公平比较。</p>
<p><strong>怎样通信：</strong>GraphTrans先局部后全局；GraphGPS每层并行；SGFormer只做一次简化全局传播；Polynormer用带乘法交互的局部到全局堆栈。融合顺序和交互函数应分别消融。</p>
<p><strong>谁能访问谁：</strong>NodeFormer学习潜在连接，Exphormer规定稀疏通信边。它们改变访问路径，不等同于减少总历史存储。大图mini-batch中的“全对”也需写明究竟是哪一批节点。</p>
<p><strong>成本移到哪里：</strong>HubGT把图操作转为预计算索引和CPU查询；GTLM通过内核查询避免显式token级偏置矩阵。GPU显存、CPU内存、总状态、预处理和在线时延必须分别计量。</p></div>
<h2>逐篇精读</h2>'''

for r in rows:
    body += '<section class="card" id="'+r['id']+'"><h3>'+r['id']+' · '+E(r['short_name'])+'</h3>'
    body += '<p><strong>'+E(r['title'])+'</strong><br>'+E(r['venue_or_version'])+'｜'+E(r['task_scope'])+'<br>'+ref(r)+' · <a href="'+E(r['source_url'])+'">论文来源页</a> · <a href="'+E(r['local_text'])+'">本地全文文本</a></p>'
    body += '<p><strong>研究问题：</strong>'+E(r['problem'])+'</p>'
    body += '<p><strong>融合位置：</strong>'+E(r['fusion_position'])+'。<strong>核心机制：</strong>'+E(r['core_mechanism'])+'</p>'
    body += '<p><strong>成本与复现：</strong>'+E(r['cost']['asymptotic'])+' '+E(r['cost']['reported'])+' '+E(r['cost']['resource_fit'])+'</p>'
    body += '<p><strong>原文方法与实验证据：</strong></p><ul>'
    for e in r['original_evidence']:
        body += '<li><strong>'+('实验记录' if e['evidence_type']=='experiment' else '方法定位')+'</strong> · '+ref(r,e['page'],'PDF第'+str(e['page'])+'页，'+e['locator'])+'：'
        if e['quote']: body += '<q>'+E(e['quote'])+'</q> '
        body += E(e['supports'])+'</li>'
    body += '</ul><p><strong>迁移建议（未执行、未证实新颖）：</strong>'+E(r['transfer_to_current_projects'])+'</p>'
    body += '<details open><summary>最小验证建议与结论边界</summary><p><strong>可做的配对对照：</strong>'+E(r['suggested_control'])+'</p><p><strong>最小验证建议：</strong>'+E(r['minimum_validation'])+'</p><p><strong>结论边界：</strong>'+E(r['claim_boundary'])+'</p><p><strong>阅读优先级：</strong>'+E(r['reading_priority'])+'</p></details></section>'

body += '''<h2>放回你的研究组合：这批论文改变什么</h2>
<p>结合本地<a href="portfolio_independent_review.txt">项目独立复核</a>，当前更合理的安排仍是完成ESN证书路线，同时用一个受控探针检验有限记忆下的延迟事件决策。图融合专题提供可用的对照和预算方法，没有提供重启已经冻结路线的证据。</p>
<table><thead><tr><th>现有资产或候选</th><th>可以迁移</th><th>需要另行建立的证据</th></tr></thead><tbody>
<tr><td>ESN_spread证书路线</td><td>Graphormer、TokenGT、Polynormer如何明确“模型能表示什么”；用定义、构造和条件区分表达能力与学习效果。</td><td>图模型表达定理不产生ESN的可训练性证书，也不补足现代SSM外推。应继续完成现有证书分支的范围与覆盖率整合。</td></tr>
<tr><td>Dynamics与Succinct理论资产</td><td>局部/全局接口消融、状态与访问预算匹配、近似误差和计算的交换。</td><td>不能把新图路由重新包装成已耗尽的selector/LoRA接口方向；新颖性与学习效果仍需直接前人对照。</td></tr>
<tr><td>有限记忆延迟事件决策</td><td>NAGphormer提供多尺度摘要参照；SGFormer与GraphGPS提供读取基线；Exphormer提供访问受限基线；GTLM提供结构化全文读取先例。</td><td>未知未来查询下的写入与丢弃决策、严格总存储、恢复证据后的修复、第二模型上的自然任务收益。</td></tr>
<tr><td>旧video与VISION_FRONTIER资产</td><td>同输入处理、逐帧对齐、标签先建、盲核验及实现语义审计；HubGT式的完整成本账本。</td><td>旧归一化统计结论、未执行的研究方案和未获资格的素材不能计作新记忆假设的实验证据。</td></tr>
<tr><td>OVS与SINN资产</td><td>实体关系和不确定性标签、视觉证据与文本捷径检查可用于小型协议审计。</td><td>图化本身不解决本体冲突、真人校准或测试集选择偏差；现有标签资产不能直接证明图模型优势。</td></tr>
</tbody></table>
<h2>4–8张GPU、2–4个人：怎样把阅读变成决定性结果</h2>
<p><strong>第一步只固定一条问题链：</strong>完整历史是否答对 → 相同字节预算下是否丢掉决定性证据 → 恢复该证据是否修复。先固定视觉编码器、分辨率、查询揭示时点与可见历史，再比较保留策略。论文中的离线全图、整图谱编码和全历史索引不能无收费地接入在线有限记忆设定。</p>
<p><strong>一个可执行的最小比较：</strong>均匀/最近帧、去重保留、一个强现有token选择器、递归摘要＋小缓存，共用同一读出器；先测写入。再固定保留集合，比较简单线性读出、局部＋全局读出和可用的结构读出，测读取。若任务需要多证据合取，再加入Polynormer式乘法交互；若瓶颈是读取次数，再加入Exphormer式稀疏访问。上述是实验设计建议，尚未执行。</p>
<p><strong>人员与算力分配：</strong>保留一人完成ESN交付；候选探针由一人负责协议/数据与直接前人对照，另一人负责基线实现和成本测量。若有第4人，负责独立核验与第二模型。起步用单卡任务并行跑配置和seed，确认残余失败后再扩多卡；GraphGPS、SGFormer、NAGphormer与Polynormer的原文均有单卡可行实例，但长上下文GTLM和HubGT的大RAM条件需单独试跑。</p>
<p><strong>进入完整开发的门槛：</strong>未按错误挑选的自然样本上存在稳定失败；全历史可答、预算模型失误、恢复少量被删证据可修复；强现有方法在同预算下仍未解决；第二模型和真实时延/总存储下仍有收益。若收益只来自更大缓存、更完整历史、更强读出或未计费预处理，应先修正比较，而不是增加一个融合模块。</p>
<p><strong>阅读顺序：</strong>Graphormer → GraphTrans＋GraphGPS → SGFormer → NAGphormer＋Exphormer → HubGT → GTLM；需要表达理论和关系表示时再精看TokenGT、NodeFormer、Polynormer。11篇覆盖的是代表机制，不能替代流式VLM记忆、query-agnostic memory、视频token压缩等子领域的专项查新。</p>
<p>资料：<a href="W06_GNN_Transformer专题/专题精读.json">11篇结构化精读JSON</a> · <a href="W06_GNN_Transformer专题/专题精读.txt">纯文本精读</a> · <a href="W06_GNN_Transformer专题/manifest.json">下载校验清单</a></p>'''

body = body.replace('<h1>', '<nav><a href="00_阅读入口.html">阅读入口</a> · <a href="02_逐篇精读汇编.html">逐篇精读汇编</a></nav><h1>', 1)
body = body.replace('11篇结构化精读JSON', '11篇结构化精读JSON').replace('W06_GNN_Transformer专题/专题精读.json', 'W06_GNN_Transformer专题/reading_extracts.json')
body += '<p class="meta">页码统一按本地PDF文件从1起计数。每篇至少2条实验记录已经回查原表；比较中的数据划分、预训练、计时范围和seed协议保留原文条件。所有迁移方向与最小验证均为建议，尚未训练或完成新颖性验证。</p>'
(PAPER/'graph_topic_body.html').write_text(body,encoding='utf-8')
plain = ['W06 GNN与Transformer融合专题精读','按主题自主选编11篇；原文证据与本地PDF已关联；迁移建议未执行复现。','']
for r in rows:
    plain += [r['id']+' '+r['title'],r['venue_or_version'],r['source_url'],
        '本地PDF（相对paper目录）：'+r['local_pdf'],
        '本地PDF（相对本txt）：'+Path(r['local_pdf']).name,
        '研究问题：'+r['problem'],
        '融合位置：'+r['fusion_position'],'机制：'+r['core_mechanism'],
        '成本：'+r['cost']['asymptotic'],'原文成本报告：'+r['cost']['reported'],
        '资源适配：'+r['cost']['resource_fit']]
    for e in r['original_evidence']:
        plain += ['证据：PDF第'+str(e['page'])+'页 '+e['locator']+'；'+e['quote']+'；'+e['supports']]
    plain += ['迁移建议（未执行、未证实新颖）：'+r['transfer_to_current_projects'],'对照建议：'+r['suggested_control'],'最小验证建议：'+r['minimum_validation'],'边界：'+r['claim_boundary'],'']
(BASE/'专题精读.txt').write_text('\n'.join(plain),encoding='utf-8')
print('Authored 11 paper records, HTML body, and plain text; quote and local-link checks passed.')
