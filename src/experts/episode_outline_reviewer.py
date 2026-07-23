"""
集纲审核专家（Episode Outline Reviewer）
基于37项「爆款漏斗」标准，逐项审查大纲和集纲
"""

from .base import BaseExpert
from typing import Dict, Any, List


class EpisodeOutlineReviewer(BaseExpert):
    """集纲审核专家：用爆款漏斗37项标准审查大纲/集纲"""
    
    def __init__(self):
        super().__init__(
            name="集纲审核",
            expert_id="episode_outline_reviewer",
            description="基于37项爆款漏斗标准，逐项审查大纲和集纲，标记✅/⚠️/❌，给出精确到集数的修改方案"
        )
    
    def build_prompt(self, context: Dict[str, Any]) -> str:
        """
        构建集纲审核专家的prompt
        
        Args:
            context: 包含以下字段：
                - project: 项目信息
                - episode_outlines: 集纲列表
                - payment_nodes: 付费节点列表
                - target_platform: 目标平台
        
        Returns:
            完整的prompt字符串
        """
        project = context.get("project", {})
        episode_outlines = context.get("episode_outlines", [])
        payment_nodes = context.get("payment_nodes", [10, 20])
        target_platform = context.get("target_platform", "抖音")
        
        # 构建集纲描述
        episode_descriptions = []
        for ep in episode_outlines:
            desc = f"""
第{ep['episode']}集：
- 概要：{ep.get('summary', '未提供')}
- 关键事件：{', '.join(ep.get('key_events', []))}
- 结尾钩子：{ep.get('hook', '未提供')}
- 钩子类型：{ep.get('cliffhanger_type', '未提供')}
"""
            episode_descriptions.append(desc)
        
        prompt = f"""你是一位资深短剧编剧和投流分析师，拥有10年以上短剧行业经验。
请使用「爆款漏斗」五模块37项审查标准，对以下短剧大纲和集纲进行逐项审查。

【项目信息】
项目名称：{project.get('name', '未命名')}
题材类型：{project.get('genre', '未指定')}
目标集数：{project.get('episode_count', '未指定')}集
故事梗概：
{project.get('synopsis', '未提供')}

目标平台：{target_platform}
付费节点：第{', '.join(map(str, payment_nodes))}集

【集纲内容】
{''.join(episode_descriptions)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【审查标准】

模块一：生死线与情绪核（前5集强检验，7项）
1.1 明暗身份差距：主角明线身份与暗线身份的差距是否拉到极致？
1.2 暗线线索前置：暗线身份的线索是否在前3集就已埋下并让观众感知？
1.3 核心目标窒息感：主角的核心目标是否在第1集就直接砸在观众脸上？
1.4 反击底层逻辑：主角面临绝境时，是否具备独立反击的底层逻辑？
1.5 无脑圣母禁令：是否存在主角无合理逻辑支撑反复原谅反派的情况？
1.6 反派动机合理性：反派的"坏"是否基于具体的利益动机？
1.7 身份切换触发机制：明暗身份的切换触发机制是否清晰？

模块二：钩子与付费卡点（8项）
2.1 卡点状态多样性：每集结尾是否精准停在致命危机/身份反转/情绪撕裂/重大悬念四种状态之一？
2.2 卡点方式轮换：整部剧的卡点方式是否多样轮换？
2.3 巧合伪卡点控制："刚好没听到/刚好错过/刚好误会"类巧合是否≤2次？
2.4 钩子揭晓时效：钩子的答案是否在下一集前30秒内揭晓？
2.5 情绪回报充分性：钩子揭晓时是否给出了足够的情绪回报？
2.6 付费节点格局变化：付费卡点集数是否迎来身份/权力格局的根本性改变？
2.7 付费后首集爽度：付费解锁后的下一集是否立刻给到极强的爽点回报？
2.8 付费节点数量与递进：全剧是否设置≥2个付费节点？爆发力度是否逐级递进？

模块三：节奏与废戏筛查（8项）
3.1 连续憋屈控制：是否存在连续3集以上纯被虐、纯憋屈的剧情？
3.2 反派嚣张极致度：打脸反扑前，反派的嚣张气焰是否压抑到了极致？
3.3 微小希望信号：憋屈段落中是否有微小的希望信号在牵引观众？
3.4 纯交代背景废戏：是否存在任何一集纯粹为了"交代背景"而没有推进核心冲突？
3.5 纯日常无冲突废戏：是否存在任何一集纯粹是"日常恋爱"而没有戏剧冲突？
3.6 每集信息增量：每一集是否至少传递了一个新的关键信息？
3.7 3集冲突起伏周期：每3集是否完成一次微小的冲突起伏？
3.8 支线必要性：支线剧情是否能用一句话说清"它对主线有什么影响"？

模块四：逻辑硬伤与视觉可行性（8项）
4.1 配角行为逻辑：配角行为是否仅仅为了强行推进剧情而违背其身份设定？
4.2 信息枢纽型配角：是否存在该知道的事不知道、不该知道的事全知道的逻辑崩塌？
4.3 暗线身份反击逻辑：主角动用暗线身份反击时，逻辑链条是否能闭合？
4.4 社会后果交代：降维打击后的社会后果/连锁反应是否做了最低限度的交代？
4.5 内心戏可视化：集纲中是否充斥着无法拍摄的内心戏描述？
4.6 情绪转折外部化：关键情绪转折是否都有对应的外部冲突动作？
4.7 AI/仿生人技术适配：若涉及AI合成，是否规避微表情技术瓶颈？
4.8 预算可行性：场景/道具/群演规模是否在短剧预算范围内？

模块五：语境与爆款元素对齐（6项）
"""
        
        # 根据目标平台选择5A或5B
        if target_platform in ["ReelShort", "DramaBox", "海外"]:
            prompt += """5.4 等级压制核心冲突：狼人/吸血鬼题材的等级压制是否作为核心冲突推进？
5.5 美式救赎宿命感：亿万富翁题材的虐恋是否带有美式"救赎与征服"的宿命感？
5.6 女性独立决策：女性角色是否具备基本的独立决策能力？
"""
        else:
            prompt += """5.1 道德批判与阶层对立：是否精准植入了强道德批判 + 强阶层对立元素？
5.2 爆款母题植入：是否包含至少一类爆款母题（战神归来/真假千金/隐形首富赘婿逆袭/手撕渣男恶婆婆/扮猪吃虎）？
5.3 道德审判闭环：结局是否包含了道德审判/因果报应的闭环？
"""
        
        prompt += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【审查要求】

