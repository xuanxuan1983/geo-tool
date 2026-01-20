#!/usr/bin/env python3
"""测试关键词和问题提取（新格式）"""
import re
from pathlib import Path

# 读取实际生成的D矩阵文件
d_matrix_file = Path("/Users/xuan/Documents/write agent/geo_business_tool/output/流程测试客户/流程测试客户_D_矩阵提取.md")
content = d_matrix_file.read_text(encoding='utf-8')

print("=" * 70)
print("测试关键词和问题提取（新格式）")
print("=" * 70)

# 提取硬核实体词
keywords = []

# 格式1: 两列表格，关键词用<br>分隔
keyword_cell_match = re.search(r'\|\s*\*\*1\.\s*硬核实体词\*\*\s*\|\s*(.+?)\s*\|', content)
if keyword_cell_match:
    cell_content = keyword_cell_match.group(1)
    print(f"\n找到硬核实体词单元格内容:")
    print(cell_content[:200] + "...")

    # 提取所有编号的关键词
    keyword_items = re.findall(r'\d+\.\s*([^<\n]+?)(?:<br>|\||$)', cell_content)
    print(f"\n提取到 {len(keyword_items)} 个关键词:")

    for idx, kw in enumerate(keyword_items, 1):
        kw = kw.strip()
        # 清理括号内容
        kw_clean = re.sub(r'\s*\([^)]*\)', '', kw)
        kw_clean = re.sub(r'\s*\[[^\]]*\]', '', kw_clean)
        kw_clean = re.sub(r'\s*（[^）]*）', '', kw_clean)

        if kw_clean and len(kw_clean) > 1:
            keywords.append(kw_clean)
            print(f"  {idx}. {kw_clean}")

# 提取预测AI热门提问
questions = []

question_cell_match = re.search(r'\|\s*\*\*4\.\s*预测\s*AI\s*热门提问\*\*\s*\|\s*(.+?)\s*\|', content)
if question_cell_match:
    cell_content = question_cell_match.group(1)
    print(f"\n找到预测AI热门提问单元格内容:")
    print(cell_content[:200] + "...")

    # 提取所有编号的问题
    question_items = re.findall(r'\d+\.\s*["""]?([^""<\n]+?)["""]?(?:<br>|\||$)', cell_content)
    print(f"\n提取到 {len(question_items)} 个问题:")

    for idx, q in enumerate(question_items, 1):
        q = q.strip()
        if q and len(q) > 5:
            q = q.strip('"').strip('"').strip('"')
            questions.append(q)
            print(f"  {idx}. {q}")

print("\n" + "=" * 70)
print(f"✅ 最终结果: {len(keywords)} 个关键词, {len(questions)} 个问题")
print("=" * 70)
