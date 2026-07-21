"""
云匠引擎 Pipeline Orchestrator
15专家调度脚本 - 处理依赖关系、并行执行、数据流转

执行模式：
- full: 完整链路（题材→创意→分集→剧本→精修→发行）
- episode_only: 仅分集开发
- script_only: 仅剧本开发
- polish_only: 仅剧本精修

依赖关系DAG：
Layer 0: ⑩实战指挥（总调度）
Layer 1: ①角色铸造、⑫世界观锻造、⑧商业包装（独立，可并行）
Layer 2: ②情感编织（依赖①）
Layer 3: ③结构建筑（依赖②）
Layer 4: ④对白大师（依赖①③）、⑪场景工匠（依赖④）
Layer 5: ⑤分集编剧（依赖①②③④）
Layer 6: ⑥格式工匠（依赖⑤）、⑬金句萃取（依赖④）
Layer 7: ⑦质量审计（依赖所有创作专家）
Layer 8: ⑨改稿编辑（依赖⑦）、⑭商业操盘（依赖⑧）
Layer 9: ⑮品控总监（依赖⑦⑭）
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import concurrent.futures


class ExecutionMode(Enum):
    """执行模式"""
    FULL = "full"  # 完整链路
    EPISODE_ONLY = "episode_only"  # 仅分集
    SCRIPT_ONLY = "script_only"  # 仅剧本
    POLISH_ONLY = "polish_only"  # 仅精修
    EVALUATE_ONLY = "evaluate_only"  # 仅评估


class ExpertStatus(Enum):
    """专家执行状态"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class ExpertConfig:
    """专家配置"""
    expert_id: str
    name: str
    layer: int  # 依赖层级
    dependencies: List[str]  # 依赖的专家ID列表
    system_prompt_file: str  # 系统提示词文件路径
    input_schema: Dict  # 输入数据结构
    output_schema: Dict  # 输出数据结构
    optional: bool = False  # 是否可选（失败不阻塞）


@dataclass
class ExpertResult:
    """专家执行结果"""
    expert_id: str
    status: ExpertStatus
    output: Optional[Dict] = None
    error: Optional[str] = None
    execution_time: float = 0.0
    retry_count: int = 0


