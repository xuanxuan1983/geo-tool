"""
飞书机器人 - GEO 助手
功能：接收飞书消息，调用 OpenAI API 执行 Prompt，返回结果

部署方式：
1. 在飞书开放平台创建应用，获取 App ID 和 App Secret
2. 配置机器人，设置消息接收地址
3. 部署此脚本到云函数（如阿里云 FC、腾讯云 SCF）或服务器
"""
import json
import hashlib
import time
import requests
from flask import Flask, request, jsonify
from openai import OpenAI
from config import OPENAI_API_KEY, FEISHU_APP_ID, FEISHU_APP_SECRET

app = Flask(__name__)
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# 飞书 API 相关
FEISHU_TENANT_ACCESS_TOKEN_URL = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
FEISHU_SEND_MESSAGE_URL = "https://open.feishu.cn/open-apis/im/v1/messages"

# Prompt 模板（简化版，完整版在 geo_prompt_runner.py）
PROMPT_TEMPLATES = {
    "D": "【语义矩阵提取】请基于以下输入，提取 5 类语义词表（各 10 条）：硬核实体词、对比短语、语义标签、热门提问、标准断言。\n输入：{input}",
    "B": "【转化路径优化】请基于以下输入，设计信任锚点→对比决策位→最后一步动作的转化路径。\n输入：{input}",
    "C": "【内容审计打分】请对以下内容进行 GEO 审计，输出总分、问题清单、整改方案。\n输入：{input}",
    "A": "【商业提案生成】请基于以下输入，生成一份 PPT 级的 GEO 商业提案，包含现状审计、SEO vs GEO 对比、策略、KPI。\n输入：{input}",
}


def get_tenant_access_token():
    """获取飞书 tenant_access_token"""
    resp = requests.post(FEISHU_TENANT_ACCESS_TOKEN_URL, json={
        "app_id": FEISHU_APP_ID,
        "app_secret": FEISHU_APP_SECRET
    })
    return resp.json().get("tenant_access_token")


def send_message(chat_id: str, content: str, msg_type: str = "text"):
    """发送消息到飞书群/个人"""
    token = get_tenant_access_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "receive_id": chat_id,
        "msg_type": msg_type,
        "content": json.dumps({"text": content})
    }
    resp = requests.post(
        f"{FEISHU_SEND_MESSAGE_URL}?receive_id_type=chat_id",
        headers=headers,
        json=data
    )
    return resp.json()


def parse_command(text: str):
    """
    解析用户命令
    格式：@GEO助手 跑D [项目名]
    返回：(prompt_type, project_name) 或 (None, None)
    """
    text = text.strip()
    
    # 匹配 "跑D"、"跑B"、"跑C"、"跑A"
    for prompt_type in ["D", "B", "C", "A"]:
        if f"跑{prompt_type}" in text:
            # 提取项目名（在命令后面的内容）
            parts = text.split(f"跑{prompt_type}")
            project_name = parts[-1].strip() if len(parts) > 1 else ""
            return prompt_type, project_name
    
    return None, None


def run_prompt(prompt_type: str, user_input: str) -> str:
    """调用 OpenAI API 执行 Prompt"""
    template = PROMPT_TEMPLATES.get(prompt_type)
    if not template:
        return f"未知的 Prompt 类型: {prompt_type}"
    
    full_prompt = template.format(input=user_input)
    
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "你是一名专业的 GEO（生成式引擎优化）专家。"},
            {"role": "user", "content": full_prompt}
        ],
        temperature=0.7,
        max_tokens=2000
    )
    
    return response.choices[0].message.content


@app.route("/webhook", methods=["POST"])
def webhook():
    """飞书消息回调"""
    data = request.json
    
    # 验证请求（URL 验证）
    if "challenge" in data:
        return jsonify({"challenge": data["challenge"]})
    
    # 处理消息事件
    event = data.get("event", {})
    message = event.get("message", {})
    chat_id = message.get("chat_id")
    content = message.get("content", "{}")
    
    try:
        text = json.loads(content).get("text", "")
    except:
        text = ""
    
    # 解析命令
    prompt_type, project_name = parse_command(text)
    
    if prompt_type:
        # 发送"正在处理"消息
        send_message(chat_id, f"⏳ 正在执行 Prompt {prompt_type}，请稍候...")
        
        # 这里应该从飞书多维表格读取项目的输入卡
        # 简化版：直接使用 project_name 作为输入
        user_input = f"项目：{project_name}" if project_name else "（未指定项目）"
        
        # 执行 Prompt
        result = run_prompt(prompt_type, user_input)
        
        # 发送结果（截断以避免消息过长）
        if len(result) > 2000:
            result = result[:2000] + "\n\n... (结果过长，已截断)"
        
        send_message(chat_id, f"✅ Prompt {prompt_type} 执行完成：\n\n{result}")
    else:
        # 帮助信息
        help_text = """👋 我是 GEO 助手，支持以下命令：

• 跑D [项目名] - 执行语义矩阵提取
• 跑B [项目名] - 执行转化路径优化
• 跑C [内容] - 执行内容审计打分
• 跑A [项目名] - 生成商业提案

示例：@GEO助手 跑D 品牌A"""
        send_message(chat_id, help_text)
    
    return jsonify({"code": 0})


if __name__ == "__main__":
    app.run(port=8080, debug=True)
