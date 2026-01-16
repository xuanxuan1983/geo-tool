# feishu_oauth.py – Minimal Feishu OAuth helper for Streamlit

import os
import requests
from urllib.parse import urlencode

# Load required env vars (must be set in .env)
FEISHU_APP_ID = os.getenv("FEISHU_APP_ID")
FEISHU_APP_SECRET = os.getenv("FEISHU_APP_SECRET")
FEISHU_REDIRECT_URI = os.getenv("FEISHU_REDIRECT_URI")

def get_auth_url(state: str = "geo_tool") -> str:
    """Generate the Feishu authorization URL.
    `state` can be any string to identify the request – we use a constant.
    """
    base = "https://open.feishu.cn/open-apis/authen/v1/index"
    params = {
        "client_id": FEISHU_APP_ID,
        "redirect_uri": FEISHU_REDIRECT_URI,
        "response_type": "code",
        "scope": "user_info",
        "state": state,
    }
    return f"{base}?{urlencode(params)}"

def exchange_code_for_token(code: str) -> dict:
    """Exchange the authorization `code` for an access token.
    Returns the JSON response from Feishu.
    """
    url = "https://open.feishu.cn/open-apis/authen/v1/access_token"
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": FEISHU_APP_ID,
        "client_secret": FEISHU_APP_SECRET,
    }
    resp = requests.post(url, json=payload)
    resp.raise_for_status()
    return resp.json()["data"]

def get_user_info(access_token: str) -> dict:
    """Fetch basic user info using the access token.
    Returns a dict with fields like `name`, `email`, `mobile`.
    """
    url = "https://open.feishu.cn/open-apis/contact/v3/users/me"
    headers = {"Authorization": f"Bearer {access_token}"}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()["data"]

# Helper used by auth.py
def feishu_login_flow(query_params: dict) -> str:
    """Process the query parameters from Streamlit after redirect.
    If ``code`` is present, exchange it and return a role string.
    Returns ``"admin"`` for now (you can extend with email checks).
    """
    code = query_params.get("code")
    if not code:
        return None
    token_data = exchange_code_for_token(code)
    access_token = token_data.get("access_token")
    if not access_token:
        return None
    user_info = get_user_info(access_token)
    # Simple role assignment – you can add domain checks here
    return "admin" if user_info.get("email", "").endswith("@yourcompany.com") else "member"
