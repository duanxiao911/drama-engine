"""
文化知识库测试
验证第5.5层：中华优秀传统文化知识库的基本功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.knowledge.culture_kb import CultureKnowledgeBase, CultureItem, AestheticInsight


def test_kb_initialization():
    """测试文化库初始化"""
    kb = CultureKnowledgeBase()
    assert kb is not None
    print("✓ 文化库初始化成功")


def test_summary():
    """测试概要输出"""
    kb = CultureKnowledgeBase()
    summary = kb.get_summary()
    assert "V1.2" in summary
    assert "双骨架" in summary
    assert "四大板块" in summary
    assert "乡土中国" in summary
    assert "美的历程" in summary
    print("✓ 文化库概要输出正常")


def test_social_structure():
    """测试社会结构骨架"""
    kb = CultureKnowledgeBase()
    
    # 获取所有概念
    concepts = kb.get_all_social_concepts()
    assert len(concepts) == 8, f"期望8个概念，实际{len(concepts)}个"
    
    # 获取单个概念
    chaju = kb.get_social_structure_concept("差序格局")
    assert chaju is not None
    assert "description" in chaju
    assert "narrative_transformation" in chaju
    assert "script_examples" in chaju
    assert len(chaju["script_examples"]) > 0
    
    print(f"✓ 社会结构骨架：{len(concepts)}个核心概念正常")


def test_aesthetic_insights():
    """测试审美意识骨架"""
    kb = CultureKnowledgeBase()
    
    all_aes = kb.get_all_aesthetics()
    assert len(all_aes) == 9, f"期望9个审美时代，实际{len(all_aes)}个"
    
    # 按关键词查询
    bronze = kb.get_aesthetic_insight("青铜")
    assert bronze is not None
    assert bronze.era == "青铜饕餮"
    assert bronze.keyword == "狞厉之美"
    
    weijin = kb.get_aesthetic_insight("魏晋")
    assert weijin is not None
    assert "人的觉醒" in weijin.keyword
    
    print(f"✓ 审美意识骨架：{len(all_aes)}个审美时代正常")


def test_four_sections():
    """测试四大板块"""
    kb = CultureKnowledgeBase()
    
    rituals = kb.get_rituals()
    daily = kb.get_daily_order()
    spirit = kb.get_spirit()
    imagery = kb.get_imagery()
    
    assert len(rituals) >= 5
    assert len(daily) >= 5
    assert len(spirit) >= 5
    assert len(imagery) >= 6
    
    # 每个条目都有完整字段
    for item in rituals:
        assert isinstance(item, CultureItem)
        assert item.id
        assert item.title
        assert item.description
        assert item.narrative_application
        assert item.source
    
    print(f"✓ 四大板块：仪式{len(rituals)}条 + 日常{len(daily)}条 + 精神{len(spirit)}条 + 意象{len(imagery)}条")


def test_theme_filter():
    """测试按主题筛选"""
    kb = CultureKnowledgeBase()
    
    # 仪式：死亡主题
    death_rituals = kb.get_rituals("死亡")
    assert len(death_rituals) > 0
    assert any("丧葬" in r.title for r in death_rituals)
    
    # 日常：代际关系
    intergen = kb.get_daily_order("代际")
    assert len(intergen) > 0
    assert any("隔代" in r.title for r in intergen)
    
    # 意象：蓝白
    blue_white = kb.get_imagery("蓝白")
    assert len(blue_white) > 0
    
    print("✓ 按主题筛选功能正常")


def test_search():
    """测试关键词搜索"""
    kb = CultureKnowledgeBase()
    
    results = kb.search("扎染")
    assert len(results) > 0
    assert results[0].section == "imagery"  # 扎染的蓝在意象库最相关
    
    results2 = kb.search("家族")
    assert len(results2) > 0
    
    # 搜索不存在的关键词
    results3 = kb.search("不存在的关键词12345")
    assert len(results3) == 0
    
    print("✓ 关键词搜索功能正常")


def test_drama_type_recommendation():
    """测试按短剧类型推荐"""
    kb = CultureKnowledgeBase()
    
    # 非遗文化题材
    rec_feiyi = kb.recommend_for_drama_type("非遗文化")
    assert rec_feiyi["ritual"]  # 非遗题材仪式最重要
    assert rec_feiyi["imagery"]
    assert len(rec_feiyi["spirit"]) >= 2
    
    # 现实题材
    rec_real = kb.recommend_for_drama_type("现实主义")
    assert rec_real["daily_order"]
    assert rec_real["spirit"]
    
    # 家庭伦理
    rec_family = kb.recommend_for_drama_type("家庭伦理")
    assert rec_family["daily_order"]
    assert rec_family["spirit"]
    
    print("✓ 短剧类型推荐功能正常")


def test_full_knowledge_export():
    """测试全库导出（用于Prompt注入）"""
    kb = CultureKnowledgeBase()
    
    full = kb.get_full_knowledge()
    assert len(full) > 5000  # 全库至少5000字
    assert "社会结构骨架" in full
    assert "审美意识骨架" in full
    assert "民俗仪式库" in full
    assert "日常秩序库" in full
    assert "精神气质库" in full
    assert "文化意象库" in full
    
    # 部分导出
    partial = kb.get_full_knowledge(sections=["ritual", "imagery"])
    assert "民俗仪式库" in partial
    assert "文化意象库" in partial
    assert "社会结构骨架" not in partial  # 没选的不出现
    
    print(f"✓ 全库导出正常（约{len(full)}字）")


def test_into_orchestrator():
    """测试集成到编排器"""
    from src.workflow.orchestrator import Orchestrator
    
    orch = Orchestrator(enable_culture_kb=True)
    assert orch.culture_kb is not None
    
    # 验证专家实例能获取文化库
    expert = orch._get_expert_instance("§0")
    assert expert.culture_kb is not None
    assert isinstance(expert.culture_kb, CultureKnowledgeBase)
    
    # 验证禁用文化库也可以
    orch_no_kb = Orchestrator(enable_culture_kb=False)
    assert orch_no_kb.culture_kb is None
    
    print("✓ 文化库集成到编排器正常")


if __name__ == "__main__":
    print("=" * 50)
    print("中华优秀传统文化知识库 V1.2 测试")
    print("=" * 50)
    
    test_kb_initialization()
    test_summary()
    test_social_structure()
    test_aesthetic_insights()
    test_four_sections()
    test_theme_filter()
    test_search()
    test_drama_type_recommendation()
    test_full_knowledge_export()
    test_into_orchestrator()
    
    print()
    print("=" * 50)
    print("✓ 全部测试通过！")
    print("=" * 50)
