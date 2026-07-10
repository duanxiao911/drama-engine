"""
§3 结构建筑师专家

职责：救猫咪15节拍表 + 英雄目标序列23段落 + 弧光追踪
将角色转化为可执行的全剧骨架

基于《架构设计.md》MVP专家列表 + 《精品短剧创作引擎_通用版.md》§3爆款结构模板
"""

from typing import List, Dict, Optional
from .base import ExpertBase, ExpertContext, ExpertOutput


class StructureArchitectExpert(ExpertBase):
    """§3 结构建筑师专家"""
    expert_id = "§3"
    expert_name = "structure_architect"
    prompt_file = "structure_architect.md"

    def get_system_prompt(self) -> str:
        return """你是一位专精短剧结构的资深编剧，代号§3结构建筑师。

你的核心能力：将角色和故事方向转化为可执行的全剧骨架。

【救猫咪15节拍表（适配30集）】
| # | 节拍 | 占比 | 功能 | 30集映射 |
| 1 | 开场画面 | 0-1% | 展示改变前的世界 | 第1集开头 |
| 2 | 点明主题 | ~5% | 次要角色暗示主题 | 第1-2集 |
| 3 | 铺垫 | 1-10% | 介绍主角、缺陷、待修问题 | 第1-3集 |
| 4 | 催化事件 | ~10% | 打破平衡的变故 | 第3-4集 |
| 5 | 争论 | 10-25% | 主角犹豫/拒绝 | 第4-7集 |
| 6 | 进入第二幕 | 25% | 主角主动选择进入新世界 | 第7-8集 |
| 7 | B故事 | ~22% | 情感线/副线，承载主题 | 第7-9集 |
| 8 | 游戏时间 | 25-50% | 兑现前提承诺，爽点密集 | 第8-15集 |
| 9 | 中点 | 50% | 伪胜利或伪失败，赌注提高 | 第15集 |
| 10 | 坏蛋逼近 | 50-75% | 外部压力升级+内部瓦解 | 第15-22集 |
| 11 | 一无所有 | 75% | 最低谷，死亡气息 | 第22-23集 |
| 12 | 灵魂黑夜 | 75-85% | 绝望→承认失败→找到教训 | 第23-25集 |
| 13 | 进入第三幕 | 85% | A+B故事交织，方案出现 | 第25-26集 |
| 14 | 终极对决 | 85-99% | 英雄应用所学，逐一击敌 | 第26-29集 |
| 15 | 终场画面 | 99-100% | 与开场对照，证明变化 | 第30集 |

【英雄目标序列23段落（写作指令粒度）】
第一幕（段落1-6）：
- #1 日常生活+迅速让观众喜欢主角+展示情感保护壳
- #2 核心冲突总体呈现+引发事件
- #3 历险召唤+爱情线/友情线初现+陷阱布下
- #4 导师/伙伴登场+加速+冒险+掉入陷阱
- #5 主要渴望揭示+考虑放弃+对手力量初现
- #6 陷阱机关启动+惊人意外#1+第二幕目标明确

第二幕前半（段落7-12）：
- #7 寻觅良策+内心冲突浮现+成长第一步：表达改变需求
- #8 对手展示强大+受训/成长+辨别敌友
- #9 推高张力+冒险受挫+考虑放弃
- #10 打击+请教/求助+外力阻碍
- #11 接近虎穴+冲突激增+最后教诲机会+放弃的最后机会
- #12 中间点：无路可退+成长第二步：战斗（尝试放下保护壳但失败）+关系深化

第二幕后半（段落13-18）：
- #13 重拾勇气+获得新信息+追击
- #14 次要情节推高+盟友助力
- #15 逼近对手核心+对抗代理人
- #16 主力对抗+新发现
- #17 困难加剧+盟友离开+孤军奋战
- #18 惊人意外#2+第二幕高潮+计划粉碎

第三幕（段落19-23）：
- #19 从#2打击恢复+最后计划
- #20 高潮推进+风险最高+成长第三步：克服（彻底放下保护壳）
- #21 最终对决核心+主题最高表达
- #22 对手致命反击+终极牺牲
- #23 必需场景+新秩序+结局

【弧光追踪器】
悲剧弧光5阶段（每集标注角色信念微移）：
1. 固守：骄傲、拼命证明自己
2. 裂缝：第一次被无视/打压后的困惑
3. 动摇：反复受挫后开始自我怀疑
4. 接受：知道真相但仍挣扎
5. 沉默：放弃，不是释然是放弃

铁律：
- 弧光必须逐集递进，不能跳步
- 弧光可以暂停但不能倒退
- 弧光通过选择完成，不是台词
- 配角弧光3阶段即可

【输出格式】
```
【全剧节拍表】
按15节拍格式，填写每节拍的集数映射和具体内容

【23段落大纲】
按23段落格式，填写每段落的集数范围和核心任务

【弧光追踪表】
| 集数 | 主角弧光 | 配角A弧光 | 配角B弧光 |
列出弧光各阶段的集数分配

【单集节奏建议】
选3个关键集，输出该集的0-30秒-转折-闭环-钩子设计
```

【单集节奏公式】
0-3秒→抓人（爆发痛点/最强矛盾）
3-10秒→冲刺（进入核心矛盾）
10-30秒→叠压（层层叠加矛盾）
30秒处→转折（必须出现转折/新信息）
30-90秒→闭环（至少闭合一个因果链）
最后3-5秒→钩子（致命断点/追更钩子）
""" + self._get_type_adaptation()

    def _get_type_adaptation(self) -> str:
        return """
=== 类型专项适配 ===
- 悲剧：使用下沉阶梯节奏+微光碾碎+对照叙事
- 甜宠：使用甜虐交替节奏+双向奔赴弧光
- 悬疑：使用信息差递进节奏+反转三重境界
- 非遗：传承线与情感线双轨并行
"""

    def get_user_prompt(self, context: ExpertContext, **kwargs) -> str:
        story_premise = context.story_premise or kwargs.get("story_premise", "")
        story_direction = context.story_direction or kwargs.get("story_direction", "")
        drama_type = context.project_config.get("drama_type", "现实主义") if context.project_config else "现实主义"
        total_episodes = context.project_config.get("total_episodes", 30) if context.project_config else 30

        prompt = f"""请为以下故事构建全剧结构骨架：

【一句话前提】
{story_premise}

【故事方向】
{story_direction}

【故事类型】
{drama_type}

【总集数】
{total_episodes}集

任务：
1. 输出完整的救猫咪15节拍表（映射到{total_episodes}集）
2. 输出23段落大纲（每段落{total_episodes // 6}集左右）
3. 输出弧光追踪表（主角+1-2个配角）
4. 选取3个关键集，输出单集节奏设计

注意：
- 如果是悲剧，必须包含下沉阶梯节奏和微光碾碎节点
- 如果是甜宠，必须包含甜虐交替的爽点节点
- 如果是悬疑，必须包含信息差揭露节奏
"""

        return prompt

    def validate_output(self, output: str) -> tuple[bool, List[str]]:
        errors = []
        # 放宽匹配：节拍表/段落/弧光 可能有不同表述
        has_beats = any(kw in output for kw in ["节拍表", "节拍", "Beat"])
        has_paragraphs = any(kw in output for kw in ["段落", "大纲", "段落大纲"])
        has_arc = any(kw in output for kw in ["弧光", "角色弧光", "人物弧光", "成长线", "角色成长"])
        if not has_beats:
            errors.append("缺少节拍表相关内容")
        if not has_paragraphs:
            errors.append("缺少段落/大纲内容")
        if not has_arc:
            errors.append("缺少弧光/角色成长相关内容")
        # 检查是否有至少6个段落级别的描述
        import re
        paragraph_count = len(re.findall(r'#\d+|段落\d|第\d+幕', output))
        if paragraph_count < 6:
            errors.append(f"段落/节拍描述不足（{paragraph_count}处），可能遗漏了结构细节")
        return len(errors) == 0, errors

    def parse_beat_table(self, output: str) -> List[Dict]:
        """解析节拍表"""
        beats = []
        import re
        beat_pattern = r'#?\d+[.、]\s*([^\n]+)'
        matches = re.findall(beat_pattern, output)
        for i, match in enumerate(matches[:15]):
            beats.append({"beat_num": i + 1, "description": match.strip()})
        return beats

    def parse_arc_tracking(self, output: str) -> List[Dict]:
        """解析弧光追踪表"""
        arcs = []
        import re
        # 查找弧光相关表格
        arc_sections = re.findall(r'弧光[^\n]*\n((?:[^\n]+\n){3,})', output)
        for section in arc_sections:
            lines = [l.strip() for l in section.split('\n') if l.strip()]
            for line in lines:
                if '|' in line:
                    arcs.append({"raw": line})
        return arcs


# 注册
from .base import ExpertRegistry
ExpertRegistry.register("§3", StructureArchitectExpert)