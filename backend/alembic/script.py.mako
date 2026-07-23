"""${message}

修订版本：${up_revision}
前置版本：${down_revision | comma,n}
创建日期：${create_date}

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
${imports if imports else ""}

# Alembic 修订标识
revision: str = ${repr(up_revision)}
down_revision: str | Sequence[str] | None = ${repr(down_revision)}
branch_labels: str | Sequence[str] | None = ${repr(branch_labels)}
depends_on: str | Sequence[str] | None = ${repr(depends_on)}


def upgrade() -> None:
    """升级数据库结构。"""
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    """降级数据库结构。"""
    ${downgrades if downgrades else "pass"}
