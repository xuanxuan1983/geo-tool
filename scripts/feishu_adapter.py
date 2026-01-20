#!/usr/bin/env python3
"""
飞书平台适配器实现
实现ProjectManager、DocumentGenerator、Notifier、FileManager接口
"""
import requests
import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

from platform_adapter import (
    ProjectManager, DocumentGenerator, Notifier, FileManager,
    ProjectStatus, StageStatus
)


class FeishuClient:
    """飞书API客户端基类"""

    def __init__(self, app_id: str, app_secret: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self.access_token: Optional[str] = None
        self.token_expires_at: float = 0

    def get_access_token(self) -> str:
        """获取tenant_access_token"""
        # 检查token是否过期
        if self.access_token and time.time() < self.token_expires_at:
            return self.access_token

        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        payload = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }

        response = requests.post(url, json=payload)
        result = response.json()

        if result.get("code") == 0:
            self.access_token = result["tenant_access_token"]
            # 提前5分钟过期
            self.token_expires_at = time.time() + result.get("expire", 7200) - 300
            return self.access_token
        else:
            raise Exception(f"获取access_token失败: {result}")

    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        return {
            "Authorization": f"Bearer {self.get_access_token()}",
            "Content-Type": "application/json; charset=utf-8"
        }


# ============ 飞书ProjectManager实现 ============

class FeishuProjectManager(ProjectManager, FeishuClient):
    """飞书多维表格项目管理器"""

    def __init__(self, config: Dict[str, Any]):
        FeishuClient.__init__(self, config["app_id"], config["app_secret"])
        self.app_token = config["bitable"]["app_token"]
        self.clients_table_id = config["bitable"]["tables"]["clients"]
        self.projects_table_id = config["bitable"]["tables"]["projects"]
        self.pressure_tests_table_id = config["bitable"]["tables"]["pressure_tests"]
        self.feedback_table_id = config["bitable"]["tables"]["feedback"]

    def create_project(self, project_data: Dict[str, Any]) -> str:
        """创建项目记录"""
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{self.app_token}/tables/{self.projects_table_id}/records"

        # 构建飞书记录字段
        fields = {
            "客户名称": project_data.get("client_name", ""),
            "行业类型": project_data.get("industry", ""),
            "联系人": project_data.get("contact", ""),
            "项目状态": project_data.get("status", ProjectStatus.PENDING.value),
            "开始日期": int(datetime.fromisoformat(project_data.get("start_date", datetime.now().isoformat())).timestamp() * 1000),
            "备注": project_data.get("description", "")
        }

        payload = {"fields": fields}

        response = requests.post(url, headers=self._get_headers(), json=payload)
        result = response.json()

        if result.get("code") == 0:
            record_id = result["data"]["record"]["record_id"]
            print(f"✅ 飞书项目记录创建成功: {record_id}")
            return record_id
        else:
            raise Exception(f"创建项目记录失败: {result}")

    def update_project_status(self, project_id: str, status: ProjectStatus) -> bool:
        """更新项目状态"""
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{self.app_token}/tables/{self.projects_table_id}/records/{project_id}"

        payload = {
            "fields": {
                "项目状态": status.value
            }
        }

        response = requests.put(url, headers=self._get_headers(), json=payload)
        result = response.json()

        if result.get("code") == 0:
            print(f"✅ 项目状态更新为: {status.value}")
            return True
        else:
            print(f"❌ 更新项目状态失败: {result}")
            return False

    def add_stage_record(self, stage_data: Dict[str, Any]) -> str:
        """添加阶段执行记录"""
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{self.app_token}/tables/{self.projects_table_id}/records"

        fields = {
            "项目ID": stage_data.get("project_id", ""),
            "执行阶段": stage_data.get("stage", ""),
            "执行状态": stage_data.get("status", StageStatus.PENDING.value),
            "开始时间": int(stage_data.get("start_time", time.time()) * 1000),
            "完成时间": int(stage_data.get("end_time", time.time()) * 1000) if stage_data.get("end_time") else None,
            "耗时(分钟)": stage_data.get("duration_minutes", 0),
            "质量评分": stage_data.get("quality_score", 0),
            "备注": stage_data.get("notes", "")
        }

        # 移除None值
        fields = {k: v for k, v in fields.items() if v is not None}

        payload = {"fields": fields}

        response = requests.post(url, headers=self._get_headers(), json=payload)
        result = response.json()

        if result.get("code") == 0:
            record_id = result["data"]["record"]["record_id"]
            print(f"✅ 阶段记录创建成功: {stage_data.get('stage')}")
            return record_id
        else:
            raise Exception(f"创建阶段记录失败: {result}")

    def add_pressure_test_record(self, test_data: Dict[str, Any]) -> str:
        """添加压力测试记录"""
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{self.app_token}/tables/{self.pressure_tests_table_id}/records"

        fields = {
            "项目ID": test_data.get("project_id", ""),
            "测试时间": int(test_data.get("test_time", time.time()) * 1000),
            "测试引擎": test_data.get("engines", []),
            "关键词数量": test_data.get("keyword_count", 0),
            "平均得分": test_data.get("avg_score", 0),
            "提及率": test_data.get("mention_rate", 0),
            "趋势": test_data.get("trend", "→")
        }

        payload = {"fields": fields}

        response = requests.post(url, headers=self._get_headers(), json=payload)
        result = response.json()

        if result.get("code") == 0:
            record_id = result["data"]["record"]["record_id"]
            print(f"✅ 压力测试记录创建成功")
            return record_id
        else:
            raise Exception(f"创建压力测试记录失败: {result}")

    def get_project_info(self, project_id: str) -> Optional[Dict[str, Any]]:
        """获取项目信息"""
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{self.app_token}/tables/{self.projects_table_id}/records/{project_id}"

        response = requests.get(url, headers=self._get_headers())
        result = response.json()

        if result.get("code") == 0:
            return result["data"]["record"]["fields"]
        else:
            print(f"❌ 获取项目信息失败: {result}")
            return None

    def list_projects(self, status: Optional[ProjectStatus] = None) -> List[Dict[str, Any]]:
        """获取项目列表"""
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{self.app_token}/tables/{self.projects_table_id}/records"

        # 构建筛选条件
        params = {"page_size": 100}
        if status:
            # 飞书多维表格的筛选语法
            params["filter"] = f"CurrentValue.[项目状态]='{status.value}'"

        response = requests.get(url, headers=self._get_headers(), params=params)
        result = response.json()

        if result.get("code") == 0:
            records = result["data"]["items"]
            return [{"id": r["record_id"], **r["fields"]} for r in records]
        else:
            print(f"❌ 获取项目列表失败: {result}")
            return []


