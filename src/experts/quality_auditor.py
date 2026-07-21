"""
§7 质量审计（Quality Auditor）

职责：对剧本进行6维度自动评分，输出结构化质量报告和改进建议
6维度：剧情张力/角色深度/对白质量/节奏把控/视觉潜力/商业潜力
评估结果作为§9改稿编辑的决策依据

基于 Wave2 架构设计
"""

import re
import json
from typing import List, Dict, Optional
from .base import ExpertBase, ExpertContext, ExpertOutput


# 6维度评分标准描述
DIMENSION_CRITERIA = {
    "plot_tension": {
        "name": "剧情张力",
        "weight": 0.25,
        "high": "每集有明确钩子+悬念，冲突层层递进",
        "mid": "主线清晰，偶有平淡但不拖沓",
        "low": "流水账式叙事，缺少戏剧冲突",
    },
    "character_depth": {
        "name": "角色深度",
        "weight": 0.20,
        "high": "三层人设完整，角色弧光清晰",
        "mid": "主角立体，配角基本合格",
        "low": "角色工具化，行为不合人设",
    },
    "dialogue_quality": {
        "name": "对白质量",
        "weight": 0.15,
        "high": "每句对白都有角色辨识度",
        "mid": "大部分对白有个性，少数模板化",
        "low": "对白空洞或角色间无法区分",
    },
    "pacing": {
        "name": "节奏把控",
        "weight": 0.15,
        "high": "信息密度合理，张弛有度",
        "mid": "整体流畅，个别集略快/略慢",
        "low": "严重节奏问题，大量无效场景",
    },
    "visual_potential": {
        "name": "视觉潜力",
        "weight": 0.15,
        "high": "场景描写极具画面感，可直接指导拍摄",
        "mid": "画面感良好，少数场景缺少细节",
        "low": "纯文字叙述，缺少视觉化描写",
    },
    "commercial_viability": {
        "name": "商业潜力",
        "weight": 0.10,
        "high": "题材有明确受众，钩子密度高",
        "mid": "有一定市场空间，差异化不足",
        "low": "受众模糊，缺少商业卖点",
    },
}


class QualityAuditorExpert(ExpertBase):
    """§7 质量审计"""
    expert_id = "§7"
    expert_name = "quality_auditor"
    prompt_file = "quality_auditor.md"

    def get_system_prompt(self) -> str:
        criteria_text = "\n".join([
            f"  - {v['name']}（权重{int(v['weight']*100)}%）：优秀={v['high']}；及格={v['mid']}；不合格={v['low']}"
            for v in DIMENSION_CRITERIA.values()
        ])

        return f"""你是一位剧本质量评估专家，代号§7质量审计。

你的核心能力：对剧本进行6维度自动评分，输出结构化质量报告。

【6维度评分标准（每项1-10分）】
{criteria_text}

【综合评分规则】
- 加权总分 = Σ(维度分 × 权重)
- S级：≥9.0（可直接投产）
- A级：7.5-8.9（微调后可投稿）
- B级：6.0-7.4（需针对性改稿）
- C级：4.0-5.9（大幅修改）
- D级：<4.0（建议重写）

【逐集分析规则】
- 对每一集独立打分，不只看整体
- 标注每集最突出的优点和最严重的问题
- 问题必须具体到集数和场景，不能泛泛而谈

【一致性校验】
- 检查角色言行是否一致
- 检查情节逻辑是否自洽
- 检查时间线是否合理

【输出格式（JSON结构）】

```json
{{
  "overall_score": 7.5,
  "grade": "A",
  "dimensions": {{
    "plot_tension": {{"score": 8, "issues": ["第5集钩子偏弱"]}},
    "character_depth": {{"score": 7, "issues": ["配角B存在感不足"]}},
    ...
  }},
  "episode_scores": [
    {{"episode": 1, "score": 8.2, "strength": "开场钩子强", "weakness": "中段节奏拖"}},
    ...
  ],
  "consistency_issues": ["第12集角色A行为与第3集矛盾"],
  "top3_improvements": [
    {{"priority": "P0", "target": "第5集", "action": "重写钩子场景"}},
    ...
  ]
}}
```
"""

    def get_user_prompt(self, context: ExpertContext, **kwargs) -> str:
        # 获取剧本内容
        script_text = ""
        if context.metadata.get("step_outputs", {}).get("§5"):
            script_text = context.metadata["step_outputs"]["§5"].get("content", "")[:8000]
        elif context.metadata.get("step_outputs", {}).get("§6"):
            script_text = context.metadata["step_outputs"]["§6"].get("content", "")[:8000]
        elif context.metadata.get("episode_scripts"):
            script_text = str(context.metadata["episode_scripts"])[:8000]

        # 角色信息
        chars_text = ""
        if context.character_cards:
            chars_text = "\n".join([
                f"- {card.get('name_line', '未命名')}"
                for card in context.character_cards[:10]
            ])

        # 大纲信息
        outline_text = ""
        if context.metadata.get("step_outputs", {}).get("§3"):
            outline_text = context.metadata["step_outputs"]["§3"].get("content", "")[:3000]

        prompt = f"""请对以下剧本进行6维度质量审计。

【剧本内容】
{script_text if script_text else "暂无剧本内容"}

【角色人设参考】
{chars_text if chars_text else "请从剧本中提取角色"}

【结构大纲参考】
{outline_text if outline_text else "请从剧本推断结构"}

任务：
1. 对6个维度分别打分（1-10分）
2. 逐集独立评分
3. 检查一致性问题
4. 输出Top 3改进建议（按优先级P0/P1/P2排序）
5. 按JSON格式输出完整质量报告
"""
        return prompt

    def validate_output(self, output: str) -> tuple[bool, List[str]]:
        errors = []
        # 尝试解析JSON
        json_match = re.search(r'\{[\s\S]*\}', output)
        if json_match:
            try:
                data = json.loads(json_match.group())
                # 检查必要字段
                if "overall_score" not in data:
                    errors.append("缺少overall_score")
                if "dimensions" not in data:
                    errors.append("缺少dimensions")
                if "top3_improvements" not in data:
                    errors.append("缺少改进建议")
            except json.JSONDecodeError:
                errors.append("JSON格式解析失败")
        else:
            # 非JSON格式也接受，但检查关键内容
            has_score = bool(re.search(r'[总评综合][分：:]\s*\d', output))
            has_dimension = any(kw in output for kw in ["剧情张力", "角色深度", "对白质量", "节奏"])
            if not has_score and not has_dimension:
                errors.append("未找到评分或维度分析")
        return len(errors) == 0, errors

    def parse_scores(self, output: str) -> Dict:
        """解析评分结果"""
        json_match = re.search(r'\{[\s\S]*\}', output)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        # 尝试从文本中提取分数
        scores = {}
        for dim_key, dim_info in DIMENSION_CRITERIA.items():
            match = re.search(rf'{dim_info["name"]}.*?(\d+(?:\.\d+)?)\s*/?\s*10', output)
            if match:
                scores[dim_key] = float(match.group(1))
        return {"dimensions": scores, "raw": output}


# 注册
from .base import ExpertRegistry
ExpertRegistry.register("§7", QualityAuditorExpert)
