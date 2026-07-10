"""
质量评分系统

基于《精品短剧创作引擎_通用版.md》§6（质量自查清单）实现：
- 六大评分维度（人物深度、对白质量、叙事结构、视觉方案、合规性、文学性）
- 0-10分制评分标准与扣分规则
- 输出质量报告

注：视觉方案评分由§13视觉导演补充，本模块提供框架接口。
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum


class ScoreLevel(Enum):
    """评分等级"""
    EXCELLENT = "优秀"
    GOOD = "良好"
    FAIR = "合格"
    POOR = "不合格"
    CRITICAL = "严重问题"


@dataclass
class DimensionScore:
    """单一维度评分"""
    dimension: str
    score: float  # 0-10
    max_score: float = 10.0
    level: ScoreLevel = ScoreLevel.FAIR
    reasons: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "dimension": self.dimension,
            "score": self.score,
            "max_score": self.max_score,
            "level": self.level.value,
            "reasons": self.reasons,
            "suggestions": self.suggestions,
        }


@dataclass
class QualityReport:
    """质量报告"""
    total_score: float = 0.0
    overall_level: ScoreLevel = ScoreLevel.FAIR
    dimensions: List[DimensionScore] = field(default_factory=list)
    critical_issues: List[str] = field(default_factory=list)
    summary: str = ""
    passed: bool = False

    def to_dict(self) -> Dict:
        return {
            "total_score": self.total_score,
            "overall_level": self.overall_level.value,
            "dimensions": [d.to_dict() for d in self.dimensions],
            "critical_issues": self.critical_issues,
            "summary": self.summary,
            "passed": self.passed,
        }


class CharacterDepthScorer:
    """人物深度评分（对应§5.1②三层四维度铸造法 + §6人设层自查）"""
    DIMENSION = "人物深度"

    # 扣分规则（对应§6人设层）
    DEDUCTION_RULES = [
        ("角色行为前后矛盾", 2.0),
        ("角色选择无法追溯明确动机", 2.0),
        ("角色仅被动受苦，无主动挣扎", 1.5),
        ("弧光通过台词而非选择完成", 1.5),
        ("缺少欲望（want/need）", 2.0),
        ("缺少恐惧维度", 1.5),
        ("人物标签化无灵魂", 2.0),
    ]

    @classmethod
    def score(cls, text: str, character_info: Optional[Dict] = None) -> DimensionScore:
        """评分人物深度"""
        score_val = 10.0
        reasons = []
        suggestions = []

        # 基础文本分析（简化版）
        if "突然" in text and "因为" not in text:
            score_val -= 1.0
            suggestions.append("出现无铺垫的突然转折，需检查角色动机")

        # 若提供character_info，进行更精确的评分
        if character_info:
            if "弧光" not in character_info:
                score_val -= 1.5
                suggestions.append("缺少角色弧光描述")
            if "want" not in character_info and "need" not in character_info:
                score_val -= 1.0
                suggestions.append("缺少欲望want/need定义")
            if "恐惧" not in character_info:
                score_val -= 0.5
                suggestions.append("缺少恐惧维度")

        level = cls._score_to_level(score_val)
        if level in [ScoreLevel.POOR, ScoreLevel.CRITICAL]:
            reasons.append(f"人物深度得分{signal}: {score_val}")
        return DimensionScore(
            dimension=cls.DIMENSION,
            score=max(0.0, score_val),
            level=level,
            reasons=reasons,
            suggestions=suggestions,
        )

    @staticmethod
    def _score_to_level(score: float) -> ScoreLevel:
        if score >= 9.0:
            return ScoreLevel.EXCELLENT
        elif score >= 7.0:
            return ScoreLevel.GOOD
        elif score >= 5.0:
            return ScoreLevel.FAIR
        elif score >= 3.0:
            return ScoreLevel.POOR
        else:
            return ScoreLevel.CRITICAL


class DialogueQualityScorer:
    """对白质量评分（对应§4对白系统 + §6对白层自查）"""
    DIMENSION = "对白质量"

    DEDUCTION_RULES = [
        ("说明性对白（作者嘴替）", 2.0),
        ("一致性对白（太和谐无冲突）", 1.5),
        ("风格统一（所有人说话一个样）", 1.5),
        ("无潜文本（心里想啥嘴上说啥）", 2.0),
        ("文艺腔泛滥", 1.5),
        ("不符合人物身份背景", 2.0),
    ]

    @classmethod
    def score(cls, text: str) -> DimensionScore:
        """评分对白质量"""
        score_val = 10.0
        reasons = []
        suggestions = []

        # AI味检测
        if "心里很难过" in text and "动作" not in text:
            score_val -= 1.0
            suggestions.append("抽象情绪描写，建议用△动作/微表情替代")

        if "突然" in text:
            score_val -= 0.5
            suggestions.append("对白中出现“突然”，检查是否为无铺垫转折")

        # 对白六宗罪检测
        if "大家都知道" in text:
            score_val -= 1.5
            suggestions.append("检测到说明性对白“大家都知道”，违反六宗罪第1条")

        if "你说得对" in text or "我也这么想的" in text:
            score_val -= 1.0
            suggestions.append("检测到一致性/太和谐对白，缺乏冲突")

        # 长度检查（精品短剧单句台词不宜过长）
        lines = [l.strip() for l in text.split("\n") if ":" in l]
        long_lines = [l for l in lines if len(l) > 50]
        if long_lines:
            score_val -= 0.5
            suggestions.append(f"发现{len(long_lines)}处过长的台词，建议遵循五字诀“短”")

        level = cls._score_to_level(score_val)
        return DimensionScore(
            dimension=cls.DIMENSION,
            score=max(0.0, score_val),
            level=level,
            reasons=reasons,
            suggestions=suggestions,
        )

    @staticmethod
    def _score_to_level(score: float) -> ScoreLevel:
        if score >= 9.0:
            return ScoreLevel.EXCELLENT
        elif score >= 7.0:
            return ScoreLevel.GOOD
        elif score >= 5.0:
            return ScoreLevel.FAIR
        elif score >= 3.0:
            return ScoreLevel.POOR
        else:
            return ScoreLevel.CRITICAL


class NarrativeStructureScorer:
    """叙事结构评分（对应§3爆款结构模板 + §6节奏层自查）"""
    DIMENSION = "叙事结构"

    # 核心检查点（对应§3.1单集节奏公式）
    STRUCTURE_CHECKS = [
        "前3秒是否甩出最强矛盾",
        "30秒处是否出现转折/新信息",
        "本集是否至少闭合了一个因果链",
        "本集是否有追更钩子",
        "困境是否比上集更深一层",
        "是否至少维持了1条信息差",
        "是否有对照组/反差",
    ]

    @classmethod
    def score(cls, text: str, episode_num: int = 1, previous_episode: Optional[str] = None) -> DimensionScore:
        """评分叙事结构"""
        score_val = 10.0
        reasons = []
        suggestions = []

        # 前3秒矛盾检测
        first_lines = "\n".join(text.split("\n")[:5])
        if "冲突" not in first_lines and "矛盾" not in first_lines and episode_num == 1:
            score_val -= 1.5
            suggestions.append("第1集前3秒未甩出最强矛盾，需直入核心冲突")

        # 钩子检测（结尾是否有钩子）
        lines = text.split("\n")
        last_meaningful = [l for l in lines if l.strip() and not l.strip().startswith("第")][-3:]
        if last_meaningful:
            last_text = "".join(last_meaningful)
            if "?" not in last_text and "！" not in last_text and "。" == last_text[-1]:
                score_val -= 1.0
                suggestions.append("结尾缺乏追更钩子，建议在情绪最烈处切断")

        # 因果链检测
        if "因为" not in text and "所以" not in text and "导致" not in text:
            score_val -= 1.0
            suggestions.append("文本缺乏因果链信号词，建议补充“因为…所以…”结构")

        level = cls._score_to_level(score_val)
        return DimensionScore(
            dimension=cls.DIMENSION,
            score=max(0.0, score_val),
            level=level,
            reasons=reasons,
            suggestions=suggestions,
        )

    @staticmethod
    def _score_to_level(score: float) -> ScoreLevel:
        if score >= 9.0:
            return ScoreLevel.EXCELLENT
        elif score >= 7.0:
            return ScoreLevel.GOOD
        elif score >= 5.0:
            return ScoreLevel.FAIR
        elif score >= 3.0:
            return ScoreLevel.POOR
        else:
            return ScoreLevel.CRITICAL


class VisualSchemeScorer:
    """视觉方案评分（对应§13视觉导演模块，本框架提供接口）"""
    DIMENSION = "视觉方案"

    @classmethod
    def score(cls, text: str) -> DimensionScore:
        """评分视觉方案（本框架为简化实现，完整评分由§13视觉导演提供）"""
        score_val = 10.0
        suggestions = []

        # 基础检查：是否包含视觉描写信号词
        visual_keywords = ["光影", "镜头", "特写", "全景", "近景", "远景", "明", "暗", "色调", "构图"]
        has_visual = any(kw in text for kw in visual_keywords)

        if not has_visual:
            score_val -= 2.0
            suggestions.append("文本缺乏视觉方案元素（光影/镜头/色调），建议补充")

        level = cls._score_to_level(score_val)
        return DimensionScore(
            dimension=cls.DIMENSION,
            score=max(0.0, score_val),
            level=level,
            suggestions=suggestions,
        )

    @staticmethod
    def _score_to_level(score: float) -> ScoreLevel:
        if score >= 9.0:
            return ScoreLevel.EXCELLENT
        elif score >= 7.0:
            return ScoreLevel.GOOD
        elif score >= 5.0:
            return ScoreLevel.FAIR
        elif score >= 3.0:
            return ScoreLevel.POOR
        else:
            return ScoreLevel.CRITICAL


class ComplianceScorer:
    """合规性评分（对应§2六大审核红线 + §6合规层自查）"""
    DIMENSION = "合规性"

    RED_LINE_KEYWORDS = {
        "超自然金手指": ["觉醒", "异能", "修仙", "金手指"],
        "暴力私刑": ["以暴制暴", "复仇", "私刑"],
        "危险道具": ["匕首", "弹簧刀", "毒针", "迷药"],
        "人格羞辱": ["掌掴", "下跪", "踩人"],
        "低俗擦边": ["露骨", "暧昧姿势"],
        "封建迷信": ["算命", "风水", "诅咒"],
    }

    @classmethod
    def score(cls, text: str) -> DimensionScore:
        """评分合规性"""
        score_val = 10.0
        reasons = []
        suggestions = []
        critical_found = []

        for category, keywords in cls.RED_LINE_KEYWORDS.items():
            for kw in keywords:
                if kw in text:
                    score_val -= 1.5
                    reasons.append(f"疑似触及{category}：{kw}")
                    suggestions.append(f"建议使用合规替代方案处理{category}")
                    critical_found.append(category)
                    break

        level = cls._score_to_level(score_val)
        if level in [ScoreLevel.POOR, ScoreLevel.CRITICAL]:
            critical_issues = [f"合规性问题[{c}]" for c in critical_found]
        else:
            critical_issues = []

        return DimensionScore(
            dimension=cls.DIMENSION,
            score=max(0.0, score_val),
            level=level,
            reasons=reasons,
            suggestions=suggestions,
        )

    @staticmethod
    def _score_to_level(score: float) -> ScoreLevel:
        if score >= 9.0:
            return ScoreLevel.EXCELLENT
        elif score >= 7.0:
            return ScoreLevel.GOOD
        elif score >= 5.0:
            return ScoreLevel.FAIR
        elif score >= 3.0:
            return ScoreLevel.POOR
        else:
            return ScoreLevel.CRITICAL


class LiteraryScorer:
    """文学性评分（对应§4.10表达升维 + §6叙事层）"""
    DIMENSION = "文学性"

    @classmethod
    def score(cls, text: str) -> DimensionScore:
        """评分文学性"""
        score_val = 10.0
        suggestions = []

        # 检查是否滥用“感觉”“觉得”类抽象词
        abstract_words = ["感觉很", "觉得很", "感到很", "我很难过", "我很开心"]
        abstract_count = sum(1 for aw in abstract_words if aw in text)
        if abstract_count > 3:
            score_val -= 1.5
            suggestions.append("存在多处抽象情绪描写，建议用具象画面/动作替代（§4.10.2工具1）")

        # 检查是否有潜文本（os标记）
        if "os" in text or "os：" in text or "os:" in text:
            score_val += 0.5  # 有os视为有潜文本意识
            score_val = min(10.0, score_val)

        # 检查意象手法
        imagery_keywords = ["像", "如同", "仿佛", "画面", "镜头"]
        if any(kw in text for kw in imagery_keywords):
            score_val += 0.2
            score_val = min(10.0, score_val)

        level = cls._score_to_level(score_val)
        return DimensionScore(
            dimension=cls.DIMENSION,
            score=max(0.0, score_val),
            level=level,
            suggestions=suggestions,
        )

    @staticmethod
    def _score_to_level(score: float) -> ScoreLevel:
        if score >= 9.0:
            return ScoreLevel.EXCELLENT
        elif score >= 7.0:
            return ScoreLevel.GOOD
        elif score >= 5.0:
            return ScoreLevel.FAIR
        elif score >= 3.0:
            return ScoreLevel.POOR
        else:
            return ScoreLevel.CRITICAL


class QualityScorer:
    """质量评分系统总入口"""
    DIMENSIONS = [
        CharacterDepthScorer,
        DialogueQualityScorer,
        NarrativeStructureScorer,
        VisualSchemeScorer,
        ComplianceScorer,
        LiteraryScorer,
    ]

    # 各维度权重（可根据项目类型调整）
    DEFAULT_WEIGHTS = {
        "人物深度": 1.2,
        "对白质量": 1.2,
        "叙事结构": 1.0,
        "视觉方案": 0.8,
        "合规性": 1.5,  # 合规性权重最高，一票否决风险
        "文学性": 0.8,
    }

    def __init__(self, custom_weights: Optional[Dict[str, float]] = None):
        self.weights = custom_weights or self.DEFAULT_WEIGHTS.copy()

    def score_all(self, text: str, episode_num: int = 1, character_info: Optional[Dict] = None) -> QualityReport:
        """对文本进行全维度质量评分"""
        report = QualityReport()
        total_weighted = 0.0
        total_weight = 0.0

        for scorer_class in self.DIMENSIONS:
            if scorer_class.DIMENSION == "人物深度":
                dim_score = scorer_class.score(text, character_info)
            else:
                dim_score = scorer_class.score(text)

            report.dimensions.append(dim_score)

            # 计算加权分数
            weight = self.weights.get(scorer_class.DIMENSION, 1.0)
            total_weighted += dim_score.score * weight
            total_weight += weight

            # 收集严重问题
            if dim_score.level in [ScoreLevel.POOR, ScoreLevel.CRITICAL]:
                report.critical_issues.append(
                    f"[{scorer_class.DIMENSION}] {dim_score.reasons[0] if dim_score.reasons else '存在质量问题'}"
                )

        # 计算总分（加权平均）
        if total_weight > 0:
            report.total_score = round(total_weighted / total_weight, 2)

        # 判断是否通过（合规性≥7且总分≥6）
        compliance_score = next((d.score for d in report.dimensions if d.dimension == "合规性"), 10.0)
        report.passed = compliance_score >= 7.0 and report.total_score >= 6.0

        # 判定总体等级
        report.overall_level = self._overall_level(report.total_score, compliance_score)

        # 生成摘要
        report.summary = self._generate_summary(report)

        return report

    @staticmethod
    def _overall_level(total: float, compliance: float) -> ScoreLevel:
        """综合判定总体等级（合规性一票否决）"""
        if compliance < 7.0:
            return ScoreLevel.CRITICAL
        if total >= 9.0:
            return ScoreLevel.EXCELLENT
        elif total >= 7.0:
            return ScoreLevel.GOOD
        elif total >= 5.0:
            return ScoreLevel.FAIR
        elif total >= 3.0:
            return ScoreLevel.POOR
        else:
            return ScoreLevel.CRITICAL

    @staticmethod
    def _generate_summary(report: QualityReport) -> str:
        """生成质量报告摘要"""
        level_map = {
            ScoreLevel.EXCELLENT: "优秀",
            ScoreLevel.GOOD: "良好",
            ScoreLevel.FAIR: "合格",
            ScoreLevel.POOR: "不合格",
            ScoreLevel.CRITICAL: "严重问题",
        }
        dim_strs = [f"{d.dimension}={d.score}({level_map[d.level]})" for d in report.dimensions]
        dims_text = " | ".join(dim_strs)
        issue_text = f" | 严重问题:{len(report.critical_issues)}项" if report.critical_issues else ""
        return f"总分={report.total_score} | {dims_text}{issue_text}"


# 示例用法
if __name__ == "__main__":
    scorer = QualityScorer()

    # 正常文本
    sample_text = """
    主角：把我的本子，还给我。
    主角os：爸爸妈妈看到一定会很高兴的。
    △主角蹲下身，开始一张一张捡起散落的作业纸。
    △他低着头，睫毛抖了一下。
    """

    report = scorer.score_all(sample_text, episode_num=1)
    print("=== 质量评分报告 ===")
    print(f"总分: {report.total_score} / 总体等级: {report.overall_level.value}")
    print(f"是否通过: {report.passed}")
    print(f"严重问题: {report.critical_issues}")
    print(f"摘要: {report.summary}")
    for dim in report.dimensions:
        print(f"  [{dim.dimension}] {dim.score} - {dim.level.value}")
        if dim.suggestions:
            print(f"    建议: {dim.suggestions}")