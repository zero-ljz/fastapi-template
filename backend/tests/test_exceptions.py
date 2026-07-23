"""验证统一错误响应的关键行为。"""

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel

from app.core.exceptions import (
    BadRequestException,
    ConflictException,
    ForbiddenException,
    NotFoundException,
    UnauthorizedException,
    register_exception_handlers,
)
from app.middleware.request_context import request_context_middleware


class ValidationPayload(BaseModel):
    quantity: int


@pytest.fixture
def exception_client():
    test_app = FastAPI()
    register_exception_handlers(test_app)
    test_app.middleware("http")(request_context_middleware)

    @test_app.get("/application")
    async def raise_application_exception():
        raise ConflictException(
            detail="名称已存在",
            error_code="NAME_ALREADY_EXISTS",
            details={"field": "name"},
        )

    @test_app.get("/unauthorized")
    async def raise_unauthorized_exception():
        raise UnauthorizedException(error_code="INVALID_ACCESS_TOKEN")

    @test_app.get("/framework")
    async def raise_framework_exception():
        raise HTTPException(status_code=418, detail="暂时无法泡茶")

    @test_app.post("/validation")
    async def validate_payload(payload: ValidationPayload):
        return payload

    @test_app.get("/unhandled")
    async def raise_unhandled_exception():
        raise RuntimeError("不应泄露的内部信息")

    with TestClient(test_app, raise_server_exceptions=False) as client:
        yield client


@pytest.mark.parametrize(
    ("exception", "status_code"),
    [
        (BadRequestException(), 400),
        (UnauthorizedException(), 401),
        (ForbiddenException(), 403),
        (NotFoundException(), 404),
        (ConflictException(), 409),
    ],
)
def test_exception_status_codes(exception, status_code):
    assert exception.status_code == status_code


def test_application_exception_uses_unified_contract(exception_client):
    response = exception_client.get("/application")

    assert response.status_code == 409
    assert response.json() == {
        "code": "NAME_ALREADY_EXISTS",
        "message": "名称已存在",
        "details": {"field": "name"},
    }
    assert response.headers["X-Request-ID"]


def test_unauthorized_exception_keeps_authentication_header(exception_client):
    response = exception_client.get("/unauthorized")

    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"
    assert response.json()["code"] == "INVALID_ACCESS_TOKEN"


@pytest.mark.parametrize(
    ("method", "path", "status_code", "code", "message"),
    [
        ("get", "/framework", 418, "HTTP_418", "暂时无法泡茶"),
        ("get", "/missing", 404, "NOT_FOUND", "资源不存在"),
        ("post", "/application", 405, "METHOD_NOT_ALLOWED", "请求方法不受支持"),
    ],
)
def test_framework_http_exceptions_use_unified_contract(
    exception_client, method, path, status_code, code, message
):
    response = exception_client.request(method, path)

    assert response.status_code == status_code
    assert response.json()["code"] == code
    assert response.json()["message"] == message
    assert response.headers["X-Request-ID"]


def test_request_validation_error_has_safe_details(exception_client):
    response = exception_client.post("/validation", json={"quantity": "many"})

    assert response.status_code == 422
    body = response.json()
    assert body["code"] == "VALIDATION_ERROR"
    assert body["details"] == [
        {
            "location": ["body", "quantity"],
            "message": "Input should be a valid integer, unable to parse string as an integer",
            "code": "int_parsing",
        }
    ]


def test_unhandled_exception_is_safe_and_traceable(exception_client):
    response = exception_client.get("/unhandled")

    assert response.status_code == 500
    assert response.json() == {
        "code": "INTERNAL_ERROR",
        "message": "服务器内部错误",
        "details": None,
    }
    assert response.headers["X-Request-ID"]
    assert "不应泄露" not in response.text
