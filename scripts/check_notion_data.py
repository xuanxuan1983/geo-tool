#!/usr/bin/env python3
"""检查Notion数据库中的实际数据"""
import yaml
from pathlib import Path
from notion_client import Client

# 加载配置
config_path = Path(__file__).parent.parent / "config" / "platform_config.yaml"
with open(config_path) as f:
    config = yaml.safe_load(f)

notion_config = config["notion"]
client = Client(auth=notion_config["api_key"])

print("=" * 60)
print("📊 客户项目数据库内容")
print("=" * 60)

try:
    # 查询客户项目数据库
    import requests
    headers = {
        "Authorization": f"Bearer {notion_config['api_key']}",
        "Notion-Version": "2022-06-28"
    }

    clients_response = requests.post(
        f"https://api.notion.com/v1/databases/{notion_config['databases']['clients']}/query",
        headers=headers
    ).json()

    if "results" in clients_response:
        print(f"\n总记录数: {len(clients_response['results'])}\n")

        for idx, page in enumerate(clients_response['results'], 1):
            props = page['properties']
            print(f"{idx}. ", end="")

            # 打印标题字段
            for key, value in props.items():
                if value['type'] == 'title':
                    title = value['title'][0]['text']['content'] if value['title'] else ""
                    print(f"{key}: {title}")

            # 打印其他字段
            for key, value in props.items():
                if value['type'] == 'select' and value.get('select'):
                    print(f"   {key}: {value['select']['name']}")
                elif value['type'] == 'rich_text' and value.get('rich_text'):
                    text = value['rich_text'][0]['text']['content'] if value['rich_text'] else ""
                    if text:
                        print(f"   {key}: {text}")
            print()
    else:
        print(f"❌ 返回错误: {clients_response}")

except Exception as e:
    print(f"❌ 查询客户项目数据库失败: {e}")

print("\n" + "=" * 60)
print("📋 项目执行记录数据库内容")
print("=" * 60)

try:
    # 查询项目执行记录数据库
    projects_response = requests.post(
        f"https://api.notion.com/v1/databases/{notion_config['databases']['projects']}/query",
        headers=headers
    ).json()

    if "results" in projects_response:
        print(f"\n总记录数: {len(projects_response['results'])}\n")

        for idx, page in enumerate(projects_response['results'], 1):
            props = page['properties']
            print(f"{idx}. ", end="")

            # 打印标题字段
            for key, value in props.items():
                if value['type'] == 'title':
                    title = value['title'][0]['text']['content'] if value['title'] else ""
                    print(f"{key}: {title}")

            # 打印其他字段
            for key, value in props.items():
                if value['type'] == 'select' and value.get('select'):
                    print(f"   {key}: {value['select']['name']}")
                elif value['type'] == 'rich_text' and value.get('rich_text'):
                    text = value['rich_text'][0]['text']['content'] if value['rich_text'] else ""
                    if text:
                        print(f"   {key}: {text}")
            print()
    else:
        print(f"❌ 返回错误: {projects_response}")

except Exception as e:
    print(f"❌ 查询项目执行记录数据库失败: {e}")
