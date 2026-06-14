import datetime
from typing import Optional

from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey, Table, Column
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class BaseMixin:
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.datetime.now(datetime.timezone.utc),
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.datetime.now(datetime.timezone.utc),
        onupdate=lambda: datetime.datetime.now(datetime.timezone.utc),
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


# 系统字典
class Option(Base, BaseMixin):
    __tablename__ = "option"

    name: Mapped[str] = mapped_column(String(255), comment="名称")
    value: Mapped[str] = mapped_column(String(255), comment="值")

    def __str__(self) -> str:
        return self.name


# 用户对项目的授权关联表
# project_user_authorize = Table(
#     "project_user_authorize",
#     Base.metadata,
#     Column("project_id", ForeignKey("project.id"), primary_key=True),
#     Column("user_id", ForeignKey("user.id"), primary_key=True),
# )


# 用户
class User(Base, BaseMixin):
    __tablename__ = "user"

    username: Mapped[str] = mapped_column(String(255), comment="用户名")
    password: Mapped[str] = mapped_column(String(255), comment="密码")
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否为超级用户")
    nickname: Mapped[str] = mapped_column(String(255), comment="昵称")

    # projects: Mapped[list["Project"]] = relationship(back_populates="user")

    # authorize_projects: Mapped[list["Project"]] = relationship(
    #     secondary=project_user_authorize,
    #     back_populates="authorize_users",
    # )

    def __str__(self) -> str:
        return self.username