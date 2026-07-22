# alembic/versions/20260711_0001_core_auth.py

"""create core user and refresh session tables

Revision ID: 20260711_0001
Revises:
Create Date: 2026-07-11
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260711_0001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False, comment="登录邮箱"),
        sa.Column(
            "username", sa.String(length=64), nullable=True, comment="可选用户名"
        ),
        sa.Column(
            "hashed_password", sa.String(length=255), nullable=False, comment="密码哈希"
        ),
        sa.Column(
            "display_name", sa.String(length=64), nullable=True, comment="显示名称"
        ),
        sa.Column(
            "avatar_url", sa.String(length=512), nullable=True, comment="头像 URL"
        ),
        sa.Column(
            "email_verified_at", sa.DateTime(), nullable=True, comment="邮箱验证时间"
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.text("1"),
            nullable=False,
            comment="是否启用",
        ),
        sa.Column(
            "is_superuser",
            sa.Boolean(),
            server_default=sa.text("0"),
            nullable=False,
            comment="是否超级管理员",
        ),
        sa.Column(
            "last_login_at", sa.DateTime(), nullable=True, comment="最后登录时间"
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
            comment="创建时间",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
            comment="更新时间",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("username"),
        comment="用户表",
    )
    op.create_index("ix_user_is_active", "user", ["is_active"], unique=False)

    op.create_table(
        "refresh_session",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column(
            "family_id", sa.String(length=36), nullable=False, comment="轮换令牌族 ID"
        ),
        sa.Column(
            "token_hash",
            sa.String(length=64),
            nullable=False,
            comment="Refresh Token SHA-256",
        ),
        sa.Column(
            "client_type",
            sa.String(length=32),
            server_default="unknown",
            nullable=False,
        ),
        sa.Column("device_name", sa.String(length=128), nullable=True),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.Column("user_agent", sa.String(length=512), nullable=True),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("last_used_at", sa.DateTime(), nullable=True),
        sa.Column("revoked_at", sa.DateTime(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
            comment="创建时间",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
            comment="更新时间",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash"),
        comment="刷新令牌会话表",
    )
    op.create_index(
        "ix_refresh_session_family_id",
        "refresh_session",
        ["family_id"],
        unique=False,
    )
    op.create_index(
        "ix_refresh_session_expires_at",
        "refresh_session",
        ["expires_at"],
        unique=False,
    )
    op.create_index(
        "ix_refresh_session_user_id",
        "refresh_session",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "ix_refresh_session_user_active",
        "refresh_session",
        ["user_id", "revoked_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_table("refresh_session")
    op.drop_table("user")
