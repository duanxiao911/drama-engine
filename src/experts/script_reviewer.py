"""
剧本审核专家（Script Reviewer）
12维度量化评估体系，诊断剧本商业潜力
"""

from .base import BaseExpert
from typing import Dict, Any, List


class ScriptReviewer(BaseExpert):
    """剧本审核专家：12维度量化评估，输出商业诊断报告"""
    
    def __init__(self):
        super().__init__(
            name="剧本审核",
            expert_id="script_reviewer",
            description="12维度量化评估体系，诊断剧本商业潜力，输出可执行的修改方案"
        )
    
    def build_prompt(self, context: Dict[str, Any]) -> str:
        """
        构建剧本审核专家的prompt
        
        Args:
            context: 包含以下字段：
                - project: 项目信息
                - script_content: 剧本正文
                - target_platform: 目标平台
        
        Returns:
            完整的prompt字符串
        """
        project = context.get("project", {})
        script_content = context.get("script_content", "未提供")
        target_platform = context.get("target_platform", "抖音")
        
        # 截取剧本内容（避免过长）
        if len(script_content) > 15000:
            script_content = script_content[:15000] + "\n\n...（剧本内容过长，已截取前15000字）..."
        
        prompt = f"""你是一位资深短剧编剧和制片人，拥有10年以上短剧行业经验。
请使用12维度量化评估体系，对以下短剧剧本进行全面商业诊断。

【项目信息】
项目名称：{project.get('name', '未命名')}
题材类型：{project.get('genre', '未指定')}
核心主题：{project.get('theme', '未指定')}
目标集数：{project.get('episode_count', '未指定')}集
目标平台：{target_platform}

故事梗概：
{project.get('synopsis', '未提供')}

人物小传：
{project.get('character_profiles', '未提供')}

【剧本正文】
{script_content}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【评估框架：12维度量化体系】

一、市场共鸣与竞争定位
1.1 目标受众精准度（90-100/70-89/50-69/<50）
- 是否精准锁定核心受众群体？
- 主角处境是否让目标受众产生代入感？
- 情感代偿机制是否清晰？

1.2 原创性与差异化（90-100/70-89/50-69/<50）
- 在同类题材中是否有独特卖点？
- 是否摆脱同质化套路？
- 是否融合社会议题提升质感？

1.3 热播契合度（90-100/70-89/50-69/<50）
- 是否契合当前短剧市场热门趋势？
- 是否与近期爆款有可比性但具备差异化？
- 是否具备话题讨论度？

二、叙事与剧本基因
2.1 叙事逻辑严密性（90-100/70-89/50-69/<50）
- 因果链条是否严密可信？
- 人物心理转变是否合理？
- 是否存在人物设定前后矛盾？
- 专业常识是否无硬伤？

2.2 钩子强度（90-100/70-89/50-69/<50）
- 前30秒是否有极具冲击力的钩子？
- 第一集结尾是否有强烈悬念？
- 前三集是否完成情绪闭环？

2.3 爽点设计（90-100/70-89/50-69/<50）
- 爽点是否多维度？
- 先抑后扬配比是否完美？
- 爽感颗粒度是否细腻？

2.4 节奏与结构（90-100/70-89/50-69/<50）
- 黄金四要素是否在前三集快速完成？
- 单集是否包含完整对抗或反转？
- 全剧主线期待值是否呈上扬曲线？

2.5 主线连贯性（90-100/70-89/50-69/<50）
- 核心矛盾是否聚焦？
- 冲突升级链条是否清晰？
- 小悬念是否集集相扣？

2.6 人物塑造（90-100/70-89/50-69/<50）
- 主角性格弧光是否清晰？
- 配角是否有独立人格？
- 反派是否过度脸谱化？

2.7 对白质量（90-100/70-89/50-69/<50）
- 台词是否短促有力？
- 金句密度是否足够？
- 人物语调是否鲜明？

2.8 悬念有效性（90-100/70-89/50-69/<50）
- 埋钩与揭钩设计是否精妙？
- 跨集大钩是否精准落在付费卡点？
- 集内小悬念密度是否足够？

三、商业化潜力
3.1 用户粘性（90-100/70-89/50-69/<50）
- 是否直击社会痛点？
- 多重代偿心理是否满足？
- 付费冲动是否强烈？

3.2 传播潜力（90-100/70-89/50-69/<50）
- 是否涉及社会性热点议题？
- 是否有极具爽感的名场面？
- 对白二创潜力是否大？

四、合规性评估
4.1 内容合规性（90-100/70-89/50-69/<50）
- 是否远离色情、暴力、血腥等红线？
- 复仇手段是否合法化？
- 家庭纠纷是否克制展现？

4.2 价值观导向（90-100/70-89/50-69/<50）
- 是否弘扬正向价值观？
- 是否传递善有善报、恶有恶报的正向逻辑？
- 家庭与情感价值观是否健康？

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【输出要求】

第一部分：评估总览
- 总体潜力评分：{总分}/100（{评级：S/A+/A/B/C/D}）
- 各维度评分汇总表

第二部分：各维度评分明细
对每个维度，列出：
- 评分和等级
- 亮点（1-3点）
- 可打磨点（1-3点，附具体修改方案）

第三部分：综合可操作建议
- P0 - 必须立即修改（否则无法过审或逻辑崩塌）
- P1 - 强烈建议修改（影响商业表现）
- P2 - 建议优化（提升品质）

第四部分：核心结论
- 300-500字总结剧本优缺点、市场潜力
- 一句话介绍（概括剧本核心卖点）
- 下一步行动建议

现在请开始评估。
"""
        
        return prompt
    
    def validate_output(self, output: str) -> bool:
        """
        验证输出是否包含必要的评估内容
        
        Args:
            output: LLM输出的评估报告
        
        Returns:
            是否通过验证
        """
        # 检查是否包含关键内容
        required_keywords = [
            "评估总览", "总体潜力评分", "维度", "亮点", "可打磨点", 
            "综合可操作建议", "核心结论"
        ]
        
        missing = [kw for kw in required_keywords if kw not in output]
        
        if missing:
            self.logger.warning(f"输出缺少关键词: {missing}")
            return False
        
        return True
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行剧本审核
        
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
