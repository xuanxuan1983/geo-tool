"""
配置文件 - API 密钥与系统设置
请将此文件中的 API 密钥替换为你自己的密钥
⚠️ 不要将此文件上传到公开仓库！
"""

# DeepSeek API 密钥（获取地址：https://platform.deepseek.com/）
DEEPSEEK_API_KEY = "sk-e7199680996d482b8464f9605a2e32f6"
DEEPSEEK_BASE_URL = "https://api.deepseek.com"

# 飞书应用凭证（获取地址：https://open.feishu.cn/）
FEISHU_APP_ID = "your-feishu-app-id"
FEISHU_APP_SECRET = "your-feishu-app-secret"

# 默认模型设置（DeepSeek）
DEFAULT_MODEL = "deepseek-chat"  # 或 deepseek-reasoner
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 4000
