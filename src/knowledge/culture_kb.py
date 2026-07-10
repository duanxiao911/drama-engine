"""
中华优秀传统文化知识库 V1.2
—— 双骨架架构（《乡土中国》社会结构骨架 + 《美的历程》审美意识骨架）

集成到引擎第5.5层，供所有AI专家共享调用。
核心原则：文化不是展示是叙事动力。

使用方法：
    from src.knowledge.culture_kb import CultureKnowledgeBase
    
    kb = CultureKnowledgeBase()
    
    # 按板块检索
    rituals = kb.get_rituals(theme="死亡与哀悼")
    daily_order = kb.get_daily_order(theme="代际关系")
    spirits = kb.get_spirit(theme="生命观")
    imagery = kb.get_imagery(theme="蓝白")
    
    # 按故事类型推荐
    suggestions = kb.recommend_for_drama_type("非遗文化")
    
    # 按审美时代推荐
    aesthetic = kb.get_aesthetic_insight("青铜饕餮")
    
    # 获取完整知识库（用于注入Prompt）
    full_kb = kb.get_full_knowledge()
"""

import json
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum


class CultureSection(Enum):
    """文化库四大板块"""
    RITUAL = "ritual"
    DAILY_ORDER = "daily_order"
    SPIRIT = "spirit"
    IMAGERY = "imagery"


class AestheticEra(Enum):
    """审美时代光谱（《美的历程》）"""
    PREHISTORIC = "prehistoric"
    BRONZE_TAOIE = "bronze_taotie"
    PRE_QIN_RATIONAL = "pre_qin"
    CHU_HAN_ROMANTIC = "chu_han"
    WEI_JIN_DANDY = "weijin"
    SUI_TANG_BRILLIANCE = "suitang"
    SONG_YUAN_LANDSCAPE = "songyuan"
    MING_QING_LITERATI = "mingqing"
    MODERN_TRANSITION = "modern"


@dataclass
class CultureItem:
    """单条文化知识条目"""
    id: str
    section: str
    theme: str
    title: str
    description: str
    narrative_application: str
    source: str
    examples: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "section": self.section,
            "theme": self.theme,
            "title": self.title,
            "description": self.description,
            "narrative_application": self.narrative_application,
            "source": self.source,
            "examples": self.examples,
        }


@dataclass
class AestheticInsight:
    """审美时代洞察条目"""
    era: str
    keyword: str
    description: str
    narrative_transformation: str
    representative_works: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "era": self.era,
            "keyword": self.keyword,
            "description": self.description,
            "narrative_transformation": self.narrative_transformation,
            "representative_works": self.representative_works,
        }


