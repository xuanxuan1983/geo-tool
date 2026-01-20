# 平台集成配置说明

## 配置文件

- `platform_config.example.yaml` - 配置模板（已提交到Git）
- `platform_config.yaml` - 实际配置文件（包含密钥，已在.gitignore中排除）

## 快速开始

### 方式1：不使用平台集成（默认）

如果不需要Notion/飞书同步功能：

```bash
# 复制示例文件
cp config/platform_config.example.yaml config/platform_config.yaml
```

保持所有API密钥为空字符串即可。系统会自动跳过平台同步，只使用本地文件功能。

### 方式2：配置Notion集成

1. 复制配置文件：
```bash
cp config/platform_config.example.yaml config/platform_config.yaml
```

2. 在 [Notion Integrations](https://www.notion.so/my-integrations) 创建Integration，获取API密钥

3. 在Notion中创建数据库：
   - 客户项目数据库
   - 项目执行记录数据库

4. 将数据库分享给Integration

5. 编辑 `platform_config.yaml`，填入：
   - `notion.api_key` - Integration密钥
   - `notion.databases.clients` - 客户数据库ID
   - `notion.databases.projects` - 项目执行记录数据库ID

6. 设置Relation关联（参见 `docs/notion_relation_setup.md`）

### 方式3：配置飞书集成

1. 复制配置文件
2. 在飞书开放平台创建应用
3. 填入 `feishu` 部分的配置
4. 详细步骤参见飞书开发文档

## Streamlit Cloud部署

在Streamlit Cloud上部署时：

### 方式A：使用Secrets管理（推荐 - 启用Notion/飞书）

**为什么需要 Secrets？**
- 本地的 `platform_config.yaml` 在 `.gitignore` 中，不会推送到 GitHub
- Streamlit Cloud 需要通过 Secrets 功能读取配置

**配置步骤**：

1. **进入 Streamlit Cloud 应用管理页面**
   - 打开你的应用
   - 点击右下角 "Manage app"
   - 点击左侧菜单的 "⚙️ Settings"

2. **打开 Secrets 编辑器**
   - 在 Settings 页面找到 "Secrets" 部分
   - 点击 "Edit Secrets" 按钮

3. **添加配置（TOML格式）**

   复制以下内容并**替换为你的实际配置**：

   ```toml
   # 格式说明：Streamlit Secrets 使用 TOML 格式
   [platform_config]
   default_platform = "notion"

   [platform_config.notion]
   api_key = "YOUR_NOTION_API_KEY"  # 替换为你的 Notion Integration 密钥

   [platform_config.notion.databases]
   clients = "YOUR_CLIENTS_DATABASE_ID"        # 替换为客户数据库ID
   projects = "YOUR_PROJECTS_DATABASE_ID"      # 替换为项目数据库ID
   pressure_tests = "YOUR_PROJECTS_DATABASE_ID"  # 可以与projects相同
   feedback = "YOUR_PROJECTS_DATABASE_ID"        # 可以与projects相同

   [platform_config.notion.pages]
   template_page_id = ""
   workspace_id = ""

   [platform_config.settings]
   auto_archive = true
   archive_days = 90
   auto_notify = true
   notify_on_completion = true
   notify_on_error = true
   upload_results = true
   keep_local_copy = true
   sync_interval_minutes = 30
   ```

   **如何获取你的实际值？**
   - `api_key`: 从本地 `config/platform_config.yaml` 第38行复制
   - `clients`: 从本地配置文件第42行复制
   - `projects`: 从本地配置文件第43行复制

4. **保存并重启应用**
   - 点击 "Save" 按钮
   - Streamlit 会自动重启应用
   - 配置将立即生效

### 方式B：不使用平台集成（跳过Notion/飞书）

如果暂时不需要平台同步功能：

- **不添加任何 Secrets**
- 系统会自动检测到没有配置文件
- 显示警告："⚠️ 平台配置文件不存在，跳过Notion/飞书同步"
- 核心功能（D→B→C→A流水线、PPT生成）正常工作

## 配置验证

在Streamlit界面的"Settings"页面，点击"测试平台连接"按钮验证配置是否正确。

## 故障排除

### 问题：提示"平台配置文件不存在"

**解决**：复制示例配置文件
```bash
cp config/platform_config.example.yaml config/platform_config.yaml
```

### 问题：连接失败

**检查**：
1. API密钥是否正确
2. 数据库是否已分享给Integration
3. 数据库ID是否正确（从URL中复制，不要包含`?v=`之后的部分）

### 问题：Streamlit Cloud上无法读取配置

**解决**：使用Streamlit Secrets功能，在应用管理页面添加secrets.toml

## 更多信息

- Notion集成设置：`docs/notion_relation_setup.md`
- 代码文档：`README.md`
