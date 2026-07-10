"""
专家基类

为每个专家模块提供统一接口规范：
- load_prompt(): 加载Prompt模板
- load_knowledge(): 加载知识库
- execute(): 执行专家逻辑
- validate_output(): 验证输出规范
- parse_output(): 将LLM输出解析为结构化数据

基于《架构设计.md》§0-§15专家架构设计
"""

import os
import re
import json
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path


@dataclass
class ExpertContext:
    """专家执行上下文：保存当前项目的所有中间产物"""
    project_name: str = ""
    story_direction: str = ""
    story_premise: str = ""
    project_config: Dict = field(default_factory=dict)
    character_cards: List[Dict] = field(default_factory=list)
    dialogue_corpus: Dict = field(default_factory=dict)
    beat_table: List[Dict] = field(default_factory=list)
    episode_outlines: List[Dict] = field(default_factory=list)
    visual_scheme: Dict = field(default_factory=dict)
    risk_level: str = "green"
    risk_warnings: List[Dict] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "project_name": self.project_name,
            "story_direction": self.story_direction,
            "story_premise": self.story_premise,
            "project_config": self.project_config,
            "character_cards": self.character_cards,
            "dialogue_corpus": self.dialogue_corpus,
            "beat_table": self.beat_table,
            "episode_outlines": self.episode_outlines,
            "visual_scheme": self.visual_scheme,
            "risk_level": self.risk_level,
            "risk_warnings": self.risk_warnings,
            "metadata": self.metadata,
        }

    def update(self, **kwargs):
        for key, val in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, val)


@dataclass
class ExpertOutput:
    """专家输出标准格式"""
    expert_name: str
    content: str = ""
    structured_data: Dict = field(default_factory=dict)
    validation_passed: bool = False
    validation_errors: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "expert_name": self.expert_name,
            "content": self.content,
            "structured_data": self.structured_data,
            "validation_passed": self.validation_passed,
            "validation_errors": self.validation_errors,
            "suggestions": self.suggestions,
        }


class PromptTemplate:
    """Prompt模板管理器"""
    def __init__(self, template_path: str):
        self.template_path = template_path
        self._raw_template: Optional[str] = None

    def load(self) -> str:
        """加载Prompt模板内容"""
        if self._raw_template is None:
            path = Path(self.template_path)
            if path.exists():
                self._raw_template = path.read_text(encoding="utf-8")
            else:
                self._raw_template = ""
        return self._raw_template

    def render(self, context: ExpertContext, **kwargs) -> str:
        """渲染Prompt模板，替换占位符"""
        template = self.load()
        variables = context.to_dict()
        variables.update(kwargs)
        for key, val in variables.items():
            placeholder = f"{{{key}}}"
            if placeholder in template:
                template = template.replace(placeholder, str(val) if val else "")
        return template

    def get_placeholders(self) -> List[str]:
        """提取模板中所有占位符"""
        template = self.load()
        return re.findall(r"\{(\w+)\}", template)


class LLMClient(ABC):
    """LLM调用封装（抽象基类）"""
    @abstractmethod
    def complete(self, prompt: str, **kwargs) -> str:
        pass

    @abstractmethod
    def complete_json(self, prompt: str, **kwargs) -> Dict:
        pass


class OpenAIClient(LLMClient):
    """OpenAI API兼容的LLM客户端"""
    def __init__(self, api_key: str = "", model: str = "gpt-4o", base_url: str = "https://api.openai.com/v1", temperature: float = 0.7, max_tokens: int = 8000):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                import openai
                self._client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url)
            except ImportError:
                self._client = None
        return self._client

    def complete(self, prompt: str, **kwargs) -> str:
        """调用LLM生成内容，失败自动重试最多3次"""
        client = self._get_client()
        if client is None:
            return self._mock_complete(prompt)

        max_retries = 3
        last_error = None

        for attempt in range(max_retries):
            try:
                response = client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=kwargs.get("temperature", self.temperature),
                    max_tokens=kwargs.get("max_tokens", self.max_tokens),
                )
                return response.choices[0].message.content
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    wait_time = 5 * (attempt + 1)
                    print(f"  ⚠ API调用失败({e})，{wait_time}秒后重试 ({attempt+1}/{max_retries})...")
                    time.sleep(wait_time)

        return f"[LLM调用失败: {last_error}] 请检查API配置"

    def complete_json(self, prompt: str, **kwargs) -> Dict:
        """调用LLM生成结构化JSON"""
        text = self.complete(prompt, **kwargs)
        try:
            json_match = re.search(r"\{[\s\S]*\}", text)
            if json_match:
                return json.loads(json_match.group())
            return json.loads(text)
        except json.JSONDecodeError:
            return {"error": "JSON解析失败", "raw_text": text}

    def _mock_complete(self, prompt: str) -> str:
        """Mock模式"""
        return f"[Mock LLM响应] 已收到Prompt，长度={len(prompt)}字符。请配置有效的API Key以获取真实LLM响应。"


