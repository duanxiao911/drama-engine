"""
FastAPI入口

提供RESTful API和WebSocket支持

Endpoints:
    POST /api/v1/create        - 完整流程
    POST /api/v1/step/{expert} - 单步执行
    GET  /api/v1/progress/{wf_id} - 获取进度
    GET  /api/v1/experts       - 列出专家
    POST /api/v1/resume/{wf_id}  - 恢复断点
    WS   /api/v1/ws/{wf_id}    - WebSocket实时对话
"""

import os
import json
import asyncio
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from datetime import datetime

# 导入项目模块
from src.config.settings import load_config, get_config, ConfigManager
from src.workflow.orchestrator import Orchestrator
from src.experts.base import OpenAIClient


# ============ Pydantic模型 ============

class CreateRequest(BaseModel):
    """完整创作请求"""
    story_direction: str = Field(..., description="故事方向描述")
    drama_type: Optional[str] = Field(None, description="故事类型")
    total_episodes: Optional[int] = Field(None, description="总集数")
    user_materials: Optional[str] = Field(None, description="用户素材（硬约束）")
    stop_at: Optional[str] = Field(None, description="可选，在指定专家处停止")


class StepRequest(BaseModel):
    """单步执行请求"""
    user_input: str = Field(..., description="输入内容")
    context: Optional[Dict] = Field(None, description="可选，外部传入的上下文")


class StepResponse(BaseModel):
    """单步执行响应"""
    expert_id: str
    content: str
    validation_passed: bool
    validation_errors: List[str]
    structured_data: Dict


class ProgressResponse(BaseModel):
    """进度查询响应"""
    workflow_id: str
    status: str
    current_step: int
    total_steps: int
    current_expert: Optional[str]
    completed_experts: List[str]
    risk_level: Optional[str]


class CreateResponse(BaseModel):
    """完整创作响应"""
    workflow_id: str
    status: str
    message: str


class ExpertInfo(BaseModel):
    """专家信息"""
    id: str
    name: str
    description: str
    in_sequence: bool


# ============ FastAPI应用 ============

# 全局状态
workflows: Dict[str, Orchestrator] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时加载配置
    config_file = os.getenv("DRAMA_CONFIG", "config.yaml")
    if os.path.exists(config_file):
        load_config(config_file)
    yield
    # 关闭时清理


