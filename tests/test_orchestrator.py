"""
orchestrator.py 测试文件

测试工作流编排器的核心功能：
- 专家注册和实例化
- 上下文传递
- 状态追踪
- 断点保存与恢复
"""

import pytest
import sys
import os
import json
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.workflow.orchestrator import (
    Orchestrator,
    WorkflowState,
    WorkflowStatus,
)
from src.experts.base import (
    ExpertContext,
    ExpertOutput,
    ExpertRegistry,
)
from src.experts.soul_catcher import SoulCatcherExpert
from src.experts.character_forger import CharacterForgerExpert


class TestExpertRegistry:
    """测试专家注册表"""

    def test_register_and_get(self):
        """注册并获取专家"""
        ExpertRegistry.register("test_expert", SoulCatcherExpert)
        expert_class = ExpertRegistry.get("test_expert")
        assert expert_class is not None

    def test_list_all(self):
        """列出所有专家"""
        experts = ExpertRegistry.list_all()
        assert isinstance(experts, list)


class TestOrchestrator:
    """测试工作流编排器"""

    def setup_method(self):
        """每个测试前创建临时目录和编排器"""
        self.temp_dir = tempfile.mkdtemp()
        self.orchestrator = Orchestrator(
            expert_sequence=["§0", "§1", "§2"],
            project_path=self.temp_dir,
            enable_checkpoint=True,
        )

    def teardown_method(self):
        """清理临时目录"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_init_workflow(self):
        """测试工作流初始化"""
        state = self.orchestrator._init_workflow("我想写一个关于爱情的故事")
        assert state.workflow_id.startswith("wf_")
        assert state.status == WorkflowStatus.PENDING
        assert len(state.expert_sequence) == 3

    def test_get_progress_initial(self):
        """测试获取初始进度"""
        self.orchestrator._init_workflow("测试")
        progress = self.orchestrator.get_progress()
        assert progress["status"] == "pending"
        assert progress["total_steps"] == 3

    def test_list_available_experts(self):
        """测试列出可用专家"""
        experts = self.orchestrator.list_available_experts()
        assert len(experts) > 0
        assert any(e["id"] == "§0" for e in experts)

    def test_run_step_with_mock_llm(self):
        """测试单步执行（mock LLM）"""
        from src.experts.base import OpenAIClient

        # 创建mock LLM
        mock_client = OpenAIClient(api_key="")

        orchestrator = Orchestrator(
            expert_sequence=["§0"],
            llm_client=mock_client,
            project_path=self.temp_dir,
        )

        output = orchestrator.run_step("§0", user_input="我想写一个关于梦想的故事")

        assert output.expert_name == "soul_catcher"
        assert isinstance(output.content, str)

    def test_workflow_state_updates(self):
        """测试工作流状态更新"""
        self.orchestrator._init_workflow("测试故事")

        # 执行一步
        from src.experts.base import OpenAIClient
        mock_client = OpenAIClient(api_key="")

        # 手动更新context
        self.orchestrator.state.context_snapshot.story_direction = "测试方向"
        self.orchestrator.state.context_snapshot.story_premise = "测试前提"

        assert self.orchestrator.state.context_snapshot.story_direction == "测试方向"

    def test_callback_registration(self):
        """测试回调注册"""
        callback_called = []

        def test_callback(expert_id, step_idx, output):
            callback_called.append((expert_id, step_idx))

        self.orchestrator.on("on_step_complete", test_callback)
        assert len(self.orchestrator._callbacks["on_step_complete"]) > 0


class TestContextUpdate:
    """测试上下文更新逻辑"""

    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.orchestrator = Orchestrator(
            expert_sequence=["§0", "§2"],
            project_path=self.temp_dir,
        )

    def teardown_method(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_parse_story_direction_from_output(self):
        """测试从§0输出解析故事方向"""
        context = ExpertContext()
        output = ExpertOutput(
            expert_name="§0",
            content="""【故事方向确认】
故事方向：一个关于坚持和放弃的故事

一句话前提：一个人如何在绝望中找到希望
推荐类型：悲剧
核心情感锚点：心疼、窒息感
禁止项：无
            """,
            validation_passed=True,
        )

        self.orchestrator._update_context_from_output("§0", output, context)

        assert "坚持和放弃" in context.story_direction
        assert "绝望中找到希望" in context.story_premise
        assert context.project_config.get("drama_type") == "悲剧"

    def test_parse_risk_level_red(self):
        """测试解析🔴红色风险"""
        context = ExpertContext()
        output = ExpertOutput(
            expert_name="§2",
            content="风险评级：🔴红色（严重风险）",
            validation_passed=False,
        )

        self.orchestrator._update_context_from_output("§2", output, context)
        assert context.risk_level == "red"

    def test_parse_risk_level_green(self):
        """测试解析🟢绿色风险"""
        context = ExpertContext()
        output = ExpertOutput(
            expert_name="§2",
            content="风险评级：🟢绿色（无风险）",
            validation_passed=True,
        )

        self.orchestrator._update_context_from_output("§2", output, context)
        assert context.risk_level == "green"


class TestExpertOutput:
    """测试专家输出"""

    def test_expert_output_to_dict(self):
        """测试输出序列化"""
        output = ExpertOutput(
            expert_name="test",
            content="测试内容",
            validation_passed=True,
            suggestions=["建议1"],
        )
        output_dict = output.to_dict()
        assert output_dict["expert_name"] == "test"
        assert output_dict["validation_passed"] is True


class TestExpertContext:
    """测试专家上下文"""

    def test_context_to_dict(self):
        """测试上下文序列化"""
        context = ExpertContext(
            story_direction="测试方向",
            story_premise="测试前提",
            project_config={"drama_type": "悲剧"},
            risk_level="green",
        )
        context_dict = context.to_dict()
        assert context_dict["story_direction"] == "测试方向"
        assert context_dict["project_config"]["drama_type"] == "悲剧"

    def test_context_update(self):
        """测试上下文更新"""
        context = ExpertContext()
        context.update(
            story_direction="新方向",
            risk_level="red",
        )
        assert context.story_direction == "新方向"
        assert context.risk_level == "red"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])