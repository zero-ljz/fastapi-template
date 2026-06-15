import os
from contextlib import asynccontextmanager
import logging
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.deps import AsyncSessionDep, SessionDep
from app.models import User

from app.api.routes import login

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    print("正在关闭应用...")

print(f"CWD: {os.getcwd()}")
print(f"ROOT_PATH: {settings.ROOT_PATH}")

app = FastAPI(debug=True, title="FastAPI应用")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 可以改成具体域名 ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_request(request: Request, call_next):
    request_line = f'{request.method} {request.url.path}{request.url.query and "?" + request.url.query} {request.scope["http_version"]}'
    headers = "\n".join(
        [f"{key}: {value}" for key, value in sorted(request.headers.items())]
    )
    body = await request.body()
    async def receive():
        return {"type": "http.request", "body": body}
    request._receive = receive
    
    response_content = f'\n{request_line}\n{headers}\n\n{body.decode(encoding="utf-8", errors="ignore")}'
    # 打印原始请求报文
    print("\n\n" + response_content)
    # 继续处理请求
    response = await call_next(request)
    return response


app.include_router(login.router)


app.mount(
    "/static", StaticFiles(directory=settings.ROOT_PATH / "static"), name="static"
)
app.mount(
    "/uploads", StaticFiles(directory=settings.ROOT_PATH / "uploads"), name="uploads"
)


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
