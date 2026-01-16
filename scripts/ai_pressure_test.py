"""
AI 压力测试脚本 - GEO 效果验收工具
功能：对固定问题集在 AI 引擎上进行测试，记录品牌是否被提及

用法：
python ai_pressure_test.py --client 悦白之几 --questions questions.json --output report.md
"""
import argparse
import json
from datetime import datetime
from pathlib import Path
from openai import OpenAI
from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)


def load_questions(path: str) -> list:
    """加载固定问题集"""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def test_question(question: str) -> str:
    """向 AI 提问并获取回答"""
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "user", "content": question}
        ],
        temperature=0.7,
        max_tokens=2000
    )
    return response.choices[0].message.content


def check_brand_mention(answer: str, brand_keywords: list) -> dict:
    """检查回答中是否提及品牌关键词"""
    mentions = {}
    answer_lower = answer.lower()
    for keyword in brand_keywords:
        mentions[keyword] = keyword.lower() in answer_lower
    return mentions


def run_pressure_test(questions: list, brand_keywords: list) -> list:
    """运行完整的压力测试"""
    results = []
    for i, q in enumerate(questions, 1):
        print(f"⏳ 测试问题 {i}/{len(questions)}: {q[:30]}...")
        try:
            answer = test_question(q)
            mentions = check_brand_mention(answer, brand_keywords)
            results.append({
                "question": q,
                "answer": answer,
                "mentions": mentions,
                "any_mention": any(mentions.values()),
                "timestamp": datetime.now().isoformat()
            })
            print(f"   ✓ 完成，品牌提及: {'是' if any(mentions.values()) else '否'}")
        except Exception as e:
            results.append({
                "question": q,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            print(f"   ✗ 错误: {e}")
    return results


def generate_report(results: list, client_name: str, brand_keywords: list) -> str:
    """生成 Markdown 格式的测试报告"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # 统计
    total = len(results)
    mentioned = sum(1 for r in results if r.get("any_mention", False))
    mention_rate = (mentioned / total * 100) if total > 0 else 0
    
    report = f"""# GEO 压力测试报告

**客户**：{client_name}
**测试时间**：{timestamp}
**测试引擎**：DeepSeek
**品牌关键词**：{', '.join(brand_keywords)}

---

## 📊 测试摘要

| 指标 | 数值 |
|------|------|
| 测试问题数 | {total} |
| 品牌被提及次数 | {mentioned} |
| **提及率** | **{mention_rate:.1f}%** |

---

## 📝 详细结果

"""
    
    for i, r in enumerate(results, 1):
        q = r.get("question", "")
        if "error" in r:
            report += f"### 问题 {i}\n**Q**: {q}\n\n❌ **错误**: {r['error']}\n\n---\n\n"
        else:
            answer = r.get("answer", "")
            mentions = r.get("mentions", {})
            any_mention = r.get("any_mention", False)
            
            mention_status = "✅ 已提及" if any_mention else "❌ 未提及"
            mention_details = ", ".join([k for k, v in mentions.items() if v]) or "无"
            
            # 截断答案以保持报告可读性
            answer_preview = answer[:500] + "..." if len(answer) > 500 else answer
            
            report += f"""### 问题 {i}
**Q**: {q}

**品牌提及**: {mention_status}（{mention_details}）

**AI 回答预览**:
> {answer_preview.replace(chr(10), chr(10) + '> ')}

---

"""
    
    report += f"""
## 🎯 改进建议

"""
    
    if mention_rate < 30:
        report += "- ⚠️ 提及率较低（<30%），建议加强语义资产投放\n"
    elif mention_rate < 60:
        report += "- 📈 提及率中等（30-60%），继续优化核心问题的语义覆盖\n"
    else:
        report += "- ✅ 提及率良好（>60%），保持当前策略并进行月度复盘\n"
    
    report += f"""
---

*报告生成时间: {timestamp}*
"""
    
    return report


def main():
    parser = argparse.ArgumentParser(description="GEO AI 压力测试工具")
    parser.add_argument("--client", "-c", required=True, help="客户名称")
    parser.add_argument("--questions", "-q", required=True, help="问题集 JSON 文件路径")
    parser.add_argument("--keywords", "-k", nargs="+", required=True, help="品牌关键词列表")
    parser.add_argument("--output", "-o", help="输出报告路径（可选）")
    
    args = parser.parse_args()
    
    # 加载问题集
    questions = load_questions(args.questions)
    print(f"✓ 已加载 {len(questions)} 个测试问题")
    
    # 运行测试
    print(f"\n开始对 {args.client} 进行 AI 压力测试...\n")
    results = run_pressure_test(questions, args.keywords)
    
    # 生成报告
    report = generate_report(results, args.client, args.keywords)
    
    # 输出报告
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"\n✓ 报告已保存到: {args.output}")
    else:
        print("\n" + "="*60)
        print(report)
        print("="*60)
    
    # 保存原始结果
    results_path = Path(args.output).with_suffix(".json") if args.output else Path("pressure_test_results.json")
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"✓ 原始结果已保存到: {results_path}")


if __name__ == "__main__":
    main()
