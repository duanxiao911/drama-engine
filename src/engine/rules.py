"""
铁律系统与规则冲突裁决

基于《精品短剧创作引擎_通用版.md》§2（核心铁律）实现：
- 规则冲突裁决四层优先级
- 六大审核红线与合规替代
- 叙事因果铁律
- 纯AI生成检测红线
- 素材铁律与禁止类素材清单
"""

from enum import Enum
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field


class RulePriority(Enum):
    """规则优先级四层（由高到低）"""
    L1_PLATFORM_COMPLIANCE = 1  # 平台合规红线（绝对不可逾越）
    L2_MATERIAL_HARD = 2        # 素材硬约束（剧情事实、人物关系、关键事件）
    L3_METHODOLOGY = 3          # 创作方法论（结构、钩子、张力节奏、反转因果）
    L4_STYLE_PREFERENCE = 4     # 风格偏好（对白语感、叙事节奏、留白程度）


@dataclass
class RedLineItem:
    """审核红线条目"""
    category: str
    prohibited: str
    alternative: str
    severity: str = "critical"  # critical / high / medium

    def to_dict(self) -> Dict:
        return {
            "category": self.category,
            "prohibited": self.prohibited,
            "alternative": self.alternative,
            "severity": self.severity,
        }


class RedLineCategory:
    """六大审核红线"""
    SUPERNATURAL_GODHAND = "超自然金手指"
    VIGILANTE_VIOLENCE = "暴力私刑"
    DANGEROUS_PROP_BLOOD = "危险道具+血腥"
    PERSONALITY_HUMILIATION_BULLYING = "人格羞辱+霸凌"
    OBSCENE_BORDERLINE = "低俗擦边"
    FEUDAL_SUPERSTITION = "封建迷信"


class ProhibitedTopics:
    """题材禁区（碰即拒）"""
    EARLY_LOVE = "早恋"
    SCHOOL_BULLYING_POSITIVE = "校园暴力正面展示"
    HISTORICAL_EVENT_MISREPRESENTATION = "历史事件误写"
    GLORIFYING_AFFAIR_THIRD_PARTY = "美化出轨/小三"
    PROMOTING_MONEY_WORSHIP = "宣扬拜金"
    FOREIGN_SNOBBISH = "境外猎奇"
    RELIGIOUS_SENSITIVITY = "宗教敏感"
    NORTHERN_MYANMAR = "缅北题材"


@dataclass
class RuleConflict:
    """规则冲突实例"""
    rule_a: str
    rule_b: str
    priority_a: RulePriority
    priority_b: RulePriority
    context: str = ""
    resolution: Optional[str] = None

    def resolve(self) -> str:
        """根据四层优先级裁决冲突"""
        if self.priority_a.value < self.priority_b.value:
            winner = self.rule_a
        elif self.priority_b.value < self.priority_a.value:
            winner = self.rule_b
        else:
            winner = "平级，建议依据具体效果取舍"
        self.resolution = winner
        return winner


