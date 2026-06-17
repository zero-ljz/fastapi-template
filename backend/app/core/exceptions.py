# app/core/exceptions.py

"""
统一异常体系

层级:
    AppException (base)
    ├── BadRequestException      (400)
    ├── UnauthorizedException    (401)
    ├── ForbiddenException       (403)
    ├── NotFoundException        (404)
    ├── ConflictException        (409)
    └── InternalServerException  (500)

用法:
    from app.core.exceptions import NotFoundException
    raise NotFoundException(detail="用户不存在")
"""

from __future__ import annotations

from typing import Any, Optional

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.logging import logger


# ---------------------------------------------------------------------------
# 异常类
# ---------------------------------------------------------------------------


class AppException(Exception):
    """应用异常基类"""

    status_code: int = 500
    detail: str = "服务器内部错误"
    error_code: str = "INTERNAL_ERROR"

    def __init__(
        self,
        detail: Optional[str] = None,
        *,
        error_code: Optional[str] = None,
        headers: Optional[dict[str, str]] = None,
        data: Any = None,
    ):
        if detail is not None:
            self.detail = detail
        if error_code is not None:
            self.error_code = error_code
        self.headers = headers
        self.data = data
        super().__init__(self.detail)


class BadRequestException(AppException):
    """400 — 请求参数错误"""

    status_code = 400
    detail = "请求参数错误"
    error_code = "BAD_REQUEST"


class UnauthorizedException(AppException):
    """401 — 未认证"""

    status_code = 401
    detail = "未认证，请先登录"
    error_code = "UNAUTHORIZED"


class ForbiddenException(AppException):
    """403 — 权限不足"""

    status_code = 403
    detail = "权限不足"
    error_code = "FORBIDDEN"


class NotFoundException(AppException):
    """404 — 资源不存在"""

    status_code = 404
    detail = "资源不存在"
    error_code = "NOT_FOUND"


class ConflictException(AppException):
    """409 — 资源冲突"""

    status_code = 409
    detail = "资源冲突"
    error_code = "CONFLICT"


class InternalServerException(AppException):
    """500 — 服务器内部错误"""

    status_code = 500
    detail = "服务器内部错误"
    error_code = "INTERNAL_ERROR"


# ---------------------------------------------------------------------------
# 全局异常处理器注册
# ---------------------------------------------------------------------------


def register_exception_handlers(app: FastAPI) -> None:
    """在 FastAPI 应用上注册全局异常处理器"""

    @app.exception_handler(AppException)
    async def app_exception_handler(
        request: Request, exc: AppException
    ) -> JSONResponse:
        """处理所有 AppException 子类"""
        logger.warning(
            "AppException | {method} {path} | {status} | {detail}",
            method=request.method,
            path=request.url.path,
            status=exc.status_code,
            detail=exc.detail,
        )
        content: dict[str, Any] = {
            "code": exc.error_code,
            "message": exc.detail,
        }
        if exc.data is not None:
            content["data"] = exc.data
        return JSONResponse(
            status_code=exc.status_code,
            content=content,
            headers=exc.headers,
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """兜底：处理所有未捕获的异常"""
        logger.exception(
            "Unhandled Exception | {method} {path} | {exc}",
            method=request.method,
            path=request.url.path,
            exc=str(exc),
        )
        return JSONResponse(
            status_code=500,
            content={
                "code": "INTERNAL_ERROR",
                "message": "服务器内部错误",
            },
        )
