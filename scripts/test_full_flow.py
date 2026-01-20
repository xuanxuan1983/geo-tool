#!/usr/bin/env python3
"""完整流程测试 - 从创建项目到Notion同步"""
import json
import time
from pathlib import Path
from datetime import datetime

# 创建测试客户数据
test_client_data = {
    "client_name": "流程测试客户",
    "industry": "医美",
    "target_audience": "25-45岁女性",
    "product": "胶原蛋白填充剂",
    "product_features": [
        "械字号III类医疗器械",
        "采用专利交联技术",
        "临床验证安全有效",
        "效果可持续12-18个月"
    ],
    "advantages": [
        "获得NMPA认证",
        "多项临床研究支持",
        "注射后即刻见效",
        "恢复期短"
    ],
    "target_keywords": [
        "胶原蛋白填充",
        "医美抗衰",
        "面部年轻化",
        "械字号填充剂"
    ],
    "competitors": [
        "玻尿酸",
        "肉毒素"
    ]
}

print("=" * 70)
print("🧪 GEO工具完整流程测试")
print("=" * 70)
print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"客户名称: {test_client_data['client_name']}")
print()

# 1. 创建输入文件
print("📝 步骤1: 创建测试输入文件")
print("-" * 70)
input_dir = Path(__file__).parent.parent / "input"
input_dir.mkdir(exist_ok=True)
input_file = input_dir / "flow_test_client.json"

with open(input_file, 'w', encoding='utf-8') as f:
    json.dump(test_client_data, f, ensure_ascii=False, indent=2)

print(f"✅ 输入文件已创建: {input_file}")
print()

# 2. 初始化平台管理器并创建项目
print("🚀 步骤2: 创建项目并同步到Notion")
print("-" * 70)

from platform_integration_manager import PlatformIntegrationManager
from platform_adapter import ProjectStatus

manager = PlatformIntegrationManager()

project_data = {
    "client_name": test_client_data['client_name'],
    "industry": test_client_data['industry'],
    "status": ProjectStatus.IN_PROGRESS.value,
    "description": f"产品: {test_client_data['product']}, 目标: 获客"
}

try:
    project_id = manager.create_new_project(project_data)
    print(f"✅ 项目已创建并同步到Notion")
    print(f"   项目ID: {project_id}")
except Exception as e:
    print(f"❌ 项目创建失败: {e}")
    exit(1)

print()

# 3. 执行D→B→C→A流程
print("⚙️  步骤3: 执行D→B→C→A全自动流水线")
print("-" * 70)

from wrapper import run_pipeline
from platform_adapter import StageStatus

client_name = test_client_data['client_name']

try:
    print("🔄 开始执行流水线...")
    start_time = time.time()

    # 执行流水线
    output_folder = run_pipeline(client_name, str(input_file))

    duration = time.time() - start_time
    print(f"✅ 流水线执行完成 (耗时: {duration:.1f}秒)")
    print(f"   输出目录: {output_folder}")

    # 检查生成的文件
    output_path = Path(output_folder)
    generated_files = list(output_path.glob("*.md"))
    print(f"\n📄 生成的文件 ({len(generated_files)}个):")
    for file in sorted(generated_files):
        size_kb = file.stat().st_size / 1024
        print(f"   - {file.name} ({size_kb:.1f} KB)")

except Exception as e:
    print(f"❌ 流水线执行失败: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print()

# 4. 同步阶段记录到Notion
print("📊 步骤4: 同步阶段记录到Notion")
print("-" * 70)

for stage in ["D", "B", "C", "A"]:
    try:
        manager.update_stage_progress(
            project_id=project_id,
            stage=stage,
            status=StageStatus.COMPLETED,
            duration_minutes=int(duration / 4)
        )
        print(f"✅ {stage}阶段记录已同步")
    except Exception as e:
        print(f"⚠️  {stage}阶段同步失败: {e}")

print()

# 5. 生成PPT
print("📊 步骤5: 生成PPT演示文稿")
print("-" * 70)

try:
    from ppt_generator import generate_ppt
    ppt_path = generate_ppt(client_name, output_folder)
    print(f"✅ PPT已生成: {ppt_path}")
except Exception as e:
    print(f"⚠️  PPT生成失败: {e}")

print()

# 6. 完成项目
print("✨ 步骤6: 标记项目完成")
print("-" * 70)

try:
    results = {
        "d_matrix": str(output_path / f"{client_name}_D_矩阵提取.md"),
        "b_conversion": str(output_path / f"{client_name}_B_转化路径.md"),
        "c_quality": str(output_path / f"{client_name}_C_质检暴改.md"),
        "a_proposal": str(output_path / f"{client_name}_A_商业提案.md"),
    }

    doc_url = manager.complete_project(project_id, client_name, results)
    print(f"✅ 项目已标记为完成")
    if doc_url:
        print(f"   文档链接: {doc_url}")
except Exception as e:
    print(f"⚠️  项目完成标记失败: {e}")

print()

# 7. 执行压力测试
print("🔥 步骤7: 执行AI压力测试（自动提取关键词和问题）")
print("-" * 70)

try:
    from wrapper import run_pressure_test

    # 使用自动提取的关键词和问题
    engines = ["deepseek"]

    print("🔄 开始压力测试...")
    test_start = time.time()

    report_path = run_pressure_test(client_name, output_folder, engines)

    test_duration = time.time() - test_start
    print(f"✅ 压力测试完成 (耗时: {test_duration:.1f}秒)")
    print(f"   报告路径: {report_path}")

    # 检查报告文件大小
    if Path(report_path).exists():
        report_size = Path(report_path).stat().st_size / 1024
        print(f"   报告大小: {report_size:.1f} KB")

except Exception as e:
    print(f"❌ 压力测试失败: {e}")
    import traceback
    traceback.print_exc()

print()

# 8. 验证总结
print("=" * 70)
print("🎉 完整流程测试完成！")
print("=" * 70)
print()
print("📋 请在Notion中验证以下内容：")
print()
print("1️⃣  客户项目数据库 (https://www.notion.so/1a57b2c1f622436b96192a7f06134f0f)")
print(f"   - 查找「{client_name}」项目")
print("   - 检查项目状态是否为「已完成」")
print("   - 查看是否有反向关联显示4个执行记录（D、B、C、A）")
print()
print("2️⃣  项目执行记录数据库 (https://www.notion.so/791f1ded941f4818b748aba51f3ffc65)")
print("   - 查找4条新记录：D阶段、B阶段、C阶段、A阶段")
print(f"   - 每条记录的「项目ID」应显示为可点击链接")
print("   - 点击链接应跳转到「流程测试客户」项目")
print()
print("3️⃣  本地文件")
print(f"   - 输出目录: {output_folder}")
print(f"   - 包含: D矩阵、B转化、C质检、A提案、压力测试报告等文件")
print()
print("✅ 如果以上都正常，说明完整流程运行成功！")
