"""
§9 改稿编辑（Revision Editor）

职责：基于§7质量审计报告的低分维度，针对性修改剧本
执行"评估-改稿-再评估"迭代循环，直到所有维度达到7.0分以上
最多3轮迭代，每轮聚焦最严重的3个问题
保留原有文风和角色语感，记录变更日志

基于 Wave2 架构设计
"""

import re
import json
from typing import List, Dict, Optional
from .base import ExpertBase, ExpertContext, ExpertOutput


class RevisionEditorExpert(ExpertBase):
    """§9 改稿编辑"""
    expert_id = "§9"
    expert_name = "revision_editor"
    prompt_file = "revision_editor.md"

    def get_system_prompt(self) -> str:
        return """你是一位剧本改稿专家，代号§9改稿编辑。

你的核心能力：基于质量审计报告，针对性修改剧本。执行"评估-改稿-再评估"迭代循环。

【改稿优先级矩阵】
- P0 必修：逻辑漏洞、角色行为矛盾、情节断裂
- P1 重要：对白平淡、节奏拖沓、场景描写不足
- P2 优化：视觉细节、情绪铺垫、悬念加强

【改稿手法库】
1. 对白强化：增加角色个性化表达，去模板化
2. 节奏调整：删减冗余场景，合并可合并的段落
3. 张力提升：在薄弱集增加钩子/悬念/反转
4. 视觉补强：为纯文字叙述补充镜头语言和动作细节
5. 角色补全：为消失的配角补充存在感和支线

【改稿铁律】
1. 只改低分部分，不动高分内容
2. 保留原有文风和角色语感
3. 每次修改必须记录 before → after + 修改原因
4. 最多3轮迭代，每轮聚焦最严重的3个问题
5. 改完自检：修改是否引入了新问题

【输出格式】

## 第X轮改稿报告

### 本轮目标（Top 3问题）
1. [P0/P1/P2] 问题描述 → 目标集数

### 变更日志
| 位置 | Before | After | 原因 |
|------|--------|-------|------|
| 第X集场景Y | 原文 | 改后 | 修改原因 |

### 修改后剧本（仅改动部分）
[仅输出修改后的场景/段落，不重复未改动的内容]

### 自检结果
- 是否引入新矛盾：是/否
- 角色一致性：通过/需关注
- 建议下一轮关注点：...
"""

    def get_user_prompt(self, context: ExpertContext, **kwargs) -> str:
        # 获取质量审计报告
        audit_report = ""
        if context.metadata.get("step_outputs", {}).get("§7"):
            audit_report = context.metadata["step_outputs"]["§7"].get("content", "")[:5000]
        elif kwargs.get("quality_report"):
            audit_report = str(kwargs["quality_report"])[:5000]

        # 获取当前剧本
        script_text = ""
        if context.metadata.get("step_outputs", {}).get("§6"):
            script_text = context.metadata["step_outputs"]["§6"].get("content", "")[:8000]
        elif context.metadata.get("step_outputs", {}).get("§5"):
            script_text = context.metadata["step_outputs"]["§5"].get("content", "")[:8000]

        # 迭代轮次
        current_round = kwargs.get("revision_round", 1)
        max_rounds = kwargs.get("max_rounds", 3)

        # 历史改稿记录
        prev_revisions = context.metadata.get("revision_history", [])
        history_text = ""
        if prev_revisions:
            history_text = "\n".join([
                f"第{r.get('round', '?')}轮：{r.get('summary', '无摘要')}"
                for r in prev_revisions
            ])

        prompt = f"""请执行第{current_round}轮改稿（最多{max_rounds}轮）。

【质量审计报告】
{audit_report if audit_report else "暂无审计报告，请自行识别剧本问题"}

【当前剧本】
{script_text if script_text else "暂无剧本内容"}

【历史改稿记录】
{history_text if history_text else "首轮改稿，无历史记录"}

任务：
1. 从审计报告中筛选所有低分维度和不合格集
2. 按优先级（P0>P1>P2）选出本轮Top 3问题
3. 针对性修改对应集的剧本内容
4. 记录完整变更日志（before/after/原因）
5. 执行自检：是否引入新问题
6. 判断是否还需要下一轮迭代
"""
        return prompt

    def validate_output(self, output: str) -> tuple[bool, List[str]]:
        errors = []
        # 检查是否有变更日志
        has_changelog = any(kw in output for kw in ["变更", "Before", "After", "修改", "改稿"])
        if not has_changelog:
            errors.append("未找到变更日志")
        # 检查是否有修改后的内容
        has_content = len(output) > 200
        if not has_content:
            errors.append("改稿内容过短")
        # 检查是否有自检结果
        has_selfcheck = any(kw in output for kw in ["自检", "检查", "是否引入"])
        if not has_selfcheck:
            errors.append("缺少自检结果")
        return len(errors) == 0, errors

    def extract_changes(self, output: str) -> List[Dict]:
        """提取变更日志"""
        changes = []
        # 尝试从表格或结构化文本中提取变更
        blocks = re.findall(r'第(\d+)集[^\n]*\n(.*?)(?=第\d+集|##|$)', output, re.DOTALL)
        for ep_num, block in blocks:
            changes.append({
                "episode": int(ep_num),
                "description": block.strip()[:500],
            })
        return changes


# 注册
from .base import ExpertRegistry
ExpertRegistry.register("§9", RevisionEditorExpert)
