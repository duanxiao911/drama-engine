"""
§1 角色铸造师专家

职责：三层四维度人设 + 弧光线 + 个性化语料库
将故事方向转化为具体可信的角色

基于《架构设计.md》MVP专家列表 + 《精品短剧创作引擎_通用版.md》§5.1②人设铸造法
"""

import re
from typing import List, Dict, Optional
from .base import ExpertBase, ExpertContext, ExpertOutput


class CharacterForgerExpert(ExpertBase):
    """§1 角色铸造师专家"""
    expert_id = "§1"
    expert_name = "character_forger"
    prompt_file = "character_forger.md"

    def get_system_prompt(self) -> str:
        return """你是一位专精人物塑造的资深编剧，代号§1角色铸造师。

你的核心能力：将抽象的故事方向铸造为有血有肉的真实角色。

角色铸造三层四维度法（必须严格遵循）：

【A. 人物三层结构】
| 层次 | 内容 | 暴露条件 |
| 公共自我（面具） | 社会身份、职业、外貌、谈吐习惯 | 小压力即可见 |
| 私人自我（隐私） | 亲密关系里的样子、脆弱、秘密 | 中压力才暴露 |
| 核心自我（本性） | 最深欲望、恐惧、价值观、底线 | 极限压力才逼出 |

【B. 人物四维度清单】
1. 生理维度：年龄、性别、外貌特征、健康/缺陷
2. 社会维度：阶层、教育、家庭、职业
3. 心理维度：欲望、执念、创伤、内疚、自尊/自卑
4. 道德维度：是非观、底线、良心

【C. 人物双驱动力】
- 表层欲望（want）：角色明确追求的（被看见、复仇、自由）
- 深层欲望（need）：角色真正需要的（自我接纳、放下执念、学会信任）
- 表层恐惧：角色害怕失去的（被抛弃、被遗忘、失去控制）
- 深层恐惧：角色不敢面对的（自己不值得被爱、自己的善良是软弱）

【D. 人物弧光三阶段】
初始状态（有执念、有偏见、有盲点）-冲突考验（不断打脸、不断痛苦、不断动摇）-终极选择（彻底改变）

【E. 人设卡片输出格式】
每个角色必须输出为以下格式（100-200字）：
```
角色名：定位，年龄范围，身份
面具：[公共自我1句话]
隐私：[私人自我1句话]
内核：[核心自我1句话]
驱力：want→need / 表层恐惧→深层恐惧
弧光：[初始]-[考验]-[终极选择]
四维度关键词：生理[ ] 社会[ ] 心理[ ] 道德[ ]
```

铁律：
- 人物不等于设定标签，人物=压力下的选择
- 每集必须让至少一个人物的一层裂开（面具被撕/隐私被窥/本性被逼出）
- 弧光必须通过选择完成，不能靠台词说"我变了"
- 人设自检六宗罪：标签化/前后矛盾/只有怪癖没灵魂/没有欲望/只有痛苦没选择/说教人物
""" + self._get_red_lines_supplement()

    def _get_red_lines_supplement(self) -> str:
        return """
=== 合规补充 ===
- 禁止超自然金手指（异能、修仙、血脉觉醒）
- 禁止暴力私刑（以暴制暴、个人复仇暴力）
- 禁止危险道具+血腥（匕首、出血特写）
- 禁止人格羞辱+霸凌正面展示
- 禁止低俗擦边
- 禁止封建迷信
"""

    def get_user_prompt(self, context: ExpertContext, **kwargs) -> str:
        story_direction = context.story_direction or kwargs.get("story_direction", "")
        story_premise = context.story_premise or kwargs.get("story_premise", "")
        story_type = context.project_config.get("drama_type", "现实主义") if context.project_config else "现实主义"

        prompt = f"""请为以下故事铸造核心角色：

【故事方向】
{story_direction}

【一句话前提】
{story_premise}

【故事类型】
{story_type}

任务：
1. 识别故事所需的核心角色（主角1-2人、反派/对手1人、关键配角1-2人）
2. 使用三层四维度法为每个核心角色铸造人设
3. 输出角色弧光线（悲剧用5阶段，甜宠/悬疑用3阶段）
4. 输出个性化语料库关键词（该角色特有的说话方式、用词习惯）

请按【E. 人设卡片输出格式】为每个角色输出完整人设卡。
"""

        return prompt

    def validate_output(self, output: str) -> tuple[bool, List[str]]:
        errors = []
        # 检查是否包含角色定义（放宽匹配）
        has_character = any(kw in output for kw in ["角色名", "主角", "反派", "人物", "对手", "配角"])
        if not has_character:
            errors.append("未找到角色定义")
        # 检查是否有角色标记（多种格式）
        card_patterns = [
            r'\*\*[^*]{2,10}\*\*[：:]',
            r'-\s*[^-\n]{2,10}[：:]',
            r'角色名[：:][^\n]+',
            r'###+\s*[^#\n]+',
        ]
        card_count = sum(len(re.findall(p, output)) for p in card_patterns)
        if card_count < 1 and "主角" not in output:
            errors.append("角色信息不足")
        return len(errors) == 0, errors

    def parse_output(self, content: str) -> Dict:
        """解析角色铸造输出为结构化数据"""
        cards = self.parse_character_cards(content)
        sd = {
            "character_cards": cards,
            "character_count": len(cards),
            "raw": content,
        }
        # 提取故事前提
        for pattern in [r'一句话前提[：:]\s*(.+)', r'核心前提[：:]\s*(.+)']:
            m = re.search(pattern, content)
            if m:
                sd["story_premise"] = m.group(1).strip()
                break
        return sd

    def parse_character_cards(self, output: str) -> List[Dict]:
        """解析输出中的角色卡片（支持多种格式）"""
        cards = []

        # 格式1：角色名：xxx
        blocks = re.split(r'角色名[：:]', output)
        if len(blocks) > 1:
            for block in blocks[1:]:
                name_match = re.match(r'\s*(\S+)', block)
                if name_match:
                    card = {"name": name_match.group(1), "raw": block.strip()[:200]}
                    for line in block.strip().split('\n'):
                        line = line.strip()
                        if line.startswith("面具：") or line.startswith("面具:"):
                            card["mask"] = line.split("：", 1)[-1].split(":", 1)[-1].strip()
                        elif line.startswith("隐私：") or line.startswith("隐私:"):
                            card["private"] = line.split("：", 1)[-1].split(":", 1)[-1].strip()
                        elif line.startswith("内核：") or line.startswith("内核:"):
                            card["core"] = line.split("：", 1)[-1].split(":", 1)[-1].strip()
                        elif line.startswith("驱力：") or line.startswith("驱力:"):
                            card["drive"] = line.split("：", 1)[-1].split(":", 1)[-1].strip()
                        elif line.startswith("弧光：") or line.startswith("弧光:"):
                            card["arc"] = line.split("：", 1)[-1].split(":", 1)[-1].strip()
                    cards.append(card)
            return cards

        # 格式2：### 角色名 或 #### 角色名
        sections = re.split(r'###+\s+', output)
        if len(sections) > 1:
            for section in sections[1:]:
                name_match = re.match(r'([^\n（(]+)', section)
                if name_match:
                    name = name_match.group(1).strip()
                    if len(name) <= 20 and name not in ['角色语料库', '对白风格卡', '钩子链设计']:
                        cards.append({"name": name, "raw": section.strip()[:200]})
            if cards:
                return cards

        # 格式3：**主角**：xxx / **反派**：xxx
        bold_blocks = re.split(r'\*\*([^*]{2,10})\*\*[：:]\s*', output)
        if len(bold_blocks) > 2:
            for i in range(1, len(bold_blocks) - 1, 2):
                name = bold_blocks[i].strip()
                body = bold_blocks[i + 1] if i + 1 < len(bold_blocks) else ""
                cards.append({"name": name, "raw": body.strip()[:200]})
            return cards

        # 格式4：- 主角：xxx / - 反派：xxx
        dash_matches = re.findall(r'-\s+([^-\n]{2,10})[：:]\s*\n([\s\S]*?)(?=\n-\s+[^-\n]{2,10}[：:]|\n#|\Z)', output)
        for name, body in dash_matches:
            cards.append({"name": name.strip(), "raw": body.strip()[:200]})

        return cards


# 注册
from .base import ExpertRegistry
ExpertRegistry.register("§1", CharacterForgerExpert)
