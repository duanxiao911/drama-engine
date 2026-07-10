"""
CLI入口

支持完整流程、单步执行、交互式对话模式

用法：
    完整流程: python -m src.api.cli "我想写一个关于XXX的故事"
    单步执行: python -m src.api.cli --step soul_catcher "我的故事方向是XXX"
    交互模式: python -m src.api.cli --interactive
    恢复断点: python -m src.api.cli --resume wf_20240101_120000

配置：
    API Key 通过 .env 文件或环境变量设置，禁止硬编码在源码中。
    参见 .env.example 文件获取完整配置格式。
"""

import argparse
import sys
import os

# ── 加载环境变量（从 .env 文件）──
# .env 文件已在 .gitignore 中，不会提交到仓库
try:
    from dotenv import load_dotenv
    load_dotenv()  # 自动加载项目根目录的 .env
except ImportError:
    # python-dotenv 未安装时，回退到纯环境变量
    pass

# 不再硬编码 API Key —— 必须通过 .env 或环境变量提供
# 如果未配置，给出明确提示而不是静默失败
if not os.getenv("DRAMA_LLM_API_KEY"):
    print("⚠️  未检测到 API Key 配置。")
    print("   请在项目根目录创建 .env 文件，写入：")
    print("   DRAMA_LLM_API_KEY=你的API密钥")
    print("   参考 .env.example 文件获取完整配置项。")
    sys.exit(1)

from typing import Optional

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.config.settings import load_config, get_config, ConfigManager
from src.workflow.orchestrator import Orchestrator
from src.experts.base import ExpertRegistry, OpenAIClient


def print_header():
    """打印标题"""
    print("=" * 60)
    print("  🎬 Drama Engine - 精品短剧创作引擎")
    print("  版本: 1.0.0")
    print("=" * 60)
    print()


def print_expert_list(orchestrator: Orchestrator):
    """打印专家列表"""
    print("可用专家列表：")
    print("-" * 40)
    for info in orchestrator.list_available_experts():
        in_seq = "✓" if info["in_sequence"] else "○"
        print(f"  [{in_seq}] {info['id']} {info['name']}")
        print(f"      {info['description']}")
    print()


def print_workflow_progress(state):
    """打印工作流进度"""
    print("\n" + "=" * 60)
    print(f"工作流状态: {state.status.value}")
    print(f"进度: {state.current_step + 1}/{state.total_steps}")
    print(f"当前专家: {state.expert_sequence[state.current_step]}")
    print("-" * 40)
    for i, expert_id in enumerate(state.expert_sequence):
        status_icon = "✓" if i in state.completed_steps else "○"
        current_icon = "→" if i == state.current_step else " "
        print(f"  {current_icon}[{status_icon}] {expert_id}")
    print("=" * 60)


def run_full_workflow(args):
    """运行完整工作流"""
    config = load_config(args.config)

    # 创建LLM客户端 —— Key 从环境变量读取，绝不硬编码
    llm_client = OpenAIClient(
        api_key=config.llm.api_key or os.getenv("DRAMA_LLM_API_KEY", ""),
        model=config.llm.model or os.getenv("DRAMA_LLM_MODEL", "deepseek-chat"),
        base_url=config.llm.base_url or os.getenv("DRAMA_LLM_BASE_URL", "https://api.deepseek.com"),
        temperature=config.llm.temperature,
    )

    # 创建编排器
    orchestrator = Orchestrator(
        llm_client=llm_client,
        knowledge_base_path=config.paths.experts_prompts,
        project_path=config.paths.root,
        enable_checkpoint=config.workflow.enable_checkpoint,
    )

    print(f"\n 开始创作：{args.story[:50]}{'...' if len(args.story) > 50 else ''}")
    print()

    # 执行工作流
    state = orchestrator.run_full(args.story)

    # 输出结果
    print_workflow_progress(state)

    # 打印各专家输出摘要
    print("\n📋 各专家输出摘要：")
    print("-" * 40)
    for expert_id, output in state.step_outputs.items():
        status = "✓" if output.validation_passed else "✗"
        preview = output.content[:100].replace("\n", " ")
        print(f"  [{status}] {expert_id}: {preview}...")

    # 保存结果
    output_dir = os.path.join(config.paths.outputs, state.workflow_id)
    os.makedirs(output_dir, exist_ok=True)

    import json
    result_file = os.path.join(output_dir, "result.json")
    with open(result_file, "w", encoding="utf-8") as f:
        json.dump({
            "workflow_id": state.workflow_id,
            "story_direction": args.story,
            "context": state.context_snapshot.to_dict() if state.context_snapshot else {},
            "outputs": {k: v.to_dict() for k, v in state.step_outputs.items()},
            "status": state.status.value,
        }, f, ensure_ascii=False, indent=2)

    print(f"\n💾 结果已保存至: {result_file}")

    # 风险提示
    if state.context_snapshot and state.context_snapshot.risk_level == "red":
        print("\n⚠️ 警告：检测到🔴红色风险等级，请仔细审查合规建议后再继续！")

    return state