class LLMAPIAdapter:
    """
    LLM API适配器 - 抽象不同平台的调用方式
    需要用户实现具体的API调用逻辑
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.platform = config.get("platform", "openai")  # openai/coze/local
    
    def call(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        """
        调用LLM API
        
        Args:
            system_prompt: 系统提示词
            user_prompt: 用户提示词
            **kwargs: 额外参数（temperature, max_tokens等）
        
        Returns:
            LLM响应文本
        """
        if self.platform == "openai":
            return self._call_openai(system_prompt, user_prompt, **kwargs)
        elif self.platform == "coze":
            return self._call_coze(system_prompt, user_prompt, **kwargs)
        elif self.platform == "local":
            return self._call_local(system_prompt, user_prompt, **kwargs)
        else:
            raise ValueError(f"Unsupported platform: {self.platform}")
    
    def _call_openai(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        """OpenAI API调用"""
        import os
        try:
            from openai import OpenAI
            
            client = OpenAI(
                api_key=os.getenv("OPENAI_API_KEY"),
                base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
            )
            
            response = client.chat.completions.create(
                model=kwargs.get("model", "gpt-4"),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 4096)
            )
            
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"OpenAI API call failed: {e}")
    
    def _call_coze(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        """Coze API调用 - 需要用户实现"""
        raise NotImplementedError("Coze API adapter not implemented yet")
    
    def _call_local(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        """本地模型调用 - 需要用户实现"""
        raise NotImplementedError("Local model adapter not implemented yet")


class PipelineOrchestrator:
    """云匠引擎流水线调度器"""
    
    def __init__(self, llm_adapter: LLMAPIAdapter, experts_base_path: str = "./experts"):
        """
        初始化调度器
        
        Args:
            llm_adapter: LLM API适配器
            experts_base_path: 专家配置文件根目录
        """
        self.llm = llm_adapter
        self.experts_base = Path(experts_base_path)
        self.experts: Dict[str, ExpertConfig] = {}
        self.results: Dict[str, ExpertResult] = {}
        self._register_experts()
    
    def _register_experts(self):
        """注册所有15个专家"""
        
        # Layer 0: 总调度
        self._register(ExpertConfig(
            expert_id="commander",
            name="⑩实战指挥",
            layer=0,
            dependencies=[],
            system_prompt_file="commander.md",
            input_schema={"project": "str", "goal": "str"},
            output_schema={"strategy": "dict", "priorities": "list"}
        ))
        
        # Layer 1: 独立专家
        self._register(ExpertConfig(
            expert_id="character_forger",
            name="§1角色铸造师",
            layer=1,
            dependencies=[],
            system_prompt_file="character_forger.md",
            input_schema={"synopsis": "str", "genre": "str"},
            output_schema={"characters": "list", "protagonist": "dict"}
        ))
        
        self._register(ExpertConfig(
            expert_id="world_forger",
            name="⑫世界观锻造",
            layer=1,
            dependencies=[],
            system_prompt_file="world_forger.md",
            input_schema={"genre": "str", "setting": "str"},
            output_schema={"world_setting": "dict"}
        ))
        
        self._register(ExpertConfig(
            expert_id="commercial_packager",
            name="⑧商业包装",
            layer=1,
            dependencies=[],
            system_prompt_file="commercial_packager.md",
            input_schema={"synopsis": "str", "genre": "str"},
            output_schema={"title": "str", "logline": "str", "tags": "list"},
            optional=True
        ))
        
        # Layer 2: 依赖角色
        self._register(ExpertConfig(
            expert_id="emotion_weaver",
            name="§2情感编织师",
            layer=2,
            dependencies=["character_forger"],
            system_prompt_file="emotion_weaver.md",
            input_schema={"characters": "list", "synopsis": "str"},
            output_schema={"emotion_arc": "dict", "tear_points": "list"}
        ))
        
        # Layer 3: 依赖情感
        self._register(ExpertConfig(
            expert_id="structure_architect",
            name="§3结构建筑师",
            layer=3,
            dependencies=["emotion_weaver"],
            system_prompt_file="structure_architect.md",
            input_schema={"emotion_arc": "dict", "synopsis": "str"},
            output_schema={"structure": "dict", "turning_points": "list"}
        ))
        
        # Layer 4: 对白和场景
        self._register(ExpertConfig(
            expert_id="dialogue_master",
            name="§4对白大师",
            layer=4,
            dependencies=["character_forger", "structure_architect"],
            system_prompt_file="dialogue_master.md",
            input_schema={"characters": "list", "structure": "dict"},
            output_schema={"dialogue_style": "dict", "signature_lines": "list"}
        ))
        
        self._register(ExpertConfig(
            expert_id="scene_craftsman",
            name="⑪场景工匠",
            layer=4,
            dependencies=["dialogue_master"],
            system_prompt_file="scene_craftsman.md",
            input_schema={"dialogue_style": "dict", "setting": "str"},
            output_schema={"scene_designs": "list"}
        ))
        
        # Layer 5: 分集编剧
        self._register(ExpertConfig(
            expert_id="episode_writer",
            name="§5分集编剧",
            layer=5,
            dependencies=["character_forger", "emotion_weaver", "structure_architect", "dialogue_master"],
            system_prompt_file="episode_writer.py",
            input_schema={"all_above": "dict", "episode_count": "int"},
            output_schema={"episodes": "list", "episode_scripts": "list"}
        ))
        
        # Layer 6: 格式和金句
        self._register(ExpertConfig(
            expert_id="format_craftsman",
            name="§6格式工匠",
            layer=6,
            dependencies=["episode_writer"],
            system_prompt_file="format_craftsman.py",
            input_schema={"episodes": "list"},
            output_schema={"formatted_script": "str"}
        ))
        
        self._register(ExpertConfig(
            expert_id="quote_extractor",
            name="⑬金句萃取",
            layer=6,
            dependencies=["dialogue_master", "episode_writer"],
            system_prompt_file="quote_extractor.md",
            input_schema={"episodes": "list", "dialogue_style": "dict"},
            output_schema={"golden_quotes": "list"},
            optional=True
        ))
        
        # Layer 7: 质量审计
        self._register(ExpertConfig(
            expert_id="quality_auditor",
            name="§7质量审计",
            layer=7,
            dependencies=["episode_writer", "format_craftsman"],
            system_prompt_file="quality_auditor.py",
            input_schema={"script": "str", "all_results": "dict"},
            output_schema={"audit_report": "dict", "score": "float"}
        ))
        
        # Layer 8: 改稿和商业操盘
        self._register(ExpertConfig(
            expert_id="revision_editor",
            name="§9改稿编辑",
            layer=8,
            dependencies=["quality_auditor"],
            system_prompt_file="revision_editor.py",
            input_schema={"script": "str", "audit_report": "dict"},
            output_schema={"revised_script": "str"}
        ))
        
        self._register(ExpertConfig(
            expert_id="commercial_operator",
            name="⑭商业操盘",
            layer=8,
            dependencies=["commercial_packager"],
            system_prompt_file="commercial_operator.md",
            input_schema={"packaging": "dict", "script": "str"},
            output_schema={"distribution_plan": "dict"},
            optional=True
        ))
        
        # Layer 9: 品控总监
        self._register(ExpertConfig(
            expert_id="quality_director",
            name="⑮品控总监",
            layer=9,
            dependencies=["quality_auditor", "commercial_operator"],
            system_prompt_file="quality_director.md",
            input_schema={"audit_report": "dict", "distribution_plan": "dict"},
            output_schema={"final_approval": "bool", "release_notes": "str"}
        ))
    
    def _register(self, config: ExpertConfig):
        """注册单个专家"""
        self.experts[config.expert_id] = config
    
    def _load_system_prompt(self, expert_id: str) -> str:
        """加载专家系统提示词"""
        config = self.experts[expert_id]
        prompt_file = self.experts_base / config.system_prompt_file
        
        if prompt_file.suffix == ".py":
            # Python文件，提取PROMPT变量
            import ast
            with open(prompt_file, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id == "PROMPT":
                            if isinstance(node.value, ast.Constant):
                                return node.value.value
            raise ValueError(f"Cannot find PROMPT variable in {prompt_file}")
        else:
            # Markdown文件，直接读取
            return prompt_file.read_text(encoding='utf-8')
    
    def _build_user_prompt(self, expert_id: str, context: Dict) -> str:
        """构建用户提示词"""
        config = self.experts[expert_id]
        
        # 收集依赖的输出
        input_data = {}
        for dep_id in config.dependencies:
            if dep_id in self.results and self.results[dep_id].output:
                input_data[dep_id] = self.results[dep_id].output
        
        # 加入项目上下文
        input_data["project"] = context.get("project", {})
        
        # 构建用户提示词
        user_prompt = f"""## 项目背景
{json.dumps(context.get('project', {}), ensure_ascii=False, indent=2)}

