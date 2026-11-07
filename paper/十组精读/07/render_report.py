import json
import pathlib
import re

base = pathlib.Path(__file__).resolve().parent.parent
items = json.loads((base / '07.json').read_text(encoding='utf-8'))
labels = {'screenshot_check':'截图核对','problem':'问题定位','mechanism':'实质机制','compute':'算力与团队适配','limits':'证据边界','transfer_hypothesis':'可迁移假设','pilot':'最小验证与停止条件','priority':'优先级'}
intro = '''第07组独立精读：递归视频生成与潜在世界模型
核对日期：2026-11-05；本次只读论文、截图及项目复核，没有训练或运行研究探针。
页码均为本地PDF顺序页；B07主文引用CVF版，补充内容明确标注arXiv版。其余引用清单对应arXiv公开PDF。

四篇机制分界：ReHyAt将时间注意力压缩为递推状态；RAD在视频自回归中协调历史状态与局部窗口；Latent-Foresight联合学习可预测的特征压缩空间；ELT在每次生成步骤内部循环共享网络。固定状态、局部缓存、共享权重及简单门控都不能自行算作新颖点。

对2–4人、4–8张高端GPU的判断：优先把RAD与ReHyAt当有限记忆候选的必要对照，借Latent-Foresight建立重建与任务效用的配对诊断，借ELT区分记忆瓶颈和读取计算不足。四篇都不提供复活已冻结C2、旧视频phase或接口选择器路线的依据。按既有组合复核保留ESN证书收尾，只开展一条有停止条件的新探针。
'''
parts = [intro]
required = {'id','title','source_url','screenshot_check','problem','mechanism','evidence','compute','limits','transfer_hypothesis','pilot','priority'}
for item in items:
    assert set(item) == required, (item['id'], set(item) ^ required)
    assert len(item['evidence']) >= 2
    cjk = len(re.findall(r'[\u4e00-\u9fff]', json.dumps(item, ensure_ascii=False)))
    print(item['id'], 'Chinese characters', cjk, 'evidence', len(item['evidence']))
    parts.append('\n' + '=' * 72 + '\n' + item['id'] + '｜' + item['title'] + '\n原文来源：' + item['source_url'] + '\n')
    for key in ['screenshot_check', 'problem', 'mechanism']:
        parts.append(labels[key] + '：' + item[key] + '\n')
    parts.append('原文证据：\n')
    for n, e in enumerate(item['evidence'], 1):
        parts.append(f"{n}. {e['claim']}【{e['page_or_table']}】\n")
    for key in ['compute', 'limits', 'transfer_hypothesis', 'pilot', 'priority']:
        parts.append(labels[key] + '：' + item[key] + '\n')
parts.append('''
补充来源：B07 arXiv完整PDF https://arxiv.org/pdf/2601.04342 （本组补充读取，第12页训练细节）。
本地补充文件：C:/Users/CAI BIN/Desktop/1/paper/十组精读/07/B07_arxiv.pdf。
可核复材料：本组07目录保留各PDF文本提取、关键表格页面渲染及B07附录文本。未修改清单、总报告或任何研究仓库。
''')
(base / '07.txt').write_text('\n'.join(parts), encoding='utf-8')
assert [x['id'] for x in items] == ['B07', 'B08', 'B09', 'B10']
print('Validated', len(items), 'entries; JSON bytes', (base / '07.json').stat().st_size, 'TXT bytes', (base / '07.txt').stat().st_size)