def run_single_step(args):
    """运行单个专家步骤"""
    config = load_config(args.config)

    llm_client = OpenAIClient(
        api_key=config.llm.api_key or os.getenv("DRAMA_LLM_API_KEY", ""),
        model=config.llm.model or os.getenv("DRAMA_LLM_MODEL", "deepseek-chat"),
        base_url=config.llm.base_url or os.getenv("DRAMA_LLM_BASE_URL", "https://api.deepseek.com"),
        temperature=config.llm.temperature,
    )

    orchestrator = Orchestrator(
        llm_client=llm_client,
        knowledge_base_path=config.paths.experts_prompts,
        project_path=config.paths.root,
    )

    expert_id = args.step
    print(f"\n🎯 执行专家: {expert_id}")
    print(f"📝 输入内容: {args.input[:100]}{'...' if len(args.input) > 100 else ''}")
    print()

    output = orchestrator.run_step(expert_id, user_input=args.input)

    print("=" * 60)
    print(f"输出结果 ({output.expert_name}):")
    print("-" * 60)
    print(output.content)
    print("-" * 60)
    print(f"验证通过: {'✓' if output.validation_passed else '✗'}")
    if output.validation_errors:
        print(f"验证问题: {output.validation_errors}")

    return output


def run_interactive(args):
    """交互式对话模式"""
    config = load_config(args.config)

    llm_client = OpenAIClient(
        api_key=config.llm.api_key or os.getenv("DRAMA_LLM_API_KEY", ""),
        model=config.llm.model or os.getenv("DRAMA_LLM_MODEL", "deepseek-chat"),
        base_url=config.llm.base_url or os.getenv("DRAMA_LLM_BASE_URL", "https://api.deepseek.com"),
        temperature=config.llm.temperature,
    )

    orchestrator = Orchestrator(
        llm_client=llm_client,
        knowledge_base_path=config.paths.experts_prompts,
        project_path=config.paths.root,
    )

    print("\n💬 交互式对话模式")
    print("输入 'help' 查看命令，输入 'exit' 退出")
    print()

    context = None
    current_expert = "§0"
    round_num = 1

    while True:
        try:
            user_input = input("\n👤 你: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n👋 再见！")
            break

        if not user_input:
            continue

        if user_input.lower() in ["exit", "quit", "q"]:
            print("\n👋 再见！")
            break

        if user_input.lower() == "help":
            print("""
命令列表：
  help     - 显示此帮助信息
  exit     - 退出程序
  context  - 显示当前上下文
  experts  - 显示专家列表
  next     - 进入下一个专家
  <任意>   - 继续当前专家对话
""")
            continue

        if user_input.lower() == "context":
            if orchestrator.state and orchestrator.state.context_snapshot:
                ctx = orchestrator.state.context_snapshot
                print(f"""
当前上下文：
  故事方向: {ctx.story_direction[:50] if ctx.story_direction else '未设置'}...
  一句话前提: {ctx.story_premise[:50] if ctx.story_premise else '未设置'}...
  风险等级: {ctx.risk_level}
  当前专家: {current_expert}
""")
            else:
                print("尚未开始工作流")
            continue

        if user_input.lower() == "experts":
            print_expert_list(orchestrator)
            continue

        # 执行当前专家
        output = orchestrator.run_step(current_expert, user_input=user_input, round_num=round_num)

        print(f"\n🤖 {output.expert_name}:")
        print("-" * 40)
        print(output.content[:500])
        if len(output.content) > 500:
            print("...(内容已截断)")
        print("-" * 40)

        # 判断是否需要切换专家
        if current_expert == "§0" and ("【故事方向确认】" in output.content or "故事方向：" in output.content):
            print("\n📍 §0灵魂捕手已完成，询问是否继续...")
            # 自动进入§2
            current_expert = "§2"
            round_num = 1
            print(f"→ 切换至 {current_expert}")
        elif output.validation_passed and "?" not in output.content:
            round_num = 1
        else:
            round_num += 1


