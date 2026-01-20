#!/usr/bin/env python3
"""
Notion平台适配器实现
实现ProjectManager、DocumentGenerator、Notifier、FileManager接口
"""
from notion_client import Client
from typing import Dict, List, Optional, Any
from datetime import datetime
import time
from pathlib import Path

from platform_adapter import (
    ProjectManager, DocumentGenerator, Notifier, FileManager,
    ProjectStatus, StageStatus
)


# ============ Notion ProjectManager实现 ============

class NotionProjectManager(ProjectManager):
    """Notion数据库项目管理器"""

    def __init__(self, config: Dict[str, Any]):
        self.client = Client(auth=config["api_key"])
        self.clients_db_id = config["databases"]["clients"]
        self.projects_db_id = config["databases"]["projects"]
        self.pressure_tests_db_id = config["databases"]["pressure_tests"]
        self.feedback_db_id = config["databases"]["feedback"]

    def create_project(self, project_data: Dict[str, Any]) -> str:
        """创建项目记录"""
        properties = {
            "客户名称": {
                "title": [{"text": {"content": project_data.get("client_name", "")}}]
            }
        }

        # 可选字段 - 如果字段不存在就跳过
        if project_data.get("industry"):
            properties["行业类型"] = {"select": {"name": project_data.get("industry", "其他")}}

        if project_data.get("status"):
            properties["项目状态"] = {"select": {"name": project_data.get("status", ProjectStatus.PENDING.value)}}
        else:
            properties["项目状态"] = {"select": {"name": ProjectStatus.PENDING.value}}

        if project_data.get("start_date"):
            properties["开始日期"] = {"date": {"start": project_data.get("start_date", datetime.now().isoformat())}}

        if project_data.get("description"):
            properties["描述"] = {"rich_text": [{"text": {"content": project_data.get("description", "")}}]}

        response = self.client.pages.create(
            parent={"database_id": self.clients_db_id},
            properties=properties
        )

        page_id = response["id"]
        print(f"✅ Notion项目记录创建成功: {page_id}")
        return page_id

    def update_project_status(self, project_id: str, status: ProjectStatus) -> bool:
        """更新项目状态"""
        try:
            self.client.pages.update(
                page_id=project_id,
                properties={
                    "项目状态": {
                        "select": {"name": status.value}
                    }
                }
            )
            print(f"✅ 项目状态更新为: {status.value}")
            return True
        except Exception as e:
            print(f"❌ 更新项目状态失败: {e}")
            return False

    def add_stage_record(self, stage_data: Dict[str, Any]) -> str:
        """添加阶段执行记录"""
        properties = {
            "任务名称": {
                "title": [{"text": {"content": f"{stage_data.get('stage', '')}阶段"}}]
            }
        }

        # 可选字段
        if stage_data.get("project_id"):
            properties["项目ID"] = {"rich_text": [{"text": {"content": stage_data.get("project_id", "")}}]}

        if stage_data.get("stage"):
            properties["执行阶段"] = {"select": {"name": stage_data.get("stage", "")}}

        if stage_data.get("status"):
            properties["状态"] = {"select": {"name": stage_data.get("status", StageStatus.PENDING.value)}}

        if stage_data.get("end_time"):
            properties["完成时间"] = {
                "date": {
                    "start": datetime.fromtimestamp(stage_data["end_time"]).isoformat()
                }
            }

        response = self.client.pages.create(
            parent={"database_id": self.projects_db_id},
            properties=properties
        )

        page_id = response["id"]
        print(f"✅ 阶段记录创建成功: {stage_data.get('stage')}")
        return page_id

    def add_pressure_test_record(self, test_data: Dict[str, Any]) -> str:
        """添加压力测试记录"""
        properties = {
            "项目ID": {
                "relation": [{"id": test_data.get("project_id", "")}]
            },
            "测试时间": {
                "date": {
                    "start": datetime.fromtimestamp(test_data.get("test_time", time.time())).isoformat()
                }
            },
            "关键词数量": {
                "number": test_data.get("keyword_count", 0)
            },
            "平均得分": {
                "number": test_data.get("avg_score", 0)
            },
            "提及率": {
                "number": test_data.get("mention_rate", 0)
            },
            "趋势": {
                "select": {"name": test_data.get("trend", "→")}
            }
        }

        response = self.client.pages.create(
            parent={"database_id": self.pressure_tests_db_id},
            properties=properties
        )

        page_id = response["id"]
        print(f"✅ 压力测试记录创建成功")
        return page_id

    def get_project_info(self, project_id: str) -> Optional[Dict[str, Any]]:
        """获取项目信息"""
        try:
            response = self.client.pages.retrieve(page_id=project_id)
            return self._parse_properties(response["properties"])
        except Exception as e:
            print(f"❌ 获取项目信息失败: {e}")
            return None

    def list_projects(self, status: Optional[ProjectStatus] = None) -> List[Dict[str, Any]]:
        """获取项目列表"""
        filter_params = {}
        if status:
            filter_params = {
                "property": "项目状态",
                "select": {
                    "equals": status.value
                }
            }

        try:
            response = self.client.databases.query(
                database_id=self.projects_db_id,
                filter=filter_params if status else None
            )

            projects = []
            for page in response["results"]:
                project = {
                    "id": page["id"],
                    **self._parse_properties(page["properties"])
                }
                projects.append(project)

            return projects
        except Exception as e:
            print(f"❌ 获取项目列表失败: {e}")
            return []

    def _parse_properties(self, properties: Dict) -> Dict[str, Any]:
        """解析Notion属性为简单字典"""
        parsed = {}
        for key, value in properties.items():
            prop_type = value["type"]

            if prop_type == "title":
                parsed[key] = value["title"][0]["text"]["content"] if value["title"] else ""
            elif prop_type == "rich_text":
                parsed[key] = value["rich_text"][0]["text"]["content"] if value["rich_text"] else ""
            elif prop_type == "select":
                parsed[key] = value["select"]["name"] if value["select"] else ""
            elif prop_type == "number":
                parsed[key] = value["number"]
            elif prop_type == "date":
                parsed[key] = value["date"]["start"] if value["date"] else None

        return parsed


