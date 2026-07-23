"""定义用户模块的数据结构。"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    username: str | None = Field(default=None, min_length=3, max_length=64)
    display_name: str | None = Field(default=None, max_length=64)

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value.replace("_", "").replace("-", "").isalnum():
            raise ValueError("用户名只能包含字母、数字、下划线和连字符")
        return value

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).lower()


class UserUpdate(BaseModel):
    display_name: str | None = Field(default=None, max_length=64)
    email: EmailStr | None = None
    avatar_url: str | None = Field(default=None, max_length=512)


class UserUpdatePassword(BaseModel):
    old_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


class UserRead(BaseModel):
    id: int
    email: EmailStr
    username: str | None = None
    display_name: str | None = None
    avatar_url: str | None = None
    email_verified_at: datetime | None = None
    is_active: bool
    is_superuser: bool
    last_login_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserListResponse(BaseModel):
    items: list[UserRead]
    total: int
    page: int
    page_size: int
