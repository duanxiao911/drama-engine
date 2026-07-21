"""
§10 实战指挥（Mission Commander）

职责：端到端工作流编排专家
调度15个专家按正确顺序执行，处理异常恢复、断点续跑、进度监控
是整个引擎的"总调度台"

基于 Wave2 架构设计
"""

import json
import time
from typing import List, Dict, Optional, Any
from .base import ExpertBase, ExpertContext, ExpertOutput, ExpertRegistry


# 专家执行顺序定义
WORKFLOW_STAGES = [
    {
        "stage": "第一波：创意与合规",
        "experts": ["§0", "§2", "§8"],
        "parallel": False,
    },
    {
        "stage": "第二波：角色与结构",
        "experts": ["§1", "§3"],
        "parallel": False,
    },
    {
        "stage": "第三波：剧本生成",
        "experts": ["§4", "§11", "§5"],
        "parallel": False,
    },
    {
        "stage": "第四波：质量闭环",
        "experts": ["§6", "§7", "§9", "§13", "§14", "§15"],
        "parallel": False,
        "loop": True,  # §7→§9 可能迭代
    },
]

# 异常处理策略
RETRY_CONFIG = {
    "max_retries": 3,
    "retry_intervals": [5, 15, 30],  # 秒
    "on_failure": "skip_and_mark",  # skip_and_mark / abort
}


class MissionCommanderExpert(ExpertBase):
    """§10 实战指挥"""
    expert_id = "§10"
    expert_name = "mission_commander"
    prompt_file = "mission_commander.md"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.execution_log: List[Dict] = []
        self.checkpoint: Dict = {}

    def get_system_prompt(self) -> str:
        return """你是云匠引擎的总调度台，代号§10实战指挥。

你的核心能力：调度15个专家按正确顺序执行，处理异常恢复、断点续跑、进度监控。

【专家执行顺序】

第一波：创意与合规
  1. §0 灵魂捕手 → 提炼故事内核
  2. §2 合规守门员 → 六大红线扫描
  3. §8 项目配置师 → 结构化项目设定

第二波：角色与结构
  4. §1 角色铸造师 → 构建人设体系
  5. §3 结构建筑师 → 节拍表+段落大纲

第三波：剧本生成
  6. §4 对白大师 → 个性化对白
  7. §11 场景工匠 → 场景氛围增强
  8. §5 分集编剧 → 完整分场剧本

第四波：质量闭环
  9. §6 格式工匠 → 格式标准化
  10. §7 质量审计 → 6维度评分
  11. §9 改稿编辑 → 针对性改稿（最多3轮迭代）
  12. §13 视觉导演 → 视觉叙事方案
  13. §14 商业操盘 → 市场分析报告
  14. §15 品控总监 → 终审签发

【异常处理策略】
- API超时：重试3次，间隔5s/15s/30s
- 输出不合格：标记问题，传递给下游专家处理
- 连续3次失败：跳过该专家，标记为"待人工介入"
- 质量审计<6.0：触发改稿编辑迭代

【断点续跑】
- 每个专家执行完成后保存检查点
- 中断后可从最近的检查点恢复

【进度报告格式】
```
进度：X/15 专家已完成
当前：§N 专家名称 [执行中/等待/完成/失败]
耗时：Xm Xs
质量：当前综合评分 X.X
```
"""

    def get_user_prompt(self, context: ExpertContext, **kwargs) -> str:
        story_direction = context.story_direction or kwargs.get("story_direction", "")
        target_platform = kwargs.get("platform", "generic")
        resume_from = kwargs.get("resume_from", None)

        prompt = f"""请执行云匠引擎全流程调度。

【故事方向】{story_direction}
【目标平台】{target_platform}
{f'【断点续跑】从 §{resume_from} 继续执行' if resume_from else ''}

任务：
1. 按4波15专家顺序依次调度执行
2. 每个专家执行后记录状态（完成/失败/跳过）
3. 异常时按策略重试或跳过
4. §7质量审计后判断是否需要§9改稿迭代
5. 最终由§15品控总监签发
6. 输出完整执行日志和进度报告
"""
        return prompt

    def validate_output(self, output: str) -> tuple[bool, List[str]]:
        errors = []
        # 检查是否包含执行日志
        has_log = any(kw in output for kw in ["进度", "执行", "完成", "调度"])
        if not has_log:
            errors.append("未找到执行日志")
        # 检查是否有状态报告
        has_status = any(kw in output for kw in ["§0", "§1", "§2", "灵魂捕手", "角色铸造"])
        if not has_status:
            errors.append("未找到专家执行状态")
        return len(errors) == 0, errors

    def build_execution_plan(self, context: ExpertContext) -> List[Dict]:
        """构建执行计划"""
        plan = []
        for stage in WORKFLOW_STAGES:
            for expert_id in stage["experts"]:
                plan.append({
                    "expert_id": expert_id,
                    "stage": stage["stage"],
                    "status": "pending",
                    "retries": 0,
                    "result": None,
                })
        return plan

    def save_checkpoint(self, step_index: int, context: ExpertContext):
        """保存检查点"""
        self.checkpoint = {
            "step_index": step_index,
            "context_snapshot": context.to_dict(),
            "execution_log": self.execution_log.copy(),
            "timestamp": time.time(),
        }

    def load_checkpoint(self) -> Optional[Dict]:
        """加载检查点"""
        return self.checkpoint if self.checkpoint else None


# 注册
from .base import ExpertRegistry
ExpertRegistry.register("§10", MissionCommanderExpert)