class RedLineSystem:
    """红线系统：扫描与合规替代"""
    def __init__(self):
        self.red_lines = self._init_red_lines()
        self.prohibited_topics = [getattr(ProhibitedTopics, attr) for attr in dir(ProhibitedTopics) if not attr.startswith("_")]

    def _init_red_lines(self) -> Dict[str, RedLineItem]:
        """初始化六大审核红线（依据§2.1）"""
        return {
            RedLineCategory.SUPERNATURAL_GODHAND: RedLineItem(
                category=RedLineCategory.SUPERNATURAL_GODHAND,
                prohibited="异能、修仙、血脉觉醒、意外变异、无理由开挂",
                alternative="退伍军人、持证运动员、专业行业技能、极限人体反应"
            ),
            RedLineCategory.VIGILANTE_VIOLENCE: RedLineItem(
                category=RedLineCategory.VIGILANTE_VIOLENCE,
                prohibited="主角以暴制暴、个人复仇暴力",
                alternative="主角仅防御/躲闪/格挡，反派最终由公安/法律制裁"
            ),
            RedLineCategory.DANGEROUS_PROP_BLOOD: RedLineItem(
                category=RedLineCategory.DANGEROUS_PROP_BLOOD,
                prohibited="匕首/尖刀/弹簧刀、毒针迷药、出血特写/伤口渗血/嘴角流血",
                alternative="木棍/塑胶摆件轻微磕碰，全程无伤口无血迹"
            ),
            RedLineCategory.PERSONALITY_HUMILIATION_BULLYING: RedLineItem(
                category=RedLineCategory.PERSONALITY_HUMILIATION_BULLYING,
                prohibited="扔钱踩人、逼迫下跪、掌掴羞辱、校园霸凌、职场欺压、拜金炫富、贫富对立",
                alternative="用侧面叙事：事后伤痕、旁观者视角、内心独白、他人转述"
            ),
            RedLineCategory.OBSCENE_BORDERLINE: RedLineItem(
                category=RedLineCategory.OBSCENE_BORDERLINE,
                prohibited="露骨画面、暧昧姿势、低俗封面",
                alternative="健康正向的情感表达"
            ),
            RedLineCategory.FEUDAL_SUPERSTITION: RedLineItem(
                category=RedLineCategory.FEUDAL_SUPERSTITION,
                prohibited="宿命诅咒、宗教妖魔、算命风水",
                alternative="用心理暗示、巧合、人性逻辑替代"
            ),
        }

    def scan(self, text: str) -> List[Dict]:
        """扫描文本中的潜在红线触发点（仅返回警示与合规替代建议）"""
        warnings = []
        for category, item in self.red_lines.items():
            if any(keyword in text for keyword in item.prohibited.split("、")[:3]):  # 简化关键词检出
                warnings.append({
                    "category": category,
                    "reason": f"疑似包含“{item.category}”相关内容",
                    "alternative": item.alternative,
                    "severity": item.severity
                })
        for topic in self.prohibited_topics:
            if topic in text:
                warnings.append({
                    "category": "题材禁区",
                    "reason": f"触及题材禁区：{topic}",
                    "alternative": "避免该题材，或改为侧面/象征化表达",
                    "severity": "critical"
                })
        return warnings


class NarrativeCausality:
    """叙事因果铁律（依据§2.3）"""
    PRINCIPLES = [
        "因果链不可断：每个转折必须前置铺垫，不能凭空发生",
        "人设驱动而非剧情驱动：角色选择必须能追溯明确动机，不能因为“剧情需要”",
        "悲剧的真实感：崩溃是多个伤口叠加+时间拉长，每个选择在当下是“只能这样”",
    ]

    @staticmethod
    def check(scene_text: str) -> Dict[str, List[str]]:
        """检查一场戏是否满足因果铁律（返回检查点与提示）"""
        issues = []
        if "突然" in scene_text and "因为" not in scene_text and "所以" not in scene_text:
            issues.append("疑似出现无铺垫的突然转折，建议补充前置因果")
        if "剧情需要" in scene_text:
            issues.append("显式使用“剧情需要”可能驱动角色，建议改为人设动机")
        if "主角死了" in scene_text and "内心撕裂" not in scene_text and "挣扎" not in scene_text:
            issues.append("结局缺乏真实感的挣扎过程，建议补充多层压力与内心撕裂")
        return {"checks": NarrativeCausality.PRINCIPLES, "issues": issues}


class AIDetectionRedLine:
    """纯AI生成检测红线（依据§2.4）"""
    INDICATORS = [
        "空洞抒情：无具体场景与细节堆砌",
        "逻辑跳跃：转折缺乏前置因果",
        "重复句式：对白/独白存在明显重复模式",
    ]

    @staticmethod
    def check(text: str) -> Dict[str, float]:
        """简单检出“AI味”指标（返回得分与问题清单）"""
        issues = []
        score = 1.0
        if "心里很难过" in text and "动作" not in text:
            issues.append("抽象情绪描写，建议具象替换")
            score -= 0.2
        if "突然" in text:
            issues.append("出现“突然”，检查是否有前置铺垫")
            score -= 0.1
        repeated = [s for s in text.split("。") if s.strip()][:10]
        if len(set(repeated)) < len(repeated) * 0.7:
            issues.append("疑似重复句式，检查对白/独白多样性")
            score -= 0.1
        return {"score": max(0.0, score), "issues": issues}


