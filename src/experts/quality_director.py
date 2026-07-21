"""
§15 品控总监（Quality Director）

职责：终审把关专家
创作流水线的最后一道关卡
全剧一致性校验（角色/时间线/空间/情感）+ 最终质量确认 + 签发
通过品控的剧本才能定稿输出

基于 Wave2 架构设计
"""

import re
from typing import List, Dict, Optional
from .base import ExpertBase, ExpertContext, ExpertOutput


# 终审通过条件
PASS_CRITERIA = {
    "min_overall_score": 7.0,
    "min_episode_score": 6.0,
    "required_checks": [
        "角色一致性",
        "时间线一致性",
        "空间逻辑",
        "情感连贯性",
    ],
}

# 一致性校验清单
CONSISTENCY_CHECKLIST = {
    "character": {
        "name": "角色一致性",
        "items": [
            "每个角色的性格特征在全剧中保持一致",
            "角色弧光按设计轨迹发展，不跳跃不突兀",
            "对白风格不跑偏（A角色不会说出B角色的语气）",
            "角色关系变化有铺垫，不突兀",
        ],
    },
    "timeline": {
        "name": "时间线一致性",
        "items": [
            "事件先后顺序正确",
            "时间跨度合理（不会一夜之间学会需要数年的技能）",
            "季节/天气与剧情时间线吻合",
            "回忆/闪回与现实时间线区分清晰",
        ],
    },
    "spatial": {
        "name": "空间逻辑",
        "items": [
            "场景地理位置合理（不会瞬移）",
            "同一场景内的道具布置保持一致",
            "角色的移动时间合理",
        ],
    },
    "emotional": {
        "name": "情感连贯性",
        "items": [
            "情绪变化有触发事件，不会无故大喜大悲",
            "情感高潮前有足够铺垫",
            "悲伤场景不会突然变搞笑（除非有合理过渡）",
        ],
    },
}


class QualityDirectorExpert(ExpertBase):
    """§15 品控总监"""
    expert_id = "§15"
    expert_name = "quality_director"
    prompt_file = "quality_director.md"

    def get_system_prompt(self) -> str:
        checklist_text = ""
        for key, category in CONSISTENCY_CHECKLIST.items():
            checklist_text += f"\n【{category['name']}】\n"
            for item in category["items"]:
                checklist_text += f"  □ {item}\n"

        return f"""你是一位终审把关专家，代号§15品控总监。

你是云匠引擎创作流水线的最后一道关卡。通过你签发的剧本才能定稿输出。

【终审通过条件】
1. §7质量审计总分 ≥ {PASS_CRITERIA['min_overall_score']}
2. 所有单集分数 ≥ {PASS_CRITERIA['min_episode_score']}
3. 以下一致性校验全部通过：
{checklist_text}

4. 所有集完整、无遗漏、无格式错误
5. 合规审查通过（无红线问题）

【终审流程】
1. 读取§7质量审计报告，确认总分和各集分数
2. 读取改稿后的最终剧本
3. 逐项执行一致性校验清单
4. 完整性检查：集数齐全、格式统一
5. 合规终审：六大红线最终扫描
6. 签发判定：通过 / 有条件通过 / 不通过

【签发结果格式】

## 终审报告

### 签发结果：通过/有条件通过/不通过

### 一致性校验
- 角色一致性：通过/未通过 [具体问题]
- 时间线一致性：通过/未通过 [具体问题]
- 空间逻辑：通过/未通过 [具体问题]
- 情感连贯性：通过/未通过 [具体问题]

### 完整性检查
- 总集数：X集（齐全/缺失）
- 格式统一：是/否
- 元数据完整：是/否

### 合规终审
- 六大红线扫描：通过/有X条风险
- AI含量标注：X%

### 条件说明（如有条件通过）
1. ...

### 签发意见
[最终评语，100字以内]
"""

    def get_user_prompt(self, context: ExpertContext, **kwargs) -> str:
        # 获取质量审计报告
        audit_report = ""
        if context.metadata.get("step_outputs", {}).get("§7"):
            audit_report = context.metadata["step_outputs"]["§7"].get("content", "")[:5000]
        elif kwargs.get("quality_report"):
            audit_report = str(kwargs["quality_report"])[:5000]

        # 获取最终剧本
        final_script = ""
        if context.metadata.get("step_outputs", {}).get("§9"):
            final_script = context.metadata["step_outputs"]["§9"].get("content", "")[:8000]
        elif context.metadata.get("step_outputs", {}).get("§6"):
            final_script = context.metadata["step_outputs"]["§6"].get("content", "")[:8000]
        elif context.metadata.get("step_outputs", {}).get("§5"):
            final_script = context.metadata["step_outputs"]["§5"].get("content", "")[:8000]

        # 角色人设（一致性校验参考）
        chars_text = ""
        if context.character_cards:
            chars_text = "\n".join([
                f"- {card.get('name_line', '未命名')}"
                for card in context.character_cards[:10]
            ])

        # 合规报告
        compliance_report = ""
        if context.metadata.get("step_outputs", {}).get("§2"):
            compliance_report = context.metadata["step_outputs"]["§2"].get("content", "")[:2000]

        prompt = f"""请执行终审签发。

【质量审计报告】
{audit_report if audit_report else "暂无审计报告"}

【最终剧本】
{final_script if final_script else "暂无剧本内容"}

【角色人设参考】
{chars_text if chars_text else "请从剧本提取"}

【合规审查报告】
{compliance_report if compliance_report else "暂无合规报告"}

任务：
1. 确认质量审计总分和各集分数是否达标
2. 逐项执行四类一致性校验（角色/时间线/空间/情感）
3. 完整性检查（集数/格式/元数据）
4. 合规终审（六大红线最终扫描）
5. 给出签发结果：通过/有条件通过/不通过
6. 如有条件通过，列出必须修改的条件
"""
        return prompt

    def validate_output(self, output: str) -> tuple[bool, List[str]]:
        errors = []
        # 检查是否有签发结果
        has_verdict = any(kw in output for kw in ["签发结果", "通过", "不通过", "有条件"])
        if not has_verdict:
            errors.append("未找到签发结果")
        # 检查是否有一致性校验
        has_consistency = any(kw in output for kw in ["角色一致性", "时间线", "空间逻辑", "情感连贯"])
        if not has_consistency:
            errors.append("缺少一致性校验")
        # 检查是否有完整性检查
        has_completeness = any(kw in output for kw in ["完整性", "集数", "齐全", "格式统一"])
        if not has_completeness:
            errors.append("缺少完整性检查")
        return len(errors) == 0, errors

    def make_verdict(self, output: str) -> Dict:
        """解析签发结果"""
        verdict = "unknown"
        if "不通过" in output:
            verdict = "rejected"
        elif "有条件通过" in output:
            verdict = "conditional"
        elif "通过" in output:
            verdict = "approved"

        conditions = []
        # 提取条件
        condition_matches = re.findall(r'(?:条件|必须|需)[：:]?\s*(.+)', output)
        conditions = [m.strip() for m in condition_matches if len(m.strip()) > 5]

        return {
            "verdict": verdict,
            "conditions": conditions,
            "raw": output[:3000],
        }


# 注册
from .base import ExpertRegistry
ExpertRegistry.register("§15", QualityDirectorExpert)
