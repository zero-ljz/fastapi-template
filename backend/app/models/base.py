"""所有 SQLAlchemy 模型共享的基类与字段。"""

from datetime import datetime

from sqlalchemy import DateTime, func, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


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