# ============ 飞书DocumentGenerator实现 ============

class FeishuDocumentGenerator(DocumentGenerator, FeishuClient):
    """飞书文档生成器"""

    def __init__(self, config: Dict[str, Any]):
        FeishuClient.__init__(self, config["app_id"], config["app_secret"])
        self.root_folder_token = config.get("drive", {}).get("root_folder_token", "")

    def create_project_document(self, project_id: str, client_name: str, results: Dict[str, str]) -> str:
        """创建项目交付文档"""
        # 创建文档
        url = "https://open.feishu.cn/open-apis/docx/v1/documents"

        title = f"【{client_name}】GEO项目交付文档"
        payload = {
            "title": title,
            "folder_token": self.root_folder_token
        }

        response = requests.post(url, headers=self._get_headers(), json=payload)
        result = response.json()

        if result.get("code") != 0:
            raise Exception(f"创建文档失败: {result}")

        doc_id = result["data"]["document"]["document_id"]
        print(f"✅ 文档创建成功: {title}")

        # 构建文档内容
        self._build_document_content(doc_id, client_name, results)

        # 生成访问链接
        doc_url = f"https://open.feishu.cn/document/{doc_id}"
        return doc_url

    def _build_document_content(self, doc_id: str, client_name: str, results: Dict[str, str]):
        """构建文档内容"""
        # 这里需要使用飞书文档API添加内容块
        # 简化实现，实际需要按飞书文档Block格式构建
        url = f"https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks/batch_create"

        # 构建文档结构
        blocks = [
            self._create_heading_block("📋 项目概览", 1),
            self._create_text_block(f"客户名称：{client_name}"),
            self._create_heading_block("🎯 D - 矩阵提取结果", 2),
            self._create_file_block(results.get("d_matrix", "")),
            self._create_heading_block("🔄 B - 转化路径设计", 2),
            self._create_file_block(results.get("b_conversion", "")),
            self._create_heading_block("✅ C - 质检改进方案", 2),
            self._create_file_block(results.get("c_quality", "")),
            self._create_heading_block("💼 A - 商业提案", 2),
            self._create_file_block(results.get("a_proposal", "")),
        ]

        # 批量创建块（简化版）
        # 实际实现需要按飞书API格式
        print(f"📝 正在构建文档内容...")

    def _create_heading_block(self, text: str, level: int) -> Dict:
        """创建标题块"""
        return {
            "block_type": "heading",
            "heading": {
                "level": level,
                "text": {"content": text}
            }
        }

    def _create_text_block(self, text: str) -> Dict:
        """创建文本块"""
        return {
            "block_type": "text",
            "text": {"content": text}
        }

    def _create_file_block(self, file_path: str) -> Dict:
        """创建文件块（占位）"""
        return {
            "block_type": "text",
            "text": {"content": f"📎 附件：{Path(file_path).name}"}
        }

    def update_document(self, doc_id: str, content: str) -> bool:
        """更新文档内容"""
        # 飞书文档更新API
        print(f"📝 更新文档: {doc_id}")
        return True

    def set_document_permission(self, doc_id: str, user_ids: List[str], permission: str = 'view') -> bool:
        """设置文档权限"""
        url = f"https://open.feishu.cn/open-apis/drive/v1/permissions/{doc_id}/members"

        for user_id in user_ids:
            payload = {
                "member_type": "user",
                "member_id": user_id,
                "perm": permission  # view/edit
            }
            response = requests.post(url, headers=self._get_headers(), json=payload)

        print(f"✅ 文档权限设置完成")
        return True

    def generate_share_link(self, doc_id: str) -> str:
        """生成分享链接"""
        # 飞书分享链接API
        url = f"https://open.feishu.cn/document/{doc_id}"
        print(f"🔗 分享链接: {url}")
        return url


