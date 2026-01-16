"""
一键运行完整 GEO 流程
用法：python run_full_pipeline.py --client 客户名 --input 客户输入.json

自动按顺序执行：D（矩阵）→ B（转化）→ C（质检）→ A（提案）
所有结果保存到 output/客户名/ 目录
"""
import argparse
import json
import os
from pathlib import Path
from datetime import datetime
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEFAULT_MODEL

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

# Prompt 定义（从 geo_prompt_runner.py 导入）
from geo_prompt_runner import PROMPTS, format_client_input


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def call_api_with_retry(prompt: str) -> str:
    """带重试机制的 API 调用"""
    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[
            {"role": "system", "content": "你是一名专业的 GEO（生成式引擎优化）专家，擅长医美行业的语义优化与内容策略。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=4000
    )
    return response.choices[0].message.content


def run_prompt(prompt_type: str, client_input: dict) -> str:
    """执行指定的 Prompt"""
    prompt_template = PROMPTS[prompt_type]
    formatted_input = format_client_input(client_input)
    full_prompt = prompt_template.format(client_input=formatted_input)
    return call_api_with_retry(full_prompt)


def run_full_pipeline(client_name: str, input_path: str, output_dir: str = None):
    """运行完整的 D→B→C→A 流水线"""
    
    # 加载客户输入
    with open(input_path, "r", encoding="utf-8") as f:
        client_input = json.load(f)
    print(f"✓ 已加载客户输入卡: {input_path}")
    
    # 创建输出目录
    if output_dir is None:
        output_dir = Path(__file__).parent.parent / "output" / client_name
    else:
        output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"✓ 输出目录: {output_dir}")
    
    # 复制输入卡到输出目录
    input_copy = output_dir / f"{client_name}_输入卡.json"
    with open(input_copy, "w", encoding="utf-8") as f:
        json.dump(client_input, f, ensure_ascii=False, indent=2)
    
    # 按顺序执行 D→B→C→A
    pipeline = [
        ("D", "矩阵提取"),
        ("B", "转化路径"),
        ("C", "质检暴改"),
        ("A", "商业提案"),
    ]
    
    results = {}
    for prompt_type, name in pipeline:
        print(f"\n⏳ 正在执行 Prompt {prompt_type}（{name}）...")
        try:
            result = run_prompt(prompt_type, client_input)
            output_file = output_dir / f"{client_name}_{prompt_type}_{name}.md"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(result)
            results[prompt_type] = {"status": "success", "file": str(output_file)}
            print(f"   ✓ 完成，已保存到: {output_file.name}")
        except Exception as e:
            results[prompt_type] = {"status": "error", "error": str(e)}
            print(f"   ✗ 错误: {e}")
    
    # 生成执行摘要
    summary = {
        "client_name": client_name,
        "input_file": str(input_path),
        "output_dir": str(output_dir),
        "execution_time": datetime.now().isoformat(),
        "results": results
    }
    summary_file = output_dir / "执行摘要.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    # 打印总结
    print("\n" + "="*60)
    print("📋 GEO 流水线执行完成")
    print("="*60)
    print(f"客户: {client_name}")
    print(f"输出目录: {output_dir}")
    print("\n生成的文件:")
    for f in output_dir.iterdir():
        if f.is_file():
            print(f"  • {f.name} ({f.stat().st_size / 1024:.1f} KB)")
    
    success_count = sum(1 for r in results.values() if r["status"] == "success")
    print(f"\n状态: {success_count}/{len(pipeline)} 个 Prompt 成功执行")
    
    return summary


def main():
    parser = argparse.ArgumentParser(description="一键运行完整 GEO 流程")
    parser.add_argument("--client", "-c", required=True, help="客户名称")
    parser.add_argument("--input", "-i", required=True, help="客户输入卡 JSON 文件路径")
    parser.add_argument("--output", "-o", help="输出目录（可选，默认为 output/客户名/）")
    
    args = parser.parse_args()
    run_full_pipeline(args.client, args.input, args.output)


if __name__ == "__main__":
    main()
