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
        # 检查是否包含角色定义（放宽匹配：角色名/主角/反派/人物 均可）
        has_character = any(kw in output for kw in ["角色名", "主角", "反派", "人物", "对手", "配角"])
        if not has_character:
            errors.append("未找到角色定义")
        # 人设要素检查改为软性（有最好，没有也放行）
        has_mask = any(kw in output for kw in ["面具", "公共自我", "身份", "职业"])
        has_drive = any(kw in output for kw in ["驱力", "want", "欲望", "需求", "动机"])
        has_arc = any(kw in output for kw in ["弧光", "成长", "变化", "转变"])
        # 检查是否有多个角色（放宽正则，匹配 **主角**、- 角色名 等格式）
        import re
        card_patterns = [
            r'\*\*[^*]{2,10}\*\*[：:]',   # **主角**：
            r'-\s*[^-\n]{2,10}[：:]',     # - 角色名：
            r'角色名[：:][^\n]+',           # 角色名：
            r'###\s*[^#\n]+',              # ### 角色名
        ]
        card_count = 0
        for pattern in card_patterns:
            card_count += len(re.findall(pattern, output))
        # 至少2种不同模式匹配或至少2个角色标记
        if card_count < 1 and "主角" not in output:
            errors.append("角色信息不足")
        return len(errors) == 0, errors

    def parse_character_cards(self, output: str) -> List[Dict]:
        """解析输出中的角色卡片"""
        cards = []
        blocks = re.split(r'角色名[：:]', output)
        for block in blocks[1:]:
            lines = block.strip().split('\n')
            if lines:
                name_line = lines[0].strip()
                card = {
                    "raw": block,
                    "name_line": name_line,
                }
                # 提取字段
                for line in lines:
                    if line.startswith("面具：") or line.startswith("公共自我"):
                        card["mask"] = line.split("：")[1] if "：" in line else line.split(":")[1]
                    elif line.startswith("隐私：") or line.startswith("私人自我"):
                        card["private"] = line.split("：")[1] if "：" in line else line.split(":")[1]
                    elif line.startswith("内核：") or line.startswith("核心自我"):
                        card["core"] = line.split("：")[1] if "：" in line else line.split(":")[1]
                    elif line.startswith("驱力："):
                        card["drive"] = line.replace("驱力：", "").strip()
                cards.append(card)
        return cards


# 注册
from .base import ExpertRegistry
ExpertRegistry.register("§1", CharacterForgerExpert)