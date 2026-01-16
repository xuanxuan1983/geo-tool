"""
多引擎 AI 压力测试脚本
支持：DeepSeek、ChatGPT、文心一言（需配置对应 API Key）

用法：
python ai_pressure_test_multi.py \
  --client 悦白之几 \
  --questions questions.json \
  --keywords 悦白之几 若境 \
  --engines deepseek chatgpt \
  --output report.md
"""
import argparse
import json
from datetime import datetime
from pathlib import Path
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL

# 引擎配置
ENGINES = {
    "deepseek": {
        "name": "DeepSeek",
        "base_url": "https://api.deepseek.com",
        "model": "deepseek-chat",
        "api_key_env": "DEEPSEEK_API_KEY"
    },
    "chatgpt": {
        "name": "ChatGPT",
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-4o-mini",
        "api_key_env": "OPENAI_API_KEY"
    }
}


def get_client(engine: str, api_key: str = None):
    """根据引擎类型获取对应的客户端"""
    config = ENGINES.get(engine)
    if not config:
        raise ValueError(f"不支持的引擎: {engine}")
    
    # 优先使用传入的 API Key，否则从 config 导入
    if api_key is None:
        if engine == "deepseek":
            api_key = DEEPSEEK_API_KEY
        else:
            import os
            api_key = os.environ.get(config["api_key_env"], "")
    
    return OpenAI(api_key=api_key, base_url=config["base_url"]), config["model"]


def load_questions(path: str) -> list:
    """加载固定问题集"""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def test_question(client, model: str, question: str) -> str:
    """向 AI 提问并获取回答（带重试）"""
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": question}],
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


def analyze_mention_position(answer: str, brand_keywords: list) -> str:
    """分析品牌提及位置（首段/中间/末尾）"""
    answer_lower = answer.lower()
    total_len = len(answer)
    
    for keyword in brand_keywords:
        pos = answer_lower.find(keyword.lower())
        if pos >= 0:
            ratio = pos / total_len
            if ratio < 0.25:
                return "首段"
            elif ratio < 0.75:
                return "中间"
            else:
                return "末尾"
    return "未提及"


