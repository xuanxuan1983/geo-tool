# wrapper.py – Utility functions to invoke GEO pipeline scripts with retry logic

import subprocess
import os
from pathlib import Path
from typing import List
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

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
    script_path = Path(__file__).parent / "ai_pressure_test_multi.py"
    engines_arg = ",".join(engines)
    cmd = [
        "python3",
        str(script_path),
        "--client",
        client_name,
        "--output_dir",
        client_folder,
        "--engines",
        engines_arg,
    ]
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
