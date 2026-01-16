# Notion 配置指南

## 一、创建工作区结构

在 Notion 中创建以下页面和数据库：

```
GEO 业务系统/
├── 📋 客户输入卡（数据库）
├── 📊 项目看板（数据库）
├── ✅ 验收卡（数据库）
└── 📁 交付物归档（页面）
```

## 二、配置「客户输入卡」数据库

按照 `notion/01_客户输入卡.md` 中的属性设置创建数据库。

## 三、配置「项目看板」数据库

按照 `notion/02_项目看板.md` 中的属性设置创建数据库。
建议使用「看板视图」按阶段分组。

## 四、配置 Make 自动化（执行 Prompt）

### 步骤 1：注册 Make 账号

访问 [Make.com](https://www.make.com/)，注册免费账号。

### 步骤 2：创建场景

1. 新建场景，添加以下模块：
   - **Notion → Watch Database Items**：监听「项目看板」数据库
   - **HTTP → Make a Request**：调用 OpenAI API
   - **Notion → Update a Database Item**：将结果写回 Notion

### 步骤 3：配置 OpenAI API 调用

HTTP 模块配置：
- **URL**: `https://api.openai.com/v1/chat/completions`
- **Method**: POST
- **Headers**:
  - `Authorization`: `Bearer YOUR_OPENAI_API_KEY`
  - `Content-Type`: `application/json`
- **Body**:
```json
{
  "model": "gpt-4o",
  "messages": [
    {"role": "system", "content": "你是一名 GEO 专家。"},
    {"role": "user", "content": "{{从 Notion 读取的 Prompt + 输入卡}}"}
  ]
}
```

### 步骤 4：设置触发条件

- 当「项目看板」中某条记录的「状态」变为「进行中」时触发
- 根据「当前阶段」字段选择对应的 Prompt（D/B/C/A）

## 五、添加 Notion 按钮（手动触发）

在项目看板的模板中添加按钮：

1. 点击 `/button` 添加按钮
2. 按钮名称：「运行 Prompt D」
3. 动作：打开链接 → 填入 Make 的 Webhook URL

## 六、权限设置（保护核心 Prompt）

1. 核心 Prompt 存储在 Make 场景中，不在 Notion 显示
2. 将「验收卡」数据库设为「只能填结果」，团队不能修改验收规则
3. 使用 Notion 权限组，不同成员看到不同页面

## 七、快速上手

1. 在「客户输入卡」中新建一条记录，填写客户信息
2. 在「项目看板」中新建一条记录，关联到该客户
3. 将项目状态改为「进行中」，Make 自动执行 Prompt
4. 等待几分钟，结果会自动写入「交付物链接」字段
