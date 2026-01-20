# wrapper.py – Utility functions to invoke GEO pipeline scripts with retry logic

import subprocess
import os
import re
from pathlib import Path
from typing import List, Tuple
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

# -------------------------------------------------------------------
# Helper: Extract keywords and questions from D matrix file
# -------------------------------------------------------------------
def _extract_keywords_and_questions(client_folder: str, client_name: str) -> Tuple[List[str], List[str]]:
    """从D矩阵提取文件中提取关键词和问题

    Returns:
        (keywords, questions) 两个列表
    """
    d_matrix_file = Path(client_folder) / f"{client_name}_D_矩阵提取.md"

    if not d_matrix_file.exists():
        raise FileNotFoundError(f"D矩阵文件不存在: {d_matrix_file}")

    content = d_matrix_file.read_text(encoding='utf-8')

    keywords = []
    questions = []

    # 提取硬核实体词 - 支持两种格式
    keywords = []

    # 格式1: 两列表格，关键词用<br>分隔
    # | **1. 硬核实体词** | 1. 关键词<br>2. 关键词<br>... |
    keyword_cell_match = re.search(r'\|\s*\*\*1\.\s*硬核实体词\*\*\s*\|\s*(.+?)\s*\|', content)
    if keyword_cell_match:
        cell_content = keyword_cell_match.group(1)
        # 提取所有编号的关键词
        keyword_items = re.findall(r'\d+\.\s*([^<\n]+?)(?:<br>|\||$)', cell_content)
        for kw in keyword_items:
            kw = kw.strip()
            # 清理括号内容
            kw = re.sub(r'\s*\([^)]*\)', '', kw)
            kw = re.sub(r'\s*\[[^\]]*\]', '', kw)
            kw = re.sub(r'\s*（[^）]*）', '', kw)
            if kw and len(kw) > 1:
                keywords.append(kw)

    # 格式2: 多行表格（备用）
    if not keywords:
        keyword_match = re.search(r'\*\*1\. 硬核实体词\*\*.*?\n\*\*2\.', content, re.DOTALL)
        if keyword_match:
            section_text = keyword_match.group(0)
            keyword_pattern = r'\|\s*(?:\*\*1\. 硬核实体词\*\*\s*)?\|?\s*\d+\s*\|\s*\*\*(.+?)\*\*'
            for match in re.finditer(keyword_pattern, section_text):
                keyword = match.group(1).strip()
                if keyword != '1. 硬核实体词' and '硬核实体词' not in keyword:
                    keyword = re.sub(r'\s*\([^)]*\)', '', keyword)
                    keyword = re.sub(r'\s*\[[^\]]*\]', '', keyword)
                    if keyword:
                        keywords.append(keyword)

    # 提取预测AI热门提问 - 支持两种格式
    questions = []

    # 格式1: 两列表格，问题用<br>分隔
    # | **4. 预测 AI 热门提问** | 1. "问题？"<br>2. "问题？"<br>... |
    question_cell_match = re.search(r'\|\s*\*\*4\.\s*预测\s*AI\s*热门提问\*\*\s*\|\s*(.+?)\s*\|', content)
    if question_cell_match:
        cell_content = question_cell_match.group(1)
        # 提取所有编号的问题
        question_items = re.findall(r'\d+\.\s*["""]?([^""<\n]+?)["""]?(?:<br>|\||$)', cell_content)
        for q in question_items:
            q = q.strip()
            # 确保问题不为空且有实际内容
            if q and len(q) > 5:
                # 移除可能的引号
                q = q.strip('"').strip('"').strip('"')
                questions.append(q)

    # 格式2: 多行表格（备用）
    if not questions:
        question_section = re.search(r'\*\*4\. 预测 AI 热门提问\*\*.*?\n(.*?)(\n\*\*|$)', content, re.DOTALL)
        if question_section:
            lines = question_section.group(1).split('\n')
            for line in lines:
                match = re.search(r'\|\s*\d+\s*\|\s*\*\*(.+?)\*\*', line)
                if match:
                    question = match.group(1).strip()
                    if question:
                        questions.append(question)

    # 如果提取失败，使用默认值
    if not keywords:
        print("⚠️ 未能从D矩阵文件中提取关键词，使用默认值")
        keywords = ["产品名称", "核心技术", "临床数据"]

    if not questions:
        print("⚠️ 未能从D矩阵文件中提取问题，使用默认值")
        questions = [
            "这个产品和玻尿酸有什么区别？",
            "效果能维持多久？",
            "有什么副作用吗？"
        ]

    print(f"✅ 提取到 {len(keywords)} 个关键词，{len(questions)} 个问题")
    return keywords, questions


