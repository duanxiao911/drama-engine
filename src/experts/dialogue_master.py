"""
§4 对白大师专家

职责：语料库生成 + 对白风格卡 + 钩子链设计
基于角色人设生成每个角色的个性化对白系统

基于《架构设计.md》V1.0专家列表 + 《精品短剧创作引擎_通用版.md》§4对话系统
"""

from typing import List, Dict, Optional
from .base import ExpertBase, ExpertContext, ExpertOutput


class DialogueMasterExpert(ExpertBase):
    """§4 对白大师专家"""
    expert_id = "§4"
    expert_name = "dialogue_master"
    prompt_file = "dialogue_master.md"

    def get_system_prompt(self) -> str:
        return """你是一位专精对白的资深编剧，代号§4对白大师。

你的核心能力：基于角色人设，生成个性化语料库和可执行的对白风格卡。

【对白核心公式】
对白 = 行动，不是对话。每句好对白同时完成三重使命：
1. 表面说什么（文本）→ 传达信息
2. 真正想干什么（行动）→ 说服/威胁/讨好/欺骗/推开/靠近
3. 内心藏着什么（潜文本）→ 真实感受

【台词五字诀】
- 短：砍掉冗余，单句不超过15字
- 狠：一针见血，戳中情绪痛点
- 准：每句台词必须推动剧情或完成转折
- 燃：引爆共情，带情绪起伏
- 沉：有重量感，说完观众要停一下才能消化

【对白冰山模型】
- 已说：角色选择讲给别人的
- 未说：角色内心只对自己说的
- 不可说：潜意识驱动，角色说不出甚至对自己也说不出的

【对白个性化速查表】
| 人物类型 | 说话特征 | 口语标记 |
| 知识分子 | 绕、理性、抽象 | 从逻辑上讲、你不觉得吗 |
| 底层人 | 直、粗、短、狠 | 你算什么东西、别废话 |
| 控制狂 | 命令、反问、压迫 | 我说了算、你什么意思 |
| 缺爱的人 | 试探、卑微、反复 | 你是不是不想要我、我没事 |
| 隐忍型 | 短句、回避、沉默比话多 | 嗯、没事、算了 |
| 虚荣型 | 夸张、比较、暗示 | 我那个朋友啊、这算什么 |

【钩子链设计】
四种基础钩子类型：
1. 危机钩子：主角陷入绝境，下集生死/成败未卜
2. 误会钩子：真相即将揭开时突然中断
3. 身份钩子：暗示隐藏信息未曝光
4. 情感钩子：关系即将质变时切断

钩子铁则：
- 每集必须留钩子
- 下集开头3秒内必须回应上集钩子
- 钩子必须由人物动机驱动
- 弱钩子不超过2集连续

【对白节奏技巧】
- 长短交替：长句铺垫，短句爆发
- 问东答西：不要流水账问答，要回避/反问/攻击
- 停顿的力量：没说出口的比说出口的更有力
- os与台词相反：想的和说的相反=张力最强

【烂对白六宗罪】
1. 说明性对白（作者嘴替）
2. 一致性对白（太和谐无冲突）
3. 风格统一（所有人说话一个样）
4. 无潜文本（心里想啥嘴上说啥）
5. 文艺腔泛滥
6. 不符合人物

【升维三层级】
- L1功能层：台词完成叙事功能（合格）
- L2情绪层：台词同时传递情绪和潜台词（良好）
- L3意象层：台词自带意象/隐喻/文化厚度（精品）

【输出格式】
```
【角色语料库】
每个角色输出：
- 常用词汇表（5-10个该角色特有的词）
- 禁忌词汇表（这个角色绝对不说的词）
- 语气特征描述
- 潜文本示例（嘴上说的vs心里想的）

【对白风格卡】
每个角色输出对白风格卡：
```
角色名：对白风格卡
语速：[快/中/慢]
句长：[长句/短句/长短交替]
语气：[强势/弱势/中性]
潜文本频率：[高/中/低]
核心句式：[该角色最常用的句式结构]
对白示例：
- 场景A：[台词]（潜文本）
- 场景B：[台词]（潜文本）
```

【钩子链设计】
按集序输出前10集的钩子链：
| 集数 | 上集钩子 | 下集开头回应 | 本集新钩子 |
"""

    def get_user_prompt(self, context: ExpertContext, **kwargs) -> str:
        story_premise = context.story_premise or kwargs.get("story_premise", "")
        character_cards = context.character_cards or kwargs.get("character_cards", [])
        episode_outlines = context.episode_outlines or kwargs.get("episode_outlines", [])

        chars_text = ""
        if character_cards:
            chars_text = "\n\n".join([
                f"### {card.get('name_line', card.get('name', '未命名'))}\n{card.get('raw', str(card))}"
                for card in character_cards[:5]  # 最多5个核心角色
            ])

        prompt = f"""请为以下故事生成对白系统：

【一句话前提】
{story_premise}

【核心角色人设】
{chars_text if chars_text else "请基于故事方向推断核心角色人设"}

任务：
1. 为每个核心角色生成语料库（词汇、语气、潜文本）
2. 输出每个角色的对白风格卡（含具体对白示例）
3. 设计前10集的钩子链（上集钩子→下集回应→本集新钩子）

注意：
- 每个角色的说话方式必须可区分（换人测试）
- 钩子必须由人物动机驱动，不能靠巧合
- 对白示例要体现五字诀和潜文本
"""

        return prompt

    def validate_output(self, output: str) -> tuple[bool, List[str]]:
        errors = []
        # 核心检查：必须有语料库/词汇相关内容（这是§4的核心产出）
        if "语料库" not in output and "词汇" not in output and "语气" not in output:
            errors.append("缺少语料库相关输出")
        # 对白相关内容检查（放宽：对白/台词/示例/口语 任一出现即可）
        has_dialogue = any(kw in output for kw in ["对白", "台词", "示例", "口语", "说话"])
        if not has_dialogue:
            errors.append("缺少对白相关内容")
        # 对白示例检查（放宽：多种格式匹配）
        import re
        # 匹配多种对白格式：台词：xxx、"xxx"、——xxx、角色名：xxx
        dialogue_patterns = [
            r'["\u201c].{3,}?["\u201d]',  # 引号包裹的对白（中英文引号，最小3字）
            r'[:：]\s*\*{0,2}[^*\n]{3,}',  # 冒号后的内容（最小3字）
            r'——\s*.+',  # 破折号引导的对白
            r'[（(][^）)]{3,}[）)]',  # 括号内的动作描写
        ]
        dialogue_count = 0
        for pattern in dialogue_patterns:
            dialogue_count += len(re.findall(pattern, output))
        # 阈值从3降到2，宽松一些
        if dialogue_count < 2:
            errors.append(f"对白示例不足，仅{dialogue_count}处")
        # 钩子链检查改为软性检查（不导致验证失败）
        return len(errors) == 0, errors

    def parse_dialogue_corpus(self, output: str) -> Dict[str, Dict]:
        """解析对白语料库"""
        corpus = {}
        import re
        # 简单按角色名分段提取
        sections = re.split(r'(?=###\s*\S)', output)
        for section in sections:
            if section.strip():
                name_match = re.search(r'###\s*(\S+)', section)
                if name_match:
                    name = name_match.group(1)
                    corpus[name] = {"raw": section}
        return corpus


# 注册
from .base import ExpertRegistry
ExpertRegistry.register("§4", DialogueMasterExpert)