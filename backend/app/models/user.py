"""用户模型。"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, DateTime, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.refresh_session import RefreshSession


class User(TimestampMixin, Base):
    """终端用户与后台管理员。"""

    __tablename__ = "user"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, comment="登录邮箱"
    )
    username: Mapped[str | None] = mapped_column(
        String(64), unique=True, nullable=True, comment="可选用户名"
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="密码哈希"
    )
    display_name: Mapped[str | None] = mapped_column(
        String(64), nullable=True, comment="显示名称"
    )
    avatar_url: Mapped[str | None] = mapped_column(
        String(512), nullable=True, comment="头像 URL"
    )
    email_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, comment="邮箱验证时间"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default="1", nullable=False, comment="是否启用"
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default="0",
        nullable=False,
        comment="是否超级管理员",
    )
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, comment="最后登录时间"
    )

    refresh_sessions: Mapped[list[RefreshSession]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    __table_args__ = (Index("ix_user_is_active", "is_active"), {"comment": "用户表"})

    def __str__(self) -> str:
        return self.display_name or self.username or self.email
