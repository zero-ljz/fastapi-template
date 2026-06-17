# app/schemas/user.py

"""用户模块 Pydantic Schemas"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# 请求 Schemas
# ---------------------------------------------------------------------------


class UserCreate(BaseModel):
    """用户注册"""

    username: str = Field(..., min_length=3, max_length=64, description="用户名")
    password: str = Field(..., min_length=6, max_length=128, description="密码")
    email: Optional[str] = Field(None, max_length=255, description="邮箱")
    nickname: Optional[str] = Field(None, max_length=64, description="昵称")

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("用户名只能包含字母、数字、下划线和连字符")
        return v


class UserUpdate(BaseModel):
    """更新用户信息"""

    nickname: Optional[str] = Field(None, max_length=64, description="昵称")
    email: Optional[str] = Field(None, max_length=255, description="邮箱")
    phone: Optional[str] = Field(None, max_length=32, description="手机号")
    avatar_url: Optional[str] = Field(None, max_length=512, description="头像URL")


class UserUpdatePassword(BaseModel):
    """修改密码"""

    old_password: str = Field(..., min_length=6, max_length=128, description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=128, description="新密码")


class UserAdminUpdate(BaseModel):
    """管理员更新用户"""

    nickname: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    status: Optional[int] = None


# ---------------------------------------------------------------------------
# 响应 Schemas
# ---------------------------------------------------------------------------


class UserRead(BaseModel):
    """用户信息（脱敏返回）"""

    id: int
    username: str
    email: Optional[str] = None
    phone: Optional[str] = None
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool
    is_superuser: bool
    status: int
    last_login_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserListResponse(BaseModel):
    """用户分页列表"""

    items: list[UserRead]
    total: int
    page: int
    page_size: int
