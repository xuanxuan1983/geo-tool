#!/usr/bin/env python3
"""清理测试数据脚本"""
import yaml
import requests
from pathlib import Path
import shutil

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
print("🧹 GEO工具测试数据清理")
print("=" * 70)

# 定义测试数据关键词
test_keywords = [
    "测试",
    "test",
    "Test",
    "关联测试",
    "流程测试"
]

# 1. 清理客户项目数据库中的测试数据
print("\n📋 步骤1: 扫描客户项目数据库")
print("-" * 70)

clients_response = requests.post(
    f"https://api.notion.com/v1/databases/{notion_config['databases']['clients']}/query",
    headers=headers
).json()

test_projects = []
for page in clients_response.get('results', []):
    props = page['properties']

    # 获取客户名称
    client_name = ""
    for key, value in props.items():
        if value['type'] == 'title' and value['title']:
            client_name = value['title'][0]['text']['content']
            break

    # 检查是否是测试数据
    is_test = any(keyword in client_name for keyword in test_keywords)

    if is_test:
        test_projects.append({
            'id': page['id'],
            'name': client_name
        })
        print(f"  🔍 找到测试项目: {client_name}")

print(f"\n共找到 {len(test_projects)} 个测试项目")

# 2. 清理项目执行记录数据库中的测试数据
print("\n📋 步骤2: 扫描项目执行记录数据库")
print("-" * 70)

projects_response = requests.post(
    f"https://api.notion.com/v1/databases/{notion_config['databases']['projects']}/query",
    headers=headers
).json()

test_records = []
test_project_ids = [p['id'] for p in test_projects]

for page in projects_response.get('results', []):
    props = page['properties']

    # 获取任务名称
    task_name = ""
    for key, value in props.items():
        if value['type'] == 'title' and value['title']:
            task_name = value['title'][0]['text']['content']
            break

    # 获取关联的项目ID
    related_project_id = None
    for key, value in props.items():
        if value['type'] == 'relation' and value.get('relation'):
            if value['relation']:
                related_project_id = value['relation'][0]['id']
                break

    # 检查是否关联到测试项目
    is_test_record = (related_project_id in test_project_ids) or \
                     any(keyword in task_name for keyword in test_keywords)

    if is_test_record:
        test_records.append({
            'id': page['id'],
            'name': task_name
        })
        print(f"  🔍 找到测试记录: {task_name}")

print(f"\n共找到 {len(test_records)} 条测试执行记录")

# 3. 询问用户确认
print("\n" + "=" * 70)
print("⚠️  确认清理")
print("=" * 70)
print(f"即将删除：")
print(f"  - {len(test_projects)} 个客户项目记录")
print(f"  - {len(test_records)} 条项目执行记录")
print()

# 列出将要删除的项目
if test_projects:
    print("客户项目:")
    for proj in test_projects:
        print(f"  • {proj['name']}")
    print()

if test_records:
    print("执行记录:")
    for rec in test_records:
        print(f"  • {rec['name']}")
    print()

response = input("确认删除以上Notion记录? (yes/no): ")

if response.lower() == 'yes':
    print("\n🗑️  开始删除Notion记录...")

    # 删除项目执行记录（先删除子记录）
    for record in test_records:
        try:
            delete_response = requests.patch(
                f"https://api.notion.com/v1/pages/{record['id']}",
                headers=headers,
                json={"archived": True}
            )
            if delete_response.status_code == 200:
                print(f"  ✅ 已删除记录: {record['name']}")
            else:
                print(f"  ❌ 删除失败: {record['name']} - {delete_response.text}")
        except Exception as e:
            print(f"  ❌ 删除出错: {record['name']} - {e}")

    # 删除客户项目
    for project in test_projects:
        try:
            delete_response = requests.patch(
                f"https://api.notion.com/v1/pages/{project['id']}",
                headers=headers,
                json={"archived": True}
            )
            if delete_response.status_code == 200:
                print(f"  ✅ 已删除项目: {project['name']}")
            else:
                print(f"  ❌ 删除失败: {project['name']} - {delete_response.text}")
        except Exception as e:
            print(f"  ❌ 删除出错: {project['name']} - {e}")

    print(f"\n✅ Notion记录清理完成！")
else:
    print("\n❌ 已取消Notion记录清理")

# 4. 清理本地测试文件
print("\n" + "=" * 70)
print("📁 步骤3: 清理本地测试文件")
print("=" * 70)

output_dir = Path(__file__).parent.parent / 'output'
test_folders = []

if output_dir.exists():
    for folder in output_dir.iterdir():
        if folder.is_dir():
            folder_name = folder.name
            is_test_folder = any(keyword in folder_name for keyword in test_keywords)

            if is_test_folder:
                test_folders.append(folder)
                print(f"  🔍 找到测试文件夹: {folder_name}")

print(f"\n共找到 {len(test_folders)} 个测试文件夹")

if test_folders:
    response = input("\n确认删除以上本地文件夹? (yes/no): ")

    if response.lower() == 'yes':
        print("\n🗑️  开始删除本地文件...")
        for folder in test_folders:
            try:
                shutil.rmtree(folder)
                print(f"  ✅ 已删除文件夹: {folder.name}")
            except Exception as e:
                print(f"  ❌ 删除失败: {folder.name} - {e}")

        print(f"\n✅ 本地文件清理完成！")
    else:
        print("\n❌ 已取消本地文件清理")
else:
    print("\n✅ 没有需要清理的本地测试文件")

# 5. 清理测试脚本生成的临时文件
print("\n" + "=" * 70)
print("📁 步骤4: 清理临时文件")
print("=" * 70)

temp_files = [
    Path(__file__).parent.parent / 'input' / 'flow_test_client.json',
    Path(__file__).parent / 'test_extraction.py',
    Path(__file__).parent / 'test_new_format_extraction.py',
    Path(__file__).parent / 'test_relation.py',
    Path(__file__).parent / 'verify_relation.py',
    Path(__file__).parent / 'check_notion_data.py',
]

temp_files_found = [f for f in temp_files if f.exists()]

if temp_files_found:
    print(f"找到 {len(temp_files_found)} 个临时文件:")
    for f in temp_files_found:
        print(f"  • {f.name}")

    response = input("\n确认删除以上临时文件? (yes/no): ")

    if response.lower() == 'yes':
        for f in temp_files_found:
            try:
                f.unlink()
                print(f"  ✅ 已删除: {f.name}")
            except Exception as e:
                print(f"  ❌ 删除失败: {f.name} - {e}")
        print(f"\n✅ 临时文件清理完成！")
    else:
        print("\n❌ 已取消临时文件清理")
else:
    print("✅ 没有需要清理的临时文件")

print("\n" + "=" * 70)
print("🎉 清理完成！")
print("=" * 70)
