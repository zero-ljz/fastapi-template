# app/main.py

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.main import api_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import logger, setup_logging
from app.middleware.request_context import request_context_middleware

# ---------------------------------------------------------------------------
# 日志初始化
# ---------------------------------------------------------------------------
setup_logging()


# ---------------------------------------------------------------------------
# 生命周期
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# FastAPI 应用
# ---------------------------------------------------------------------------

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)

# 注册全局异常处理器
register_exception_handlers(app)

# ---------------------------------------------------------------------------
# 请求日志中间件
# ---------------------------------------------------------------------------


app.middleware("http")(request_context_middleware)


# ---------------------------------------------------------------------------
# API 路由
# ---------------------------------------------------------------------------

app.include_router(api_router, prefix=settings.API_V1_STR)


# 健康检查
@app.get(f"{settings.API_V1_STR}/health", tags=["系统"])
async def health_check():
    """健康检查接口"""
    return {"status": "ok", "version": settings.VERSION}


# ---------------------------------------------------------------------------
# 静态文件
# ---------------------------------------------------------------------------

app.mount(
    "/static", StaticFiles(directory=settings.ROOT_PATH / "static"), name="static"
)
app.mount(
    "/uploads", StaticFiles(directory=settings.ROOT_PATH / "uploads"), name="uploads"
)
