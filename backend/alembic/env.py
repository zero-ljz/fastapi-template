# alembic/env.py

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.core.config import settings
from app.models import Base

# 这是 Alembic 配置对象，它提供了对当前使用的 .ini 文件中值的访问权限。
config = context.config

# 解释 Python 日志记录的配置文件。
# 这行代码基本上设置了日志记录器。
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 在此处添加模型的元数据对象以支持自动生成功能
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# 来自配置文件的其他值（由 env.py 的需求定义）
# 可获取：
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def get_url():
    return f"mysql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"


def run_migrations_offline() -> None:
    """以“离线”模式运行迁移。

    此配置仅通过URL设置上下文环境，
    并未指定引擎（尽管在此处也可接受引擎配置）。
    通过跳过引擎创建步骤，
    我们甚至无需依赖可用的DBAPI。

    在此调用 context.execute() 会将给定的字符串发送到脚本输出。

    """
    # 2. 动态获取 URL
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
    """以“在线”模式运行迁移。

    在此场景中，我们需要创建一个引擎
    并将连接关联到上下文。

    """

    # 获取 alembic.ini 的配置节
    configuration = config.get_section(config.config_ini_section, {})

    # 3. 动态注入正确的数据库 URL
    url = get_url()
    configuration["sqlalchemy.url"] = url

    # 使用注入后的配置创建引擎
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
