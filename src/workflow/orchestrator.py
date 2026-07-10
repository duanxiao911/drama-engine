"""
工作流编排器

管理专家执行顺序、上下文传递、状态追踪和断点续传

基于《架构设计.md》用户交互流程：
§0灵魂捕手→§2合规守门员→§8项目配置师→§1角色铸造师→§4对白大师→§3结构建筑师→§13视觉导演
"""

import json
import os
import re
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from pathlib import Path
from enum import Enum

from src.experts.base import ExpertBase, ExpertContext, ExpertOutput, ExpertRegistry
from src.experts.soul_catcher import SoulCatcherExpert
from src.experts.character_forger import CharacterForgerExpert
from src.experts.compliance_guard import ComplianceGuardExpert
from src.experts.structure_architect import StructureArchitectExpert
from src.experts.dialogue_master import DialogueMasterExpert
from src.experts.project_configurator import ProjectConfiguratorExpert
from src.experts.visual_director import VisualDirectorExpert
from src.experts.episode_writer import EpisodeWriterExpert
from src.knowledge.culture_kb import CultureKnowledgeBase


class WorkflowStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


@dataclass
class WorkflowState:
    workflow_id: str
    status: WorkflowStatus = WorkflowStatus.PENDING
    current_step: int = 0
    total_steps: int = 8
    expert_sequence: List[str] = field(default_factory=list)
    completed_steps: List[int] = field(default_factory=list)
    context_snapshot: Optional[ExpertContext] = None
    step_outputs: Dict[str, ExpertOutput] = field(default_factory=dict)
    error_message: Optional[str] = None
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at