def run_pressure_test(questions: list, brand_keywords: list, engines: list) -> dict:
    """在多个引擎上运行压力测试"""
    all_results = {}
    
    for engine in engines:
        print(f"\n🔧 正在测试引擎: {ENGINES[engine]['name']}")
        try:
            client, model = get_client(engine)
        except Exception as e:
            print(f"   ⚠️ 无法初始化 {engine}: {e}")
            all_results[engine] = {"error": str(e)}
            continue
        
        results = []
        for i, q in enumerate(questions, 1):
            print(f"   ⏳ 问题 {i}/{len(questions)}: {q[:25]}...")
            try:
                answer = test_question(client, model, q)
                mentions = check_brand_mention(answer, brand_keywords)
                position = analyze_mention_position(answer, brand_keywords)
                results.append({
                    "question": q,
                    "answer": answer,
                    "mentions": mentions,
                    "any_mention": any(mentions.values()),
                    "position": position,
                    "timestamp": datetime.now().isoformat()
                })
                status = "✓ 提及" if any(mentions.values()) else "✗ 未提及"
                print(f"      {status} (位置: {position})")
            except Exception as e:
                results.append({
                    "question": q,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
                print(f"      ✗ 错误: {e}")
        
        all_results[engine] = results
    
    return all_results


def generate_multi_engine_report(all_results: dict, client_name: str, brand_keywords: list, engines: list) -> str:
    """生成多引擎对比报告"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    report = f"""# GEO 多引擎压力测试报告

**客户**：{client_name}
**测试时间**：{timestamp}
**测试引擎**：{', '.join([ENGINES[e]['name'] for e in engines])}
**品牌关键词**：{', '.join(brand_keywords)}

---

## 📊 跨引擎对比摘要

| 引擎 | 问题数 | 提及次数 | 提及率 | 首段占位 |
|------|--------|----------|--------|----------|
"""
    
    for engine in engines:
        results = all_results.get(engine, [])
        if isinstance(results, dict) and "error" in results:
            report += f"| {ENGINES[engine]['name']} | - | - | 错误 | - |\n"
            continue
        
        total = len(results)
        mentioned = sum(1 for r in results if r.get("any_mention", False))
        first_pos = sum(1 for r in results if r.get("position") == "首段")
        mention_rate = (mentioned / total * 100) if total > 0 else 0
        first_rate = (first_pos / total * 100) if total > 0 else 0
        
        report += f"| {ENGINES[engine]['name']} | {total} | {mentioned} | {mention_rate:.0f}% | {first_rate:.0f}% |\n"
    
    report += "\n---\n\n"
    
    # 各引擎详细结果
    for engine in engines:
        results = all_results.get(engine, [])
        if isinstance(results, dict) and "error" in results:
            report += f"## {ENGINES[engine]['name']} — 错误\n\n{results['error']}\n\n---\n\n"
            continue
        
        report += f"## {ENGINES[engine]['name']} 详细结果\n\n"
        
        for i, r in enumerate(results, 1):
            q = r.get("question", "")
            if "error" in r:
                report += f"### Q{i}: {q[:30]}...\n❌ 错误: {r['error']}\n\n"
            else:
                any_mention = r.get("any_mention", False)
                position = r.get("position", "未提及")
                answer_preview = r.get("answer", "")[:300] + "..."
                
                status = "✅ 已提及" if any_mention else "❌ 未提及"
                report += f"### Q{i}: {q[:30]}...\n**状态**: {status} | **位置**: {position}\n\n> {answer_preview.replace(chr(10), chr(10) + '> ')}\n\n"
        
        report += "---\n\n"
    
    # 改进建议
    report += "## 🎯 改进建议\n\n"
    
    # 计算平均提及率
    avg_rates = []
    for engine in engines:
        results = all_results.get(engine, [])
        if isinstance(results, list) and len(results) > 0:
            mentioned = sum(1 for r in results if r.get("any_mention", False))
            avg_rates.append(mentioned / len(results) * 100)
    
    if avg_rates:
        avg = sum(avg_rates) / len(avg_rates)
        if avg < 30:
            report += "- ⚠️ 跨引擎平均提及率较低（<30%），建议加强语义资产投放\n"
        elif avg < 60:
            report += "- 📈 跨引擎平均提及率中等（30-60%），继续优化核心问题的语义覆盖\n"
        else:
            report += "- ✅ 跨引擎平均提及率良好（>60%），保持当前策略\n"
    
    report += f"\n---\n\n*报告生成时间: {timestamp}*\n"
    
    return report


def main():
    parser = argparse.ArgumentParser(description="多引擎 AI 压力测试")
    parser.add_argument("--client", "-c", required=True, help="客户名称")
    parser.add_argument("--questions", "-q", required=True, help="问题集 JSON 文件路径")
    parser.add_argument("--keywords", "-k", nargs="+", required=True, help="品牌关键词列表")
    parser.add_argument("--engines", "-e", nargs="+", default=["deepseek"], 
                        choices=list(ENGINES.keys()), help="测试引擎列表")
    parser.add_argument("--output", "-o", help="输出报告路径")
    
    args = parser.parse_args()
    
    # 加载问题集
    questions = load_questions(args.questions)
    print(f"✓ 已加载 {len(questions)} 个测试问题")
    print(f"✓ 测试引擎: {', '.join(args.engines)}")
    
    # 运行测试
    all_results = run_pressure_test(questions, args.keywords, args.engines)
    
    # 生成报告
    report = generate_multi_engine_report(all_results, args.client, args.keywords, args.engines)
    
    # 输出
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"\n✓ 报告已保存到: {args.output}")
        
        # 保存原始结果
        results_path = Path(args.output).with_suffix(".json")
        with open(results_path, "w", encoding="utf-8") as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
        print(f"✓ 原始结果已保存到: {results_path}")
    else:
        print("\n" + "="*60)
        print(report)


if __name__ == "__main__":
    main()
