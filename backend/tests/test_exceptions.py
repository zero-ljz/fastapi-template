"""
异常体系测试。

- 验证各异常类的状态码。
- 验证自定义详情与错误代码。
- 验证全局异常处理器的响应格式。
"""

from app.core.exceptions import (
    AppException,
    BadRequestException,
    ConflictException,
    ForbiddenException,
    NotFoundException,
    UnauthorizedException,
)

# 异常类属性测试


class TestExceptionClasses:
    """验证异常类基础属性。"""

    def test_bad_request_exception(self):
        """错误请求异常的状态码应为 400。"""
        exc = BadRequestException()
        assert exc.status_code == 400

    def test_unauthorized_exception(self):
        """未认证异常的状态码应为 401。"""
        exc = UnauthorizedException()
        assert exc.status_code == 401

    def test_forbidden_exception(self):
        """禁止访问异常的状态码应为 403。"""
        exc = ForbiddenException()
        assert exc.status_code == 403

    def test_not_found_exception(self):
        """资源不存在异常的状态码应为 404。"""
        exc = NotFoundException()
        assert exc.status_code == 404

    def test_conflict_exception(self):
        """资源冲突异常的状态码应为 409。"""
        exc = ConflictException()
        assert exc.status_code == 409

    def test_custom_detail(self):
        """支持自定义详情。"""
        exc = AppException(detail="自定义错误")
        assert exc.detail == "自定义错误"

    def test_custom_error_code(self):
        """支持自定义错误代码。"""
        exc = AppException(error_code="CUSTOM_CODE")
        assert exc.error_code == "CUSTOM_CODE"


# 全局异常处理器响应格式测试


class TestExceptionResponseFormat:
    """通过实际请求验证异常处理器返回的数据格式。"""

    def test_exception_response_format(self, client, admin_auth_headers):
        """
        请求不存在的用户编号，触发资源不存在异常，
        验证响应为 404 且包含错误代码和消息字段。
        """
        response = client.get("/api/v1/users/99999", headers=admin_auth_headers)
        assert response.status_code == 404
        data = response.json()
        assert "code" in data
        assert "message" in data
        assert data["code"] == "NOT_FOUND"