def resume_workflow(args):
    """从断点恢复工作流"""
    config = load_config(args.config)

    llm_client = OpenAIClient(
        api_key=config.llm.api_key or os.getenv("DRAMA_LLM_API_KEY", ""),
        model=config.llm.model or os.getenv("DRAMA_LLM_MODEL", "deepseek-chat"),
        base_url=config.llm.base_url or os.getenv("DRAMA_LLM_BASE_URL", "https://api.deepseek.com"),
    )

    orchestrator = Orchestrator(
        llm_client=llm_client,
        knowledge_base_path=config.paths.experts_prompts,
        project_path=config.paths.root,
    )

    print(f"\n🔄 从断点恢复: {args.resume}")
    state = orchestrator.resume(args.resume)

    print_workflow_progress(state)
    return state


def main():
    """CLI主入口"""
    parser = argparse.ArgumentParser(
        description="Drama Engine - 精品短剧创作引擎 CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("story", nargs="?", help="故事方向描述")
    parser.add_argument("--config", "-c", help="配置文件路径", default="config.yaml")
    parser.add_argument("--step", "-s", help="指定执行单个专家（如soul_catcher）")
    parser.add_argument("--input", "-i", help="单步执行的输入内容", default="")
    parser.add_argument("--interactive", help="启动交互式对话模式", action="store_true")
    parser.add_argument("--resume", "-r", help="从断点恢复工作流")
    parser.add_argument("--list-experts", "-l", help="列出所有专家", action="store_true")
    parser.add_argument("--version", "-v", action="version", version="Drama Engine 1.0.0")

    args = parser.parse_args()

    print_header()

    # 列出专家
    if args.list_experts:
        config = load_config(args.config) if os.path.exists(args.config) else get_config()
        llm_client = OpenAIClient(api_key="")
        orchestrator = Orchestrator(llm_client=llm_client)
        print_expert_list(orchestrator)
        return

    # 恢复断点
    if args.resume:
        resume_workflow(args)
        return

    # 单步执行
    if args.step:
        if not args.input and not args.story:
            print("错误：单步执行需要 --input 或直接提供故事内容")
            return
        run_single_step(argparse.Namespace(
            step=args.step,
            input=args.input or args.story or "",
            config=args.config,
        ))
        return

    # 交互式模式
    if args.interactive:
        run_interactive(args)
        return

    # 完整流程
    if args.story:
        run_full_workflow(args)
        return

    # 无参数，显示帮助
    parser.print_help()
    print("\n示例：")
    print("  python -m src.api.cli \"我想写一个关于大理白族姑娘进城打工的故事\"")
    print("  python -m src.api.cli --step soul_catcher \"我的故事是关于...\"")


if __name__ == "__main__":
    main()
