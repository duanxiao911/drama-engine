"""
类型适配系统

基于《精品短剧创作引擎_通用版.md》§14（类型适配指南）实现：
- 支持类型：悲剧、现实主义、甜宠、悬疑、非遗文化
- 每种类型的节奏公式、情绪点类型、结局设计
- 悲剧专项：下沉阶梯节奏、微光碾碎、对照叙事
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum


class DramaType(Enum):
    """短剧类型枚举"""
    TRAGEDY = "悲剧"
    REALISM = "现实主义"
    SWEET_PET = "甜宠"
    SUSPENSE = "悬疑"
    INTANGIBLE_CULTURAL = "非遗文化"


@dataclass
class TypeAdapter:
    """类型适配器"""
    drama_type: DramaType
    name: str
    description: str
    rhythm_formula: str
    emotion_point_types: List[str]
    ending_design: str
    special_rules: List[str] = field(default_factory=list)
    arc_structure: str = ""
    forbidden_patterns: List[str] = field(default_factory=list)


class TypeAdapterRegistry:
    """类型适配注册表"""
    _adapters: Dict[DramaType, TypeAdapter] = {}

    @classmethod
    def register(cls, adapter: TypeAdapter):
        cls._adapters[adapter.drama_type] = adapter

    @classmethod
    def get(cls, drama_type: DramaType) -> Optional[TypeAdapter]:
        return cls._adapters.get(drama_type)

    @classmethod
    def get_all(cls) -> Dict[DramaType, TypeAdapter]:
        return cls._adapters.copy()


def _init_adapters():
    """初始化所有类型适配器（基于§14方法论）"""
    # 悲剧适配器
    tragedy_adapter = TypeAdapter(
        drama_type=DramaType.TRAGEDY,
        name="悲剧类型适配",
        description="悲剧与爽剧根本区别：挣扎-微光-更深的暗，观众情绪向下坠但理解加深",
        rhythm_formula="下沉阶梯节奏：起点有光-外部打击-微光（还有人在）-关系崩塌-微光-自我瓦解-微光-底部（接受就这样吧）",
        emotion_point_types=[
            "心碎点：角色付出真心，换来冷漠或背叛",
            "无力点：角色拼尽全力，结果毫无改变",
            "误解点：角色因信息差做出错误选择，事后无法挽回",
            "认命点：角色放弃挣扎，观众比角色更痛",
        ],
        ending_design="不是绝望，是带着伤活下去；反思空间让观众离开后还在想；最后一道微光不碾碎",
        special_rules=[
            "高光早于崩溃：必须先让观众爱上角色的光芒，崩溃才有力",
            "人物不洗白：没有角色是纯粹的坏人或好人",
            "悲剧不可消解：不能用其实有人一直爱他来抵消前面的痛",
            "禁止用自杀/死亡制造高潮：悲剧高潮是活着但心死了",
            "情绪来源是内心撕裂：不是外部羞辱的画面",
            "反派反在冷漠：最伤人的不是打了你，是当你是空气",
            "微光碾碎：微光必须真实，被碾碎时因果驱动，不是硬来",
            "微光越来越弱：后期微光只能是一个眼神、一秒的沉默",
            "对照叙事：高光早于崩溃，对照要具体，间隔至少5集",
        ],
        arc_structure="固守（骄傲/证明自己）-裂缝（第一次被无视后的困惑）-动摇（反复受挫后自我怀疑）-接受（知道真相但仍挣扎）-沉默（放弃，不是释然是放弃）",
        forbidden_patterns=["一路黑到底不给微光", "微光是假希望", "用自杀/死亡制造高潮", "强行洗白或消解痛苦"],
    )
    TypeAdapterRegistry.register(tragedy_adapter)

    # 现实主义适配器
    realism_adapter = TypeAdapter(
        drama_type=DramaType.REALISM,
        name="现实主义类型适配",
        description="基于真实社会背景，聚焦普通人的生存困境与情感挣扎",
        rhythm_formula="贴近生活的脉冲式节奏：日常-冲突-短暂喘息-更大冲突，每集至少一个现实痛点",
        emotion_point_types=["生存压力：经济、职场、家庭的现实困境", "情感撕裂：亲情/友情/爱情的现实摩擦", "尊严受损：面子与里子的两难", "微光时刻：陌生人善意、小小确幸"],
        ending_design="开放式闭合：问题可能未完全解决，但角色有了新的认知或选择",
        special_rules=["细节必须真实可信：空间、行为、情感细节必须有出处", "避免脸谱化：好人和坏人都有自私和软弱", "情绪克制：不过度煽情，留白比宣泄更有力", "侧面叙事处理敏感内容"],
        arc_structure="日常状态-困境显现-挣扎与妥协-抉择时刻-新平衡",
        forbidden_patterns=["过度美化或丑化某一群体", "脱离实际的悬浮细节", "用巧合推动剧情"],
    )
    TypeAdapterRegistry.register(realism_adapter)

    # 甜宠适配器
    sweet_pet_adapter = TypeAdapter(
        drama_type=DramaType.SWEET_PET,
        name="甜宠类型适配",
        description="主打甜蜜互动与双向治愈，冲突来源于外部压力而非CP内部",
        rhythm_formula="甜虐交替：甜蜜互动（存款）-外部误会/压力（制造张力）-坦诚/相守（取款）-新的甜蜜起点",
        emotion_point_types=["心动瞬间：不经意的身体接触、眼神交汇", "吃醋/占有欲：对方被别人关注时的微妙反应", "误解与吃醋：外部压力造成的误会", "相守时刻：共同面对困难后的甜蜜升级"],
        ending_design="双向奔赴的甜蜜收尾，通常是正向结局",
        special_rules=["CP互动必须有化学反应", "外部矛盾为主：家庭反对、身份差距、误解等", "甜要有层次：从暧昧-确认-守护-共同成长", "虐是为甜服务的：误会不能拖太久"],
        arc_structure="相遇/误会-互相了解-确认心意-外部考验-甜蜜相守",
        forbidden_patterns=["三角恋狗血套路", "CP之间互相伤害的虐", "恶意误会长时间不澄清", "一方过度卑微"],
    )
    TypeAdapterRegistry.register(sweet_pet_adapter)

    # 悬疑适配器
    suspense_adapter = TypeAdapter(
        drama_type=DramaType.SUSPENSE,
        name="悬疑类型适配",
        description="通过信息差、谜题揭示、紧张节奏制造观看动力",
        rhythm_formula="谜题-线索-误导-新谜题-真相揭露的递进节奏，每集至少一个信息增量或反转",
        emotion_point_types=["悬念点：关键信息未揭露，观众急迫想知道", "反转点：真相揭露后的认知重构", "紧张点：危机逼近、危险时刻", "解密时刻：关键线索串联后的恍然大悟"],
        ending_design="真相大白或真相背后的选择，通常有认知层面的冲击力",
        special_rules=["信息差是核心引擎", "每条线索都有用：埋的伏笔必须回收", "反转要合理：出人意料但回看能发现线索", "节奏紧凑：不拖沓"],
        arc_structure="谜题呈现-线索收集-误导分支-真相逼近-终极揭露-余韵反思",
        forbidden_patterns=["为反转而反转的虚假线索", "关键信息靠巧合揭露", "最后靠主角嘴炮解密", "反派智商突然下线"],
    )
    TypeAdapterRegistry.register(suspense_adapter)

    # 非遗文化适配器
    intangible_adapter = TypeAdapter(
        drama_type=DramaType.INTANGIBLE_CULTURAL,
        name="非遗文化类型适配",
        description="以非遗技艺/文化传承为核心，融合现实主义或情感叙事",
        rhythm_formula="传承线与情感线双轨并行：技艺困境-传承危机-情感支撑-突破/式微的开放式结局",
        emotion_point_types=["技艺困境：传统技艺在现代社会的生存挣扎", "传承之痛：老一代与新一代的观念冲突", "文化之美：非遗技艺的独特魅力与工匠精神", "情感羁绊：师徒情、亲情、爱情的交织"],
        ending_design="开放式：技艺可能式微但精神传承，或新与旧的融合重生",
        special_rules=["非遗知识必须真实准确", "文化元素自然融入：不是说明书式的介绍", "人物要有代表性：老匠人的坚守、年轻人的困境与选择", "正面呈现非遗之美"],
        arc_structure="技艺呈现-困境显现-挣扎与选择-突破/融合/式微-精神延续",
        forbidden_patterns=["非遗知识错误或不准确", "用猎奇视角消费非遗", "刻意卖惨博同情", "文化元素与故事脱节"],
    )
    TypeAdapterRegistry.register(intangible_adapter)


_init_adapters()


class TypeAdapterManager:
    """类型适配管理器"""

    def __init__(self):
        self._registry = TypeAdapterRegistry

    def get_adapter(self, drama_type: DramaType) -> Optional[TypeAdapter]:
        return TypeAdapterRegistry.get(drama_type)

    def get_adapter_by_name(self, type_name: str) -> Optional[TypeAdapter]:
        try:
            dtype = DramaType(type_name)
            return TypeAdapterRegistry.get(dtype)
        except ValueError:
            return None

    def list_all_types(self) -> List[str]:
        return [dt.value for dt in DramaType]

    def apply_adapter(self, drama_type: DramaType, content: Dict) -> Dict:
        adapter = self.get_adapter(drama_type)
        if not adapter:
            return {"error": f"未知的类型: {drama_type}"}
        return {
            "type": adapter.name,
            "description": adapter.description,
            "rhythm_formula": adapter.rhythm_formula,
            "emotion_point_types": adapter.emotion_point_types,
            "ending_design": adapter.ending_design,
            "special_rules": adapter.special_rules,
            "arc_structure": adapter.arc_structure,
            "structure_suggestions": self._generate_structure_suggestions(adapter),
        }

    def _generate_structure_suggestions(self, adapter: TypeAdapter) -> Dict:
        suggestions = {"opening": "", "conflict_pattern": "", "emotion_distribution": "", "ending_guidance": ""}
        if adapter.drama_type == DramaType.TRAGEDY:
            suggestions["opening"] = "前3集必须展示角色的高光，让观众爱上角色的光芒"
            suggestions["conflict_pattern"] = "外部-关系-自我，三层困境逐步升级，每层之间必须有真实微光"
            suggestions["emotion_distribution"] = "每集至少1个心碎点或无力点；每5-8集1个误解点；全剧高潮是认命点"
            suggestions["ending_guidance"] = "保留最后一道微光不碾碎，结局是带着伤活下去而非绝望"
        elif adapter.drama_type == DramaType.REALISM:
            suggestions["opening"] = "用真实的日常场景建立角色，观众3秒内判断这就是我身边的人"
            suggestions["conflict_pattern"] = "现实压力+情感摩擦交织，困境要具体可信"
            suggestions["emotion_distribution"] = "情绪克制，不过度煽情；留白比宣泄更有力"
            suggestions["ending_guidance"] = "开放式闭合，问题可能未完全解决但角色有新认知"
        elif adapter.drama_type == DramaType.SWEET_PET:
            suggestions["opening"] = "建立CP化学反应，首集要有让人心动的互动瞬间"
            suggestions["conflict_pattern"] = "外部矛盾为主（误会/家庭反对/身份差距），不以CP互撕为主线"
            suggestions["emotion_distribution"] = "甜-虐-甜的循环，误会及时化解，不恶意拉长"
            suggestions["ending_guidance"] = "双向奔赴的甜蜜收尾，情感升华"
        elif adapter.drama_type == DramaType.SUSPENSE:
            suggestions["opening"] = "抛出核心谜题，3秒内制造必须知道答案的悬念"
            suggestions["conflict_pattern"] = "线索-误导-新线索-反转，信息差是核心引擎"
            suggestions["emotion_distribution"] = "每集至少一个信息增量或反转，节奏紧凑不拖沓"
            suggestions["ending_guidance"] = "真相大白或真相背后的选择，有认知冲击力"
        elif adapter.drama_type == DramaType.INTANGIBLE_CULTURAL:
            suggestions["opening"] = "展示非遗技艺之美，同时呈现传承困境"
            suggestions["conflict_pattern"] = "传承线（技艺困境）与情感线（师徒/亲情）双轨并行"
            suggestions["emotion_distribution"] = "文化之美与情感羁绊交织，不刻意卖惨"
            suggestions["ending_guidance"] = "开放式结局，技艺可能式微但精神延续，或新旧融合"
        return suggestions

    def export_all_rules(self) -> List[Dict]:
        rules = []
        for dtype, adapter in TypeAdapterRegistry.get_all().items():
            rules.append({
                "type": dtype.value,
                "name": adapter.name,
                "description": adapter.description,
                "rhythm_formula": adapter.rhythm_formula,
                "emotion_point_types": adapter.emotion_point_types,
                "ending_design": adapter.ending_design,
                "special_rules": adapter.special_rules,
                "forbidden_patterns": adapter.forbidden_patterns,
            })
        return rules


__all__ = ["DramaType", "TypeAdapter", "TypeAdapterRegistry", "TypeAdapterManager"]


if __name__ == "__main__":
    manager = TypeAdapterManager()
    print("=== 支持的类型 ===")
    print(manager.list_all_types())
    print("\n=== 悲剧类型适配规则 ===")
    rules = manager.apply_adapter(DramaType.TRAGEDY, {})
    for key, val in rules.items():
        print(f"{key}: {val}")
    print("\n=== 导出所有类型规则 ===")
    all_rules = manager.export_all_rules()
    print(f"共 {len(all_rules)} 种类型适配规则")