#!/usr/bin/env python3
"""验证Notion数据库关联配置"""
import yaml
import requests
from pathlib import Path

config_path = Path(__file__).parent.parent / 'config' / 'platform_config.yaml'
with open(config_path) as f:
    config = yaml.safe_load(f)

notion_config = config['notion']
headers = {
    'Authorization': f"Bearer {notion_config['api_key']}",
    'Notion-Version': '2022-06-28'
}

# 查询项目执行记录数据库结构
response = requests.get(
    f"https://api.notion.com/v1/databases/{notion_config['databases']['projects']}",
    headers=headers
).json()

print('📋 项目执行记录数据库字段：')
print('=' * 60)

relation_field_name = None
for name, prop in response['properties'].items():
    prop_type = prop['type']
    print(f'{name}:')
    print(f'  类型: {prop_type}')
    if prop_type == 'relation':
        db_id = prop['relation']['database_id']
        print(f'  ✅ 关联到数据库: {db_id}')
        relation_field_name = name
    print()

if relation_field_name:
    print(f"✅ 找到Relation字段: '{relation_field_name}'")
else:
    print("❌ 未找到Relation字段")
