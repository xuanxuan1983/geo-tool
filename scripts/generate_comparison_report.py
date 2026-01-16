"""
Before/After 对比报告生成器
用于对比 GEO 执行前后的 AI 压力测试结果

用法：
python generate_comparison_report.py \
  --before before_results.json \
  --after after_results.json \
  --client 悦白之几 \
  --output comparison_report.md
"""
import argparse
import json
from datetime import datetime
from pathlib import Path


def load_results(path: str) -> dict:
    """加载压力测试结果"""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def calculate_metrics(results: list) -> dict:
    """计算关键指标"""
    if not results or not isinstance(results, list):
        return {"total": 0, "mentioned": 0, "rate": 0, "first_pos": 0, "first_rate": 0}
    
    total = len(results)
    mentioned = sum(1 for r in results if r.get("any_mention", False))
    first_pos = sum(1 for r in results if r.get("position") == "首段")
    
    return {
        "total": total,
        "mentioned": mentioned,
        "rate": (mentioned / total * 100) if total > 0 else 0,
        "first_pos": first_pos,
        "first_rate": (first_pos / total * 100) if total > 0 else 0
    }


def generate_comparison_report(before_data: dict, after_data: dict, client_name: str, 
                                before_date: str = None, after_date: str = None) -> str:
    """生成 Before/After 对比报告"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # 尝试从结果中提取日期
    if before_date is None:
        if isinstance(before_data, list) and len(before_data) > 0:
            before_date = before_data[0].get("timestamp", "未知")[:10]
        else:
            before_date = "GEO执行前"
    
    if after_date is None:
        if isinstance(after_data, list) and len(after_data) > 0:
            after_date = after_data[0].get("timestamp", "未知")[:10]
        else:
            after_date = "GEO执行后"
    
    # 计算指标
    before_metrics = calculate_metrics(before_data if isinstance(before_data, list) else [])
    after_metrics = calculate_metrics(after_data if isinstance(after_data, list) else [])
    
    # 计算变化
    rate_change = after_metrics["rate"] - before_metrics["rate"]
    first_rate_change = after_metrics["first_rate"] - before_metrics["first_rate"]
    
    # 判断趋势
    trend_icon = "📈" if rate_change > 0 else ("📉" if rate_change < 0 else "➡️")
    
    report = f"""# GEO 效果对比报告

**客户**：{client_name}
**报告生成时间**：{timestamp}

---

## 📊 核心指标对比

| 指标 | {before_date} | {after_date} | 变化 |
|------|---------------|--------------|------|
| **提及率** | {before_metrics['rate']:.0f}% | {after_metrics['rate']:.0f}% | {trend_icon} {rate_change:+.0f}% |
| **首段占位率** | {before_metrics['first_rate']:.0f}% | {after_metrics['first_rate']:.0f}% | {'+' if first_rate_change >= 0 else ''}{first_rate_change:.0f}% |
| 测试问题数 | {before_metrics['total']} | {after_metrics['total']} | - |
| 被提及次数 | {before_metrics['mentioned']} | {after_metrics['mentioned']} | {after_metrics['mentioned'] - before_metrics['mentioned']:+d} |

---

## 📈 变化趋势分析

