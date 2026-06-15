#!/usr/bin/env python

"""
初始化种子数据。

容器入口会在 Alembic 迁移后执行本脚本。当前仅在配置了环境变量时
创建首个超级管理员，保持幂等，避免和数据库迁移职责混在一起。
"""

import sys
from pathlib import Path

ROOT_PATH = Path(__file__).resolve().parent.parent
if str(ROOT_PATH) not in sys.path:
    sys.path.insert(0, str(ROOT_PATH))

from app.core.config import settings
from app.core.db import SessionLocal
from app.core.logging import logger, setup_logging
from app.core.security import get_password_hash
from app.models import User
from app.services.user import get_user_by_username


def init_superuser() -> None:
    if not settings.FIRST_SUPERUSER or not settings.FIRST_SUPERUSER_PASSWORD:
        logger.info("未配置 FIRST_SUPERUSER / FIRST_SUPERUSER_PASSWORD，跳过首个超级管理员初始化")
        return

    with SessionLocal() as db:
        existing = get_user_by_username(db, settings.FIRST_SUPERUSER)
        if existing:
            logger.info("超级管理员已存在，跳过初始化 | username={}", settings.FIRST_SUPERUSER)
            return

        user = User(
            username=settings.FIRST_SUPERUSER,
            email=settings.FIRST_SUPERUSER_EMAIL or None,
            password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
            nickname=settings.FIRST_SUPERUSER,
            is_active=True,
            is_superuser=True,
            status=1,
        )
        db.add(user)
        db.commit()
        logger.info("已创建首个超级管理员 | username={}", settings.FIRST_SUPERUSER)


def main() -> None:
    setup_logging()
    init_superuser()


if __name__ == "__main__":
    main()

