# Backend

## 数据模型

默认只有两张业务表：

- `user`：终端用户与超级管理员
- `refresh_session`：按设备记录 Refresh Token 哈希、有效期和撤销状态

模板不默认包含 RBAC、多租户、通知、字典、文件或演示业务表。

核心 API 路由、认证依赖和 Service 全部使用 `AsyncSession`。同步引擎只用于 Alembic、初始化和维护脚本，禁止在 `async def` API 中调用同步数据库 Session。

## 本地启动

```bash
cp .env.example .env
pip install -r requirements-dev.txt
alembic upgrade head
python -m app.initial_data  # 首次需要管理员时显式执行
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
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
alembic revision --autogenerate -m "description"
alembic upgrade head
alembic downgrade -1
```

当前首个迁移是新的精简基线。旧版模板没有正式迁移版本，如果已有旧版开发数据库，请备份需要的数据后重建数据库。

## 依赖管理

`requirements.in` 和 `requirements-dev.in` 只维护直接依赖及兼容版本范围；自动生成的 `requirements.txt` 和 `requirements-dev.txt` 精确锁定完整依赖树，安装和部署始终使用 `.txt` 文件。

升级依赖后重新生成锁文件：

```bash
python -m piptools compile --upgrade --strip-extras --index-url=https://pypi.org/simple requirements.in
python -m piptools compile --upgrade --strip-extras --index-url=https://pypi.org/simple --output-file=requirements-dev.txt requirements-dev.in
```

两个锁文件应一起提交。开发锁通过 `-c requirements.txt` 与运行时锁保持同一版本。

## 测试与代码规范

```bash
python -m pytest -q
ruff check .
ruff format --check .
```