class MaterialIronRules:
    """素材铁律（依据§2.5）"""
    SOURCE_PRIORITY_LEVELS = [
        "1. 真实经历（100%真实，创作自由度最低）",
        "2. 新闻报道（90%真实，事实不能改，细节可调整）",
        "3. 田野调查（80%真实，氛围真实，具体事件可虚构）",
        "4. 文献研究（70%真实，基于事实二次创作）",
        "5. AI生成（不可控，创作自由度最高，但需验证）"
    ]

    USAGE_PRINCIPLES = [
        "原则一：不能照搬真实事件，需改头换面",
        "原则二：核心细节必须有出处（空间、行为、情感细节）",
        "原则三：情感记忆比事实更重要（抽象情绪转化为具体场景）"
    ]

    FORBIDDEN_MATERIAL_TYPES = [
        "无来源的社会新闻",
        "AI编造的“真实案例”",
        "道听途说的行业内幕",
        "网络段子和都市传说",
    ]

    @staticmethod
    def validate_material_source(source_desc: str) -> Tuple[bool, str]:
        """验证素材来源是否符合优先级与禁止清单"""
        desc = source_desc.lower()
        if any(banned in desc for banned in ["道听途说", "网络段子", "ai编造", "无来源"]):
            return False, "素材触及禁止清单"
        if any(p in desc for p in ["真实经历", "新闻报道", "田野调查", "文献研究"]):
            return True, "素材来源可信度高"
        if "ai生成" in desc:
            return True, "AI生成素材需经田野调查级别验证"
        return True, "素材来源未明确，建议补充出处"


class RulesEngine:
    """规则引擎总入口：裁决冲突、红线扫描、因果检查、素材验证"""
    def __init__(self):
        self.red_line_system = RedLineSystem()
        self.narrative_causality = NarrativeCausality()
        self.ai_detection = AIDetectionRedLine()
        self.material_rules = MaterialIronRules()

    def resolve_conflict(self, conflict: RuleConflict) -> str:
        """裁决规则冲突"""
        return conflict.resolve()

    def scan_red_lines(self, text: str) -> List[Dict]:
        """红线扫描"""
        return self.red_line_system.scan(text)

    def check_causality(self, scene_text: str) -> Dict:
        """检查叙事因果"""
        return self.narrative_causality.check(scene_text)

    def check_ai_detection(self, text: str) -> Dict:
        """AI生成检测红线检查"""
        return self.ai_detection.check(text)

    def validate_material(self, source_desc: str) -> Tuple[bool, str]:
        """素材来源验证"""
        return self.material_rules.validate_material_source(source_desc)

    def export_red_lines(self) -> Dict[str, RedLineItem]:
        """导出红线条目供外部使用"""
        return self.red_line_system.red_lines


# 示例用法
if __name__ == "__main__":
    engine = RulesEngine()
    # 红线扫描示例
    warnings = engine.scan_red_lines("主角突然觉醒血脉之力，用匕首刺向敌人")
    print("红线扫描结果:", warnings)
    # 冲突裁决示例
    conflict = RuleConflict(
        rule_a="素材事实：主角服药自杀",
        rule_b="合规红线：禁止自杀正面展示",
        priority_a=RulePriority.L2_MATERIAL_HARD,
        priority_b=RulePriority.L1_PLATFORM_COMPLIANCE,
        context="素材写了服药自杀的事实，但合规红线不能正面展示",
    )
    resolution = engine.resolve_conflict(conflict)
    print("冲突裁决结果:", resolution)
    # 因果检查示例
    causality_check = engine.check_causality("主角突然决定离开家乡")
    print("因果检查结果:", causality_check)
    # AI检测示例
    ai_check = engine.check_ai_detection("他心里很难过，突然觉得世界崩塌")
    print("AI检测得分与问题:", ai_check)
    # 素材验证示例
    valid, msg = engine.validate_material("来自真实经历改编")
    print("素材验证:", valid, msg)