# 后端

## 数据模型

默认只有两张业务表：

- `user`：终端用户与超级管理员
- `refresh_session`：按设备记录 Refresh Token 哈希、有效期和撤销状态

模板不默认包含 RBAC、多租户、通知、字典、文件或演示业务表。

核心 API 路由、认证依赖和 Service 全部使用 `AsyncSession`。同步引擎只用于 Alembic、初始化和维护脚本，禁止在 `async def` API 中调用同步数据库 Session。

## 代码边界

- `app/models/` 按数据模型拆分文件，并通过 `app.models` 统一导出公共模型；
- `app/middleware/` 保存 HTTP 请求级中间件，`main.py` 只负责应用组装；
- `app/services/` 实现业务逻辑，只执行查询、写入和 `flush()`，不决定事务提交；
- 写接口通过 `app.core.unit_of_work` 在路由层统一 `commit/rollback`，一个完整用例只提交一次。

Refresh Token 复用检测是一个特殊事务：接口虽然返回 401，但必须提交对同一令牌族的撤销。该语义通过 Unit of Work 的 `commit_on` 显式声明。

## 本地启动

```bash
cp .env.example .env
uv sync --locked --dev
uv run alembic upgrade head
uv run python -m app.initial_data  # 首次需要管理员时显式执行
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

初始化脚本不会随应用启动自动执行。需要管理员时手动运行，它只会幂等创建 `.env` 中配置的首个超级管理员，不会写入演示账号或业务数据。

Docker 环境可显式运行：

```bash
docker compose exec app python -m app.initial_data
```

## 主要认证接口

```text
POST /api/v1/login/access-token  登录；Web 只返回 Access Token，桌面和移动端同时返回 Refresh Token
POST /api/v1/login/refresh       轮换 Refresh Token
POST /api/v1/login/logout        退出当前设备
POST /api/v1/login/logout-all    退出全部设备
```

`/login/access-token` 使用 OAuth2 表单，其中 `username` 字段可以填写邮箱或用户名。

## 数据库迁移

```bash
uv run alembic revision --autogenerate -m "description"
uv run alembic upgrade head
uv run alembic downgrade -1
```

当前首个迁移是新的精简基线。旧版模板没有正式迁移版本，如果已有旧版开发数据库，请备份需要的数据后重建数据库。

## 依赖管理

`pyproject.toml` 维护 Python 3.12+ 约束、运行时依赖和开发依赖组；`uv.lock` 精确锁定完整的跨平台依赖树。二者都应提交，日常安装、CI 和 Docker 均使用锁文件。

常用依赖命令：

```bash
uv sync --locked --dev              # 按锁文件同步开发环境
uv add fastapi                      # 添加或更新运行时依赖
uv add --dev pytest                 # 添加或更新开发依赖
uv lock --upgrade                   # 升级全部允许范围内的依赖
uv lock --upgrade-package fastapi   # 只升级指定依赖
```

项目支持 Python 3.12 至当前最新稳定版；`.python-version` 和 Docker 使用最低支持版本，CI 覆盖全部受支持的次版本。修改依赖后提交更新后的 `pyproject.toml` 与 `uv.lock`。

## 测试与代码规范

```bash
uv run pytest -q
uv run ruff check .
uv run ruff format --check .
uv run mypy
```
