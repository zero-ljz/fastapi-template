"""配置 Alembic 迁移环境。"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import URL, engine_from_config, pool

from app.core.config import settings
from app.models import Base

# 获取 Alembic 配置对象
config = context.config

# 加载日志配置
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 设置用于自动生成迁移的模型元数据
target_metadata = Base.metadata


def get_url() -> str:
    """构造可正确处理特殊字符的数据库连接地址。"""
    return URL.create(
        drivername=settings.DB_DRIVER,
        username=settings.DB_USER,
        password=settings.DB_PASSWORD,
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        database=settings.DB_NAME,
    ).render_as_string(hide_password=False)


def run_migrations_offline() -> None:
    """以“离线”模式运行迁移。

    离线模式不创建数据库引擎，只把生成的 SQL 写入脚本输出。
    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """创建数据库连接并以“在线”模式运行迁移。"""

    # 获取 Alembic 配置节并注入数据库连接地址
    configuration = config.get_section(config.config_ini_section, {})
    url = get_url()
    configuration["sqlalchemy.url"] = url

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,  # 检查类型变化（如长度、精度）
            compare_server_default=True,  # 检查默认值变化（如 DEFAULT 0 改为 1）
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
