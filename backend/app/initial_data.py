"""幂等创建首个超级管理员，不生成任何演示业务数据。"""

from sqlalchemy import select

from app.core.config import settings
from app.core.db import SessionLocal
from app.core.logging import logger, setup_logging
from app.core.security import get_password_hash
from app.models import User


def init_superuser() -> None:
    if not settings.FIRST_SUPERUSER_EMAIL or not settings.FIRST_SUPERUSER_PASSWORD:
        logger.info(
            "未配置 FIRST_SUPERUSER_EMAIL / FIRST_SUPERUSER_PASSWORD，跳过管理员初始化"
        )
        return

    email = settings.FIRST_SUPERUSER_EMAIL.lower()
    with SessionLocal() as db:
        existing = db.scalar(select(User).where(User.email == email))
        if existing:
            logger.info("超级管理员已存在，跳过初始化 | email={}", email)
            return

        username = settings.FIRST_SUPERUSER or None
        if username and db.scalar(select(User).where(User.username == username)):
            logger.warning(
                "管理员用户名已被占用，改为仅使用邮箱登录 | username={}", username
            )
            username = None
        db.add(
            User(
                email=email,
                username=username,
                hashed_password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
                display_name=username or "Administrator",
                is_active=True,
                is_superuser=True,
            )
        )
        db.commit()
        logger.info("已创建首个超级管理员 | email={}", email)


def main() -> None:
    setup_logging()
    init_superuser()


if __name__ == "__main__":
    main()
