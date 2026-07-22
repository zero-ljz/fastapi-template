"""Refresh Token 会话模型。"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


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
