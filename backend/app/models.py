# app/models.py

"""通用商业 API 模板的核心数据模型。"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    String,
    func,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
        comment="创建时间",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=func.now(),
        nullable=False,
        comment="更新时间",
    )


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


class RefreshSession(TimestampMixin, Base):
    """按设备保存 Refresh Token 状态；Access Token 仍使用无状态 JWT。"""

    __tablename__ = "refresh_session"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    family_id: Mapped[str] = mapped_column(
        String(36), nullable=False, index=True, comment="轮换令牌族 ID"
    )
    token_hash: Mapped[str] = mapped_column(
        String(64), unique=True, nullable=False, comment="Refresh Token SHA-256"
    )
    client_type: Mapped[str] = mapped_column(
        String(32), default="unknown", server_default="unknown", nullable=False
    )
    device_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(512), nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    user: Mapped[User] = relationship(back_populates="refresh_sessions")

    __table_args__ = (
        Index("ix_refresh_session_user_active", "user_id", "revoked_at"),
        {"comment": "刷新令牌会话表"},
    )

    def __str__(self) -> str:
        return f"{self.client_type}:{self.device_name or self.id}"