class ExpertBase(ABC):
    """专家模块基类"""
    expert_id: str = ""
    expert_name: str = ""
    knowledge_dir: str = "knowledge/experts"
    prompt_file: str = ""

    def __init__(self, llm_client: Optional[LLMClient] = None, knowledge_base_path: Optional[str] = None, culture_kb=None):
        self.llm_client = llm_client or OpenAIClient()
        self.knowledge_base_path = knowledge_base_path
        self.culture_kb = culture_kb
        self._prompt_template: Optional[PromptTemplate] = None

    def get_prompt_template(self) -> PromptTemplate:
        if self._prompt_template is None:
            if self.knowledge_base_path:
                template_path = os.path.join(self.knowledge_base_path, self.prompt_file)
            else:
                template_path = os.path.join(self.knowledge_dir, self.prompt_file)
            self._prompt_template = PromptTemplate(template_path)
        return self._prompt_template

    @abstractmethod
    def get_system_prompt(self) -> str:
        pass

    @abstractmethod
    def get_user_prompt(self, context: ExpertContext, **kwargs) -> str:
        pass

    @abstractmethod
    def validate_output(self, output: str) -> tuple[bool, List[str]]:
        pass

    def parse_output(self, content: str) -> Dict:
        return {}

    def load_knowledge(self) -> str:
        if self.knowledge_base_path:
            kb_path = os.path.join(self.knowledge_base_path, self.expert_name + ".md")
        else:
            kb_path = os.path.join(self.knowledge_dir, self.expert_name, "资料汇编.md")
        if os.path.exists(kb_path):
            return Path(kb_path).read_text(encoding="utf-8")
        return ""

    def execute(self, context: ExpertContext, **kwargs) -> ExpertOutput:
        """执行专家逻辑：生成Prompt → 调用LLM → 验证输出 → 解析结构化数据"""
        output = ExpertOutput(expert_name=self.expert_name)

        user_prompt = self.get_user_prompt(context, **kwargs)

        system_prompt = self.get_system_prompt()
        knowledge = self.load_knowledge()
        if knowledge:
            system_prompt = f"{system_prompt}\n\n=== 专家知识库 ===\n{knowledge}"

        if self.culture_kb:
            culture_summary = self.culture_kb.get_summary()
            system_prompt = f"{system_prompt}\n\n=== 中华优秀传统文化知识库（第5.5层） ===\n{culture_summary}\n\n调用方式：根据当前故事类型和主题，从文化知识库中提取相关元素融入创作。文化不是展示是叙事动力——仪式的荒诞推动觉醒，节令的更替推动转折，禁忌的存在推动冲突。"

        full_prompt = f"{system_prompt}\n\n=== 用户输入 ===\n{user_prompt}"

        # 调用LLM（支持max_tokens从kwargs传入）
        llm_kwargs = {}
        if "max_tokens" in kwargs:
            llm_kwargs["max_tokens"] = kwargs["max_tokens"]
        output.content = self.llm_client.complete(full_prompt, **llm_kwargs)

        passed, errors = self.validate_output(output.content)
        output.validation_passed = passed
        output.validation_errors = errors

        parsed = self.parse_output(output.content)
        if parsed:
            output.structured_data = parsed

        return output

    def format_output(self, content: str) -> str:
        return content


class ExpertRegistry:
    """专家注册表"""
    _experts: Dict[str, type] = {}

    @classmethod
    def register(cls, expert_id: str, expert_class: type):
        cls._experts[expert_id] = expert_class

    @classmethod
    def get(cls, expert_id: str) -> Optional[type]:
        return cls._experts.get(expert_id)

    @classmethod
    def list_all(cls) -> List[str]:
        return list(cls._experts.keys())

    @classmethod
    def create_instance(cls, expert_id: str, **kwargs) -> Optional[ExpertBase]:
        expert_class = cls.get(expert_id)
        if expert_class:
            return expert_class(**kwargs)
        return None


__all__ = [
    "ExpertContext",
    "ExpertOutput",
    "PromptTemplate",
    "LLMClient",
    "OpenAIClient",
    "ExpertBase",
    "ExpertRegistry",
]