## 上游专家输出
{json.dumps(input_data, ensure_ascii=False, indent=2)}

## 任务要求
请根据以上信息，完成你的专业工作，并严格按照输出格式要求返回JSON结果。
"""
        return user_prompt
    
    def _execute_expert(self, expert_id: str, context: Dict) -> ExpertResult:
        """执行单个专家"""
        config = self.experts[expert_id]
        start_time = time.time()
        
        try:
            # 加载系统提示词
            system_prompt = self._load_system_prompt(expert_id)
            
            # 构建用户提示词
            user_prompt = self._build_user_prompt(expert_id, context)
            
            # 调用LLM
            response = self.llm.call(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.7,
                max_tokens=4096
            )
            
            # 解析响应
            output = self._parse_response(expert_id, response)
            
            execution_time = time.time() - start_time
            
            return ExpertResult(
                expert_id=expert_id,
                status=ExpertStatus.SUCCESS,
                output=output,
                execution_time=execution_time
            )
        
        except Exception as e:
            execution_time = time.time() - start_time
            return ExpertResult(
                expert_id=expert_id,
                status=ExpertStatus.FAILED,
                error=str(e),
                execution_time=execution_time
            )
    
    def _parse_response(self, expert_id: str, response: str) -> Dict:
        """解析LLM响应为JSON"""
        # 尝试提取JSON
        import re
        
        # 查找JSON代码块
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response)
        if json_match:
            json_str = json_match.group(1)
        else:
            # 尝试直接解析
            json_str = response
        
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON from {expert_id}: {e}\nResponse: {response[:500]}")
    
    def execute(self, project: Dict, mode: ExecutionMode = ExecutionMode.FULL, 
                parallel: bool = True) -> Dict[str, ExpertResult]:
        """
        执行流水线
        
        Args:
            project: 项目信息
            mode: 执行模式
            parallel: 是否并行执行无依赖的专家
        
        Returns:
            所有专家的执行结果
        """
        context = {"project": project, "mode": mode.value}
        self.results = {}
        
        # 根据模式确定需要执行的专家
        experts_to_run = self._get_experts_for_mode(mode)
        
        # 按层级分组
        layers = {}
        for expert_id in experts_to_run:
            config = self.experts[expert_id]
            if config.layer not in layers:
                layers[config.layer] = []
            layers[config.layer].append(expert_id)
        
        # 逐层执行
        for layer in sorted(layers.keys()):
            expert_ids = layers[layer]
            
            if parallel and len(expert_ids) > 1:
                # 并行执行同层专家
                with concurrent.futures.ThreadPoolExecutor(max_workers=len(expert_ids)) as executor:
                    futures = {
                        executor.submit(self._execute_expert, eid, context): eid 
                        for eid in expert_ids
                    }
                    for future in concurrent.futures.as_completed(futures):
                        expert_id = futures[future]
                        self.results[expert_id] = future.result()
            else:
                # 串行执行
                for expert_id in expert_ids:
                    self.results[expert_id] = self._execute_expert(expert_id, context)
            
            # 检查是否有失败的必需专家
            for expert_id in expert_ids:
                result = self.results[expert_id]
                if result.status == ExpertStatus.FAILED and not self.experts[expert_id].optional:
                    raise RuntimeError(f"Required expert {expert_id} failed: {result.error}")
        
        return self.results
    
    def _get_experts_for_mode(self, mode: ExecutionMode) -> List[str]:
        """根据执行模式返回需要运行的专家列表"""
        if mode == ExecutionMode.FULL:
            return list(self.experts.keys())
        elif mode == ExecutionMode.EPISODE_ONLY:
            # 只跑到分集编剧
            return ["commander", "character_forger", "world_forger", "emotion_weaver",
                    "structure_architect", "dialogue_master", "episode_writer"]
        elif mode == ExecutionMode.SCRIPT_ONLY:
            # 只跑分集到剧本
            return ["episode_writer", "format_craftsman", "quality_auditor"]
        elif mode == ExecutionMode.POLISH_ONLY:
            # 只跑精修
            return ["revision_editor", "quality_auditor"]
        elif mode == ExecutionMode.EVALUATE_ONLY:
            # 只跑评估
            return ["quality_auditor"]
        else:
            raise ValueError(f"Unknown mode: {mode}")
    
    def get_execution_report(self) -> Dict:
        """生成执行报告"""
        report = {
            "total_experts": len(self.experts),
            "executed": len(self.results),
            "successful": sum(1 for r in self.results.values() if r.status == ExpertStatus.SUCCESS),
            "failed": sum(1 for r in self.results.values() if r.status == ExpertStatus.FAILED),
            "total_time": sum(r.execution_time for r in self.results.values()),
            "details": []
        }
        
        for expert_id, result in self.results.items():
            report["details"].append({
                "expert_id": expert_id,
                "name": self.experts[expert_id].name,
                "status": result.status.value,
                "execution_time": result.execution_time,
                "error": result.error
            })
        
        return report


# ===== 使用示例 =====

def main():
    """示例：如何运行引擎"""
    
    # 1. 配置LLM适配器
    llm_config = {
        "platform": "openai",
        # 需要在环境变量中设置 OPENAI_API_KEY 和 OPENAI_BASE_URL
    }
    
    # 2. 创建适配器实例
    adapter = LLMAPIAdapter(llm_config)
    
    # 3. 创建调度器
    orchestrator = PipelineOrchestrator(
        llm_adapter=adapter,
        experts_base_path="./experts"  # 专家配置文件目录
    )
    
    # 4. 准备项目信息
    project = {
        "name": "岭上之路",
        "genre": "男频/职场/励志",
        "synopsis": "一个大专生在深圳打拼，从底层销售做到上市公司CEO的故事...",
        "target_audience": "18-35岁男性",
        "episode_count": 30,
        "theme": "逆袭、奋斗、兄弟情"
    }
    
    # 5. 执行流水线
    try:
        results = orchestrator.execute(
            project=project,
            mode=ExecutionMode.FULL,
            parallel=True
        )
        
        # 6. 生成报告
        report = orchestrator.get_execution_report()
        print(json.dumps(report, ensure_ascii=False, indent=2))
        
        # 7. 获取最终剧本
        if "format_craftsman" in results and results["format_craftsman"].output:
            final_script = results["format_craftsman"].output.get("formatted_script", "")
            print("\n=== 最终剧本 ===")
            print(final_script[:2000])  # 打印前2000字符
    
    except Exception as e:
        print(f"Pipeline execution failed: {e}")
        report = orchestrator.get_execution_report()
        print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
