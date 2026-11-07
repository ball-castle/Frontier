import json
import re
from pathlib import Path

group_dir = Path(__file__).resolve().parent.parent
items = json.loads((group_dir / '09.json').read_text(encoding='utf-8'))
labels = {
    'screenshot_check': '截图与来源核对', 'problem': '研究问题',
    'mechanism': '核心机制', 'compute': '算力与完整成本',
    'limits': '证据边界', 'transfer_hypothesis': '可迁移假设与碰撞',
    'pilot': '建议最小探针（未执行）', 'priority': '优先级'
}
parts = [
    '第09组：测试时记忆、视觉量化、语言对称性与架构发现',
    '核查日期：2026-11-05。PDF页码均为本地PDF的1起始页码。已实际阅读方法、公式、主实验及相关附录，并渲染核对关键图表。建议基于2–4人、4–8张高端GPU；本次未训练、未运行科学实验。'
]
for item in items:
    parts.extend(['\n' + '=' * 70, item['id'] + '  ' + item['title'], '原始来源：' + item['source_url']])
    for key in ['screenshot_check', 'problem', 'mechanism']:
        parts.extend(['\n' + labels[key], item[key]])
    parts.append('\n具体原文证据')
    for i, evidence in enumerate(item['evidence'], 1):
        parts.append(f"{i}. {evidence['claim']}【{evidence['page_or_table']}】")
    for key in ['compute', 'limits', 'transfer_hypothesis', 'pilot', 'priority']:
        parts.extend(['\n' + labels[key], item[key]])
    if 'novelty_check' in item:
        check = item['novelty_check']
        parts.extend(['\n附：记忆方向查新记录', check['scope']])
        for source in check['sources']:
            parts.extend([source['title'], source['url'], source['finding']])
        parts.append(check['decision'])
    text = ''.join(str(v) for k, v in item.items() if k not in ['novelty_check', 'title', 'source_url', 'id'])
    print(item['id'], 'Chinese chars', len(re.findall('[\u4e00-\u9fff]', text)), 'evidence', len(item['evidence']))
    assert all(item[k] for k in labels)
    assert len(item['evidence']) >= 2
assert [item['id'] for item in items] == ['B15', 'B16', 'B17', 'B18']
output = group_dir / '09.txt'
output.write_text('\n'.join(parts) + '\n', encoding='utf-8')
assert len(json.loads((group_dir / '09.json').read_text(encoding='utf-8'))) == 4
assert output.stat().st_size > 10000
print('Verified IDs, schema, evidence; TXT bytes:', output.stat().st_size)