"""
    
    # 提及率分析
    if rate_change > 20:
        report += f"### ✅ 提及率显著提升 (+{rate_change:.0f}%)\n\n"
        report += "GEO 策略执行效果明显，AI 对品牌的认知和引用意愿大幅增强。\n\n"
    elif rate_change > 5:
        report += f"### 📈 提及率稳步提升 (+{rate_change:.0f}%)\n\n"
        report += "GEO 策略初见成效，建议继续加强语义资产投放。\n\n"
    elif rate_change > -5:
        report += f"### ➡️ 提及率基本持平 ({rate_change:+.0f}%)\n\n"
        report += "需要检查内容投放质量和平台覆盖度。\n\n"
    else:
        report += f"### ⚠️ 提及率下降 ({rate_change:.0f}%)\n\n"
        report += "需要分析原因：竞品活动增加？内容覆盖不足？建议复盘调整策略。\n\n"
    
    # 首段占位分析
    if first_rate_change > 10:
        report += f"### ✅ 首段占位率提升 (+{first_rate_change:.0f}%)\n\n"
        report += "品牌在 AI 答案中的"黄金位置"出现更频繁，决策影响力增强。\n\n"
    elif first_rate_change > 0:
        report += f"### 📈 首段占位略有提升 (+{first_rate_change:.0f}%)\n\n"
        report += "建议继续优化核心问题的语义锚点，争取更多首段曝光。\n\n"
    
    # 逐题对比
    report += "---\n\n## 📝 逐题对比详情\n\n"
    
    if isinstance(before_data, list) and isinstance(after_data, list):
        max_len = max(len(before_data), len(after_data))
        for i in range(max_len):
            before_q = before_data[i] if i < len(before_data) else None
            after_q = after_data[i] if i < len(after_data) else None
            
            q_text = before_q.get("question", "") if before_q else (after_q.get("question", "") if after_q else "")
            
            before_status = "✅" if before_q and before_q.get("any_mention") else "❌"
            after_status = "✅" if after_q and after_q.get("any_mention") else "❌"
            
            before_pos = before_q.get("position", "-") if before_q else "-"
            after_pos = after_q.get("position", "-") if after_q else "-"
            
            # 判断变化
            if before_q and after_q:
                if not before_q.get("any_mention") and after_q.get("any_mention"):
                    change = "🆕 新增提及"
                elif before_q.get("any_mention") and not after_q.get("any_mention"):
                    change = "⚠️ 失去提及"
                elif before_pos != after_pos and after_pos == "首段":
                    change = "📈 进入首段"
                else:
                    change = "-"
            else:
                change = "-"
            
            report += f"| Q{i+1} | {q_text[:30]}... | {before_status} ({before_pos}) | {after_status} ({after_pos}) | {change} |\n"
    
    # 行动建议
    report += "\n---\n\n## 🎯 下一步行动建议\n\n"
    
    if rate_change > 10:
        report += "1. ✅ 当前策略有效，继续执行\n"
        report += "2. 扩大问题集覆盖范围，测试更多长尾问题\n"
        report += "3. 将成功案例整理成客户交付报告\n"
    elif rate_change > 0:
        report += "1. 继续投放高权重平台内容\n"
        report += "2. 针对未提及的问题，补充对应的语义资产\n"
        report += "3. 增加内容的"硬核锚点"密度\n"
    else:
        report += "1. ⚠️ 复盘内容投放策略\n"
        report += "2. 检查竞品近期的 GEO 动作\n"
        report += "3. 考虑增加投放频率和平台覆盖\n"
    
    report += f"\n---\n\n*报告生成时间: {timestamp}*\n"
    
    return report


def main():
    parser = argparse.ArgumentParser(description="GEO Before/After 对比报告生成器")
    parser.add_argument("--before", "-b", required=True, help="执行前的测试结果 JSON")
    parser.add_argument("--after", "-a", required=True, help="执行后的测试结果 JSON")
    parser.add_argument("--client", "-c", required=True, help="客户名称")
    parser.add_argument("--before-date", help="执行前日期（可选）")
    parser.add_argument("--after-date", help="执行后日期（可选）")
    parser.add_argument("--output", "-o", help="输出报告路径")
    
    args = parser.parse_args()
    
    # 加载结果
    before_data = load_results(args.before)
    after_data = load_results(args.after)
    print(f"✓ 已加载测试结果")
    
    # 生成报告
    report = generate_comparison_report(
        before_data, after_data, args.client,
        args.before_date, args.after_date
    )
    
    # 输出
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"✓ 对比报告已保存到: {args.output}")
    else:
        print("\n" + "="*60)
        print(report)


if __name__ == "__main__":
    main()
