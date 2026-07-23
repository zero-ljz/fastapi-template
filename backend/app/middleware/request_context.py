"""请求标识与访问日志中间件。"""

from collections.abc import Awaitable, Callable
from time import perf_counter
from uuid import uuid4

from fastapi import Request, Response

from app.core.logging import logger


async def request_context_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    """记录请求标识、状态码与耗时，不记录可能包含敏感信息的查询参数。"""
    request_id = uuid4().hex
    request.state.request_id = request_id
    started_at = perf_counter()

    with logger.contextualize(request_id=request_id):
        response = await call_next(request)
        duration_ms = (perf_counter() - started_at) * 1000
        logger.info(
            "HTTP request | method={} | path={} | status={} | duration_ms={:.2f}",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )

    response.headers["X-Request-ID"] = request_id
    return response
