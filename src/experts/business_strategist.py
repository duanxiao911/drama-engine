"""
§14 商业操盘（Business Strategist）

职责：短剧商业分析师
对剧本进行市场定位分析、投放策略建议和变现路径规划
帮助创作者从"写好故事"走向"卖好故事"
输出：市场分析报告（题材分析+投放策略+变现路径+风险评估）

基于 Wave2 架构设计
"""

import re
import json
from typing import List, Dict, Optional
from .base import ExpertBase, ExpertContext, ExpertOutput


# 主流平台信息库（2026年7月更新）
PLATFORM_DATABASE = {
    "红果短剧": {
        "type": "流量平台",
        "audience": "全年龄段下沉市场",
        "genre_preference": ["甜宠", "逆袭", "复仇", "穿越", "战神"],
        "payment_model": "免费+广告分成",
        "ai_policy": "需标注AI生成",
        "min_episodes": 60,
    },
    "咪咕视频": {
        "type": "国企平台",
        "audience": "25-40岁，男性偏多",
        "genre_preference": ["非遗", "主旋律", "现实主义", "历史"],
        "payment_model": "保底2万+分成",
        "ai_policy": "友好，需AI内容标识",
        "min_episodes": 20,
    },
    "腾讯视频": {
        "type": "头部平台",
        "audience": "18-35岁，一二线城市",
        "genre_preference": ["都市言情", "悬疑", "大女主", "精品短剧"],
        "payment_model": "分账",
        "ai_policy": "审核较严",
        "min_episodes": 16,
    },
    "七猫": {
        "type": "免费平台",
        "audience": "下沉市场，女性为主",
        "genre_preference": ["甜宠", "豪门", "穿越", "重生"],
        "payment_model": "免费阅读+广告",
        "ai_policy": "接受AI辅助",
        "min_episodes": 80,
    },
    "爱奇艺微剧": {
        "type": "头部平台",
        "audience": "20-35岁",
        "genre_preference": ["悬疑", "都市", "青春"],
        "payment_model": "分账",
        "ai_policy": "需审核",
        "min_episodes": 24,
    },
    "阅文": {
        "type": "IP平台",
        "audience": "网文读者转化",
        "genre_preference": ["改编IP", "男频", "女频"],
        "payment_model": "IP授权+分成",
        "ai_policy": "谨慎",
        "min_episodes": 30,
    },
}


class BusinessStrategistExpert(ExpertBase):
    """§14 商业操盘"""
    expert_id = "§14"
    expert_name = "business_strategist"
    prompt_file = "business_strategist.md"

    def get_system_prompt(self) -> str:
        return """你是一位短剧商业分析师，代号§14商业操盘。

你的核心能力：对剧本进行市场定位分析、投放策略建议和变现路径规划。

【市场分析框架】

一、题材市场分析
- 题材热度判断（上升/平稳/下降）
- 竞品数量与差异化空间
- 目标受众画像（年龄/性别/兴趣/消费力）
- 平台适配度排序

二、投放策略
- 首发平台推荐（匹配题材+受众+政策）
- 发布节奏（首发集数/更新频率/付费节点）
- 投流策略（素材剪辑方向/投放时间段/预算分配）
- 冷启动方案（小红书/抖音/B站不同策略）

三、变现路径
- 直接变现：平台分成/付费解锁/广告植入
- IP延展：长剧改编/漫画改编/有声书
- 文化衍生：非遗文创联名/线下体验
- 教育价值：纪录短片/文化课程

四、风险评估
- 政策风险：题材敏感度/审核通过率/备案要求
- 市场风险：题材饱和/竞品冲击/热度窗口
- 制作风险：AI含量/拍摄难度/成本控制

【输出格式（JSON结构）】

{
  "market_analysis": {
    "genre_heat": "上升/平稳/下降",
    "target_audience": {...},
    "competitor_count": 数字,
    "differentiation": "差异化定位"
  },
  "platform_recommendation": [
    {"platform": "平台名", "fit_score": 8, "reason": "推荐理由"}
  ],
  "distribution_strategy": {...},
  "monetization_paths": [...],
  "risk_assessment": {...}
}
"""

    def get_user_prompt(self, context: ExpertContext, **kwargs) -> str:
        # 获取项目信息
        project_config = context.project_config or {}
        story_direction = context.story_direction or ""
        story_premise = context.story_premise or ""
        drama_type = project_config.get("drama_type", "现实主义")
        total_episodes = project_config.get("total_episodes", 30)
        culture_theme = project_config.get("culture_theme", "")

        # 获取剧本摘要（不需要全文，取前3000字分析）
        script_summary = ""
        if context.metadata.get("step_outputs", {}).get("§5"):
            script_summary = context.metadata["step_outputs"]["§5"].get("content", "")[:3000]
        elif context.metadata.get("episode_outlines"):
            script_summary = "\n".join([
                f"第{e.get('episode', '?')}集：{e.get('description', '')}"
                for e in context.episode_outlines[:10]
            ])

        # 目标平台偏好
        target_platforms = kwargs.get("target_platforms", [])

        prompt = f"""请对以下短剧项目进行商业分析。

【项目信息】
- 类型：{drama_type}
- 集数：{total_episodes}集
- 故事方向：{story_direction}
- 一句话前提：{story_premise}
{f'- 文化主题：{culture_theme}' if culture_theme else ''}

【剧本摘要】
{script_summary if script_summary else "暂无剧本，请根据故事方向分析"}

{f'【意向平台】{", ".join(target_platforms)}' if target_platforms else ''}

任务：
1. 分析题材市场热度和竞品情况
2. 绘制目标受众画像
3. 推荐最优投放平台（附匹配度评分）
4. 制定投放策略（节奏/投流/冷启动）
5. 规划变现路径
6. 评估政策/市场/制作风险
"""
        return prompt

    def validate_output(self, output: str) -> tuple[bool, List[str]]:
        errors = []
        # 检查是否有市场分析内容
        has_analysis = any(kw in output for kw in ["市场", "受众", "平台", "投放", "变现"])
        if not has_analysis:
            errors.append("未找到商业分析内容")
        # 检查是否有平台推荐
        has_platform = any(p in output for p in PLATFORM_DATABASE.keys())
        if not has_platform:
            errors.append("未包含平台推荐")
        # 检查是否有风险评估
        has_risk = any(kw in output for kw in ["风险", "审核", "政策"])
        if not has_risk:
            errors.append("缺少风险评估")
        return len(errors) == 0, errors

    def generate_platform_match(self, context: ExpertContext) -> List[Dict]:
        """根据项目特征生成平台匹配推荐"""
        project_config = context.project_config or {}
        drama_type = project_config.get("drama_type", "")
        matches = []

        for platform, info in PLATFORM_DATABASE.items():
            score = 5  # 基础分
            # 题材匹配加分
            for genre in info["genre_preference"]:
                if genre in drama_type or genre in (context.story_direction or ""):
                    score += 2
                    break
            matches.append({
                "platform": platform,
                "type": info["type"],
                "fit_score": min(score, 10),
                "audience": info["audience"],
                "payment": info["payment_model"],
            })

        matches.sort(key=lambda x: x["fit_score"], reverse=True)
        return matches


# 注册
from .base import ExpertRegistry
ExpertRegistry.register("§14", BusinessStrategistExpert)