# ============ Notion DocumentGenerator实现 ============

class NotionDocumentGenerator(DocumentGenerator):
    """Notion页面生成器"""

    def __init__(self, config: Dict[str, Any]):
        self.client = Client(auth=config["api_key"])
        self.workspace_id = config["pages"].get("workspace_id", "")
        self.template_page_id = config["pages"].get("template_page_id", "")

    def create_project_document(self, project_id: str, client_name: str, results: Dict[str, str]) -> str:
        """创建项目交付文档"""
        # 创建页面
        title = f"【{client_name}】GEO项目交付文档"

        # 构建页面内容块
        children = [
            self._create_heading_block("📋 项目概览", 1),
            self._create_paragraph_block(f"客户名称：{client_name}"),
            self._create_heading_block("🎯 D - 矩阵提取结果", 2),
            self._create_file_block(results.get("d_matrix", "")),
            self._create_heading_block("🔄 B - 转化路径设计", 2),
            self._create_file_block(results.get("b_conversion", "")),
            self._create_heading_block("✅ C - 质检改进方案", 2),
            self._create_file_block(results.get("c_quality", "")),
            self._create_heading_block("💼 A - 商业提案", 2),
            self._create_file_block(results.get("a_proposal", "")),
            self._create_heading_block("📈 压力测试报告", 2),
            self._create_file_block(results.get("pressure_test", "")),
        ]

        response = self.client.pages.create(
            parent={"page_id": self.workspace_id} if self.workspace_id else {"workspace": True},
            properties={
                "title": [{"text": {"content": title}}]
            },
            children=children
        )

        page_id = response["id"]
        page_url = response["url"]
        print(f"✅ Notion文档创建成功: {title}")
        return page_url

    def _create_heading_block(self, text: str, level: int) -> Dict:
        """创建标题块"""
        heading_type = f"heading_{level}"
        return {
            "object": "block",
            "type": heading_type,
            heading_type: {
                "rich_text": [{"text": {"content": text}}]
            }
        }

    def _create_paragraph_block(self, text: str) -> Dict:
        """创建段落块"""
        return {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"text": {"content": text}}]
            }
        }

    def _create_file_block(self, file_path: str) -> Dict:
        """创建文件块（显示文件名）"""
        return {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"text": {"content": f"📎 附件：{Path(file_path).name if file_path else '无'}"}}]
            }
        }

    def update_document(self, doc_id: str, content: str) -> bool:
        """更新文档内容"""
        try:
            # Notion更新需要添加新块
            print(f"📝 更新Notion文档: {doc_id}")
            return True
        except Exception as e:
            print(f"❌ 更新文档失败: {e}")
            return False

    def set_document_permission(self, doc_id: str, user_ids: List[str], permission: str = 'view') -> bool:
        """设置文档权限"""
        # Notion权限管理
        print(f"✅ Notion文档权限设置（占位实现）")
        return True

    def generate_share_link(self, doc_id: str) -> str:
        """生成分享链接"""
        try:
            page = self.client.pages.retrieve(page_id=doc_id)
            return page["url"]
        except Exception as e:
            print(f"❌ 获取分享链接失败: {e}")
            return ""


# ============ Notion Notifier实现 ============

class NotionNotifier(Notifier):
    """Notion通知器（通过邮件或其他方式）"""

    def __init__(self, config: Dict[str, Any]):
        # Notion本身没有通知功能，需要集成第三方服务
        self.email_config = config.get("email", {})

    def send_progress_notification(self, project_id: str, stage: str, status: StageStatus, message: str) -> bool:
        """发送进度通知"""
        # 这里可以集成邮件或Slack等
        print(f"📧 [Notion通知] 项目 {project_id} - {stage} - {status.value}")
        print(f"   {message}")
        return True

    def send_completion_notification(self, project_id: str, client_name: str, doc_url: str) -> bool:
        """发送完成通知"""
        print(f"📧 [Notion通知] 项目完成: {client_name}")
        print(f"   查看文档: {doc_url}")
        return True

    def send_alert(self, alert_type: str, message: str) -> bool:
        """发送告警通知"""
        print(f"⚠️  [Notion告警] {alert_type}: {message}")
        return True


# ============ Notion FileManager实现 ============

class NotionFileManager(FileManager):
    """Notion文件管理器"""

    def __init__(self, config: Dict[str, Any]):
        self.client = Client(auth=config["api_key"])
        # Notion不直接管理文件，文件通常上传到外部存储
        print("⚠️  Notion不支持文件存储，建议使用云存储服务")

    def create_client_folder(self, client_name: str) -> str:
        """创建客户文件夹（Notion中创建页面）"""
        response = self.client.pages.create(
            parent={"workspace": True},
            properties={
                "title": [{"text": {"content": client_name}}]
            }
        )
        return response["id"]

    def upload_file(self, folder_id: str, file_path: str) -> str:
        """上传文件（Notion需要外部存储）"""
        # Notion不支持直接文件上传，返回本地路径
        print(f"⚠️  Notion不支持文件上传，文件位于: {file_path}")
        return file_path

    def list_files(self, folder_id: str) -> List[Dict[str, Any]]:
        """列出文件（占位实现）"""
        return []
