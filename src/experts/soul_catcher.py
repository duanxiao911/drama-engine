"""
§0 灵魂捕手专家

职责：对话式追问（2-5轮），确认故事方向
将用户模糊的想法转化为清晰的故事方向

基于《架构设计.md》MVP专家列表 + 《精品短剧创作引擎_通用版.md》§0
"""

from typing import List, Dict, Optional
from .base import ExpertBase, ExpertContext, ExpertOutput


class SoulCatcherExpert(ExpertBase):
    """§0 灵魂捕手专家"""
    expert_id = "§0"
    expert_name = "soul_catcher"
    prompt_file = "soul_catcher.md"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.conversation_history: List[Dict] = []

    def get_system_prompt(self) -> str:
        return """你是一位专精精品短剧的资深编剧，代号§0灵魂捕手。

你的核心能力：通过精准追问，将用户模糊的创作想法转化为清晰、可执行的故事方向。

灵魂捕手工作流：
1. 倾听用户原始想法（可能只是一句话、一个情绪、一个画面）
2. 从以下6个维度发起追问（每次最多2个维度，不必全问）：
   - 核心人物：谁是这个故事的主角？他/她想要什么？
   - 核心冲突：最大的矛盾是什么？谁在阻挡主角？
   - 情感基调：这是一个悲伤的、温暖的、还是热血的故事？
   - 真实来源：这个故事有真实素材吗？还是纯虚构？
   - 目标受众：谁会来看这个故事？
   - 类型偏好：悲剧/甜宠/现实主义/悬疑/非遗？

3. 当收集到足够信息时，输出【故事方向确认】

【故事方向确认】格式：
```
故事方向：[一句话故事方向，含人物+核心冲突+情感基调]
一句话前提：[主题+人物+冲突+结论，如“被遗弃的孩子拼命证明自己值得被爱，却发现最深的伤害来自最亲的人”]
推荐类型：[悲剧/现实主义/甜宠/悬疑/非遗文化]
核心情感锚点：[观众看完会产生的核心感受]
禁止项：[用户明确禁止的方向，如无则填“无”]
```

铁律：
- 不要一次追问超过2个维度，保持对话轻量
- 用户可能只想聊一聊，不要急于输出完整方向
- 追问要精准，触及故事的核心痛点
- 严格遵守引擎§2六大审核红线和叙事因果铁律
"""

    def get_user_prompt(self, context: ExpertContext, **kwargs) -> str:
        user_input = kwargs.get("user_input", "")
        round_num = kwargs.get("round_num", 1)
        self.conversation_history.append({"role": "user", "content": user_input})

        prompt_parts = []
        if round_num == 1:
            prompt_parts.append(f"用户说：{user_input}")
            prompt_parts.append("请开始第一轮追问，精准触及故事核心痛点（最多2个维度）。")
        else:
            prompt_parts.append(f"用户回复：{user_input}")
            prompt_parts.append(f"当前对话轮次：第{round_num}轮（共最多5轮）。")
            prompt_parts.append("如果已收集足够信息，请输出【故事方向确认】；否则继续追问。")

        prompt_parts.append(f"\n历史对话：{self.conversation_history}")
        return "\n".join(prompt_parts)

    def validate_output(self, output: str) -> tuple[bool, List[str]]:
        errors = []
        # 如果包含【故事方向确认】，视为可以结束
        if "【故事方向确认】" in output or "故事方向：" in output:
            # 检查是否包含必要字段
            required = ["故事方向：", "一句话前提：", "推荐类型：", "核心情感锚点："]
            missing = [f for f in required if f not in output]
            if missing:
                errors.append(f"【故事方向确认】缺少必要字段：{missing}")
                return False, errors
            return True, []
        # 否则检查是否有有效追问
        if "？" not in output and "?" not in output:
            errors.append("输出既不是追问也不包含故事方向确认")
        return len(errors) == 0, errors

    def should_continue(self, output: str, context: ExpertContext) -> bool:
        """判断是否需要继续对话"""
        # 如果已经输出了【故事方向确认】，不需要继续
        if "【故事方向确认】" in output:
            return False
        # 如果超过5轮，强制结束
        if len(self.conversation_history) >= 5:
            return False
        return True


# 注册
from .base import ExpertRegistry
ExpertRegistry.register("§0", SoulCatcherExpert)