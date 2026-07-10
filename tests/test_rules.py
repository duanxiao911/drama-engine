"""
rules.py 测试文件

测试铁律系统的核心功能：
- 规则冲突裁决
- 红线扫描
- 叙事因果检查
- AI生成检测
- 素材验证
"""

import pytest
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.engine.rules import (
    RulesEngine,
    RuleConflict,
    RulePriority,
    RedLineSystem,
    NarrativeCausality,
    AIDetectionRedLine,
    MaterialIronRules,
    RedLineCategory,
)


class TestRuleConflictResolution:
    """测试规则冲突裁决"""

    def test_material_priority_higher_than_style(self):
        """素材事实（第2层）应优先于风格偏好（第4层）"""
        conflict = RuleConflict(
            rule_a="素材：主角服药自杀",
            rule_b="风格偏好：希望有强烈的死亡画面",
            priority_a=RulePriority.L2_MATERIAL_HARD,
            priority_b=RulePriority.L4_STYLE_PREFERENCE,
        )
        result = conflict.resolve()
        assert result == conflict.rule_a
        assert conflict.resolution == conflict.rule_a

    def test_compliance_priority_over_material(self):
        """合规红线（第1层）应优先于素材事实（第2层）"""
        conflict = RuleConflict(
            rule_a="素材：主角服药自杀",
            rule_b="合规红线：禁止自杀正面展示",
            priority_a=RulePriority.L2_MATERIAL_HARD,
            priority_b=RulePriority.L1_PLATFORM_COMPLIANCE,
        )
        result = conflict.resolve()
        assert result == conflict.rule_b  # 合规胜出

    def test_methodology_vs_style(self):
        """创作方法论（第3层）应优先于风格偏好（第4层）"""
        conflict = RuleConflict(
            rule_a="风格偏好：喜欢长篇对白",
            rule_b="方法论：精品短剧台词五字诀“短”",
            priority_a=RulePriority.L4_STYLE_PREFERENCE,
            priority_b=RulePriority.L3_METHODOLOGY,
        )
        result = conflict.resolve()
        assert result == conflict.rule_b


class TestRedLineSystem:
    """测试红线扫描系统"""

    def setup_method(self):
        self.scanner = RedLineSystem()

    def test_detect_supernatural_godhand(self):
        """检测超自然金手指"""
        text = "主角突然觉醒了异能血脉之力"
        warnings = self.scanner.scan(text)
        categories = [w["category"] for w in warnings]
        assert RedLineCategory.SUPERNATURAL_GODHAND in categories

    def test_detect_violence(self):
        """检测暴力私刑"""
        text = "主角决定以暴制暴，复仇杀死反派"
        warnings = self.scanner.scan(text)
        categories = [w["category"] for w in warnings]
        assert RedLineCategory.VIGILANTE_VIOLENCE in categories

    def test_detect_bullying(self):
        """检测人格羞辱+霸凌"""
        text = "反派逼迫主角下跪，当众羞辱他"
        warnings = self.scanner.scan(text)
        categories = [w["category"] for w in warnings]
        assert RedLineCategory.PERSONALITY_HUMILIATION_BULLYING in categories

    def test_detect_prohibited_topic(self):
        """检测题材禁区"""
        text = "故事发生在缅北地区，主角是当地人"
        warnings = self.scanner.scan(text)
        categories = [w["category"] for w in warnings]
        assert "题材禁区" in categories

    def test_clean_text_no_warnings(self):
        """正常文本不触发警告"""
        text = "主角是一名退伍军人，他在城市里找工作"
        warnings = self.scanner.scan(text)
        assert len(warnings) == 0

    def test_alternative_suggestions_provided(self):
        """红线警告应包含合规替代方案"""
        text = "主角觉醒了异能"
        warnings = self.scanner.scan(text)
        assert len(warnings) > 0
        assert "alternative" in warnings[0]
        assert warnings[0]["alternative"] != ""


class TestNarrativeCausality:
    """测试叙事因果铁律"""

    def test_detect_ungrounded_sudden_change(self):
        """检测无铺垫的突然转折"""
        scene = "主角突然决定离开家乡，再也不回来"
        result = NarrativeCausality.check(scene)
        assert len(result["issues"]) > 0
        assert "无铺垫" in result["issues"][0]

    def test_narrative_driven_by_plot(self):
        """检测“剧情需要”驱动"""
        scene = "主角因为剧情需要，突然性格大变"
        result = NarrativeCausality.check(scene)
        assert any("剧情需要" in issue for issue in result["issues"])

    def test_grounded_scene_passes(self):
        """有因果铺垫的场景通过检查"""
        scene = "因为母亲多年忽视，主角终于无法忍受，决定离开家乡"
        result = NarrativeCausality.check(scene)
        assert len(result["issues"]) == 0


class TestAIDetection:
    """测试AI生成检测"""

    def test_detect_abstract_emotion_without_action(self):
        """检测无动作描写的抽象情绪"""
        text = "他心里很难过，觉得世界都崩塌了"
        result = AIDetectionRedLine.check(text)
        assert result["score"] < 1.0
        assert len(result["issues"]) > 0

    def test_detect_repetitive_sentences(self):
        """检测重复句式"""
        text = "我很难过。我真的很。我真的很难过。"
        result = AIDetectionRedLine.check(text)
        assert len(result["issues"]) > 0

    def test_natural_text_passes(self):
        """自然的文本通过检测"""
        text = "主角攥紧了拳头，指节发白，一句话都没说。"
        result = AIDetectionRedLine.check(text)
        assert result["score"] >= 1.0


class TestMaterialRules:
    """测试素材铁律"""

    def test_forbidden_material_rejected(self):
        """禁止类素材被拒绝"""
        valid, msg = MaterialIronRules.validate_material_source("道听途说")
        assert valid is False

    def test_verified_material_accepted(self):
        """有来源的素材被接受"""
        valid, msg = MaterialIronRules.validate_material_source("基于真实采访和新闻报道")
        assert valid is True

    def test_ai_material_needs_verification(self):
        """AI生成素材需要验证"""
        valid, msg = MaterialIronRules.validate_material_source("AI生成的内容")
        assert valid is True  # 接受但提示需要验证


class TestRulesEngine:
    """测试规则引擎总入口"""

    def setup_method(self):
        self.engine = RulesEngine()

    def test_full_red_line_scan(self):
        """完整红线扫描"""
        text = "主角觉醒金手指，用匕首刺杀反派"
        warnings = self.engine.scan_red_lines(text)
        assert len(warnings) >= 2  # 至少两个类别触发

    def test_conflict_resolution_integration(self):
        """冲突裁决集成"""
        conflict = RuleConflict(
            rule_a="素材事实不可改",
            rule_b="合规红线必须遵守",
            priority_a=RulePriority.L2_MATERIAL_HARD,
            priority_b=RulePriority.L1_PLATFORM_COMPLIANCE,
        )
        result = self.engine.resolve_conflict(conflict)
        assert result == conflict.rule_b  # 合规胜出

    def test_ai_detection_integration(self):
        """AI检测集成"""
        text = "她心里很伤心，突然觉得世界都崩塌了"
        result = self.engine.check_ai_detection(text)
        assert result["score"] < 1.0
        assert len(result["issues"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])