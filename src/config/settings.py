"""
配置管理系统

支持YAML配置文件 + 环境变量 + pydantic-settings
"""

import os
import yaml
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
from pathlib import Path
from pydantic import BaseModel, Field


class LLMConfig(BaseModel):
    """LLM配置"""
    provider: str = "openai"  # openai / azure / local
    api_key: str = ""
    model: str = "gpt-4o"
    base_url: str = "https://api.openai.com/v1"
    temperature: float = 0.7
    max_tokens: int = 4000
    timeout: int = 60


class ProjectPaths(BaseModel):
    """项目路径配置"""
    root: str = "./workspace"
    knowledge_base: str = "./knowledge"
    experts_prompts: str = "./knowledge/experts"
    checkpoints: str = "./workspace/checkpoints"
    outputs: str = "./workspace/outputs"


class APIConfig(BaseModel):
    """API服务器配置"""
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    cors_origins: List[str] = Field(default_factory=lambda: ["*"])
    log_level: str = "INFO"


class WorkflowConfig(BaseModel):
    """工作流配置"""
    expert_sequence: List[str] = Field(
        default_factory=lambda: ["§0", "§2", "§8", "§1", "§4", "§3", "§13"]
    )
    enable_checkpoint: bool = True
    checkpoint_interval: int = 1  # 每N步保存一次断点
    stop_on_validation_error: bool = False
    max_retries: int = 3


class Settings(BaseModel):
    """全局配置"""
    app_name: str = "Drama Engine"
    version: str = "1.0.0"
    llm: LLMConfig = Field(default_factory=LLMConfig)
    paths: ProjectPaths = Field(default_factory=ProjectPaths)
    api: APIConfig = Field(default_factory=APIConfig)
    workflow: WorkflowConfig = Field(default_factory=WorkflowConfig)
    default_drama_type: str = "现实主义"
    default_total_episodes: int = 30

    class Config:
        env_prefix = "DRAMA_"


class ConfigManager:
    """
    配置管理器

    支持加载顺序：
    1. 默认配置（代码中的默认值）
    2. YAML配置文件
    3. 环境变量（优先级最高）
    """

    _instance: Optional["ConfigManager"] = None
    _settings: Optional[Settings] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def load(
        cls,
        config_file: Optional[str] = None,
        env_prefix: str = "DRAMA_",
        **overrides,
    ) -> Settings:
        """加载配置"""
        settings_dict: Dict[str, Any] = {}

        # 1. 从YAML加载
        if config_file and os.path.exists(config_file):
            with open(config_file, "r", encoding="utf-8") as f:
                yaml_config = yaml.safe_load(f)
                if yaml_config:
                    settings_dict.update(yaml_config)

        # 2. 从环境变量加载
        for key, value in os.environ.items():
            if key.startswith(env_prefix):
                config_key = key[len(env_prefix):].lower()
                # 支持嵌套：DRAMA_LLM_API_KEY -> llm.api_key
                if "_" in config_key:
                    parts = config_key.split("_", 1)
                    settings_dict.setdefault(parts[0], {})
                    settings_dict[parts[0]][parts[1]] = value
                else:
                    settings_dict[config_key] = value

        # 3. 应用覆盖参数
        settings_dict.update(overrides)

        # 4. 构建Settings
        cls._settings = Settings(**settings_dict)
        return cls._settings

    @classmethod
    def get(cls) -> Settings:
        """获取当前配置（懒加载默认配置）"""
        if cls._settings is None:
            cls._settings = cls.load()
        return cls._settings

    @classmethod
    def reload(cls, config_file: Optional[str] = None) -> Settings:
        """重新加载配置"""
        cls._settings = None
        return cls.load(config_file=config_file)

    @classmethod
    def save_to_yaml(cls, file_path: str):
        """将当前配置保存为YAML"""
        settings = cls.get()
        settings_dict = settings.model_dump()

        # 移除空字符串（不保存未设置的字段）
        def clean_dict(d):
            if isinstance(d, dict):
                return {k: clean_dict(v) for k, v in d.items() if v != "" and v is not None}
            return d

        with open(file_path, "w", encoding="utf-8") as f:
            yaml.dump(clean_dict(settings_dict), f, allow_unicode=True, default_flow_style=False)

    @classmethod
    def get_llm_config(cls) -> LLMConfig:
        return cls.get().llm

    @classmethod
    def get_paths(cls) -> ProjectPaths:
        return cls.get().paths

    @classmethod
    def get_api_config(cls) -> APIConfig:
        return cls.get().api

    @classmethod
    def get_workflow_config(cls) -> WorkflowConfig:
        return cls.get().workflow


def load_config(config_file: Optional[str] = None) -> Settings:
    """快捷函数：加载配置"""
    return ConfigManager.load(config_file)


def get_config() -> Settings:
    """快捷函数：获取当前配置"""
    return ConfigManager.get()


# 示例YAML配置模板
EXAMPLE_CONFIG_YAML = """
app_name: "Drama Engine"
version: "1.0.0"

llm:
  provider: "openai"
  api_key: ""  # 请在此填入你的API Key
  model: "gpt-4o"
  base_url: "https://api.openai.com/v1"
  temperature: 0.7
  max_tokens: 4000

paths:
  root: "./workspace"
  knowledge_base: "./knowledge"
  experts_prompts: "./knowledge/experts"
  checkpoints: "./workspace/checkpoints"
  outputs: "./workspace/outputs"

api:
  host: "0.0.0.0"
  port: 8000
  debug: false
  cors_origins:
    - "*"
  log_level: "INFO"

workflow:
  expert_sequence:
    - "§0"
    - "§2"
    - "§8"
    - "§1"
    - "§4"
    - "§3"
    - "§13"
  enable_checkpoint: true
  checkpoint_interval: 1
  stop_on_validation_error: false
  max_retries: 3

default_drama_type: "现实主义"
default_total_episodes: 30
"""


__all__ = [
    "Settings",
    "LLMConfig",
    "ProjectPaths",
    "APIConfig",
    "WorkflowConfig",
    "ConfigManager",
    "load_config",
    "get_config",
    "EXAMPLE_CONFIG_YAML",
]