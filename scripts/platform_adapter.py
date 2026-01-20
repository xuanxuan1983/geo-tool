#!/usr/bin/env python3
"""
平台适配器抽象层
支持飞书和Notion的统一接口
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


class Platform(Enum):
    """支持的平台类型"""
    FEISHU = "feishu"
    NOTION = "notion"


class ProjectStatus(Enum):
    """项目状态"""
    PENDING = "待启动"
    IN_PROGRESS = "进行中"
    COMPLETED = "已完成"
    PAUSED = "暂停"


class StageStatus(Enum):
    """阶段执行状态"""
    PENDING = "待执行"
    RUNNING = "执行中"
    COMPLETED = "已完成"
    FAILED = "失败"


# ============ 抽象接口定义 ============

class ProjectManager(ABC):
    """项目管理抽象接口"""

    @abstractmethod
    def create_project(self, project_data: Dict[str, Any]) -> str:
        """
        创建项目记录

        Args:
            project_data: 项目数据
                - client_name: 客户名称
                - industry: 行业类型
                - contact: 联系人
                - start_date: 开始日期
                - team_members: 项目组成员
                - description: 项目描述

        Returns:
            project_id: 项目唯一ID
        """
        pass

    @abstractmethod
    def update_project_status(self, project_id: str, status: ProjectStatus) -> bool:
        """
        更新项目状态

        Args:
            project_id: 项目ID
            status: 新状态

        Returns:
            是否成功
        """
        pass

    @abstractmethod
    def add_stage_record(self, stage_data: Dict[str, Any]) -> str:
        """
        添加阶段执行记录

        Args:
            stage_data: 阶段数据
                - project_id: 关联项目ID
                - stage: 执行阶段 (D/B/C/A)
                - status: 执行状态
                - start_time: 开始时间
                - end_time: 完成时间
                - duration_minutes: 耗时(分钟)
                - result_file: 结果文件路径
                - quality_score: 质量评分

        Returns:
            stage_record_id: 记录ID
        """
        pass

    @abstractmethod
    def add_pressure_test_record(self, test_data: Dict[str, Any]) -> str:
        """
        添加压力测试记录

        Args:
            test_data: 测试数据
                - project_id: 关联项目ID
                - test_time: 测试时间
                - engines: 测试引擎列表
                - keyword_count: 关键词数量
                - avg_score: 平均得分
                - mention_rate: 提及率
                - trend: 趋势
                - report_file: 报告文件路径

        Returns:
            test_record_id: 记录ID
        """
        pass

    @abstractmethod
    def get_project_info(self, project_id: str) -> Optional[Dict[str, Any]]:
        """
        获取项目信息

        Args:
            project_id: 项目ID

        Returns:
            项目信息字典，不存在则返回None
        """
        pass

    @abstractmethod
    def list_projects(self, status: Optional[ProjectStatus] = None) -> List[Dict[str, Any]]:
        """
        获取项目列表

        Args:
            status: 筛选状态（可选）

        Returns:
            项目列表
        """
        pass


class DocumentGenerator(ABC):
    """文档生成抽象接口"""

    @abstractmethod
    def create_project_document(self, project_id: str, client_name: str, results: Dict[str, str]) -> str:
        """
        创建项目交付文档

        Args:
            project_id: 项目ID
            client_name: 客户名称
            results: 结果字典
                - d_matrix: D阶段结果文件路径
                - b_conversion: B阶段结果文件路径
                - c_quality: C阶段结果文件路径
                - a_proposal: A阶段结果文件路径
                - pressure_test: 压力测试报告路径

        Returns:
            document_url: 文档访问链接
        """
        pass

    @abstractmethod
    def update_document(self, doc_id: str, content: str) -> bool:
        """
        更新文档内容

        Args:
            doc_id: 文档ID
            content: 更新内容

        Returns:
            是否成功
        """
        pass

    @abstractmethod
    def set_document_permission(self, doc_id: str, user_ids: List[str], permission: str = 'view') -> bool:
        """
        设置文档权限

        Args:
            doc_id: 文档ID
            user_ids: 用户ID列表
            permission: 权限类型 (view/edit)

        Returns:
            是否成功
        """
        pass

    @abstractmethod
    def generate_share_link(self, doc_id: str) -> str:
        """
        生成分享链接

        Args:
            doc_id: 文档ID

        Returns:
            分享链接URL
        """
        pass


class Notifier(ABC):
    """通知推送抽象接口"""

    @abstractmethod
    def send_progress_notification(self, project_id: str, stage: str, status: StageStatus, message: str) -> bool:
        """
        发送进度通知

        Args:
            project_id: 项目ID
            stage: 当前阶段
            status: 阶段状态
            message: 通知消息

        Returns:
            是否成功
        """
        pass

    @abstractmethod
    def send_completion_notification(self, project_id: str, client_name: str, doc_url: str) -> bool:
        """
        发送完成通知

        Args:
            project_id: 项目ID
            client_name: 客户名称
            doc_url: 文档链接

        Returns:
            是否成功
        """
        pass

    @abstractmethod
    def send_alert(self, alert_type: str, message: str) -> bool:
        """
        发送告警通知

        Args:
            alert_type: 告警类型
            message: 告警消息

        Returns:
            是否成功
        """
        pass


class FileManager(ABC):
    """文件管理抽象接口"""

    @abstractmethod
    def create_client_folder(self, client_name: str) -> str:
        """
        创建客户文件夹

        Args:
            client_name: 客户名称

        Returns:
            folder_id: 文件夹ID
        """
        pass

    @abstractmethod
    def upload_file(self, folder_id: str, file_path: str) -> str:
        """
        上传文件

        Args:
            folder_id: 文件夹ID
            file_path: 本地文件路径

        Returns:
            file_url: 文件访问URL
        """
        pass

    @abstractmethod
    def list_files(self, folder_id: str) -> List[Dict[str, Any]]:
        """
        列出文件夹内文件

        Args:
            folder_id: 文件夹ID

        Returns:
            文件列表
        """
        pass


# ============ 平台适配器工厂 ============

class PlatformAdapterFactory:
    """平台适配器工厂类"""

    @staticmethod
    def create_project_manager(platform: Platform, config: Dict[str, Any]) -> ProjectManager:
        """创建项目管理器"""
        if platform == Platform.FEISHU:
            from feishu_adapter import FeishuProjectManager
            return FeishuProjectManager(config)
        elif platform == Platform.NOTION:
            from notion_adapter import NotionProjectManager
            return NotionProjectManager(config)
        else:
            raise ValueError(f"不支持的平台: {platform}")

    @staticmethod
    def create_document_generator(platform: Platform, config: Dict[str, Any]) -> DocumentGenerator:
        """创建文档生成器"""
        if platform == Platform.FEISHU:
            from feishu_adapter import FeishuDocumentGenerator
            return FeishuDocumentGenerator(config)
        elif platform == Platform.NOTION:
            from notion_adapter import NotionDocumentGenerator
            return NotionDocumentGenerator(config)
        else:
            raise ValueError(f"不支持的平台: {platform}")

    @staticmethod
    def create_notifier(platform: Platform, config: Dict[str, Any]) -> Notifier:
        """创建通知器"""
        if platform == Platform.FEISHU:
            from feishu_adapter import FeishuNotifier
            return FeishuNotifier(config)
        elif platform == Platform.NOTION:
            from notion_adapter import NotionNotifier
            return NotionNotifier(config)
        else:
            raise ValueError(f"不支持的平台: {platform}")

    @staticmethod
    def create_file_manager(platform: Platform, config: Dict[str, Any]) -> FileManager:
        """创建文件管理器"""
        if platform == Platform.FEISHU:
            from feishu_adapter import FeishuFileManager
            return FeishuFileManager(config)
        elif platform == Platform.NOTION:
            from notion_adapter import NotionFileManager
            return NotionFileManager(config)
        else:
            raise ValueError(f"不支持的平台: {platform}")