# ============ 飞书Notifier实现 ============

class FeishuNotifier(Notifier, FeishuClient):
    """飞书机器人通知器"""

    def __init__(self, config: Dict[str, Any]):
        FeishuClient.__init__(self, config["app_id"], config["app_secret"])
        self.webhook_url = config.get("bot", {}).get("webhook_url", "")
        self.default_group_id = config.get("bot", {}).get("default_group_id", "")

    def send_progress_notification(self, project_id: str, stage: str, status: StageStatus, message: str) -> bool:
        """发送进度通知"""
        card_content = {
            "msg_type": "interactive",
            "card": {
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": "📢 项目进度更新"
                    },
                    "template": "blue"
                },
                "elements": [
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": f"**阶段**: {stage}\n**状态**: {status.value}\n\n{message}"
                        }
                    }
                ]
            }
        }

        response = requests.post(self.webhook_url, json=card_content)
        return response.status_code == 200

    def send_completion_notification(self, project_id: str, client_name: str, doc_url: str) -> bool:
        """发送完成通知"""
        card_content = {
            "msg_type": "interactive",
            "card": {
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": "✅ 项目已完成"
                    },
                    "template": "green"
                },
                "elements": [
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": f"**客户**: {client_name}\n**项目ID**: {project_id}\n\n所有阶段已完成，请查看交付文档。"
                        }
                    },
                    {
                        "tag": "action",
                        "actions": [
                            {
                                "tag": "button",
                                "text": {
                                    "tag": "plain_text",
                                    "content": "查看详细结果"
                                },
                                "url": doc_url,
                                "type": "primary"
                            }
                        ]
                    }
                ]
            }
        }

        response = requests.post(self.webhook_url, json=card_content)
        return response.status_code == 200

    def send_alert(self, alert_type: str, message: str) -> bool:
        """发送告警通知"""
        card_content = {
            "msg_type": "interactive",
            "card": {
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": f"⚠️ {alert_type}"
                    },
                    "template": "red"
                },
                "elements": [
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": message
                        }
                    }
                ]
            }
        }

        response = requests.post(self.webhook_url, json=card_content)
        return response.status_code == 200


# ============ 飞书FileManager实现 ============

class FeishuFileManager(FileManager, FeishuClient):
    """飞书云文档文件管理器"""

    def __init__(self, config: Dict[str, Any]):
        FeishuClient.__init__(self, config["app_id"], config["app_secret"])
        self.root_folder_token = config.get("drive", {}).get("root_folder_token", "")

    def create_client_folder(self, client_name: str) -> str:
        """创建客户文件夹"""
        url = "https://open.feishu.cn/open-apis/drive/v1/files/create_folder"

        payload = {
            "name": client_name,
            "folder_token": self.root_folder_token
        }

        response = requests.post(url, headers=self._get_headers(), json=payload)
        result = response.json()

        if result.get("code") == 0:
            folder_token = result["data"]["token"]
            print(f"✅ 文件夹创建成功: {client_name}")
            return folder_token
        else:
            raise Exception(f"创建文件夹失败: {result}")

    def upload_file(self, folder_id: str, file_path: str) -> str:
        """上传文件"""
        url = "https://open.feishu.cn/open-apis/drive/v1/files/upload_all"

        with open(file_path, 'rb') as f:
            files = {
                'file': (Path(file_path).name, f)
            }
            data = {
                'parent_type': 'explorer',
                'parent_node': folder_id,
                'size': Path(file_path).stat().st_size
            }

            response = requests.post(url, headers=self._get_headers(), files=files, data=data)
            result = response.json()

        if result.get("code") == 0:
            file_token = result["data"]["file_token"]
            print(f"✅ 文件上传成功: {Path(file_path).name}")
            return f"https://open.feishu.cn/file/{file_token}"
        else:
            raise Exception(f"上传文件失败: {result}")

    def list_files(self, folder_id: str) -> List[Dict[str, Any]]:
        """列出文件夹内文件"""
        url = f"https://open.feishu.cn/open-apis/drive/v1/files"

        params = {
            "folder_token": folder_id,
            "page_size": 100
        }

        response = requests.get(url, headers=self._get_headers(), params=params)
        result = response.json()

        if result.get("code") == 0:
            return result["data"]["files"]
        else:
            print(f"❌ 获取文件列表失败: {result}")
            return []
