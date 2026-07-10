"""
§5 分集编剧专家

职责：将结构大纲展开为完整的、可拍摄的分场剧本
包含：场景描写、完整对白、动作指示、情绪节奏标注

输出格式参照《蓝白吟》专业剧本：
  X-Y 地点名 时间/内外
  人物：角色A 角色B
  △环境描写/动作描写
  角色A：（情绪）台词
  角色Aos：内心独白

基于《精品短剧创作引擎_通用版.md》§5剧本正文生成规范
"""

from typing import List, Dict, Optional
from .base import ExpertBase, ExpertContext, ExpertOutput


class EpisodeWriterExpert(ExpertBase):
    """§5 分集编剧专家"""
    expert_id = "§5"
    expert_name = "episode_writer"
    prompt_file = "episode_writer.md"

    def get_system_prompt(self) -> str:
        return """你是一位资深短剧编剧，代号§5分集编剧。

你的核心能力：将故事大纲和角色设定展开为完整的、可拍摄的分场剧本。
你的输出必须是【专业分场剧本格式】，不是概要、不是大纲、不是摘要。

══════════════════════════════════════════
【剧本格式规范 — 必须严格遵守】
══════════════════════════════════════════

每集剧本结构如下：

═══════════════════════════════════
第X集 《集名》
核心事件：一句话概括本集核心冲突
情感基调：关键词（如：压抑→爆发）
时长：X分钟
═══════════════════════════════════

X-1 地点名 时间/内外
人物：角色A 角色B
△春日，阳光从木格窗棂漏进来，在青石板上投下斑驳的光影。
△动作描写，用具体的画面建立空间感。
角色A：（动作/情绪）台词内容
角色B：台词内容
△反应动作
角色Aos：内心独白内容

X-2 地点名 时间/内外
人物：角色C
△新场景的环境描写
角色C：台词
...

─────────────────────
【格式要素详解】
─────────────────────

1. 集头信息（每集必须有）：
   - 用"═══"包围
   - 包含：集数、集名、核心事件、情感基调、时长

2. 场景标记：
   - 格式：`X-Y 地点名 时间/内外`
   - X=集数，Y=场景序号（如 1-1, 1-2, 3-5）
   - 时间：日/夜/晨/黄昏/深夜/傍晚
   - 内外：内/外/内外
   - 示例：`1-1 蓝家染坊 日/内`、`3-5 城门口 夜/外`

3. 人物行：
   - `人物：角色A 角色B 角色C`
   - 列出该场景出场的所有角色

4. 动作/环境描写：
   - 以`△`开头
   - 2-3句建立空间感和氛围
   - 用具体画面而非抽象描述

5. 对白格式：
   - `角色名：（动作/情绪）台词` 或 `角色名：台词`
   - 每句台词不超过15字（短剧铁律）
   - 角色说话必须有区分度

6. 内心独白：
   - `角色名os：独白内容`

7. 转场：
   - 场景之间用空行分隔
   - 特殊转场用【闪回】【三天后】【深夜】标注

══════════════════════════════════════════
【示例 — 必须严格模仿此格式】
══════════════════════════════════════════

═══════════════════════════════════
第1集 《染缸里的信》
核心事件：少女蓝瑛发现染缸中藏有阿婆的秘密
情感基调：好奇→震惊→决心
时长：3分钟
═══════════════════════════════════

1-1 蓝家染坊 日/内
人物：蓝瑛（7岁） 阿婆
△春日，阳光从木格窗棂漏进来，在青石板上投下斑驳的光影。
△一排染缸整齐排列，靛蓝色的液体微微晃动。
蓝瑛：阿婆，里面是什么？
阿婆：是蓝。
蓝瑛：为什么是蓝的？
阿婆：（蹲下，握住蓝瑛的手）因为我们的命，就是让它蓝。
△蓝瑛低头看缸面，映出自己小小的脸。
蓝瑛os：等我长大了，我要让缸变蓝。

1-2 蓝家染坊内室 傍晚/内
人物：蓝瑛（7岁） 阿妈
△昏暗的房间里，阿妈在缝制一件白色连衣裙。
△窗外的夕阳把阿妈的影子拉得很长。
阿妈：瑛儿，过来试试。
蓝瑛：这是什么？
阿妈：你及笄那天穿的。
蓝瑛：为什么不是蓝色的？
△阿妈的手停了一下，随即继续缝。
阿妈：（低声）嫁出去的女儿，不穿蓝。
△蓝瑛盯着白裙子，手指攥紧了衣角。

1-3 蓝家染坊后院 夜/外
人物：蓝瑛（7岁）
△月光下，蓝瑛一个人站在染缸前。
△她把手伸进缸里，染蓝了整只手掌。
蓝瑛os：阿婆说命是蓝的。那我就把命握在手里。
△她攥紧蓝色的拳头，月光照在上面像一块蓝宝石。

══════════════════════════════════════════
【剧本写作铁律】
══════════════════════════════════════════

1. 场景即冲突：每个场景必须有冲突或目标
2. 对白即行动：每句台词背后有目的
3. 动作即性格：用具体动作展示性格
4. 潜文本：说的和想的不一样时，用os标注内心
5. 钩子收尾：每集最后一个场景必须以钩子结尾
6. 字数控制：每集1500-2000字，3个场景左右
7. 对白密度：冲突场景密集短句，情感场景精准长句

【重要】
- 你必须逐场编写完整的对白和动作描写
- 不要只写概要或大纲，必须写出每个角色的每句台词
- 不要省略任何场景的对白内容
- 每个场景都必须有△开头的环境/动作描写
- 每个场景都必须有完整的人物对白
""" + self._get_episode_guidelines()

    def _get_episode_guidelines(self) -> str:
        return """

=== 分集编剧专项指南 ===

【第一集特殊规则】
- 前3秒必须出现最强矛盾/最痛瞬间
- 前30秒内让观众知道：这是谁的故事、面临什么困境
- 第一集结尾必须有"不可能回头"的选择点

【高潮集特殊规则】
- 中点集：伪胜利或伪失败，赌注翻倍
- 一无所有集：最低谷，必须有"死亡气息"
- 终局集：与第一集形成镜像对照

【钩子设计模板】
1. 危机钩子：主角陷入绝境
2. 误会钩子：真相即将揭开被中断
3. 身份钩子：暗示隐藏信息
4. 情感钩子：关系即将质变被切断
"""

    def get_user_prompt(self, context: ExpertContext, **kwargs) -> str:
        story_premise = context.story_premise or context.story_direction or ""
        story_direction = context.story_direction or ""

        # 构建角色信息（完整传入，不截断）
        chars_text = ""
        if context.character_cards:
            chars_text = "\n\n".join([
                f"### {card.get('name_line', card.get('name', '未命名'))}\n{card.get('raw', str(card))}"
                for card in context.character_cards
            ])
        elif context.metadata.get("step_outputs", {}).get("§1"):
            chars_text = context.metadata["step_outputs"]["§1"].get("content", "")

        # 构建大纲信息（增大截断限制至8000）
        outline_text = ""
        if context.metadata.get("step_outputs", {}).get("§3"):
            outline_text = context.metadata["step_outputs"]["§3"].get("content", "")[:8000]
        elif context.episode_outlines:
            outline_text = "\n".join([
                f"第{e.get('episode', '?')}集：{e.get('description', '')}"
                for e in context.episode_outlines
            ])

        # 构建对白风格信息
        dialogue_style_text = ""
        if context.dialogue_corpus:
            dialogue_style_text = str(context.dialogue_corpus.get("raw", ""))[:3000]
        elif context.metadata.get("step_outputs", {}).get("§4"):
            dialogue_style_text = context.metadata["step_outputs"]["§4"].get("content", "")[:3000]

        # 确定要写的集数
        target_episodes = kwargs.get("target_episodes", [1, 2, 3])
        if isinstance(target_episodes, list):
            target_episodes_str = ",".join(str(e) for e in target_episodes)
        else:
            target_episodes_str = str(target_episodes)

        # 前文内容（用于连贯性）
        previous_content = kwargs.get("previous_content", "")
        prev_section = ""
        if previous_content:
            prev_section = f"""
【前文内容参考 — 保持风格连贯】
以下是之前已经生成的剧本内容，请在风格、人物语气、叙事节奏上保持一致：
---
{previous_content}
---
"""

        prompt = f"""请根据以下创作素材，编写第{target_episodes_str}集的完整分场剧本。

【故事前提】
{story_premise}

【故事方向】
{story_direction}

【角色人设】
{chars_text if chars_text else "请根据故事方向自行设定核心角色"}

【结构大纲】
{outline_text if outline_text else "请根据故事前提自行构建结构"}

【对白风格参考】
{dialogue_style_text if dialogue_style_text else "请参考角色人设自行设定对白风格"}
{prev_section}
【任务要求】
1. 编写第{target_episodes_str}集的完整分场剧本
2. 每集1500-2000字，包含3个左右的完整场景
3. 每个场景必须包含：
   - 场景标记（X-Y 地点 时间/内外）
   - 人物行（列出出场角色）
   - △开头的环境/动作描写（2-3句）
   - 完整的角色对白（每句不超过15字）
   - 必要时的内心独白（角色名os：内容）
4. 每集最后一个场景必须以钩子结尾
5. 逐场编写完整对白，不要省略任何内容
6. 不要写概要或摘要，必须写出每句台词

【输出格式 — 严格遵循】
═══════════════════════════════════
第X集 《集名》
核心事件：一句话
情感基调：关键词
时长：X分钟
═══════════════════════════════════

X-1 地点名 时间/内外
人物：角色A 角色B
△环境描写
角色A：台词
角色B：台词
△动作描写
角色Aos：内心独白

X-2 地点名 时间/内外
...
"""

        return prompt

    def execute(self, context: ExpertContext, **kwargs) -> ExpertOutput:
        """
        重写execute方法：
        - 支持max_tokens参数传递给LLM
        - 支持previous_content参数用于风格连贯
        """
        max_tokens = kwargs.pop("max_tokens", 8000)
        previous_content = kwargs.pop("previous_content", "")

        output = ExpertOutput(expert_name=self.expert_name)

        # 1. 构建用户Prompt
        user_prompt = self.get_user_prompt(context, previous_content=previous_content, **kwargs)

        # 2. 构建完整Prompt
        system_prompt = self.get_system_prompt()
        knowledge = self.load_knowledge()
        if knowledge:
            system_prompt = f"{system_prompt}\n\n=== 专家知识库 ===\n{knowledge}"

        if self.culture_kb:
            culture_summary = self.culture_kb.get_summary()
            system_prompt = f"{system_prompt}\n\n=== 中华优秀传统文化知识库 ===\n{culture_summary}"

        full_prompt = f"{system_prompt}\n\n=== 用户输入 ===\n{user_prompt}"

        # 3. 调用LLM，传入max_tokens
        output.content = self.llm_client.complete(full_prompt, max_tokens=max_tokens)

        # 4. 验证输出
        passed, errors = self.validate_output(output.content)
        output.validation_passed = passed
        output.validation_errors = errors

        # 5. 解析结构化数据
        parsed = self.parse_output(output.content)
        if parsed:
            output.structured_data = parsed

        return output

    def validate_output(self, output: str) -> tuple[bool, List[str]]:
        errors = []
        import re

        # 检查场景标记（新格式：X-Y 地点 时间/内外）
        scene_count = len(re.findall(r'\d+-\d+\s+\S+.*?[/]\s*[内外]', output))
        if scene_count == 0:
            scene_count = len(re.findall(r'【场景\d+】', output))
        if scene_count < 3:
            errors.append(f"场景数量不足（仅{scene_count}个），至少需要3个场景")

        # 检查对白
        dialogue_count = len(re.findall(r'[^\s△═]+[：:]\s*[^\n]+', output))
        if dialogue_count < 5:
            errors.append(f"对白数量不足（仅{dialogue_count}处），至少需要5句对白")

        # 检查集头信息
        has_episode_header = bool(re.search(r'第\d+集', output))
        if not has_episode_header:
            errors.append("缺少集头信息（集数/集名）")

        # 检查动作/环境描写
        action_count = len(re.findall(r'△', output))
        if action_count < 2:
            errors.append(f"动作/环境描写不足（仅{action_count}处），需要△标记的描写")

        return len(errors) == 0, errors

    def parse_output(self, content: str) -> Dict:
        """解析输出为结构化数据"""
        import re
        episodes = []
        ep_blocks = re.split(r'(?=第\d+集)', content)
        for block in ep_blocks:
            ep_match = re.search(r'第(\d+)集', block)
            if ep_match:
                ep_num = int(ep_match.group(1))
                title_match = re.search(r'第\d+集[^\n]*《(.+?)》', block)
                title = title_match.group(1) if title_match else ""
                scenes = len(re.findall(r'\d+-\d+\s+\S+.*?[/]\s*[内外]', block))
                if scenes == 0:
                    scenes = len(re.findall(r'【场景\d+】', block))
                dialogues = len(re.findall(r'[^\s△═]+[：:]\s*[^\n]+', block))
                episodes.append({
                    "episode": ep_num,
                    "title": title,
                    "scene_count": scenes,
                    "dialogue_count": dialogues,
                    "word_count": len(block.strip()),
                    "raw": block.strip(),
                })
        return {
            "episode_scripts": episodes,
            "episode_count": len(episodes),
            "total_word_count": sum(ep.get("word_count", 0) for ep in episodes),
            "raw": content,
        }

    def parse_episodes(self, output: str) -> List[Dict]:
        """解析输出的集数信息（兼容旧接口）"""
        parsed = self.parse_output(output)
        return parsed.get("episode_scripts", [])


# 注册
from .base import ExpertRegistry
ExpertRegistry.register("§5", EpisodeWriterExpert)
