from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import logger, setup_logging
from app.core.exceptions import register_exception_handlers
from app.api.main import api_router
from app.admin import register_admin


# ---------------------------------------------------------------------------
# 日志初始化
# ---------------------------------------------------------------------------
setup_logging()


# ---------------------------------------------------------------------------
# 生命周期
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("应用启动 | {} v{} | 环境: {}", settings.PROJECT_NAME, settings.VERSION, settings.ENVIRONMENT)
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
    allow_origins=["*"],  # 生产环境应改为具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册全局异常处理器
register_exception_handlers(app)

# SQLAdmin 后台，访问路径: /admin
register_admin(app)


# ---------------------------------------------------------------------------
# 请求日志中间件
# ---------------------------------------------------------------------------

@app.middleware("http")
async def log_request(request: Request, call_next):
    """记录每个 HTTP 请求的关键信息"""
    # 构造请求行
    query = f"?{request.url.query}" if request.url.query else ""
    request_line = f"{request.method} {request.url.path}{query}"

    logger.debug("→ {}", request_line)

    response = await call_next(request)

    logger.debug("← {} | {}", request_line, response.status_code)
    return response


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


# ---------------------------------------------------------------------------
# 前端 SPA 兜底
# ---------------------------------------------------------------------------

@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    public_path = settings.ROOT_PATH.parent / "frontend" / "dist"
    file_path = public_path / full_path
    if file_path.is_file():
        return FileResponse(file_path)
    index_path = public_path / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="Not Found")
    return FileResponse(index_path)