1. 每个模块逐条标记 ✅/⚠️/❌
2. ⚠️和❌项必须给出具体的定位（第几集、哪个场景）和修改方向
3. 模块一出现❌直接报告"人设/逻辑需重构"，不必继续后续模块
4. 所有建议必须可执行——说"加冲突"不够，要说"在第5集结尾增加主角亮出信物的反转"
5. 审查完成后给出总评：这个剧本离"可以投流"还有多远？

【输出格式】

第一部分：审查总览
- 🔴 致命风险：X项
- 🟡 预警项：Y项
- 🟢 通过项：Z项
- 综合评级：S/A/B/C/D

第二部分：逐模块审查结果
对每个模块，列出所有检查项的标记、定位、问题和建议

第三部分：修改优先级清单
- P0 - 必须立即修改（否则无法过审）
- P1 - 强烈建议修改（影响商业表现）
- P2 - 建议优化（提升留存率）

第四部分：总评与建议
- 200-300字总结优缺点
- 下一步行动建议

现在请开始审查。
"""
        
        return prompt
    
    def validate_output(self, output: str) -> bool:
        """
        验证输出是否包含必要的审查内容
        
        Args:
            output: LLM输出的审查报告
        
        Returns:
            是否通过验证
        """
        # 检查是否包含关键内容
        required_keywords = [
            "模块一", "模块二", "审查总览", "修改优先级", "总评"
        ]
        
        missing = [kw for kw in required_keywords if kw not in output]
        
        if missing:
            self.logger.warning(f"输出缺少关键词: {missing}")
            return False
        
        return True
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行集纲审核
        
        Args:
            context: 上下文信息
        
        Returns:
            审核结果
        """
        # 构建prompt
        prompt = self.build_prompt(context)
        
        # 调用LLM API（由父类提供）
        response = self.call_llm(prompt)
        
        # 验证输出
        is_valid = self.validate_output(response)
        
        return {
            "expert_id": self.expert_id,
            "status": "success" if is_valid else "warning",
            "output": response,
            "validation": {
                "is_valid": is_valid,
                "contains_required_sections": is_valid
            }
        }
