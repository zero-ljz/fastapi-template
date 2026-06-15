# tests/test_exceptions.py

"""
异常体系测试
- 各异常类的 status_code 验证
- 自定义 detail / error_code
- 全局异常处理器的响应格式
"""

import pytest

from app.core.exceptions import (
    AppException,
    BadRequestException,
    UnauthorizedException,
    ForbiddenException,
    NotFoundException,
    ConflictException,
)


# ===================================================================
# 异常类属性测试
# ===================================================================

class TestExceptionClasses:
    """异常类基础属性验证"""

    def test_bad_request_exception(self):
        """BadRequestException 状态码应为 400"""
        exc = BadRequestException()
        assert exc.status_code == 400

    def test_unauthorized_exception(self):
        """UnauthorizedException 状态码应为 401"""
        exc = UnauthorizedException()
        assert exc.status_code == 401

    def test_forbidden_exception(self):
        """ForbiddenException 状态码应为 403"""
        exc = ForbiddenException()
        assert exc.status_code == 403

    def test_not_found_exception(self):
        """NotFoundException 状态码应为 404"""
        exc = NotFoundException()
        assert exc.status_code == 404

    def test_conflict_exception(self):
        """ConflictException 状态码应为 409"""
        exc = ConflictException()
        assert exc.status_code == 409

    def test_custom_detail(self):
        """自定义 detail 信息"""
        exc = AppException(detail="自定义错误")
        assert exc.detail == "自定义错误"

    def test_custom_error_code(self):
        """自定义 error_code"""
        exc = AppException(error_code="CUSTOM_CODE")
        assert exc.error_code == "CUSTOM_CODE"


# ===================================================================
# 全局异常处理器响应格式测试
# ===================================================================

class TestExceptionResponseFormat:
    """通过实际请求验证异常处理器返回的 JSON 格式"""

    def test_exception_response_format(self, client, admin_auth_headers):
        """
        请求不存在的用户 ID，触发 NotFoundException，
        验证响应为 404 且包含 code / message 字段。
        """
        response = client.get(
            "/api/v1/users/99999", headers=admin_auth_headers
        )
        assert response.status_code == 404
        data = response.json()
        assert "code" in data
        assert "message" in data
        assert data["code"] == "NOT_FOUND"
