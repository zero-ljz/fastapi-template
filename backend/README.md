# FastAPI Template Backend

后端基于 FastAPI、SQLAlchemy 2.0、Alembic、MySQL 构建，包含用户认证、统一异常、SQLAdmin 后台、数据库迁移、种子数据和测试基础设施。

## 本地启动

1. 创建数据库。

```bash
mysql -u root -p -e "CREATE DATABASE db1 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

2. 准备环境变量。

```bash
cp .env.example .env
```

编辑 `.env`，至少修改 `SECRET_KEY`、`DB_PASSWORD`、`FIRST_SUPERUSER_PASSWORD`。

3. 安装依赖。

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

4. 执行数据库迁移并初始化数据。

```bash
alembic upgrade head
python app/initial_data.py
```

5. 启动开发服务。

```bash
python run.py
```

## Docker Compose

在项目根目录运行：

```bash
docker-compose up -d
```

启动后访问：

- Swagger: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
- SQLAdmin: http://127.0.0.1:8000/admin

## 数据库迁移

```bash
alembic revision --autogenerate -m "describe_change"
alembic upgrade head
```

## 测试与代码规范

```bash
pytest
ruff check .
```

## 架构说明

后端采用分层结构：

- `app/api`: API 路由和依赖注入
- `app/core`: 配置、数据库、日志、安全、异常、邮件
- `app/services`: 业务逻辑
- `app/schemas`: Pydantic 请求和响应模型
- `app/models.py`: SQLAlchemy ORM 模型
- `tests`: 自动化测试

核心领域模型共 14 个：

- Auth & RBAC: User, Role, Permission, RolePermission, UserRole
- System: Dictionary, SystemConfig, OperationLog
- Workspace: Workspace, WorkspaceUser
- Business: Node, Item, Notification, FileAsset

接口遵循 REST 风格，业务异常统一返回 `code` 和 `message` 字段。
