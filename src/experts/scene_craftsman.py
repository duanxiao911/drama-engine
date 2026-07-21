"""
§11 场景工匠（Scene Craftsman）

职责：场景氛围细化专家
将剧本中的场景描写从"够用"提升到"沉浸式"
通过五感系统（视觉+听觉+嗅觉+触觉+味觉）和环境叙事增强画面代入感
融入非遗/地域文化元素的文化质感

基于 Wave2 架构设计
"""

import re
from typing import List, Dict, Optional
from .base import ExpertBase, ExpertContext, ExpertOutput


# 五感系统定义
FIVE_SENSES = {
    "visual": {
        "name": "视觉",
        "required": True,
        "elements": ["光影", "色彩", "构图"],
        "examples": ["自然光/人工光/烛光", "主色调+点缀色", "远景/中景/特写"],
    },
    "audio": {
        "name": "听觉",
        "required": True,
        "elements": ["环境音", "动作音", "静默"],
        "examples": ["街道喧嚣/虫鸣/风声", "脚步/开门/翻书", "刻意留白"],
    },
    "smell": {
        "name": "嗅觉",
        "required": False,
        "elements": ["自然气息", "工艺气味", "生活气息"],
        "examples": ["泥土/花香/雨后空气", "靛蓝染料/棉布/木屑", "饭菜香/旧书"],
    },
    "touch": {
        "name": "触觉",
        "required": False,
        "elements": ["温度", "质感", "痛感"],
        "examples": ["冷风/热铁/凉水面", "粗糙麻布/光滑丝绸", "针刺/绳勒"],
    },
    "taste": {
        "name": "味觉",
        "required": False,
        "elements": ["味觉体验"],
        "examples": ["泪水咸味/茶水苦涩/饭食温热"],
    },
}


class SceneCraftsmanExpert(ExpertBase):
    """§11 场景工匠"""
    expert_id = "§11"
    expert_name = "scene_craftsman"
    prompt_file = "scene_craftsman.md"

    def get_system_prompt(self) -> str:
        senses_text = "\n".join([
            f"  {'[必选]' if v['required'] else '[选用]'} {v['name']}：{', '.join(v['elements'])}"
            for v in FIVE_SENSES.values()
        ])

        return f"""你是一位场景氛围细化专家，代号§11场景工匠。

你的核心能力：将剧本中的场景描写从"够用"提升到"沉浸式"，通过五感系统和环境叙事增强画面代入感。

【五感系统】
{senses_text}

【场景氛围三层结构】
1. 基础氛围：场景基调（时间+空间+光线+色彩建立的基调）
2. 情绪氛围：角色带入的情绪（角色进入后，空间因角色情绪产生变化）
3. 转折氛围：剧情变化导致氛围转变（冲突爆发/和解/揭秘时的氛围骤变）

【环境叙事原则】
- 用环境细节暗示角色情绪和剧情走向，不是直接说明
- 物件承载记忆：旧照片/褪色信/磨旧的手镯——物件比台词更有分量
- 天气即情绪：暴雨=崩溃/转折，晴转阴=危机将至，日出=重生
- 文化质感：非遗/地域文化元素融入场景（扎染的靛蓝气息、织机的声响、大理的风）

【场景描写模板】

【场景X】内景/外景 地点 时间

[氛围标注]
视觉：[光影+色彩+构图]
听觉：[环境音+动作音]
[嗅觉/触觉/味觉：场景需要时补充]

[环境描写：2-3句建立空间感]
[情绪氛围：角色带入后的空间变化]

角色名：台词

[转折标注：氛围变化时标注]

【铁律】
1. 每个场景至少激活3种感官（视觉+听觉为必选）
2. 环境描写不超过3句，不要喧宾夺主
3. 氛围为剧情服务，不写与情绪无关的景色
4. 文化元素是叙事动力，不是装饰品
"""

    def get_user_prompt(self, context: ExpertContext, **kwargs) -> str:
        # 获取原始剧本
        script_text = ""
        if context.metadata.get("step_outputs", {}).get("§5"):
            script_text = context.metadata["step_outputs"]["§5"].get("content", "")[:8000]
        elif context.metadata.get("episode_scripts"):
            script_text = str(context.metadata["episode_scripts"])[:8000]

        # 项目配置
        project_config = context.project_config or {}
        story_direction = context.story_direction or ""
        culture_theme = project_config.get("culture_theme", "")

        # 视觉方案参考
        visual_scheme = ""
        if context.visual_scheme:
            visual_scheme = str(context.visual_scheme)[:2000]
        elif context.metadata.get("step_outputs", {}).get("§13"):
            visual_scheme = context.metadata["step_outputs"]["§13"].get("content", "")[:2000]

        prompt = f"""请对以下剧本进行场景氛围增强。

【故事方向】{story_direction}
{f'【文化主题】{culture_theme}' if culture_theme else ''}

【原始剧本】
{script_text if script_text else "暂无剧本内容"}

{f'【视觉方案参考】\n{visual_scheme}' if visual_scheme else ''}

任务：
1. 逐场景检查当前氛围描写是否达到沉浸标准
2. 为每个场景补充五感描写（至少视觉+听觉+1种其他感官）
3. 建立三层氛围结构（基础→情绪→转折）
4. 融入与故事相关的文化质感元素
5. 用环境叙事替代直接情绪说明
6. 输出增强后的完整场景描写
"""
        return prompt

    def validate_output(self, output: str) -> tuple[bool, List[str]]:
        errors = []
        # 检查是否有氛围标注
        has_atmosphere = any(kw in output for kw in ["氛围", "视觉：", "听觉：", "光影", "环境音"])
        if not has_atmosphere:
            errors.append("未找到氛围描写标注")
        # 检查是否有感官元素
        sense_count = 0
        for sense in FIVE_SENSES.values():
            if any(kw in output for kw in sense["examples"][:2]):
                sense_count += 1
        if sense_count < 2:
            errors.append(f"感官元素不足（仅{sense_count}种，至少3种）")
        # 检查是否有场景标记
        scene_count = len(re.findall(r'【场景', output))
        if scene_count < 1:
            errors.append("未找到场景标记")
        return len(errors) == 0, errors

    def extract_sense_coverage(self, output: str) -> Dict:
        """提取五感覆盖情况"""
        coverage = {}
        for key, sense in FIVE_SENSES.items():
            found = any(kw in output for kw in sense["elements"] + sense["examples"][:2])
            coverage[key] = {
                "name": sense["name"],
                "detected": found,
                "required": sense["required"],
            }
        return coverage


# 注册
from .base import ExpertRegistry
ExpertRegistry.register("§11", SceneCraftsmanExpert)