def create_app() -> FastAPI:
    """创建FastAPI应用"""
    config = get_config()

    app = FastAPI(
        title="Drama Engine API",
        description="精品短剧创作引擎 API",
        version="1.0.0",
        lifespan=lifespan,
    )

    # CORS配置
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.api.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 创建LLM客户端工厂
    def create_llm_client() -> OpenAIClient:
        return OpenAIClient(
            api_key=config.llm.api_key or os.getenv("OPENAI_API_KEY", ""),
            model=config.llm.model,
            base_url=config.llm.base_url,
            temperature=config.llm.temperature,
        )

    # ============ API路由 ============

    @app.get("/")
    async def root():
        return {
            "name": "Drama Engine API",
            "version": "1.0.0",
            "docs": "/docs",
        }

    @app.get("/health")
    async def health():
        return {"status": "healthy"}

    @app.post("/api/v1/create", response_model=CreateResponse)
    async def create_story(request: CreateRequest, background_tasks: BackgroundTasks):
        """
        启动完整创作工作流

        这是一个异步操作，工作流将在后台执行。
        使用 /api/v1/progress/{workflow_id} 查询进度。
        """
        config = get_config()

        llm_client = create_llm_client()
        orchestrator = Orchestrator(
            llm_client=llm_client,
            knowledge_base_path=config.paths.experts_prompts,
            project_path=config.paths.root,
            enable_checkpoint=config.workflow.enable_checkpoint,
        )

        # 初始化上下文
        from src.experts.base import ExpertContext
        context = ExpertContext(
            story_direction=request.story_direction,
            project_config={
                "drama_type": request.drama_type or config.default_drama_type,
                "total_episodes": request.total_episodes or config.default_total_episodes,
                "user_materials": request.user_materials,
            } if any([request.drama_type, request.total_episodes, request.user_materials]) else {},
        )

        # 后台执行工作流
        workflow_id = f"wf_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        workflows[workflow_id] = orchestrator

        async def run_workflow():
            try:
                orchestrator._init_workflow(request.story_direction)
                orchestrator.state.context_snapshot = context
                orchestrator.run_full(request.story_direction, stop_at=request.stop_at)
            except Exception as e:
                if orchestrator.state:
                    orchestrator.state.status = "failed"
                    orchestrator.state.error_message = str(e)

        background_tasks.add_task(run_workflow)

        return CreateResponse(
            workflow_id=workflow_id,
            status="started",
            message=f"工作流已启动，workflow_id: {workflow_id}",
        )

    @app.post("/api/v1/step/{expert_id}", response_model=StepResponse)
    async def run_step(expert_id: str, request: StepRequest):
        """
        执行单个专家步骤
        """
        config = get_config()

        llm_client = create_llm_client()
        orchestrator = Orchestrator(
            llm_client=llm_client,
            knowledge_base_path=config.paths.experts_prompts,
            project_path=config.paths.root,
        )

        from src.experts.base import ExpertContext
        context = None
        if request.context:
            context = ExpertContext(**request.context)

        output = orchestrator.run_step(expert_id, context=context, user_input=request.user_input)

        return StepResponse(
            expert_id=output.expert_name,
            content=output.content,
            validation_passed=output.validation_passed,
            validation_errors=output.validation_errors,
            structured_data=output.structured_data,
        )

    @app.get("/api/v1/progress/{workflow_id}", response_model=ProgressResponse)
    async def get_progress(workflow_id: str):
        """
        查询工作流进度
        """
        if workflow_id not in workflows:
            raise HTTPException(status_code=404, detail=f"工作流 {workflow_id} 未找到")

        orchestrator = workflows[workflow_id]
        progress = orchestrator.get_progress()

        context = orchestrator.state.context_snapshot if orchestrator.state else None

        return ProgressResponse(
            workflow_id=workflow_id,
            status=progress.get("status", "unknown"),
            current_step=progress.get("current_step", 0),
            total_steps=progress.get("total_steps", 7),
            current_expert=progress.get("current_expert"),
            completed_experts=progress.get("completed_experts", []),
            risk_level=context.risk_level if context else None,
        )

    @app.get("/api/v1/experts", response_model=List[ExpertInfo])
    async def list_experts():
        """
        列出所有可用的专家
        """
        config = get_config()
        llm_client = create_llm_client()
        orchestrator = Orchestrator(
            llm_client=llm_client,
            knowledge_base_path=config.paths.experts_prompts,
        )

        return [
            ExpertInfo(**info)
            for info in orchestrator.list_available_experts()
        ]

    @app.get("/api/v1/result/{workflow_id}")
    async def get_result(workflow_id: str):
        """
        获取工作流完整结果
        """
        if workflow_id not in workflows:
            raise HTTPException(status_code=404, detail=f"工作流 {workflow_id} 未找到")

        orchestrator = workflows[workflow_id]
        if not orchestrator.state:
            raise HTTPException(status_code=404, detail="工作流尚未初始化")

        state = orchestrator.state
        return {
            "workflow_id": workflow_id,
            "status": state.status.value,
            "context": state.context_snapshot.to_dict() if state.context_snapshot else {},
            "outputs": {k: v.to_dict() for k, v in state.step_outputs.items()},
        }

    @app.post("/api/v1/resume/{workflow_id}")
    async def resume_workflow(workflow_id: str):
        """
        从断点恢复工作流
        """
        config = get_config()

        llm_client = create_llm_client()
        orchestrator = Orchestrator(
            llm_client=llm_client,
            knowledge_base_path=config.paths.experts_prompts,
            project_path=config.paths.root,
        )

        try:
            state = orchestrator.resume(workflow_id)
            workflows[workflow_id] = orchestrator
            return {
                "workflow_id": workflow_id,
                "status": state.status.value,
                "message": "工作流已恢复",
            }
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))

    @app.websocket("/api/v1/ws/{workflow_id}")
    async def websocket_endpoint(websocket: WebSocket, workflow_id: str):
        """
        WebSocket实时对话

        支持实时接收工作流输出和发送用户输入
        """
        await websocket.accept()

        config = get_config()
        llm_client = create_llm_client()

        # 获取或创建工作流
        if workflow_id in workflows:
            orchestrator = workflows[workflow_id]
        else:
            orchestrator = Orchestrator(
                llm_client=llm_client,
                knowledge_base_path=config.paths.experts_prompts,
                project_path=config.paths.root,
            )
            workflows[workflow_id] = orchestrator

        # 注册实时回调
        async def on_step_complete(expert_id, step_idx, output):
            await websocket.send_json({
                "type": "step_complete",
                "expert_id": expert_id,
                "step_index": step_idx,
                "content": output.content[:500],
                "validation_passed": output.validation_passed,
            })

        orchestrator.on("on_step_complete", on_step_complete)

        try:
            while True:
                data = await websocket.receive_json()
                msg_type = data.get("type")

                if msg_type == "start":
                    story_direction = data.get("story_direction", "")
                    orchestrator._init_workflow(story_direction)

                    await websocket.send_json({
                        "type": "started",
                        "workflow_id": orchestrator.state.workflow_id,
                    })

                    # 异步执行
                    asyncio.create_task(
                        orchestrator.run_full(story_direction)
                    )

                elif msg_type == "user_input":
                    user_input = data.get("content", "")
                    expert_id = data.get("expert_id", "§0")

                    output = orchestrator.run_step(expert_id, user_input=user_input)

                    await websocket.send_json({
                        "type": "step_output",
                        "expert_id": expert_id,
                        "content": output.content,
                        "validation_passed": output.validation_passed,
                    })

                elif msg_type == "progress":
                    progress = orchestrator.get_progress()
                    await websocket.send_json({
                        "type": "progress",
                        **progress,
                    })

        except WebSocketDisconnect:
            pass
        finally:
            await websocket.close()

    return app


# 创建应用实例
app = create_app()


def run_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """运行API服务器"""
    import uvicorn
    uvicorn.run(
        "src.api.server:app",
        host=host,
        port=port,
        reload=reload,
    )


if __name__ == "__main__":
    run_server()