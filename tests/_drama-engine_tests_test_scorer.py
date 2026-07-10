"""
scorer.py 测试文件

测试质量评分系统的核心功能：
- 六大维度评分
- 扣分规则
- 质量报告生成
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.engine.scorer import (
    QualityScorer,
    CharacterDepthScorer,
    DialogueQualityScorer,
    NarrativeStructureScorer,
    VisualSchemeScorer,
    ComplianceScorer,
    LiteraryScorer,
    ScoreLevel,
)


class TestCharacterDepthScorer:
    """测试人物深度评分"""

    def test_novel_like_text_penalized(self):
        """小说式抽象描写被扣分"""
        text = "主角心里很难过，觉得被全世界抛弃了"
        score = CharacterDepthScorer.score(text)
        assert score.score < 10.0
        assert len(score.suggestions) > 0

    def test_character_with_arc_passes(self):
        """有人设弧光的文本表现更好"""
        text_with_arc = "主角攥紧拳头，决定不再沉默。他选择站出来面对这一切。"
        score = CharacterDepthScorer.score(text_with_arc)
        assert score.score >= 8.0


class TestDialogueQualityScorer:
    """测试对白质量评分"""

    def test_expository_dialogue_penalized(self):
        """说明性对白被扣分"""
        text = '大家都知道，我们公司三年前就破产了。'
        score = DialogueQualityScorer.score(text)
        assert score.score < 10.0
        assert any("说明性" in s for s in score.suggestions)

    def test_harmonious_dialogue_penalized(self):
        """一致性/太和谐对白被扣分"""
        text = 'A：你的想法很好。B：我也这么想的。'
        score = DialogueQualityScorer.score(text)
        assert score.score < 10.0

    def test_good_dialogue_with_subtext_passes(self):
        """有潜文本的好对白通过"""
        good_dialogue = """
主角：把我的本子，还给我。
主角os：爸爸妈妈看到一定会很高兴的。
△主角蹲下身，开始一张一张捡起散落的作业纸。
        """
        score = DialogueQualityScorer.score(good_dialogue)
        assert score.score >= 8.0


class TestNarrativeStructureScorer:
    """测试叙事结构评分"""

    def test_ep1_without_conflict_penalized(self):
        """第1集无冲突开头被扣分"""
        text = "阳光明媚，主角走在上学的路上。"
        score = NarrativeStructureScorer.score(text, episode_num=1)
        assert score.score < 10.0
        assert any("前3秒" in s for s in score.suggestions)

    def test_scene_with_cause_effect_passes(self):
        """有因果链的场景表现更好"""
        text = "因为母亲多年不回家，主角决定离开。"
        score = NarrativeStructureScorer.score(text)
        assert score.score >= 8.0


class TestVisualSchemeScorer:
    """测试视觉方案评分"""

    def test_text_without_visual_elements_penalized(self):
        """无视觉元素的文本被扣分"""
        text = "主角很难过，决定离开。"
        score = VisualSchemeScorer.score(text)
        assert score.score < 10.0

    def test_text_with_visual_elements_passes(self):
        """有视觉元素的文本表现更好"""
        text = "阳光透过窗户洒在地板上，主角站在阴影里。"
        score = VisualSchemeScorer.score(text)
        assert score.score >= 8.0


class TestComplianceScorer:
    """测试合规性评分"""

    def test_detect_violation_keywords(self):
        """检测违规关键词"""
        text = "主角觉醒了异能，用匕首刺向敌人"
        score = ComplianceScorer.score(text)
        assert score.score < 10.0
        assert len(score.reasons) >= 2

    def test_clean_text_passes(self):
        """合规文本通过"""
        text = "主角是一名退伍军人，用合法手段维护权益"
        score = ComplianceScorer.score(text)
        assert score.score >= 9.0

    def test_critical_level_for_red_line(self):
        """红线违规触发critical等级"""
        text = "主角用匕首刺杀反派，这是以暴制暴"
        score = ComplianceScorer.score(text)
        assert score.level in [ScoreLevel.POOR, ScoreLevel.CRITICAL]


class TestLiteraryScorer:
    """测试文学性评分"""

    def test_excessive_abstract_words_penalized(self):
        """过度抽象描写被扣分"""
        text = "他感觉很悲伤，她觉得很开心，我觉得很难过"
        score = LiteraryScorer.score(text)
        assert score.score < 10.0
        assert any("抽象" in s for s in score.suggestions)

    def test_text_with_os_bonus(self):
        """有os标记的文本获得加分"""
        text = "主角os：我真的好累啊。主角：嗯，没事。"
        score = LiteraryScorer.score(text)
        assert score.score >= 8.0


class TestQualityScorer:
    """测试质量评分系统总入口"""

    def setup_method(self):
        self.scorer = QualityScorer()

    def test_full_scorer_produces_report(self):
        """完整评分生成报告"""
        text = """
主角：把我的本子，还给我。
主角os：爸爸妈妈看到一定会很高兴的。
△主角蹲下身，开始一张一张捡起散落的作业纸。
△他低着头，睫毛抖了一下。
因为母亲从不关心他，他决定好好读书证明自己。
        """
        report = self.scorer.score_all(text, episode_num=1)
        assert report.total_score > 0
        assert len(report.dimensions) == 6
        assert report.overall_level is not None

    def test_red_line_breaks_pass(self):
        """红线违规导致pass=False"""
        text = "主角用匕首刺杀反派，血流满面"
        report = self.scorer.score_all(text)
        assert report.passed is False

    def test_custom_weights_applied(self):
        """自定义权重生效"""
        scorer = QualityScorer(custom_weights={"合规性": 2.0})
        text = "主角正常地说话做事，没有任何违规"
        report = scorer.score_all(text)
        assert report.total_score > 0

    def test_report_to_dict(self):
        """报告可序列化为字典"""
        text = "主角os：我没事。主角：嗯。"
        report = self.scorer.score_all(text)
        report_dict = report.to_dict()
        assert "total_score" in report_dict
        assert "dimensions" in report_dict
        assert isinstance(report_dict["dimensions"], list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])