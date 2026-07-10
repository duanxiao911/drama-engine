# Drama Engine - 精品短剧创作引擎

> 1人 + 8个AI专家 = 完整制作团队。唯一懂人物灵魂的精品短剧创作引擎。

## 项目概述

Drama Engine 是一个基于 67000 字创作方法论的 Python 智能体引擎，专为精品短剧创作设计。区别于市面 99% 的量产爽剧工具，本引擎专注于**现实题材、悲剧、家庭伦理、非遗文化**等需要文学功底和人物深度的类型。

输入一句话故事方向，引擎自动调度 8 位 AI 专家协作，产出：
- 完整故事大纲（30集结构）
- 角色设定卡（三层四维度人设 + 弧光线）
- 分集剧本（专业格式，含场景、对白、动作描写）
- 视觉方案（镜头设计 + 光影系统）
- Word 格式导出（可直接投稿）

### Loop Engineering 实践

本引擎是 Loop Engineering 范式在短剧创作领域的落地实践——从实际创作需求中自发生长，四要素完整映射：

| Loop Engineering | 本引擎对应 | 说明 |
|-----------------|-----------|------|
| Goal | 核心铁律系统 + 质量评分 | 四层优先级铁律 + 6维度评分 |
| Sub-agents | 8个专家模块 | 每个AI专家 = 独立子代理，按序协作 |
| Evaluator | 合规守门员 + 质量评分 | 引擎内自动评分 + 结构化验证 |
| Memory | 项目配置 + 文化知识库 | 跨轮次上下文 + 持久化知识 |

## 核心特性

- **8专家全链路协作**：§0→§2→§8→§1→§4→§3→§5→§13，从方向到成片剧本一站式产出
- **专业剧本格式输出**：场景标记、角色对白加粗、动作描写灰色斜体、内心独白标注，Word 一键导出
- **通用内核 + 项目配置双层架构**：换项目只需替换 §8 配置
- **中华优秀传统文化知识库**：双骨架（乡土中国+美的历程），适配非遗题材
- **合规优先**：内置六大审核红线扫描
- **质量闭环**：0-10分质量评分 + 结构化验证

## 架构（六层设计）

```
第1层   API接口层       FastAPI / CLI
第2层   工作流编排层    专家调度 + 上下文管理 + 状态追踪
第3层   专家Prompt层    8个专家模块（§0-§13），可扩展至15个
第4层   核心引擎层      铁律系统 + 规则裁决 + 质量评分 + 类型适配
第5层   项目配置层      §8配置 + 语料库 + 素材约束 + 合规清单
第5.5层 文化知识库      中华优秀传统文化知识库（双骨架架构）
```

```
drama-engine/
├── src/
│   ├── engine/           # 核心引擎（第4层）
│   │   ├── rules.py      # 铁律系统
│   │   ├── scorer.py     # 质量评分
│   │   └── type_adapter.py # 类型适配
│   ├── experts/          # 专家模块（第3层，8个）
│   │   ├── base.py           # 专家基类 + LLM客户端
│   │   ├── soul_catcher.py   # §0 灵魂捕手
│   │   ├── compliance_guard.py # §2 合规守门员
│   │   ├── project_configurator.py # §8 项目配置师
│   │   ├── character_forger.py # §1 角色铸造师
│   │   ├── dialogue_master.py # §4 对白大师
│   │   ├── structure_architect.py # §3 结构建筑师
│   │   ├── episode_writer.py # §5 分场编剧
│   │   └── visual_director.py # §13 视觉导演
│   ├── export/           # 产出导出模块
│   │   └── final_assembler.py # 全链路结果组装
│   ├── workflow/          # 工作流编排
│   │   └── orchestrator.py
│   ├── knowledge/         # 文化知识库
│   │   └── culture_kb.py
│   ├── config/            # 配置管理
│   └── api/               # 入口（CLI + FastAPI）
├── convert_to_word.py    # JSON → Word 专业格式导出
├── knowledge/experts/     # 各专家Prompt模板
├── knowledge/culture/     # 文化知识库文档
├── tests/                 # 测试
└── examples/              # 示例配置
```

## 专家序列

| 编号 | 专家 | 职责 | 状态 |
|------|------|------|------|
| §0 | 灵魂捕手 | 对话式追问，确认故事方向 | MVP |
| §2 | 合规守门员 | 红线扫描，风险评级 | MVP |
| §8 | 项目配置师 | 拆解为可执行的项目设定 | MVP |
| §1 | 角色铸造师 | 三层四维度人设 + 弧光线 | MVP |
| §4 | 对白大师 | 语料库 + 风格卡 + 钩子链 | MVP |
| §3 | 结构建筑师 | 15节拍表 + 23段落 + 弧光追踪 | MVP |
| §5 | 分场编剧 | 批量生成分集专业剧本（5集×6轮） | MVP |
| §13 | 视觉导演 | 光影系统 + 镜头系统 + 声音系统 | MVP |

## 安装

```bash
# 克隆项目
git clone <repo-url>
cd drama-engine

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env，填入你的 API Key 和 Base URL
```

### 环境变量

```bash
# .env 文件
DRAMA_LLM_API_KEY=your-api-key
DRAMA_LLM_BASE_URL=https://api.openai.com/v1
DRAMA_LLM_MODEL=gpt-4o
```

## 快速开始

### CLI 模式（推荐）

```bash
# 完整流程 - 输入故事方向，自动跑完8个专家
$env:PYTHONIOENCODING="utf-8"
python -m src.api.cli "我想写一个关于大理白族姑娘传承扎染技艺的故事"
```

### 导出 Word 文档

```bash
# 将引擎产出的 JSON 转为专业格式 Word
python convert_to_word.py workspace/outputs/<workflow_id>/result.json
```

生成的 Word 文档包含：
- 集头信息（集数、核心事件、情感走向）
- 场景标记（SCENE 01 / 日/内 / 地点）
- 角色对白（角色名居中加粗）
- 动作描写（△标记，灰色斜体）
- 内心独白（加粗斜体标注）

### API 模式

```bash
uvicorn src.api.server:app --host 0.0.0.0 --port 8000
```

## 核心方法论

本引擎基于 67000 字创作方法论开发，核心规则包括：

- **六大审核红线**：超自然金手指、暴力私刑、危险道具、人格羞辱、低俗擦边、封建迷信
- **叙事因果铁律**：因果链不可断、人设驱动而非剧情驱动
- **15节拍表**：救猫咪结构适配30集
- **23段落大纲**：写作指令粒度
- **弧光追踪**：每集标注角色信念微移
- **对白五字诀**：短、狠、准、燃、沉
- **类型适配**：悲剧/甜宠/悬疑/非遗各有专项规则

## 测试

```bash
pytest tests/ -v
```

## 项目示例

参考 `examples/bai_tie_dye_config.yaml` 了解如何配置一个非遗传承项目。

## 参赛信息

- **赛事**：SynNovator OPC全球青年培育赛 S3（数字文化赛道 track-60）
- **W2阶段交付**：核心引擎代码 + 8个MVP专家模块 + Word导出
- **Demo**: https://duanxiao911.github.io/loop-studio-demo/

## License

MIT License
