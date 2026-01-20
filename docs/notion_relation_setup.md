# Notion数据库关联配置指南

## 目标
将"项目执行记录"数据库与"客户项目数据库"建立关联关系

## 操作步骤

### 1. 在"项目执行记录"数据库中添加Relation字段

1. 打开"项目执行记录"数据库：
   https://www.notion.so/791f1ded941f4818b748aba51f3ffc65

2. 点击数据库右上角的"+" 添加新列

3. 配置字段：
   - **字段名称**：`关联项目`（或保留现有的"项目ID"字段名）
   - **字段类型**：选择 **Relation（关联）**
   - **关联到的数据库**：选择"客户项目数据库"
   - **显示方式**：建议选择"Show as page"

4. 点击"Create"创建字段

### 2. （可选）删除旧的"项目ID"文本字段

如果您创建了新的"关联项目"字段，可以删除旧的纯文本"项目ID"字段：
1. 点击旧字段的下拉菜单
2. 选择"Delete property"

### 3. 在"客户项目数据库"中查看反向关联

创建Relation后，Notion会自动在"客户项目数据库"中创建反向关联字段：
1. 打开"客户项目数据库"：
   https://www.notion.so/1a57b2c1f622436b96192a7f06134f0f

2. 您会看到一个新字段（通常叫"项目执行记录"或类似名称）
3. 点击任意客户项目，就能看到它的所有D、B、C、A阶段记录

### 4. （推荐）添加Rollup字段统计

在"客户项目数据库"中可以添加统计字段：

**示例：统计执行记录数量**
1. 添加新列
2. 类型：Rollup
3. Relation：选择刚创建的反向关联字段
4. Property：选择"任务名称"
5. Calculate：选择"Count all"
6. 重命名为"执行记录数"

**示例：统计总耗时**
1. 添加新列
2. 类型：Rollup
3. Relation：选择反向关联字段
4. Property：选择"完成时间"
5. Calculate：选择"Count all"或其他统计方式

## 获取Relation字段名称

配置完成后，请运行以下命令查看字段名称：

```bash
cd "/Users/xuan/Documents/write agent/geo_business_tool/scripts"
python3 -c "
import yaml
import requests
from pathlib import Path

config_path = Path.cwd().parent / 'config' / 'platform_config.yaml'
with open(config_path) as f:
    config = yaml.safe_load(f)

headers = {
    'Authorization': f'Bearer {config[\"notion\"][\"api_key\"]}',
    'Notion-Version': '2022-06-28'
}

# 查询项目执行记录数据库结构
response = requests.get(
    f'https://api.notion.com/v1/databases/{config[\"notion\"][\"databases\"][\"projects\"]}',
    headers=headers
).json()

print('项目执行记录数据库字段：')
for name, prop in response['properties'].items():
    print(f'  - {name}: {prop[\"type\"]}')
    if prop['type'] == 'relation':
        print(f'    → 关联到: {prop[\"relation\"][\"database_id\"]}')
"
```

## 验证配置

配置完成后，我会修改代码使用新的Relation字段。

---

**配置完成后请告诉我**，我会更新代码以使用Relation关联。
