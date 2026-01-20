#!/usr/bin/env python3
"""测试Notion关联功能"""
import yaml
from pathlib import Path
from datetime import datetime
from notion_adapter import NotionProjectManager
from platform_adapter import StageStatus

# 加载配置
config_path = Path(__file__).parent.parent / 'config' / 'platform_config.yaml'
with open(config_path) as f:
    config = yaml.safe_load(f)

# 初始化管理器
manager = NotionProjectManager(config['notion'])

print("=" * 60)
print("测试1: 创建测试项目")
print("=" * 60)

# 创建测试项目
project_data = {
    "client_name": "关联测试客户",
    "industry": "医美",
    "description": "测试Relation关联功能"
}

project_id = manager.create_project(project_data)
print(f"✅ 项目创建成功: {project_id}\n")

print("=" * 60)
print("测试2: 创建阶段记录（使用Relation）")
print("=" * 60)

# 创建阶段记录
stage_data = {
    "project_id": project_id,
    "stage": "D",
    "status": StageStatus.COMPLETED.value,
    "end_time": datetime.now().timestamp()
}

stage_id = manager.add_stage_record(stage_data)
print(f"✅ 阶段记录创建成功: {stage_id}\n")

print("=" * 60)
print("测试3: 验证关联")
print("=" * 60)
print(f"请在Notion中验证：")
print(f"1. 打开客户项目数据库，找到「关联测试客户」")
print(f"2. 点击该项目，应该能看到关联的「D阶段」执行记录")
print(f"3. 点击「项目执行记录」数据库中的「D阶段」记录")
print(f"4. 「项目ID」列应该显示为可点击的链接，点击可跳转到客户项目")
print("\n✅ 如果以上都正常，说明Relation关联配置成功！")
