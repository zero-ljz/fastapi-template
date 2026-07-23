"""创建并配置 FastAPI 应用。"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.main import api_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import logger, setup_logging
from app.middleware.request_context import request_context_middleware

# 初始化日志
setup_logging()

# 管理应用生命周期


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(
        "应用启动 | {} v{} | 环境: {}",
        settings.PROJECT_NAME,
        settings.VERSION,
        settings.ENVIRONMENT,
    )
    yield
    logger.info("应用关闭")


# 创建应用实例

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# 配置跨域资源共享
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)

# 注册异常处理器
register_exception_handlers(app)

# 注册请求日志中间件
app.middleware("http")(request_context_middleware)

# 注册接口路由
app.include_router(api_router, prefix=settings.API_V1_STR)


# 健康检查
@app.get(f"{settings.API_V1_STR}/health", tags=["系统"], summary="健康检查")
async def health_check():
    """返回应用健康状态。"""
    return {"status": "ok", "version": settings.VERSION}


# 挂载静态文件目录
app.mount(
    "/static", StaticFiles(directory=settings.ROOT_PATH / "static"), name="static"
)
app.mount(
    "/uploads", StaticFiles(directory=settings.ROOT_PATH / "uploads"), name="uploads"
)
