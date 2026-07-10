# FastAPI Template

面向商业 API、SaaS、桌面端和移动端后端的精简 FastAPI 模板。后端核心只包含用户与刷新会话，不预设具体业务模型；前端目录预留给 React + TypeScript + Vite。

## 核心能力

- FastAPI + SQLAlchemy 2.0 + Alembic + MySQL
- 核心 API 使用 `async def + AsyncSession`，同步引擎仅供后台与运维脚本
- Redis 服务与环境配置预留
- 短期 JWT Access Token
- 按设备保存、轮换和撤销的 Refresh Token
- 邮箱或用户名登录
- SQLAdmin 后台
- 统一异常响应与 Loguru 日志
- Pytest 测试和 Ruff 代码检查
- Docker Compose 本地编排

## 核心数据模型

```text
User
└── RefreshSession
```

SaaS 组织、开放 API Key、异步任务、文件和审计模型应按项目需要单独添加。

## 快速启动

```bash
cd backend
cp .env.example .env
pip install -r requirements-dev.txt
alembic upgrade head
python app/initial_data.py
python run.py
```

或者在项目根目录运行：

```bash
docker compose --env-file backend/.env up -d
```

- API 文档：http://127.0.0.1:8000/docs
- 后台管理：http://127.0.0.1:8000/admin
- 健康检查：http://127.0.0.1:8000/api/v1/health

## 认证流程

登录返回短期 JWT `access_token` 和长期 `refresh_token`。普通 API 请求只校验 JWT，不查询会话表；仅刷新、退出和安全事件会访问 `RefreshSession`。

客户端可以在登录时通过 `X-Client-Type` 和 `X-Device-Name` 标识设备。刷新令牌每次使用后都会轮换，复用旧令牌会撤销同一设备的整个令牌族。

## 环境变量

复制 [backend/.env.example](backend/.env.example) 后，至少修改：

- `SECRET_KEY`
- `DB_PASSWORD`
- `FIRST_SUPERUSER_PASSWORD`
- `BACKEND_CORS_ORIGINS`

生产环境必须设置 `ENVIRONMENT=production`、`DEBUG=false`，并使用强随机密钥。配置校验会拒绝使用模板默认密钥启动生产环境。

## 验证

```bash
cd backend
python -m pytest -q
ruff check .
ruff format --check .
```

> 此版本是新的精简数据基线。如果本地已有旧版演示数据库，请先备份需要的数据，再重建开发数据库或 Docker 数据卷。