# -------------------------------------------------------------------
# Helper: run a command and capture output
# -------------------------------------------------------------------
@retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry=retry_if_exception_type(subprocess.CalledProcessError))
def _run_cmd(cmd: List[str], cwd: Path = None) -> subprocess.CompletedProcess:
    """Run a shell command with retry.
    Raises ``subprocess.CalledProcessError`` on failure after retries.
    """
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        return result
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e.cmd}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        raise RuntimeError(f"Pipeline failed: {e.stderr}") from e

# -------------------------------------------------------------------
# 1️⃣ Run full D→B→C→A pipeline
# -------------------------------------------------------------------
def run_pipeline(client_name: str, input_json_path: str) -> str:
    """Execute the full GEO pipeline for a client.
    Returns the path to the client output folder.
    """
    script_path = Path(__file__).parent / "run_full_pipeline.py"
    cmd = ["python3", str(script_path), "--client", client_name, "--input", input_json_path]
    _run_cmd(cmd, cwd=Path(__file__).parent)
    # The pipeline creates files under ../output/<client_name>
    return str(Path(__file__).parent.parent / "output" / client_name)

# -------------------------------------------------------------------
# 2️⃣ Run AI pressure test (multi‑engine)
# -------------------------------------------------------------------
def run_pressure_test(client_name: str, client_folder: str, engines: List[str]) -> str:
    """Run pressure test for a client using selected engines.
    Returns the path to the generated markdown report.
    """
    # 从D矩阵文件中提取关键词和问题
    try:
        keywords, questions = _extract_keywords_and_questions(client_folder, client_name)
    except Exception as e:
        print(f"⚠️  提取关键词和问题失败: {e}")
        print("使用默认值继续...")
        keywords = ["产品名称", "核心技术", "临床数据"]
        questions = ["这个产品和玻尿酸有什么区别？", "效果能维持多久？"]

    # 保存问题列表到JSON文件
    import json
    questions_json_path = Path(client_folder) / "questions.json"
    with open(questions_json_path, 'w', encoding='utf-8') as f:
        json.dump(questions[:10], f, ensure_ascii=False, indent=2)

    script_path = Path(__file__).parent / "ai_pressure_test_multi.py"
    engines_arg = ",".join(engines)

    cmd = [
        "python3",
        str(script_path),
        "--client",
        client_name,
        "--output",
        str(Path(client_folder) / "压力测试报告.md"),
        "--engines",
        engines_arg,
        "--questions",
        str(questions_json_path),
        "--keywords"
    ]

    # 添加关键词参数
    cmd.extend(keywords[:10])  # 最多10个关键词

    _run_cmd(cmd, cwd=Path(__file__).parent)
    # The script writes a report named "压力测试报告.md" inside the client folder
    report_path = Path(client_folder) / "压力测试报告.md"
    return str(report_path)

# -------------------------------------------------------------------
# 3️⃣ Generate before/after comparison report
# -------------------------------------------------------------------
def generate_comparison_report(before_json: str, after_json: str, client_name: str) -> str:
    """Generate a comparison markdown report from two pressure‑test JSON files.
    Returns the path to the generated markdown file.
    """
    script_path = Path(__file__).parent / "generate_comparison_report.py"
    cmd = [
        "python3",
        str(script_path),
        "--before",
        before_json,
        "--after",
        after_json,
        "--client",
        client_name,
    ]
    _run_cmd(cmd, cwd=Path(__file__).parent)
    # The script creates a file named "对比报告.md" in the same directory as the after_json
    report_path = Path(after_json).parent / "对比报告.md"
    return str(report_path)

# End of wrapper.py
