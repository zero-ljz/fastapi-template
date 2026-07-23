"""定义通用响应结构。"""

from typing import Any

from pydantic import BaseModel


class Message(BaseModel):
    message: str


class HealthResponse(BaseModel):
    status: str
    version: str


class ErrorResponse(BaseModel):
    code: str
    message: str
    details: dict[str, Any] | None = None


class ValidationIssue(BaseModel):
    location: list[str | int]
    message: str
    code: str


class ValidationErrorResponse(BaseModel):
    code: str
    message: str
    details: list[ValidationIssue]