class CultureKnowledgeBase:
    """
    中华优秀传统文化知识库（双骨架架构）
    
    社会结构骨架（《乡土中国》）：指导「中国人怎么相处」
    审美意识骨架（《美的历程》）：指导「中国人怎么感受」
    
    四大板块交织两个骨架使用：
    - 民俗仪式库（ritual）：仪式的荒诞推动觉醒
    - 日常秩序库（daily_order）：节令的更替推动转折
    - 精神气质库（spirit）：精神困境推动内心戏
    - 文化意象库（imagery）：意象的出现推动情绪
    """

    def __init__(self):
        self._rituals: List[CultureItem] = []
        self._daily_orders: List[CultureItem] = []
        self._spirits: List[CultureItem] = []
        self._imagery: List[CultureItem] = []
        self._aesthetics: List[AestheticInsight] = []
        self._social_structure = {}
        self._init_knowledge()

    # ========== 初始化 ==========

    def _init_knowledge(self):
        """初始化所有文化知识"""
        self._init_social_structure()
        self._init_aesthetic_insights()
        self._init_rituals()
        self._init_daily_order()
        self._init_spirit()
        self._init_imagery()

    def _init_social_structure(self):
        """社会结构骨架：《乡土中国》8个核心概念"""
        self._social_structure = {
            "差序格局": {
                "description": "中国社会不是一捆一捆扎清楚的柴，而是把一块石头丢在水面上所发生的一圈圈推出去的波纹。每个人都是他社会影响所推出去的圈子的中心。",
                "narrative_transformation": "主角的行为逻辑由亲疏远近决定——对家人的承诺可以打破规则，对外人的怀疑来自格局差异。冲突往往产生于两种格局的碰撞（乡土格局vs现代契约格局）。",
                "script_examples": [
                    "女主拒绝了城里人的投资合作，因为「不是自己人」——投资人用契约精神谈合作，女主用差序格局判断信任",
                    "奶奶宁可把染坊传给侄子也不传给外姓徒弟，哪怕徒弟手艺更好——差序格局中血缘重于能力",
                ]
            },
            "礼治秩序": {
                "description": "乡土社会不是人治也不是法治，而是礼治。礼是按着仪式做的意思，不是靠外在权力推行，而是从教化中养成了个人的敬畏之感。",
                "narrative_transformation": "人物的内心冲突往往是礼治秩序与个人欲望的拉扯。守礼不是被迫的，是刻进骨子里的——打破礼的人，首先要面对的不是惩罚，是自己内心的恐惧和羞耻。",
                "script_examples": [
                    "女主想追求自己的爱情，但每次想开口就想起奶奶的话「女子要守本分」——不是奶奶在管她，是她脑子里的礼在管她",
                    "男主在外打拼多年，回乡后第一反应是给长辈磕头——这不是表演，是肌肉记忆",
                ]
            },
            "熟人社会": {
                "description": "乡土社会是一个熟人社会，是没有陌生人的社会。规矩是「习」出来的，不是「学」出来的。在熟悉的环境里，甚至不需要法律，规矩就在每个人心里。",
                "narrative_transformation": "故事的张力可以来自「陌生人闯入熟人社会」。一个外来者带来的不仅是新信息，更是一整套不同的行为逻辑。熟人社会的人看陌生人，首先不是看他说什么，而是看他「懂不懂规矩」。",
                "script_examples": [
                    "城里来的设计师想改造扎染作坊，第一天就犯了众怒——他直接走进染坊摸布料，按规矩外人不能碰染缸",
                    "全村人都知道谁和谁有矛盾，但谁都不说破——这是熟人社会的默契",
                ]
            },
            "血缘与地缘": {
                "description": "血缘是身份社会的基础，地缘是契约社会的基础。从血缘结合转变到地缘结合是社会性质的转变，也是现代社会的开始。",
                "narrative_transformation": "这是城乡题材、迁徙题材的核心矛盾。一个从乡土走出来的人，身上同时带着血缘的羁绊和地缘的向往。他/她的挣扎，本质上是两种社会身份的撕扯。",
                "script_examples": [
                    "女主在城市生活了五年，已经习惯了契约关系，但一回村就自动切换回血缘身份——她是奶奶的孙女、是这家的人，不是「我自己」",
                    "外乡来的手艺人手艺再好，村里人总觉得「他不是这儿的人」——地缘身份比能力更先被定义",
                ]
            },
            "家族与家": {
                "description": "在西洋，家是生育社群，是暂时的；在中国乡土，家是事业社群，是绵续的。家是个绵续性的事业社群，它的主轴是父子之间、婆媳之间，是纵的，不是横的。",
                "narrative_transformation": "中国的家族不是爱情的产物，是事业的单位。这解释了为什么很多家庭里夫妻相敬如宾但婆媳斗争激烈——因为家庭的功能重心不在夫妻关系，而在代际传承。",
                "script_examples": [
                    "奶奶和孙女的矛盾，本质上是「谁来继承这个家」的问题——不是爱不爱的问题，是家族事业交接的问题",
                    "男主想做自己喜欢的事，父亲说「你对不起列祖列宗」——这不是夸张，在家族事业逻辑里，个人爱好确实是对家族的背叛",
                ]
            },
            "男女有别": {
                "description": "乡土社会中，男女的关系被安排成「不必求同」的格局——男主外女主内，夫妻之间不需要深刻的理解，只要分工合作。感情满足在同性和同年龄的群体中去找。",
                "narrative_transformation": "传统故事里的爱情悲剧，根源往往不是坏人破坏，而是「男女有别」这个结构性的安排。两个人明明相爱，但整个社会结构都在告诉他们「你们不需要亲密」。",
                "script_examples": [
                    "一对夫妻相敬如宾了一辈子，临死前才第一次说心里话——不是不爱，是一辈子都在按「男女有别」的规矩活",
                    "女主和闺蜜无话不谈，但和丈夫一天说不了三句话——这不代表婚姻不幸，这是乡土社会的常态",
                ]
            },
            "无为政治": {
                "description": "乡土社会的权力结构名义上是专制的，实际上是挂名的、无为的。天高皇帝远，真正管着日常生活的不是皇权，是礼俗。",
                "narrative_transformation": "故事里的「规矩」不需要有个具体的恶人在执行。真正压迫人的是那个看不见摸不着但每个人都在遵守的东西——比反派更强大的对手是秩序本身。",
                "script_examples": [
                    "女主想打破规矩，但找不到具体的「敌人」——奶奶不是坏人，村长不是坏人，所有人都是好心，但所有人加起来就是在逼她就范",
                    "一个人对抗的从来不是某个人，是一整套已经运转了几千年的秩序",
                ]
            },
            "名实分离": {
                "description": "在长老统治下，人们不能公然反对传统，但可以在实践中悄悄改变。表面上承认旧的名字、旧的规矩，实际上内容已经换了。这是中国社会变迁的独特方式。",
                "narrative_transformation": "中国故事里的人物很少有彻底的「革命者」，更多的是「改良者」——嘴上说着老规矩，实际行动已经在改变。这种表里不一是智慧，也是无奈。",
                "script_examples": [
                    "奶奶嘴上说「传男不传女」，但暗地里早就把最核心的染布配方教给了孙女——名是旧的，实已经换了",
                    "村长在会上说要保持传统，转头就支持年轻人搞直播带货——名实分离不是虚伪，是乡土社会的生存智慧",
                ]
            },
        }

    def _init_aesthetic_insights(self):
        """审美意识骨架：《美的历程》9个审美时代"""
        self._aesthetics = [
            AestheticInsight(
                era="远古图腾",
                keyword="龙飞凤舞",
                description="原始巫术礼仪中的审美萌芽。远古歌舞、图腾纹饰、彩陶纹样，不是为了好看，是为了生存——图腾是群体认同的来源，歌舞是集体力量的凝聚。美从诞生之日起就和集体生命捆绑在一起。",
                narrative_transformation="写仪式、写群体性活动、写族群认同的时候，可以参考远古图腾的审美逻辑——美不是装饰，是生存本身。仪式越庄严，说明生存压力越大。",
                representative_works=["仰韶彩陶", "马家窑文化舞蹈纹彩陶盆", "龙图腾演变"],
            ),
            AestheticInsight(
                era="青铜饕餮",
                keyword="狞厉之美",
                description="青铜时代的美是恐怖的、狞厉的。饕餮纹那些张着大嘴的怪兽，不是装饰，是威慑——是统治阶级用审美形式维持社会秩序。但在那恐怖的外形下面，是人类童年时期的原始力量感。",
                narrative_transformation="写权威、写传统的压迫感、写令人敬畏的古老规矩，可以用狞厉之美的审美逻辑。美不一定是舒服的，令人不安的美往往更有力量。",
                representative_works=["司母戊鼎", "四羊方尊", "三星堆青铜面具"],
            ),
            AestheticInsight(
                era="先秦理性",
                keyword="实践理性",
                description="春秋战国是中国思想的轴心时代。儒家把巫术礼仪理性化、生活化，变成日常的人伦秩序；道家则追求与天地合一的精神自由。两者共同塑造了中国人的审美底色——既入世又出世，既讲规矩又想逍遥。",
                narrative_transformation="写儒道互补的人物——表面守礼，内心逍遥；或者相反。中国传统人物的魅力往往在于这种张力：身在规矩中，心在天地外。",
                representative_works=["《论语》", "《庄子》", "先秦诸子散文"],
            ),
            AestheticInsight(
                era="楚汉浪漫",
                keyword="屈骚传统",
                description="楚汉文化是浪漫的、激情的、想象力飞扬的。从《楚辞》到汉赋，从马王堆帛画到霍去病墓石刻，充满了和神鬼、天地、宇宙对话的雄心。这是中国人最富想象力的审美时代。",
                narrative_transformation="写理想主义者、写有浪漫气质的人物、写和天地自然有连接的场景，参考楚汉浪漫的气势。不是小桥流水的美，是大风起兮云飞扬的美。",
                representative_works=["屈原《离骚》", "马王堆T型帛画", "霍去病墓石兽"],
            ),
            AestheticInsight(
                era="魏晋风度",
                keyword="人的觉醒",
                description="魏晋是中国历史上第一次「人的觉醒」——人不再只是伦理和政治的工具，人的才情、容貌、气质本身就有价值。吃药、喝酒、清谈、隐逸，竹林七贤代表了一种对规训的反抗。",
                narrative_transformation="写觉醒的人物、写对抗规训的人物、写「我就要活成我自己」的人物，魏晋风度是最好的审美参照。觉醒不是喊口号，是从骨子里透出的对生命本身的珍视。",
                representative_works=["《世说新语》", "王羲之书法", "顾恺之绘画"],
            ),
            AestheticInsight(
                era="盛唐之音",
                keyword="青春、自由、力量",
                description="盛唐的美是少年的美、青春的美。李白的诗、张旭的草书、吴道子的画、敦煌的飞天——都是一种不受拘束的力量感。那时候的中国人最自信，因为知道自己是世界的中心。",
                narrative_transformation="写人物最意气风发的阶段、写事业上升期、写那种「全世界都在我脚下」的感觉，参考盛唐气象。不是成熟的美，是锋芒毕露的美。",
                representative_works=["李白诗歌", "张旭狂草", "敦煌壁画"],
            ),
            AestheticInsight(
                era="宋元山水",
                keyword="无我之境",
                description="宋元山水画的最高境界是「无我」——画家不是在画风景，是在画自己和宇宙的关系。人在山水间是渺小的，但又是融入的。这是一种东方式的存在美学：我不说话，但我存在。",
                narrative_transformation="写沉默的人物、写用行动代替语言的场景、写人和自然的关系，参考宋元山水的「无我之境」。最深的情感往往不在对话里，在画面的留白里。",
                representative_works=["范宽《溪山行旅图》", "马远《寒江独钓图》", "元四家山水"],
            ),
            AestheticInsight(
                era="明清文艺",
                keyword="世情与人性",
                description="明清是市民文化兴起的时代。从《金瓶梅》到《红楼梦》，从昆曲到年画，审美从帝王将相走向了普通人的日常生活。世俗的、琐碎的、甚至有点俗气的生活本身，成了审美的对象。",
                narrative_transformation="写普通人的生活、写日常中的诗意、写小人物的悲欢，参考明清文艺的世情传统。不要看不起柴米油盐，最深的人性往往藏在最琐碎的日常里。",
                representative_works=["《红楼梦》", "《金瓶梅》", "昆曲《牡丹亭》", "清明上河图"],
            ),
            AestheticInsight(
                era="近现代转型",
                keyword="撕裂与重生",
                description="从鸦片战争到今天，中国审美一直在传统与现代之间撕裂。一边是几千年的文化基因，一边是扑面而来的现代生活。这种撕裂本身就是当代中国最真实的审美状态。",
                narrative_transformation="写当代题材，特别是非遗、传统手艺、城乡碰撞的题材，核心审美就是这种撕裂感。不要假装一切都很和谐，撕裂本身就是真实的美。",
                representative_works=["鲁迅《呐喊》", "刘海粟油画", "当代乡土电影"],
            ),
        ]

    def _init_rituals(self):
        """民俗仪式库：仪式的荒诞推动觉醒"""
        self._rituals = [
            CultureItem(
                id="ritual_001",
                section="ritual",
                theme="死亡与哀悼",
                title="白族丧葬仪式",
                description="白族丧葬融合了佛教、道教和本土巫教元素。流程含入殓、守灵、出殡、下葬、守孝。重要特征：葬礼上要唱「哭丧调」，不仅是悲伤的表达，也是对死者一生的回顾和评价；孝子要在棺前摔碎一个陶罐（「摔丧」），象征与过去的决裂。",
                narrative_application="用一场葬礼作为开场或转折——葬礼是所有隐藏关系浮出水面的时刻。平时不说的话、平时不认的人、平时不承认的秘密，在葬礼上都会冒出来。哭丧调可以作为情感锚点，同一个调子在全剧中反复出现，每次出现人物关系都不同。",
                source="白族民俗研究 + 田野调查",
                examples=[
                    "第8集转折点：奶奶的葬礼上，女主本来想走，听到哭丧调里唱到奶奶年轻时也想逃，但最后还是留了下来——女主第一次理解了奶奶",
                    "摔丧的陶罐上有奶奶亲手扎染的纹样——摔碎的不是陶罐，是女主和过去的关系",
                ],
            ),
            CultureItem(
                id="ritual_002",
                section="ritual",
                theme="婚俗与嫁娶",
                title="白族婚俗",
                description="白族婚姻有「抢亲」遗风（已演变为仪式性表演）、哭嫁（新娘出嫁前要哭，表达对娘家的不舍）、进门跨火盆（驱邪）、拜天地高堂等。新娘进门时要踩着铺在地上的扎染布走——意味着把「外面的不干净」都留在布上，干干净净进婆家。",
                narrative_application="婚礼是展示文化最直观的场景，但不要只展示——让婚礼的某个环节成为冲突的爆发点。比如：新娘拒绝踩扎染布进门（表示她不接受这门亲事/不接受这个身份），或者婚礼进行中有人突然说破一个秘密。仪式越正规，打破仪式的冲击就越强。",
                source="白族民俗研究",
                examples=[
                    "第15集：女主被逼婚，婚礼上她拒绝踩扎染布，赤着脚走出了大门——所有人都惊呆了，因为这是对整个仪式的否定",
                ],
            ),
            CultureItem(
                id="ritual_003",
                section="ritual",
                theme="祭祀与神灵",
                title="本主崇拜",
                description="白族独特的宗教信仰——每个村子都有自己的「本主」（保护神）。本主不一定是正神，可以是英雄、祖先、甚至是一块石头一棵树。本主节的时候，全村人要把本主像从庙里请出来，绕着村子游行，叫「迎本主」。",
                narrative_application="本主崇拜是理解乡土社会的钥匙——神不是高高在上的，是和村子一起生活的。可以用本主节作为社群凝聚力的展示，也可以用「质疑本主」作为觉醒的起点——当一个人开始怀疑全村人都信的东西，就是他/她真正独立的时候。",
                source="《白族本主文化》",
                examples=[
                    "第20集：染坊要拆了，大家去求本主，只有女主说「本主要是灵，奶奶就不会死了」——这句话说出口的瞬间，她和这个村子的关系就变了",
                ],
            ),
            CultureItem(
                id="ritual_004",
                section="ritual",
                theme="成年礼",
                title="白族少女成年礼",
                description="白族少女十四五岁时有「换裙子」仪式——把小时候的裙子换成成人样式的裙子，同时改变发型。仪式由家里的女性长辈主持，意味着少女正式成为成年人，可以参与成人的事务、承担成人的责任。",
                narrative_application="成年礼是人物弧光的绝佳载体——换裙子之前和之后，人物的选择要发生变化。可以用「换裙子」作为象征性场景：表面换的是衣服，实际换的是身份和选择。",
                source="白族民俗研究",
                examples=[
                    "第5集：女主完成成年礼，换上了新裙子，但心里想的是「我不想变成奶奶那样的人」——仪式完成了，但内心的反抗刚刚开始",
                ],
            ),
            CultureItem(
                id="ritual_005",
                section="ritual",
                theme="节日庆典",
                title="三月街 / 绕三灵",
                description="三月街是白族最盛大的节日，每年农历三月在大理举行，集物资交流、赛马、歌舞、宗教活动为一体。绕三灵则是另一种群体性祭祀活动，人们沿着固定路线走，边走边唱边跳，既是祭神也是狂欢。",
                narrative_application="大型节日是群像戏的天然舞台——所有人都在，所有关系线都可以交汇。可以用节日作为重要转折的发生场景：越热闹的场合，越适合发生最孤独的事。",
                source="白族民俗研究",
                examples=[
                    "第12集：三月街上人山人海，所有人都在狂欢，女主一个人站在人群里，收到了城里来的offer——热闹是他们的，她的选择是孤独的",
                ],
            ),
        ]

    def _init_daily_order(self):
        """日常秩序库：节令的更替推动转折"""
        self._daily_orders = [
            CultureItem(
                id="daily_001",
                section="daily_order",
                theme="代际关系",
                title="隔代抚养",
                description="中国乡土社会中，父母外出打工、孩子由祖辈抚养是普遍现象。奶奶/外婆带大的孩子，和父母有感情上的隔阂，但和祖辈有最深的羁绊。这种代际关系是理解当代中国乡土的关键入口。",
                narrative_application="隔代抚养本身就是一个天然的戏剧结构——孩子和祖辈是「旧」的，父母是「新」的。孩子在中间，两边拉扯。祖辈的死亡往往是孩子真正长大的节点——因为那个最旧但最温暖的东西不在了。",
                source="《乡土中国》+ 当代乡土研究",
                examples=[
                    "女主从小跟奶奶长大，父母在城里打工，半年回来一次。她对父母的感情是礼貌的生疏，对奶奶是不讲理的依赖",
                    "奶奶去世后，女主第一次给妈妈打电话，两个人在电话里都哭了，因为她们突然成了最亲的人",
                ],
            ),
            CultureItem(
                id="daily_002",
                section="daily_order",
                theme="节气与生活节奏",
                title="二十四节气与劳作节奏",
                description="传统农耕社会的生活节奏完全由节气决定。什么时候播种、什么时候收获、什么时候做什么事，节气就是时间表。这种节奏和现代人996的时间感完全不同——它是循环的、缓慢的、和自然同步的。",
                narrative_application="用节气作为时间标记。不用「三个月后」，用「从清明到白露」。每个节气可以对应人物的一个状态——立春时心怀希望，芒种时最忙碌，立秋时收获也失落，冬至时最低谷也最适合转折。",
                source="二十四节气 + 《乡土中国》",
                examples=[
                    "全剧30集对应一年中的节气：第1集立春（奶奶去世女主回家），第8集芒种（染坊最忙的时候也是女主最挣扎的时候），第15集立秋（做出选择），第22集霜降（最低谷），第30集冬至后（重新出发）",
                ],
            ),
            CultureItem(
                id="daily_003",
                section="daily_order",
                theme="人情往来",
                title="随礼与人情",
                description="乡土社会的「随礼」不是送礼，是人情的记账本。谁家办了事谁来了、随了多少，都是要记住的，因为以后要还。人情不是钱，是社会关系的货币。一个人如果不随礼，等于主动退出熟人社会。",
                narrative_application="随礼是展示人物在社群中位置的好方式。一个人随礼的方式、金额、态度，能看出他和村里人关系的亲疏。主角离开村子的标志之一，可以是「再也不回去随礼了」——不是舍不得钱，是在退出那个关系网。",
                source="《乡土中国》+ 日常观察",
                examples=[
                    "第7集：村里有人办喜事，女主随了双倍的礼，大家都夸她懂事——但女主自己知道，这是她最后一次随礼了，她在还人情",
                ],
            ),
            CultureItem(
                id="daily_004",
                section="daily_order",
                theme="家庭分工",
                title="男主外女主内",
                description="传统家庭分工：男人在外干活挣钱，女人在家操持家务、照顾老小。这种分工不是谁规定的，是代代相传的「就该这样」。在传统手艺家庭里，往往还有「传男不传女」的潜规则，哪怕女儿比儿子更有天赋。",
                narrative_application="打破「男主外女主内」是女性成长题材的核心动力。女主想继承手艺、想走出家门、想自己决定命运，每一步都在打破这个秩序。打破的不是某个具体的规矩，是整个家庭分工的底层逻辑。",
                source="《乡土中国》「男女有别」",
                examples=[
                    "奶奶嘴上说染坊是传给孙子的，但实际干活、教手艺的都是孙女——奶奶自己也在打破她信奉了一辈子的规矩",
                ],
            ),
            CultureItem(
                id="daily_005",
                section="daily_order",
                theme="邻里关系",
                title="远亲不如近邻",
                description="乡土社会中，邻里关系有时候比亲戚还重要。日常借个东西、帮个忙、看个孩子，都是邻里在做。但邻里之间也最容易产生矛盾——因为太近了，一点摩擦都会被放大。好的时候像一家人，坏的时候能翻脸十年不说话。",
                narrative_application="邻里是最好的「希腊合唱队」——他们的议论就是社会舆论本身。主角做什么事，不用直接说大家怎么看，拍几场邻里聊天的戏就够了。邻里的态度变化，就是整个村子的态度变化。",
                source="《乡土中国》「熟人社会」",
                examples=[
                    "第1集：女主刚回村，几个老太太在村口晒太阳，看见她就小声议论「哟，那不是老李家的孙女吗，在城里混不下去回来了吧」",
                    "第30集：女主的染坊成功了，还是那几个老太太在村口晒太阳，看见她就热情招呼「囡囡回来了，来家里吃饭啊」",
                ],
            ),
        ]

    def _init_spirit(self):
        """精神气质库：精神困境推动内心戏"""
        self._spirits = [
            CultureItem(
                id="spirit_001",
                section="spirit",
                theme="生命观",
                title="儒道互补的生死观",
                description="中国人对死亡的态度是双重的：儒家说「未知生焉知死」，强调活在当下、尽好人的本分；道家说「齐生死」，把生死看作自然变化的一部分。两种态度交织在一起，形成了中国人独特的生命观——不害怕死亡，但要好好活着。",
                narrative_application="写人物面对死亡（自己的或亲人的）的时候，可以用这种儒道交织的态度。不是一味的悲伤，也不是一味的超脱。白天该干活干活（儒家的入世），夜深人静时抬头看天觉得生死都一样（道家的超然）。这种矛盾比单一的悲伤更有深度。",
                source="《美的历程》先秦理性 + 道家思想",
                examples=[
                    "奶奶知道自己快不行了，白天还在染布，跟没事人一样；晚上一个人的时候，摸着手艺最好的那块布，轻轻说「也该走了」",
                ],
            ),
            CultureItem(
                id="spirit_002",
                section="spirit",
                theme="家族意识",
                title="光宗耀祖与家族使命",
                description="中国人最深的精神驱动力之一是「光宗耀祖」。个人的成功不是自己的事，是整个家族的事。反过来，个人的失败也是对家族的亏欠。这种意识既是动力也是枷锁——它让人有力量，也让人不自由。",
                narrative_application="写有家族使命的人物，他/她的每一个选择都要问自己：「对得起列祖列宗吗？」人物最大的成长，就是从「为家族活」变成「为自己活」——这不是不孝，是真正的觉醒。",
                source="《乡土中国》家族 + 中国传统文化",
                examples=[
                    "奶奶一辈子都在守着染坊，不是因为她喜欢染布，是因为「这是祖宗传下来的，不能在我手里断了」——直到临死前她才对女主说「你要是不想守，就不守了」",
                ],
            ),
            CultureItem(
                id="spirit_003",
                section="spirit",
                theme="面子与尊严",
                title="面子文化",
                description="「面子」是理解中国人行为的关键词。面子不是虚荣，是一个人在熟人社会中的全部信用和尊严。为了面子，人可以做很多违背本意的事；丢了面子，等于在社群中社会性死亡。",
                narrative_application="很多冲突的表层是事情本身，深层是「面子」问题。比如两个人吵架，道理谁对谁错不重要，重要的是谁在众人面前输了气势、丢了面子。写人物关系的时候，记得把「面子」这个维度加进去。",
                source="《乡土中国》+ 日常观察",
                examples=[
                    "村长和女主吵架，其实村长知道女主说得对，但他不能让步——一让步他在村里就没威信了，以后说话没人听",
                ],
            ),
            CultureItem(
                id="spirit_004",
                section="spirit",
                theme="精神归宿",
                title="安土重迁与落叶归根",
                description="乡土社会的人对土地有执念——「树高千丈，落叶归根」。哪怕在外闯荡一辈子，老了还是想回来。根在哪里，心就在哪里。但对年轻一代来说，「根」的概念变模糊了——他们出生在城市，或者很小就离开了故乡。",
                narrative_application="写迁徙题材、返乡题材，核心矛盾就是「归还是不归」。不是简单的「要不要回去」，是「哪里才是我的家」。人物最后不一定回去，但她要找到自己的「根」在哪里——可能不是某个地方，是某种精神。",
                source="《乡土中国》「血缘与地缘」",
                examples=[
                    "第28集：女主在城里站稳了脚跟，但每次路过卖扎染布的店都要停下来看——她发现自己不是想回到那个村子，是想念那种「有根」的感觉。最后她在城里开了自己的染坊，把根带走了",
                ],
            ),
            CultureItem(
                id="spirit_005",
                section="spirit",
                theme="集体与个体",
                title="集体主义中的个人觉醒",
                description="中国文化是集体主义的——个人要服从家庭、家族、集体。但现代化的过程，就是个人意识觉醒的过程。从「我们」到「我」，这是一百多年来中国最深刻的精神变迁，也是很多故事的核心驱动力。",
                narrative_application="中国故事的经典母题：一个人从集体中走出来，寻找自我。这个过程是痛苦的，因为集体不只是约束，也是温暖和保护。觉醒的代价，就是失去那种被保护的安全感。",
                source="《乡土中国》「差序格局」 + 魏晋风度（人的觉醒）",
                examples=[
                    "女主一开始和村里所有人一样，按部就班地活。直到奶奶去世，她突然问自己：「如果奶奶不在了，我是谁？」——这个问题把她从「李家的孙女」变成了「我自己」",
                ],
            ),
        ]

    def _init_imagery(self):
        """文化意象库：意象的出现推动情绪"""
        self._imagery = [
            CultureItem(
                id="img_001",
                section="imagery",
                theme="蓝白",
                title="扎染的蓝与白",
                description="扎染的颜色是靛蓝和白。蓝是板蓝根的颜色，是苍山洱海的颜色，是天空的颜色。白是本色，是白布，是大理的云。蓝白之间的晕染，是中国传统审美的典型——不是黑白分明的，是渐变的、模糊的、有余地的。",
                narrative_application="蓝白可以贯穿全剧的视觉系统。每一种情绪对应一种扎染纹样：平静时是均匀的蓝，激动时是深靛蓝，忧伤时是晕开的蓝白，和解时是蓝白交融。人物关系的变化，可以用染布的变化来暗示。",
                source="白族扎染工艺 + 审美意识骨架",
                examples=[
                    "第1集：女主回村，奶奶刚染好的布挂在院子里，全是深蓝色——奶奶的身体还硬朗，规矩还完整",
                    "第15集：女主自己染布，染出来的是不均匀的蓝白相间——她在两种身份之间拉扯",
                    "第30集：女主的新染布，蓝和白融合得很好，有了新的纹样——她找到了自己的方式",
                ],
            ),
            CultureItem(
                id="img_002",
                section="imagery",
                theme="水",
                title="水与流动",
                description="中国文化对水的情感很复杂：老子说「上善若水」，孔子说「逝者如斯夫」，水既是最柔软的也是最有力量的，既是生命的来源也是时间的象征。",
                narrative_application="水是万能意象。染坊里的水是劳作，河边的水是思考，雨水是情绪，溪水是时间的流逝。同一条河，第1集和第30集出现，人物的状态完全不一样——河还是那条河，人已经不是那个人了。",
                source="道家思想 + 中国文化意象",
                examples=[
                    "奶奶教女主染布：「染布就是和水打交道，你急不得，水有它自己的节奏」——说的是染布，也是人生",
                ],
            ),
            CultureItem(
                id="img_003",
                section="imagery",
                theme="月亮",
                title="月是故乡明",
                description="月亮是中国文学里最古老的意象之一。从「举头望明月低头思故乡」到「人有悲欢离合月有阴晴圆缺」，月亮承载了中国人所有关于思念、团圆、缺憾的情感。",
                narrative_application="月亮是远程情感沟通的载体。两个人不在一个地方，但看着同一个月亮——这个意象永远有效。用不用看故事类型，但只要涉及思念、距离、牵挂，月亮都能上。",
                source="中国古典诗词",
                examples=[
                    "第10集：女主在城里的出租屋，奶奶在村里的院子里，两个人同时抬头看月亮。不用打电话，观众知道她们在想彼此",
                ],
            ),
            CultureItem(
                id="img_004",
                section="imagery",
                theme="老物件",
                title="传家宝与旧物",
                description="中国人对老物件有特殊的情感——一个旧镯子、一个老染缸、一本旧账本，背后都是几代人的故事。物件本身不值钱，但它承载的记忆和情感是无价的。",
                narrative_application="老物件是人物弧光的标记物。故事开始时，老物件是束缚（我不想守着这些旧东西）；故事结束时，老物件是连接（我理解了你们，我带着你们继续走）。同一个物件，人物的态度变了，人物就成长了。",
                source="日常观察 + 文化心理",
                examples=[
                    "奶奶的老花镜：第1集女主觉得又老又土，随手放一边；第30集女主自己戴上了奶奶的老花镜在染布——她变成了奶奶，但又不是奶奶",
                ],
            ),
            CultureItem(
                id="img_005",
                section="imagery",
                theme="食物",
                title="家常饭与味道记忆",
                description="中国人的情感很多时候是通过食物表达的。妈妈做的饭、奶奶做的饭、家乡的味道——味道是最顽固的记忆，比视觉和听觉更持久。",
                narrative_application="食物是最生活化的情感载体。和解不一定要说「我原谅你了」，可以是「吃饭吧，菜凉了」。两个人关系好不好，看他们吃饭的样子就知道——拘谨还是放松，客气还是随便。",
                source="日常观察 + 中国饮食文化",
                examples=[
                    "女主和妈妈吵架了，谁也不说话。妈妈默默盛了一碗饭放在女主面前，女主吃了一口就哭了——是小时候的味道，也是妈妈说不出口的道歉",
                ],
            ),
            CultureItem(
                id="img_006",
                section="imagery",
                theme="霸王鞭",
                title="霸王鞭舞",
                description="白族传统舞蹈霸王鞭，舞者手持一根竹鞭（两端扎有铜钱），击打肩、肘、腰、腿、地面，发出有节奏的声响。既是舞蹈也是武术，既有力量感又有韵律感。",
                narrative_application="霸王鞭是白族文化中最有视觉冲击力的元素之一。可以作为情感爆发的载体——开心的时候跳，愤怒的时候跳，悲伤的时候也能跳。不同的情绪，同一个舞蹈，跳法不一样。",
                source="白族民俗",
                examples=[
                    "第25集：所有的事都很糟，女主一个人在院子里跳霸王鞭，越跳越快，越跳越用力，铜钱的声音从清脆变成沉闷——她不是在跳舞，是在发泄",
                ],
            ),
        ]

    # ========== 查询接口 ==========

    def get_rituals(self, theme: Optional[str] = None) -> List[CultureItem]:
        """获取民俗仪式库条目"""
        if theme:
            return [r for r in self._rituals if theme in r.theme or theme in r.title]
        return self._rituals

    def get_daily_order(self, theme: Optional[str] = None) -> List[CultureItem]:
        """获取日常秩序库条目"""
        if theme:
            return [r for r in self._daily_orders if theme in r.theme or theme in r.title]
        return self._daily_orders

    def get_spirit(self, theme: Optional[str] = None) -> List[CultureItem]:
        """获取精神气质库条目"""
        if theme:
            return [r for r in self._spirits if theme in r.theme or theme in r.title]
        return self._spirits

    def get_imagery(self, theme: Optional[str] = None) -> List[CultureItem]:
        """获取文化意象库条目"""
        if theme:
            return [r for r in self._imagery if theme in r.theme or theme in r.title]
        return self._imagery

    def get_social_structure_concept(self, concept_name: str) -> Optional[Dict]:
        """获取社会结构骨架的某个核心概念"""
        return self._social_structure.get(concept_name)

    def get_all_social_concepts(self) -> List[str]:
        """获取所有社会结构概念名"""
        return list(self._social_structure.keys())

    def get_aesthetic_insight(self, era_keyword: str) -> Optional[AestheticInsight]:
        """按时代关键词获取审美洞察"""
        for item in self._aesthetics:
            if era_keyword in item.era or era_keyword in item.keyword:
                return item
        return None

    def get_all_aesthetics(self) -> List[AestheticInsight]:
        """获取所有审美时代洞察"""
        return self._aesthetics

    def recommend_for_drama_type(self, drama_type: str) -> Dict[str, List[CultureItem]]:
        """
        根据短剧类型推荐相关文化知识

        Args:
            drama_type: 短剧类型（非遗文化、现实主义、家庭伦理、悲剧、甜宠、悬疑等）

        Returns:
            按板块分类的推荐条目字典
        """
        drama_type = drama_type.lower()
        recommendations = {
            "ritual": [],
            "daily_order": [],
            "spirit": [],
            "imagery": [],
        }

        if "非遗" in drama_type or "文化" in drama_type or "民族" in drama_type:
            recommendations["ritual"] = self._rituals
            recommendations["imagery"] = [i for i in self._imagery if i.theme in ["蓝白", "霸王鞭"]]
            recommendations["spirit"] = self.get_spirit("家族") + self.get_spirit("精神归宿")
            recommendations["daily_order"] = self.get_daily_order("代际关系") + self.get_daily_order("家庭分工")

        elif "现实" in drama_type or "乡土" in drama_type:
            recommendations["daily_order"] = self._daily_orders
            recommendations["spirit"] = self._spirits
            recommendations["imagery"] = [i for i in self._imagery if i.theme in ["老物件", "食物", "水"]]

        elif "家庭" in drama_type or "伦理" in drama_type:
            recommendations["daily_order"] = self.get_daily_order("代际关系") + self.get_daily_order("家庭分工") + self.get_daily_order("邻里关系")
            recommendations["spirit"] = self.get_spirit("家族意识") + self.get_spirit("面子与尊严")
            recommendations["imagery"] = [i for i in self._imagery if i.theme in ["老物件", "食物"]]

        elif "悲剧" in drama_type:
            recommendations["ritual"] = self.get_rituals("死亡")
            recommendations["spirit"] = self.get_spirit("生命观") + self.get_spirit("集体与个体")

        return recommendations

    def get_full_knowledge(self, sections: Optional[List[str]] = None) -> str:
        """
        获取完整知识库文本，用于注入LLM Prompt

        Args:
            sections: 指定板块（ritual/daily_order/spirit/imagery/social_structure/aesthetic），默认全部
        """
        all_sections = ["social_structure", "aesthetic", "ritual", "daily_order", "spirit", "imagery"]
        target_sections = sections or all_sections

        output_parts = []

        if "social_structure" in target_sections:
            output_parts.append("=" * 60)
            output_parts.append("【社会结构骨架：《乡土中国》8个核心概念】")
            output_parts.append("=" * 60)
            for name, data in self._social_structure.items():
                output_parts.append(f"\n■ {name}")
                output_parts.append(f"  定义：{data['description']}")
                output_parts.append(f"  叙事转化：{data['narrative_transformation']}")
                output_parts.append(f"  剧本示例：")
                for ex in data["script_examples"]:
                    output_parts.append(f"    - {ex}")

        if "aesthetic" in target_sections:
            output_parts.append("\n" + "=" * 60)
            output_parts.append("【审美意识骨架：《美的历程》9个审美时代】")
            output_parts.append("=" * 60)
            for item in self._aesthetics:
                output_parts.append(f"\n■ {item.era}（{item.keyword}）")
                output_parts.append(f"  特征：{item.description}")
                output_parts.append(f"  叙事转化：{item.narrative_transformation}")
                output_parts.append(f"  代表作品：{', '.join(item.representative_works)}")

        section_map = {
            "ritual": ("民俗仪式库（仪式的荒诞推动觉醒）", self._rituals),
            "daily_order": ("日常秩序库（节令的更替推动转折）", self._daily_orders),
            "spirit": ("精神气质库（精神困境推动内心戏）", self._spirits),
            "imagery": ("文化意象库（意象的出现推动情绪）", self._imagery),
        }

        for key, (title, items) in section_map.items():
            if key in target_sections:
                output_parts.append("\n" + "=" * 60)
                output_parts.append(f"【{title}】")
                output_parts.append("=" * 60)
                for item in items:
                    output_parts.append(f"\n◆ {item.title}（{item.theme}）")
                    output_parts.append(f"  描述：{item.description}")
                    output_parts.append(f"  叙事运用：{item.narrative_application}")
                    output_parts.append(f"  来源：{item.source}")
                    if item.examples:
                        output_parts.append(f"  示例：")
                        for ex in item.examples:
                            output_parts.append(f"    - {ex}")

        return "\n".join(output_parts)

    def get_summary(self) -> str:
        """获取文化库概要（用于专家系统提示词开头）"""
        return f"""中华优秀传统文化知识库 V1.2
双骨架架构：社会结构骨架（《乡土中国》{len(self._social_structure)}个核心概念）
          + 审美意识骨架（《美的历程》{len(self._aesthetics)}个审美时代）
四大板块：
  - 民俗仪式库：{len(self._rituals)}条（仪式的荒诞推动觉醒）
  - 日常秩序库：{len(self._daily_orders)}条（节令的更替推动转折）
  - 精神气质库：{len(self._spirits)}条（精神困境推动内心戏）
  - 文化意象库：{len(self._imagery)}条（意象的出现推动情绪）
核心原则：文化不是展示是叙事动力
"""

    def search(self, keyword: str, limit: int = 10) -> List[CultureItem]:
        """关键词搜索整个文化库"""
        keyword = keyword.lower()
        all_items = self._rituals + self._daily_orders + self._spirits + self._imagery
        scored = []
        for item in all_items:
            score = 0
            if keyword in item.title.lower():
                score += 5
            if keyword in item.theme.lower():
                score += 3
            if keyword in item.description.lower():
                score += 2
            if keyword in item.narrative_application.lower():
                score += 2
            if score > 0:
                scored.append((score, item))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [item for _, item in scored[:limit]]


__all__ = [
    "CultureKnowledgeBase",
    "CultureItem",
    "AestheticInsight",
    "CultureSection",
    "AestheticEra",
]
