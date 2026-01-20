#!/usr/bin/env python3
"""自动清理测试数据（无需确认）"""
import yaml
import requests
from pathlib import Path
import shutil
import sys

# 加载配置
config_path = Path(__file__).parent.parent / 'config' / 'platform_config.yaml'
with open(config_path) as f:
    config = yaml.safe_load(f)

notion_config = config['notion']
headers = {
    'Authorization': f"Bearer {notion_config['api_key']}",
    'Notion-Version': '2022-06-28'
}

print("=" * 70)
print("🧹 GEO工具测试数据自动清理")
print("=" * 70)

# 定义测试数据关键词
test_keywords = [
    "测试",
    "test",
    "Test",
    "关联测试",
    "流程测试"
]

# 1. 清理客户项目数据库
print("\n📋 步骤1: 清理客户项目数据库")
print("-" * 70)

clients_response = requests.post(
    f"https://api.notion.com/v1/databases/{notion_config['databases']['clients']}/query",
    headers=headers
).json()

test_projects = []
deleted_projects = 0

for page in clients_response.get('results', []):
    props = page['properties']

    client_name = ""
    for key, value in props.items():
        if value['type'] == 'title' and value['title']:
            client_name = value['title'][0]['text']['content']
            break

    is_test = any(keyword in client_name for keyword in test_keywords)

    if is_test:
        try:
            delete_response = requests.patch(
                f"https://api.notion.com/v1/pages/{page['id']}",
                headers=headers,
                json={"archived": True}
            )
            if delete_response.status_code == 200:
                print(f"  ✅ 已删除项目: {client_name}")
                deleted_projects += 1
            else:
                print(f"  ❌ 删除失败: {client_name}")
        except Exception as e:
            print(f"  ❌ 删除出错: {client_name} - {e}")

print(f"\n✅ 共删除 {deleted_projects} 个测试项目")

# 2. 清理项目执行记录
print("\n📋 步骤2: 清理项目执行记录数据库")
print("-" * 70)

projects_response = requests.post(
    f"https://api.notion.com/v1/databases/{notion_config['databases']['projects']}/query",
    headers=headers
).json()

deleted_records = 0

for page in projects_response.get('results', []):
    props = page['properties']

    task_name = ""
    for key, value in props.items():
        if value['type'] == 'title' and value['title']:
            task_name = value['title'][0]['text']['content']
            break

    # 简单策略：删除所有阶段记录和包含测试关键词的记录
    is_test_record = any(keyword in task_name for keyword in test_keywords) or \
                     task_name in ["D阶段", "B阶段", "C阶段", "A阶段", "测试任务"]

    if is_test_record:
        try:
            delete_response = requests.patch(
                f"https://api.notion.com/v1/pages/{page['id']}",
                headers=headers,
                json={"archived": True}
            )
            if delete_response.status_code == 200:
                print(f"  ✅ 已删除记录: {task_name}")
                deleted_records += 1
            else:
                print(f"  ❌ 删除失败: {task_name}")
        except Exception as e:
            print(f"  ❌ 删除出错: {task_name} - {e}")

print(f"\n✅ 共删除 {deleted_records} 条执行记录")

# 3. 清理本地测试文件
print("\n📁 步骤3: 清理本地测试文件")
print("-" * 70)

output_dir = Path(__file__).parent.parent / 'output'
deleted_folders = 0

if output_dir.exists():
    for folder in output_dir.iterdir():
        if folder.is_dir():
            folder_name = folder.name
            is_test_folder = any(keyword in folder_name for keyword in test_keywords)

            if is_test_folder:
                try:
                    shutil.rmtree(folder)
                    print(f"  ✅ 已删除文件夹: {folder_name}")
                    deleted_folders += 1
                except Exception as e:
                    print(f"  ❌ 删除失败: {folder_name} - {e}")

print(f"\n✅ 共删除 {deleted_folders} 个测试文件夹")

# 4. 清理临时测试脚本
print("\n📁 步骤4: 清理临时测试脚本")
print("-" * 70)

temp_files = [
    Path(__file__).parent.parent / 'input' / 'flow_test_client.json',
    Path(__file__).parent / 'test_extraction.py',
    Path(__file__).parent / 'test_new_format_extraction.py',
    Path(__file__).parent / 'test_relation.py',
    Path(__file__).parent / 'verify_relation.py',
    Path(__file__).parent / 'check_notion_data.py',
    Path(__file__).parent / 'test_full_flow.py',
]

deleted_files = 0
for f in temp_files:
    if f.exists():
        try:
            f.unlink()
            print(f"  ✅ 已删除: {f.name}")
            deleted_files += 1
        except Exception as e:
            print(f"  ❌ 删除失败: {f.name} - {e}")

print(f"\n✅ 共删除 {deleted_files} 个临时文件")

# 总结
print("\n" + "=" * 70)
print("🎉 清理完成！")
print("=" * 70)
print(f"总计:")
print(f"  • Notion项目记录: {deleted_projects}")
print(f"  • Notion执行记录: {deleted_records}")
print(f"  • 本地文件夹: {deleted_folders}")
print(f"  • 临时脚本: {deleted_files}")
print("=" * 70)
