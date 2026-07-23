"""汇总应用接口路由。"""

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.api.routes import login, users
from app.schemas.common import ErrorResponse, ValidationErrorResponse


def _error_response(
    description: str,
    model: type[BaseModel] = ErrorResponse,
) -> dict[str, Any]:
    return {
        "model": model,
        "description": description,
        "headers": {
            "X-Request-ID": {
                "description": "用于关联服务端日志的请求标识",
                "schema": {"type": "string"},
            }
        },
    }


COMMON_ERROR_RESPONSES: dict[int | str, dict[str, Any]] = {
    400: _error_response("请求参数错误"),
    401: _error_response("未认证或认证已失效"),
    403: _error_response("权限不足"),
    404: _error_response("资源不存在"),
    409: _error_response("资源冲突"),
    422: _error_response("请求数据校验失败", ValidationErrorResponse),
    500: _error_response("服务器内部错误"),
}

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
