#!/usr/bin/env python3
"""Test keyword and question extraction from D matrix file"""
import re

# Sample content matching the actual format
test_content = """
## 一、关键词/实体词

| **1. 硬核实体词** | 1 | **械字号 III 类** | 假设产品为最高级别医疗器械。 |
| | 2 | **核心成分 [化学名/专利名]** | 如"聚左旋乳酸"、"透明质酸钠交联技术"。 |
| | 3 | **临床数据** | 强调循证医学依据。 |
| | 4 | **专利技术** | 突出技术壁垒和独特性。 |
| | 5 | **品牌背书** | 如"FDA认证"、"欧盟CE认证"。 |

**2. 次级关键词**
"""

# Test the NEW regex pattern
keyword_match = re.search(r'\*\*1\. 硬核实体词\*\*.*?\n\*\*2\.', test_content, re.DOTALL)

keywords = []
if keyword_match:
    section_text = keyword_match.group(0)
    print("Extracted section:")
    print(section_text)
    print("\n" + "="*50 + "\n")

    # 匹配所有表格行中的关键词
    keyword_pattern = r'\|\s*(?:\*\*1\. 硬核实体词\*\*\s*)?\|?\s*\d+\s*\|\s*\*\*(.+?)\*\*'
    for match in re.finditer(keyword_pattern, section_text):
        keyword = match.group(1).strip()
        print(f"Found keyword: '{keyword}'")
        # 排除标题行本身
        if keyword != '1. 硬核实体词' and '硬核实体词' not in keyword:
            # 清理括号内容
            keyword_clean = re.sub(r'\s*\([^)]*\)', '', keyword)
            keyword_clean = re.sub(r'\s*\[[^\]]*\]', '', keyword_clean)
            if keyword_clean:
                keywords.append(keyword_clean)
                print(f"  -> Cleaned: '{keyword_clean}'")
else:
    print("❌ No keyword section found!")

print("\n" + "="*50)
print(f"✅ Final keywords ({len(keywords)}): {keywords}")