class Orchestrator:
    """工作流编排器"""

    DEFAULT_SEQUENCE = ["§0", "§2", "§8", "§1", "§4", "§3", "§5", "§13"]

    SEQUENCE_DESCRIPTIONS = {
        "§0": "灵魂捕手：对话式追问，确认故事方向",
        "§2": "合规守门员：红线扫描，输出风险评级",
        "§8": "项目配置师：将方向拆解为完整项目设定",
        "§1": "角色铸造师：三层四维度人设+弧光线",
        "§4": "对白大师：语料库生成+对白风格卡+钩子链",
        "§3": "结构建筑师：救猫咪节拍表+23段落+弧光追踪",
        "§5": "分集编剧：将大纲展开为完整分场剧本",
        "§13": "视觉导演：光影系统+镜头系统+声音系统",
    }

    def __init__(
        self,
        expert_sequence: Optional[List[str]] = None,
        llm_client=None,
        knowledge_base_path: Optional[str] = None,
        project_path: Optional[str] = None,
        enable_checkpoint: bool = True,
        enable_culture_kb: bool = True,
    ):
        self.expert_sequence = expert_sequence or self.DEFAULT_SEQUENCE
        self.llm_client = llm_client
        self.knowledge_base_path = knowledge_base_path
        self.project_path = project_path or "./workspace"
        self.enable_checkpoint = enable_checkpoint

        # 第5.5层：中华优秀传统文化知识库
        self.culture_kb = CultureKnowledgeBase() if enable_culture_kb else None

        self.state: Optional[WorkflowState] = None
        self._expert_instances: Dict[str, ExpertBase] = {}
        self._callbacks: Dict[str, List[Callable]] = {
            "on_step_start": [],
            "on_step_complete": [],
            "on_step_error": [],
            "on_workflow_complete": [],
        }

    def _get_expert_instance(self, expert_id: str) -> Optional[ExpertBase]:
        """获取专家实例（懒加载+缓存）"""
        if expert_id in self._expert_instances:
            return self._expert_instances[expert_id]

        expert_class = ExpertRegistry.get(expert_id)
        if expert_class:
            instance = expert_class(
                llm_client=self.llm_client,
                knowledge_base_path=self.knowledge_base_path,
                culture_kb=self.culture_kb,
            )
            self._expert_instances[expert_id] = instance
            return instance
        return None

    def _init_workflow(self, user_input: str, **kwargs) -> WorkflowState:
        workflow_id = f"wf_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        context = ExpertContext(
            story_direction=user_input,
            metadata={
                "user_input": user_input,
                "created_at": datetime.now().isoformat(),
            },
        )
        state = WorkflowState(
            workflow_id=workflow_id,
            expert_sequence=self.expert_sequence,
            context_snapshot=context,
            total_steps=len(self.expert_sequence),
            status=WorkflowStatus.PENDING,
        )
        self.state = state
        return state

    def _execute_step(self, step_index: int, context: ExpertContext, **kwargs) -> ExpertOutput:
        """执行单个专家步骤"""
        expert_id = self.expert_sequence[step_index]
        expert_instance = self._get_expert_instance(expert_id)

        if not expert_instance:
            return ExpertOutput(
                expert_name=expert_id,
                content=f"[错误] 未找到专家: {expert_id}",
                validation_passed=False,
                validation_errors=[f"专家{expert_id}未注册"],
            )

        self._trigger_callback("on_step_start", expert_id, step_index, context)

        try:
            # §5分集编剧：使用分批生成逻辑
            if expert_id == "§5":
                output = self._execute_episode_batch(expert_instance, context, **kwargs)
            else:
                output = expert_instance.execute(context, **kwargs)

            self._update_context_from_output(expert_id, output, context)
            self._trigger_callback("on_step_complete", expert_id, step_index, output)

            return output

        except Exception as e:
            error_output = ExpertOutput(
                expert_name=expert_id,
                content=f"[执行错误] {str(e)}",
                validation_passed=False,
                validation_errors=[str(e)],
            )
            self._trigger_callback("on_step_error", expert_id, step_index, e)
            return error_output

    def _execute_episode_batch(self, expert, context: ExpertContext, **kwargs) -> ExpertOutput:
        """
        §5分集编剧分批生成：每次5集，循环生成完整分场剧本。
        每批传入前文内容以保持风格连贯。
        """
        total_episodes = 30
        if context.project_config:
            ep_val = context.project_config.get("episodes") or context.project_config.get("total_episodes")
            if ep_val:
                try:
                    total_episodes = int(ep_val)
                except (ValueError, TypeError):
                    pass

        batch_size = 5
        all_content = []

        for batch_start in range(1, total_episodes + 1, batch_size):
            batch_end = min(batch_start + batch_size - 1, total_episodes)
            episodes = list(range(batch_start, batch_end + 1))

            print(f"  [§5] 生成第{batch_start}-{batch_end}集剧本...")

            prev_content = "\n".join(all_content[-2000:]) if all_content else ""

            output = expert.execute(
                context,
                target_episodes=episodes,
                previous_content=prev_content,
                max_tokens=16000,
            )
            all_content.append(output.content)
            print(f"  [§5] 第{batch_start}-{batch_end}集完成，字数约{len(output.content)}")

        combined_content = "\n\n".join(all_content)
        print(f"  [§5] 全部{total_episodes}集剧本生成完成，总字数约{len(combined_content)}")

        return ExpertOutput(
            expert_name="§5",
            content=combined_content,
            structured_data={"episode_scripts": {"raw": combined_content}, "raw": combined_content},
            validation_passed=True,
        )

    def _update_context_from_output(self, expert_id: str, output: ExpertOutput, context: ExpertContext):
        """从专家输出更新context"""
        if expert_id == "§0":
            sd = {}
            if "故事方向：" in output.content or "故事方向:" in output.content:
                dir_match = re.search(r'故事方向[：:]\s*(.+)', output.content)
                if dir_match:
                    sd["story_direction"] = dir_match.group(1).strip()
                    context.story_direction = dir_match.group(1).strip()
                    if not context.story_premise:
                        context.story_premise = dir_match.group(1).strip()
            if "一句话前提：" in output.content or "一句话前提:" in output.content:
                prem_match = re.search(r'一句话前提[：:]\s*(.+)', output.content)
                if prem_match:
                    sd["story_premise"] = prem_match.group(1).strip()
                    context.story_premise = prem_match.group(1).strip()
            if "推荐类型：" in output.content or "推荐类型:" in output.content:
                type_match = re.search(r'推荐类型[：:]\s*(.+)', output.content)
                if type_match:
                    sd["drama_type"] = type_match.group(1).strip()
                    if not context.project_config:
                        context.project_config = {}
                    context.project_config["drama_type"] = type_match.group(1).strip()
            sd["raw"] = output.content
            output.structured_data = sd

        elif expert_id == "§2":
            context.risk_level = self._parse_risk_level(output.content)
            context.risk_warnings = self._parse_warnings(output.content)
            output.structured_data = {
                "risk_level": context.risk_level,
                "risk_warnings": context.risk_warnings,
                "raw": output.content,
            }

        elif expert_id == "§8":
            if "project_config" not in context.metadata:
                context.metadata["project_config"] = {}
            context.metadata["project_config"]["raw"] = output.content
            sd = {"raw": output.content}
            if not context.story_premise:
                prem_match = re.search(r'一句话前提[：:]\s*(.+)', output.content)
                if prem_match:
                    context.story_premise = prem_match.group(1).strip()
                    sd["story_premise"] = context.story_premise
                else:
                    overview_match = re.search(r'(?:项目概述|故事概述|核心前提)[：:]\s*(.+)', output.content)
                    if overview_match:
                        context.story_premise = overview_match.group(1).strip()
                        sd["story_premise"] = context.story_premise
            for key, patterns in {
                "title": [r'剧名[：:]\s*(.+)'],
                "episodes": [r'集数[：:]\s*(\d+)', r'(\d+)\s*集'],
                "genre": [r'类型[：:]\s*(.+)'],
            }.items():
                for p in patterns:
                    m = re.search(p, output.content)
                    if m:
                        sd[key] = m.group(1).strip()
                        break
            output.structured_data = sd

        elif expert_id == "§1":
            cards = self._parse_character_cards(output.content)
            context.character_cards = cards
            # 无论如何都保存完整原始内容到metadata
            if not context.metadata.get("step_outputs"):
                context.metadata["step_outputs"] = {}
            context.metadata["step_outputs"]["§1"] = {"content": output.content}
            output.structured_data = {
                "character_cards": cards,
                "character_count": len(cards),
                "raw": output.content,
            }

        elif expert_id == "§4":
            context.dialogue_corpus = {"raw": output.content}
            output.structured_data = {
                "dialogue_corpus": {"raw": output.content},
                "raw": output.content,
            }

        elif expert_id == "§3":
            beats = self._parse_beats(output.content)
            outlines = self._parse_outlines(output.content, context.project_config.get("total_episodes", 30) if context.project_config else 30)
            context.beat_table = beats
            context.episode_outlines = outlines
            # 保存完整原始内容
            if not context.metadata.get("step_outputs"):
                context.metadata["step_outputs"] = {}
            context.metadata["step_outputs"]["§3"] = {"content": output.content}
            output.structured_data = {
                "beat_table": beats,
                "episode_outlines": outlines,
                "beat_count": len(beats),
                "outline_count": len(outlines),
                "raw": output.content,
            }

        elif expert_id == "§5":
            if "episode_scripts" not in context.metadata:
                context.metadata["episode_scripts"] = {}
            context.metadata["episode_scripts"]["raw"] = output.content
            output.structured_data = {
                "episode_scripts": {"raw": output.content},
                "raw": output.content,
            }

        elif expert_id == "§13":
            context.visual_scheme = {"raw": output.content}
            output.structured_data = {
                "visual_scheme": {"raw": output.content},
                "raw": output.content,
            }

    @staticmethod
    def _parse_risk_level(content: str) -> str:
        m = re.search(r'风险评级[：:]\s*(.+)', content)
        if m:
            line = m.group(1)
            if "🔴" in line or "红" in line or "red" in line.lower():
                return "red"
            if "🟡" in line or "黄" in line or "yellow" in line.lower():
                return "yellow"
            if "🟢" in line or "绿" in line or "green" in line.lower():
                return "green"
        if "🔴" in content:
            return "red"
        elif "🟡" in content:
            return "yellow"
        return "green"

    @staticmethod
    def _parse_warnings(content: str) -> List[Dict]:
        warnings = []
        lines = content.split('\n')
        for line in lines:
            if '→' in line and any(r in line for r in ['红线', '风险', '禁区']):
                warnings.append({"raw": line.strip(), "severity": "high" if '🔴' in line else "medium"})
        return warnings

    @staticmethod
    def _parse_character_cards(content: str) -> List[Dict]:
        """
        宽松的多策略角色卡解析器。
        策略1: 角色名[：:]xxx
        策略2: 按 ### 分割
        策略3: 按 **名字** 模式
        策略4: 按 ## 大标题分割
        策略5: 兜底 - 整段内容作为单个角色卡
        """
        cards = []

        # 策略1
        blocks = re.split(r'角色名[：:]', content)
        if len(blocks) > 1:
            for block in blocks[1:]:
                name_match = re.match(r'\s*(\S+)', block)
                if name_match:
                    cards.append({"name": name_match.group(1), "raw": block.strip()})
            if cards:
                return cards

        # 策略2
        sections = re.split(r'###\s+', content)
        if len(sections) > 1:
            for section in sections[1:]:
                first_line = section.split('\n')[0].strip()
                skip_patterns = ['语料库', '角色分析总结', '使用方法', '输出说明', '总结', '附注', '注释']
                if any(p in first_line for p in skip_patterns):
                    continue
                section_content = section.strip()
                if len(section_content) > 20:
                    name_match = re.match(r'([^\n（(：:，,]{2,20})', first_line)
                    if name_match:
                        name = name_match.group(1).strip().strip('*').strip()
                        if name and len(name) >= 2:
                            cards.append({"name": name, "name_line": first_line, "raw": section_content})
            if cards:
                return cards

        # 策略3
        bold_blocks = re.split(r'\*\*([^*]+)\*\*', content)
        if len(bold_blocks) > 2:
            for i in range(1, len(bold_blocks), 2):
                name = bold_blocks[i].strip()
                if len(name) >= 2 and len(name) <= 15 and i + 1 < len(bold_blocks):
                    block_content = bold_blocks[i + 1].strip()
                    if len(block_content) > 20:
                        cards.append({"name": name, "raw": block_content})
            if cards:
                return cards

        # 策略4
        h2_sections = re.split(r'##\s+', content)
        if len(h2_sections) > 2:
            for section in h2_sections[1:]:
                first_line = section.split('\n')[0].strip()
                skip_patterns = ['角色', '人物', '总', '附录', '说明', '使用']
                if any(p in first_line for p in skip_patterns):
                    continue
                if len(section.strip()) > 30:
                    name_match = re.match(r'([^\n（(：:，,]{2,20})', first_line)
                    if name_match:
                        name = name_match.group(1).strip().strip('*').strip()
                        cards.append({"name": name, "name_line": first_line, "raw": section.strip()})
            if cards:
                return cards

        # 策略5（兜底）
        if content.strip():
            cards.append({"name": "主要角色", "raw": content.strip()})

        return cards

    @staticmethod
    def _parse_beats(content: str) -> List[Dict]:
        beats = []
        beat_nums = re.findall(r'#?\d+[.、]\s*', content)
        for i, _ in enumerate(beat_nums[:15]):
            beats.append({"beat_num": i + 1})
        return beats

    @staticmethod
    def _parse_outlines(content: str, total_episodes: int = 30) -> List[Dict]:
        outlines = []
        ep_pattern = r'【?第?\s*(\d+)\s*集[】:]?\s*(.{10,100})'
        matches = re.findall(ep_pattern, content)
        for ep_num, desc in matches:
            outlines.append({
                "episode": int(ep_num) if ep_num.isdigit() else 0,
                "description": desc.strip(),
            })
        return outlines

    def _trigger_callback(self, event: str, *args):
        for callback in self._callbacks.get(event, []):
            try:
                callback(*args)
            except Exception:
                pass

    def on(self, event: str, callback: Callable):
        if event in self._callbacks:
            self._callbacks[event].append(callback)

    def _save_checkpoint(self):
        if not self.enable_checkpoint or not self.state:
            return
        checkpoint_path = os.path.join(self.project_path, f"{self.state.workflow_id}.checkpoint.json")
        os.makedirs(os.path.dirname(checkpoint_path), exist_ok=True)
        with open(checkpoint_path, "w", encoding="utf-8") as f:
            json.dump({
                "workflow_id": self.state.workflow_id,
                "status": self.state.status.value,
                "current_step": self.state.current_step,
                "expert_sequence": self.state.expert_sequence,
                "completed_steps": self.state.completed_steps,
                "context": self.state.context_snapshot.to_dict() if self.state.context_snapshot else {},
                "step_outputs": {k: v.to_dict() for k, v in self.state.step_outputs.items()},
            }, f, ensure_ascii=False, indent=2)

    def _load_checkpoint(self, workflow_id: str) -> Optional[WorkflowState]:
        checkpoint_path = os.path.join(self.project_path, f"{workflow_id}.checkpoint.json")
        if not os.path.exists(checkpoint_path):
            return None
        with open(checkpoint_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        context = ExpertContext(**data.get("context", {}))
        outputs = {k: ExpertOutput(**v) for k, v in data.get("step_outputs", {}).items()}
        state = WorkflowState(
            workflow_id=data["workflow_id"],
            status=WorkflowStatus(data["status"]),
            current_step=data["current_step"],
            expert_sequence=data["expert_sequence"],
            completed_steps=data["completed_steps"],
            context_snapshot=context,
            step_outputs=outputs,
        )
        return state

    def run_full(self, user_input: str, stop_at: Optional[str] = None, **kwargs) -> WorkflowState:
        state = self._init_workflow(user_input)
        state.status = WorkflowStatus.RUNNING

        for step_idx, expert_id in enumerate(self.expert_sequence):
            state.current_step = step_idx
            output = self._execute_step(step_idx, state.context_snapshot, **kwargs)
            state.step_outputs[expert_id] = output
            state.completed_steps.append(step_idx)

            if not output.validation_passed:
                pass

            self._save_checkpoint()

            if expert_id == "§2" and getattr(state.context_snapshot, "risk_level", None) == "red":
                pass

            if stop_at and expert_id == stop_at:
                state.status = WorkflowStatus.PAUSED
                state.updated_at = datetime.now().isoformat()
                return state

        state.status = WorkflowStatus.COMPLETED
        state.updated_at = datetime.now().isoformat()
        self._trigger_callback("on_workflow_complete", state)
        return state

    def run_step(self, expert_id: str, context: Optional[ExpertContext] = None, **kwargs) -> ExpertOutput:
        if expert_id not in self.expert_sequence:
            return ExpertOutput(
                expert_name=expert_id,
                content=f"[错误] 专家{expert_id}不在当前工作流序列中",
                validation_passed=False,
                validation_errors=[f"专家{expert_id}不在序列{self.expert_sequence}中"],
            )

        step_idx = self.expert_sequence.index(expert_id)
        working_context = context or (self.state.context_snapshot if self.state else ExpertContext())
        output = self._execute_step(step_idx, working_context, **kwargs)

        if self.state:
            self.state.step_outputs[expert_id] = output
            self.state.context_snapshot = working_context
            self._save_checkpoint()

        return output

    def resume(self, workflow_id: str) -> WorkflowState:
        state = self._load_checkpoint(workflow_id)
        if not state:
            raise ValueError(f"未找到断点: {workflow_id}")
        self.state = state
        state.status = WorkflowStatus.RUNNING

        for step_idx, expert_id in enumerate(self.expert_sequence):
            if step_idx in state.completed_steps:
                continue
            state.current_step = step_idx
            output = self._execute_step(step_idx, state.context_snapshot)
            state.step_outputs[expert_id] = output
            state.completed_steps.append(step_idx)
            self._save_checkpoint()

        state.status = WorkflowStatus.COMPLETED
        state.updated_at = datetime.now().isoformat()
        return state

    def get_progress(self) -> Dict:
        if not self.state:
            return {"status": "not_started"}
        return {
            "workflow_id": self.state.workflow_id,
            "status": self.state.status.value,
            "current_step": self.state.current_step,
            "total_steps": self.state.total_steps,
            "current_expert": self.expert_sequence[self.state.current_step] if self.state.current_step < len(self.expert_sequence) else None,
            "completed_experts": [self.expert_sequence[i] for i in self.state.completed_steps],
            "completed_count": len(self.state.completed_steps),
        }

    def list_available_experts(self) -> List[Dict]:
        experts = []
        for expert_id, desc in self.SEQUENCE_DESCRIPTIONS.items():
            name = desc.split("：")[1] if "：" in desc else expert_id
            experts.append({
                "id": expert_id,
                "name": name,
                "description": desc,
                "in_sequence": expert_id in self.expert_sequence,
            })
        return experts


def create_default_orchestrator(**kwargs) -> Orchestrator:
    """创建默认配置的工作流编排器"""
    return Orchestrator(**kwargs)


__all__ = ["Orchestrator", "WorkflowState", "WorkflowStatus"]
