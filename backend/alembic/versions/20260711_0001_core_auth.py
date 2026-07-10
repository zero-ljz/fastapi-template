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
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("username", sa.String(length=64), nullable=True),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("display_name", sa.String(length=64), nullable=True),
        sa.Column("avatar_url", sa.String(length=512), nullable=True),
        sa.Column("email_verified_at", sa.DateTime(), nullable=True),
        sa.Column(
            "is_active", sa.Boolean(), server_default=sa.text("1"), nullable=False
        ),
        sa.Column(
            "is_superuser", sa.Boolean(), server_default=sa.text("0"), nullable=False
        ),
        sa.Column("last_login_at", sa.DateTime(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
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
        sa.Column("family_id", sa.String(length=36), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
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
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
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
    op.drop_index("ix_refresh_session_user_active", table_name="refresh_session")
    op.drop_index("ix_refresh_session_user_id", table_name="refresh_session")
    op.drop_index("ix_refresh_session_expires_at", table_name="refresh_session")
    op.drop_index("ix_refresh_session_family_id", table_name="refresh_session")
    op.drop_table("refresh_session")
    op.drop_index("ix_user_is_active", table_name="user")
    op.drop_table("user")
