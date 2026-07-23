"""配置基于 Loguru 的统一日志系统。"""

import logging
import sys

from loguru import logger

from app.core.config import settings


# 将标准库日志转发到 Loguru
class InterceptHandler(logging.Handler):
    """将 Python 标准库日志转发给 Loguru。"""

    def emit(self, record: logging.LogRecord) -> None:
        # 获取对应的 Loguru 日志级别
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # 定位真实调用方
        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging() -> None:
    """初始化标准输出日志；生产环境输出结构化 JSON。"""

    log_level = settings.LOG_LEVEL.upper()
    is_production = settings.ENVIRONMENT.lower() == "production"

    logger.remove()
    logger.configure(extra={"request_id": "-"})

    logger.add(
        sys.stdout,
        level=log_level,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "request_id={extra[request_id]} | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        ),
        colorize=sys.stdout.isatty() and not is_production,
        serialize=is_production,
        enqueue=True,
        backtrace=True,
        diagnose=settings.DEBUG,
    )

    # 接管 Uvicorn、SQLAlchemy 和 Alembic 等日志
    for name in (
        "uvicorn",
        "uvicorn.error",
        "uvicorn.access",
        "sqlalchemy.engine",
        "alembic",
        "fastapi",
    ):
        logging.getLogger(name).handlers = [InterceptHandler()]
        logging.getLogger(name).propagate = False

    # 配置根日志记录器
    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(log_level)

    logger.info(
        "日志系统初始化完成 | level={} | format={}",
        log_level,
        "json" if is_production else "text",
    )
