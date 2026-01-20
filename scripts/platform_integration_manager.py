#!/usr/bin/env python3
"""
平台集成管理器
统一管理飞书和Notion平台的集成
"""
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from platform_adapter import (
    Platform, PlatformAdapterFactory,
    ProjectManager, DocumentGenerator, Notifier, FileManager,
    ProjectStatus, StageStatus
)


class PlatformIntegrationManager:
    """平台集成管理器 - 简化平台操作"""

    def __init__(self, config_path: str = None):
        """
        初始化平台集成管理器

        Args:
            config_path: 配置文件路径，默认为 config/platform_config.yaml
        """
        # 优先从 Streamlit Secrets 读取配置
        try:
            import streamlit as st
            if hasattr(st, 'secrets') and 'platform_config' in st.secrets:
                print("📦 从 Streamlit Secrets 加载配置")
                self.config = dict(st.secrets['platform_config'])
            else:
                raise KeyError("No secrets found")
        except (ImportError, KeyError):
            # 从文件读取配置
            if config_path is None:
                config_path = Path(__file__).parent.parent / "config" / "platform_config.yaml"

            print(f"📦 从文件加载配置: {config_path}")
            with open(config_path) as f:
                self.config = yaml.safe_load(f)

        # 获取默认平台
        platform_name = self.config.get("default_platform", "feishu")
        self.platform = Platform.FEISHU if platform_name == "feishu" else Platform.NOTION

        # 初始化适配器
        platform_config = self.config.get(platform_name, {})
        self.project_manager: ProjectManager = PlatformAdapterFactory.create_project_manager(
            self.platform, platform_config
        )
        self.document_generator: DocumentGenerator = PlatformAdapterFactory.create_document_generator(
            self.platform, platform_config
        )
        self.notifier: Notifier = PlatformAdapterFactory.create_notifier(
            self.platform, platform_config
        )
        self.file_manager: FileManager = PlatformAdapterFactory.create_file_manager(
            self.platform, platform_config
        )

        print(f"✅ 平台集成管理器已初始化 - 使用平台: {platform_name.upper()}")

    def switch_platform(self, platform_name: str):
        """
        切换平台

        Args:
            platform_name: 平台名称 (feishu/notion)
        """
        self.platform = Platform.FEISHU if platform_name == "feishu" else Platform.NOTION
        platform_config = self.config.get(platform_name, {})

        self.project_manager = PlatformAdapterFactory.create_project_manager(
            self.platform, platform_config
        )
        self.document_generator = PlatformAdapterFactory.create_document_generator(
            self.platform, platform_config
        )
        self.notifier = PlatformAdapterFactory.create_notifier(
            self.platform, platform_config
        )
        self.file_manager = PlatformAdapterFactory.create_file_manager(
            self.platform, platform_config
        )

        print(f"✅ 已切换到平台: {platform_name.upper()}")

    # ============ 高级封装方法 ============

    def create_new_project(self, client_data: Dict[str, Any]) -> str:
        """
        创建新项目并自动同步到平台

        Args:
            client_data: 客户数据字典

        Returns:
            project_id: 项目ID
        """
        print(f"\n🚀 开始创建项目: {client_data.get('client_name')}")

        # 1. 创建项目记录
        project_id = self.project_manager.create_project(client_data)

        # 2. 创建文件夹（如果支持）
        try:
            folder_id = self.file_manager.create_client_folder(client_data["client_name"])
            print(f"📁 客户文件夹已创建: {folder_id}")
        except Exception as e:
            print(f"⚠️  创建文件夹失败: {e}")

        # 3. 发送通知
        self.notifier.send_progress_notification(
            project_id=project_id,
            stage="项目创建",
            status=StageStatus.COMPLETED,
            message=f"客户【{client_data.get('client_name')}】的项目已成功创建！"
        )

        return project_id

    def update_stage_progress(
        self,
        project_id: str,
        stage: str,
        status: StageStatus,
        duration_minutes: int = 0,
        result_file: str = None
    ):
        """
        更新阶段进度

        Args:
            project_id: 项目ID
            stage: 阶段 (D/B/C/A)
            status: 阶段状态
            duration_minutes: 耗时（分钟）
            result_file: 结果文件路径
        """
        # 1. 添加阶段记录
        stage_data = {
            "project_id": project_id,
            "stage": stage,
            "status": status.value,
            "start_time": datetime.now().timestamp(),
            "duration_minutes": duration_minutes,
            "notes": f"{stage}阶段执行完成" if status == StageStatus.COMPLETED else f"{stage}阶段执行中"
        }

        if status == StageStatus.COMPLETED:
            stage_data["end_time"] = datetime.now().timestamp()

        self.project_manager.add_stage_record(stage_data)

        # 2. 发送进度通知
        stage_names = {
            "D": "D - 矩阵提取",
            "B": "B - 转化路径设计",
            "C": "C - 质检暴改",
            "A": "A - 商业提案"
        }

        self.notifier.send_progress_notification(
            project_id=project_id,
            stage=stage_names.get(stage, stage),
            status=status,
            message=f"耗时: {duration_minutes}分钟" if duration_minutes else "正在执行中..."
        )

    def complete_project(
        self,
        project_id: str,
        client_name: str,
        results: Dict[str, str]
    ) -> str:
        """
        完成项目并生成交付文档

        Args:
            project_id: 项目ID
            client_name: 客户名称
            results: 结果文件字典
                - d_matrix: D阶段结果文件路径
                - b_conversion: B阶段结果文件路径
                - c_quality: C阶段结果文件路径
                - a_proposal: A阶段结果文件路径
                - pressure_test: 压力测试报告路径

        Returns:
            doc_url: 交付文档链接
        """
        print(f"\n✅ 项目完成: {client_name}")

        # 1. 更新项目状态
        self.project_manager.update_project_status(project_id, ProjectStatus.COMPLETED)

        # 2. 生成交付文档
        doc_url = self.document_generator.create_project_document(
            project_id=project_id,
            client_name=client_name,
            results=results
        )

        # 3. 上传结果文件（如果支持）
        try:
            folder_id = self.file_manager.create_client_folder(client_name)
            for stage, file_path in results.items():
                if file_path and Path(file_path).exists():
                    self.file_manager.upload_file(folder_id, file_path)
                    print(f"📤 已上传: {Path(file_path).name}")
        except Exception as e:
            print(f"⚠️  上传文件失败: {e}")

        # 4. 发送完成通知
        self.notifier.send_completion_notification(
            project_id=project_id,
            client_name=client_name,
            doc_url=doc_url
        )

        return doc_url

    def add_pressure_test_result(
        self,
        project_id: str,
        engines: list,
        keyword_count: int,
        avg_score: float,
        mention_rate: float,
        trend: str = "→"
    ):
        """
        添加压力测试结果

        Args:
            project_id: 项目ID
            engines: 测试引擎列表
            keyword_count: 关键词数量
            avg_score: 平均得分
            mention_rate: 提及率
            trend: 趋势 (↑/→/↓)
        """
        test_data = {
            "project_id": project_id,
            "test_time": datetime.now().timestamp(),
            "engines": engines,
            "keyword_count": keyword_count,
            "avg_score": avg_score,
            "mention_rate": mention_rate,
            "trend": trend
        }

        self.project_manager.add_pressure_test_record(test_data)
        print(f"📊 压力测试结果已记录: 平均分 {avg_score}, 提及率 {mention_rate}%")

    def get_current_platform(self) -> str:
        """获取当前平台名称"""
        return "飞书" if self.platform == Platform.FEISHU else "Notion"

    def get_all_projects(self, status: Optional[ProjectStatus] = None) -> list:
        """获取所有项目列表"""
        return self.project_manager.list_projects(status)


# ============ 便捷函数 ============

def get_platform_manager(config_path: str = None) -> PlatformIntegrationManager:
    """
    获取平台集成管理器实例（单例模式）

    Args:
        config_path: 配置文件路径

    Returns:
        PlatformIntegrationManager实例
    """
    if not hasattr(get_platform_manager, "_instance"):
        get_platform_manager._instance = PlatformIntegrationManager(config_path)
    return get_platform_manager._instance


# ============ 测试代码 ============

if __name__ == "__main__":
    # 测试平台集成
    manager = PlatformIntegrationManager()

    # 测试创建项目
    test_data = {
        "client_name": "测试品牌",
        "industry": "医美",
        "contact": "张三",
        "start_date": datetime.now().isoformat(),
        "description": "这是一个测试项目"
    }

    project_id = manager.create_new_project(test_data)
    print(f"\n项目ID: {project_id}")

    # 测试更新阶段
    manager.update_stage_progress(
        project_id=project_id,
        stage="D",
        status=StageStatus.COMPLETED,
        duration_minutes=5
    )

    # 测试获取项目列表
    projects = manager.get_all_projects()
    print(f"\n当前项目数: {len(projects)}")
