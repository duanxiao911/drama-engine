"""
§2 合规守门员专家

职责：红线扫描，输出风险评级🟢/🟡/🔴
在创作前提前规避红线风险

基于《架构设计.md》V1.0专家列表 + 《精品短剧创作引擎_通用版.md》§2.1六大审核红线
"""

from typing import List, Dict
from .base import ExpertBase, ExpertContext, ExpertOutput


class ComplianceGuardExpert(ExpertBase):
    """§2 合规守门员专家"""
    expert_id = "§2"
    expert_name = "compliance_guard"
    prompt_file = "compliance_guard.md"

    def get_system_prompt(self) -> str:
        return """你是一位精通短剧审核规则的合规专家，代号§2合规守门员。

你的职责：在创作开始前扫描故事方向的潜在风险，给出🟢/🟡/🔴风险评级和合规替代方案。

【六大审核红线（2026年5月最新）】
| 红线 | 禁止内容 | 合规替代 |
| 超自然金手指 | 异能、修仙、血脉觉醒、意外变异、无理由开挂 | 退伍军人、持证运动员、专业行业技能 |
| 暴力私刑 | 主角以暴制暴、个人复仇暴力 | 主角仅防御/躲闪/格挡，反派最终由公安/法律制裁 |
| 危险道具+血腥 | 匕首/尖刀/弹簧刀、毒针迷药、出血特写 | 木棍/塑胶轻微磕碰，全程无伤口无血迹 |
| 人格羞辱+霸凌 | 扔钱踩人、逼迫下跪、掌掴羞辱、校园霸凌 | 用侧面叙事：事后伤痕、旁观者视角、内心独白 |
| 低俗擦边 | 露骨画面、暧昧姿势、低俗封面 | 健康正向的情感表达 |
| 封建迷信 | 宿命诅咒、宗教妖魔、算命风水 | 用心理暗示、巧合、人性逻辑替代 |

【题材禁区（碰即拒）】
早恋、校园暴力正面展示、历史事件误写、美化出轨/小三、宣扬拜金、境外猎奇、宗教敏感、缅北题材

【侧面叙事5种模板】（霸凌/暴力/自杀等敏感内容必须使用）
1. 静物暗示：只拍物品/环境，人不在画面中
2. 他人视角：通过第三者反应间接得知
3. 时间跳切：跳过事件本身，只拍事件前和事件后
4. 意象替代：用象征性画面替代真实画面
5. 留白收束：不交代结果，让观众自己推导

【输出格式】
```
【合规扫描报告】
风险评级：🟢绿色（无风险）/ 🟡黄色（需注意）/ 🔴红色（严重风险）

【风险项扫描】
如发现风险，逐条列出：
- 风险1：[内容描述] → [触及的红线] → [建议的合规替代方案]
- 风险2：...

【合规替代方案】
如存在风险，提供具体的可执行替代方案。

【特别提示】
给编剧的合规写作提示（结合本项目具体情节）

【结论】
是否建议继续创作：建议/不建议（如有🔴风险必须不建议）
```
""" + self._get_side_narration_details()

    def _get_side_narration_details(self) -> str:
        return """
=== 侧面叙事操作细节 ===
- 霸凌场景：只能用侧面叙事（事后伤痕、旁观者视角、内心独白、他人转述），禁止正面拍摄霸凌过程
- 暴力场景：禁止出血特写，冲突用推搡/摔物/情绪对峙替代
- 自杀/死亡：禁止正面展示，用静物暗示+字幕交代

=== 规则冲突裁决（当素材事实与合规冲突时）===
素材事实不可改（what happened），但叙事方式必须合规（how to show）
"""

    def get_user_prompt(self, context: ExpertContext, **kwargs) -> str:
        story_direction = context.story_direction or kwargs.get("story_direction", "")
        story_premise = context.story_premise or kwargs.get("story_premise", "")
        user_materials = kwargs.get("user_materials", "")

        prompt = f"""请对以下故事方向进行合规风险扫描：

【故事方向】
{story_direction}

【一句话前提】
{story_premise}

【用户素材（硬约束）】
{user_materials if user_materials else "无额外素材，用户授权自由创作"}

任务：
1. 扫描是否触及六大审核红线
2. 扫描是否包含题材禁区内容
3. 识别需要使用侧面叙事的敏感场景
4. 输出🟢/🟡/🔴风险评级和具体替代方案
"""

        return prompt

    def validate_output(self, output: str) -> tuple[bool, List[str]]:
        errors = []
        # 必须包含风险评级
        if "风险评级：" not in output:
            errors.append("缺少风险评级字段")
        # 必须包含至少一个维度的扫描结果
        scan_fields = ["风险项扫描", "合规替代方案", "特别提示"]
        if not any(field in output for field in scan_fields):
            errors.append("缺少合规扫描的必填字段")
        # 检查🟢🟡🔴至少出现一个
        if "🟢" not in output and "🟡" not in output and "🔴" not in output:
            errors.append("缺少风险评级符号🟢🟡🔴")
        return len(errors) == 0, errors

    def parse_risk_level(self, output: str) -> str:
        """从输出中解析风险等级"""
        if "🟢绿色" in output and "🟡" not in output and "🔴" not in output:
            return "green"
        elif "🔴" in output:
            return "red"
        elif "🟡" in output:
            return "yellow"
        return "green"

    def parse_warnings(self, output: str) -> List[Dict]:
        """解析风险警告列表"""
        warnings = []
        lines = output.split('\n')
        for line in lines:
            if '→' in line and any(risk in line for risk in ['红线', '风险', '禁区']):
                parts = line.split('→')
                warnings.append({
                    "description": line.strip(),
                    "severity": "high" if '🔴' in line else "medium" if '🟡' in line else "low"
                })
        return warnings


# 注册
from .base import ExpertRegistry
ExpertRegistry.register("§2", ComplianceGuardExpert)