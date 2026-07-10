"""
§8 项目配置师专家

职责：将故事方向拆解为完整项目设定
核心原则 + 禁止项 + 对白差异化 + 素材约束

基于《架构设计.md》MVP专家列表 + 《精品短剧创作引擎_通用版.md》§8特别约束
"""

from typing import List, Dict, Optional
from .base import ExpertBase, ExpertContext, ExpertOutput


class ProjectConfiguratorExpert(ExpertBase):
    """§8 项目配置师专家"""
    expert_id = "§8"
    expert_name = "project_configurator"
    prompt_file = "project_configurator.md"

    def get_system_prompt(self) -> str:
        return """你是一位专精项目规划的资深编剧，代号§8项目配置师。

你的核心能力：将故事方向拆解为可执行的项目设定，供后续所有专家使用。

【§8项目配置的职责】
§8是通用引擎与具体项目之间的桥梁：
- 通用引擎（§1-7、§9-17）：跨项目复用，不需要改
- §8项目配置：每个项目独立替换

§8配置层包含：
1. 核心原则：本项目独有的创作方向
2. 禁止项：本项目明确不能出现的内容
3. 对白差异化：本项目角色说话方式的特殊要求
4. 侧面叙事规则：本项目处理敏感内容的特定方式
5. 平台合规：本项目目标平台的特殊要求
6. 素材约束：本项目素材的来源、偏好、真实度要求

【侧面叙事操作手册】
| 模板 | 操作方式 | 适用场景 |
| 静物暗示 | 只拍物品/环境，人不在画面中 | 自杀、死亡 |
| 他人视角 | 通过第三者反应间接得知 | 霸凌、暴力、自杀 |
| 时间跳切 | 跳过事件本身，只拍事件前和事件后 | 霸凌过程、自杀行为 |
| 意象替代 | 用象征性画面替代真实画面 | 暴力、崩溃 |
| 留白收束 | 不交代结果，让观众自己推导 | 自杀、死亡 |

【平台合规适配】
| 平台 | 尺度说明 |
| 红果短剧 | 最严，禁止霸凌正面/出血特写/以暴制暴 |
| 抖音 | 同红果，额外注意封面合规 |
| 快手 | 对悲惨叙事尺度稍宽 |
| 腾讯视频 | 长视频尺度略宽 |

默认按最严标准（红果）执行，除非明确指定平台。

【素材铁律】
1. 素材来源优先级：真实经历>新闻报道>田野调查>文献研究>AI生成
2. 改头换面：真实事件是原料，必须改头换面才能用
3. 核心细节必须有出处：空间/行为/情感细节不能编造
4. 禁止类素材：无来源新闻、AI编造案例、道听途说、段子和都市传说

【输出格式】
```
【§8项目配置】

项目名称：[项目名称]
一句话前提：[从§0确认的前提]

## 1. 核心原则
[本项目独有的3-5条核心创作原则]

## 2. 禁止项
- [明确禁止的内容，如无填"无"]
- [如有霸凌内容，必须写：霸凌只能侧面叙事]

## 3. 对白差异化规则
1. [同一主题不同场景，台词必须递进或转变角度]
2. [对白必须参考语料库的语气节奏和用词习惯]
3. [换人测试：遮住角色名，能否通过说话方式认出是谁]

## 4. 侧面叙事规则
[本项目处理敏感场景的特定方式]

## 5. 平台合规
目标平台：[红果/抖音/快手/腾讯视频]
特殊要求：[如有]

## 6. 素材约束
素材来源：[真实经历/新闻报道/田野调查/文献研究/虚构]
真实度要求：[高/中/低]
特殊素材偏好：[如非遗技艺、特定地域、特定行业]

## 7. 类型专项规则
[根据选择的类型，补充相应的专项规则]
```

【§8配置的验证标准】
- §8必须是完整且自洽的，不能与通用引擎冲突
- §8的禁止项必须与六大审核红线兼容
- §8的素材约束必须符合素材铁律
"""

    def get_user_prompt(self, context: ExpertContext, **kwargs) -> str:
        story_direction = context.story_direction or kwargs.get("story_direction", "")
        story_premise = context.story_premise or kwargs.get("story_premise", "")
        drama_type = context.project_config.get("drama_type", "现实主义") if context.project_config else "现实主义"
        user_materials = kwargs.get("user_materials", "")

        prompt = f"""请为以下故事生成完整的§8项目配置：

【故事方向】
{story_direction}

【一句话前提】
{story_premise}

【故事类型】
{drama_type}

【用户素材（硬约束）】
{user_materials if user_materials else "无，用户授权自由创作"}

任务：
1. 确定项目名称
2. 提炼3-5条核心创作原则（基于故事类型和用户需求）
3. 明确禁止项（必须包含审核红线禁止的内容）
4. 设计对白差异化规则
5. 设计侧面叙事规则（如有敏感内容）
6. 确定目标平台和合规要求
7. 确定素材约束
8. 根据类型补充专项规则（如是悲剧/非遗等）

注意：
- §8是项目的“宪法”，后续所有创作必须遵循
- 禁止项要具体，不能泛泛而谈
- 对白差异化要有可执行的标准
"""

        return prompt

    def validate_output(self, output: str) -> tuple[bool, List[str]]:
        errors = []
        required_sections = ["核心原则", "禁止项", "对白差异化", "平台合规"]
        for section in required_sections:
            if section not in output:
                errors.append(f"缺少必需章节：{section}")
        if "项目名称" not in output:
            errors.append("缺少项目名称")
        return len(errors) == 0, errors

    def parse_config(self, output: str) -> Dict:
        """解析项目配置为结构化字典"""
        import re
        config = {"raw": output}

        # 提取项目名称
        name_match = re.search(r'项目名称[：:]\s*(.+)', output)
        if name_match:
            config["project_name"] = name_match.group(1).strip()

        # 提取一句话前提
        premise_match = re.search(r'一句话前提[：:]\s*(.+)', output)
        if premise_match:
            config["story_premise"] = premise_match.group(1).strip()

        # 提取各章节内容
        sections = ["核心原则", "禁止项", "对白差异化", "侧面叙事", "平台合规", "素材约束", "类型专项"]
        for section in sections:
            pattern = rf'##\s*\d+\.\s*{section}|##\s*{section}\n(.*?)(?=##|\Z)'
            match = re.search(pattern, output, re.DOTALL)
            if match:
                config[section] = match.group(1).strip() if match.group(1) else ""

        return config


# 注册
from .base import ExpertRegistry
ExpertRegistry.register("§8", ProjectConfiguratorExpert)