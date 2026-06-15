# app/core/logging.py

"""
统一日志系统 — 基于 loguru

用法:
    from app.core.logging import logger
    logger.info("Hello {name}", name="World")
"""

import logging
import sys
from pathlib import Path

from loguru import logger

from app.core.config import settings


# ---------------------------------------------------------------------------
# 拦截标准库 logging → 转发到 loguru
# ---------------------------------------------------------------------------

class InterceptHandler(logging.Handler):
    """将 stdlib logging 的日志拦截并转发给 loguru"""

    def emit(self, record: logging.LogRecord) -> None:
        # 获取对应的 loguru 日志级别
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # 找到真正的调用方
        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging() -> None:
    """初始化日志配置，应在应用启动时调用"""

    log_level = settings.LOG_LEVEL.upper()

    # 移除 loguru 默认 handler
    logger.remove()

    # 控制台输出（彩色）
    logger.add(
        sys.stderr,
        level=log_level,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> — "
            "<level>{message}</level>"
        ),
        colorize=True,
        backtrace=True,
        diagnose=settings.DEBUG,
    )

    # 文件输出（按天轮转）
    log_dir = settings.ROOT_PATH / "logs"
    log_dir.mkdir(exist_ok=True)

    logger.add(
        str(log_dir / "{time:YYYY-MM-DD}.log"),
        level=log_level,
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} — {message}",
        rotation="00:00",       # 每天午夜轮转
        retention="30 days",    # 保留 30 天
        compression="gz",       # 压缩旧日志
        encoding="utf-8",
        enqueue=True,           # 线程安全
    )

    # 拦截 uvicorn / sqlalchemy / alembic 等标准库日志
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access",
                 "sqlalchemy.engine", "alembic", "fastapi"):
        logging.getLogger(name).handlers = [InterceptHandler()]
        logging.getLogger(name).propagate = False

    # 设置 root logger
    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(log_level)

    logger.info("日志系统初始化完成 (级别: {})", log_level)
