"""定义应用异常及其全局处理器。"""

from collections.abc import Mapping
from typing import ClassVar

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import JsonValue
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import logger

type ErrorDetails = dict[str, JsonValue] | None


class AppException(Exception):
    """应用异常基类。"""

    status_code: int = 500
    detail: str = "服务器内部错误"
    error_code: str = "INTERNAL_ERROR"
    default_headers: ClassVar[dict[str, str] | None] = None

    def __init__(
        self,
        detail: str | None = None,
        *,
        error_code: str | None = None,
        headers: dict[str, str] | None = None,
        details: ErrorDetails = None,
    ) -> None:
        if detail is not None:
            self.detail = detail
        if error_code is not None:
            self.error_code = error_code
        self.headers = headers if headers is not None else self.default_headers
        self.details = details
        super().__init__(self.detail)


class BadRequestException(AppException):
    status_code = 400
    detail = "请求参数错误"
    error_code = "BAD_REQUEST"


class UnauthorizedException(AppException):
    status_code = 401
    detail = "未认证，请先登录"
    error_code = "UNAUTHORIZED"
    default_headers = {"WWW-Authenticate": "Bearer"}


class ForbiddenException(AppException):
    status_code = 403
    detail = "权限不足"
    error_code = "FORBIDDEN"


class NotFoundException(AppException):
    status_code = 404
    detail = "资源不存在"
    error_code = "NOT_FOUND"


class ConflictException(AppException):
    status_code = 409
    detail = "资源冲突"
    error_code = "CONFLICT"


_FRAMEWORK_ERRORS: dict[int, tuple[str, str]] = {
    401: ("UNAUTHORIZED", "未认证或认证已失效"),
    404: ("NOT_FOUND", "资源不存在"),
    405: ("METHOD_NOT_ALLOWED", "请求方法不受支持"),
}


def _build_error_response(
    *,
    status_code: int,
    code: str,
    message: str,
    details: ErrorDetails | list[JsonValue] = None,
    headers: Mapping[str, str] | None = None,
) -> JSONResponse:
    """构造符合统一错误协议的响应。"""
    return JSONResponse(
        status_code=status_code,
        content={
            "code": code,
            "message": message,
            "details": details,
        },
        headers=dict(headers or {}),
    )


def register_exception_handlers(app: FastAPI) -> None:
    """在 FastAPI 应用上注册全局异常处理器。"""

    @app.exception_handler(AppException)
    async def app_exception_handler(
        request: Request, exc: AppException
    ) -> JSONResponse:
        return _build_error_response(
            status_code=exc.status_code,
            code=exc.error_code,
            message=exc.detail,
            details=exc.details,
            headers=exc.headers,
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        code, message = _FRAMEWORK_ERRORS.get(
            exc.status_code,
            (
                f"HTTP_{exc.status_code}",
                exc.detail if isinstance(exc.detail, str) else "请求失败",
            ),
        )

        return _build_error_response(
            status_code=exc.status_code,
            code=code,
            message=message,
            headers=exc.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def request_validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        issues: list[JsonValue] = [
            {
                "location": [
                    item if isinstance(item, (str, int)) else str(item)
                    for item in error["loc"]
                ],
                "message": str(error["msg"]),
                "code": str(error["type"]),
            }
            for error in exc.errors()
        ]
        return _build_error_response(
            status_code=422,
            code="VALIDATION_ERROR",
            message="请求数据校验失败",
            details=issues,
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        request_id: str = request.state.request_id
        with logger.contextualize(request_id=request_id):
            logger.exception(
                "Unhandled Exception | {method} {path} | {exc}",
                method=request.method,
                path=request.url.path,
                exc=str(exc),
            )
        return _build_error_response(
            status_code=500,
            code="INTERNAL_ERROR",
            message="服务器内部错误",
            headers={"X-Request-ID": request_id},
        )
