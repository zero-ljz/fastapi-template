# FastAPI Template

面向 Web、桌面端和移动端的通用 FastAPI 应用模板。后端核心只包含用户与刷新会话，不预设具体业务模型；Web 前端基于 React + TypeScript + Vite，并与 API 独立构建部署。

## 核心能力

- FastAPI + SQLAlchemy 2.0 + Alembic + MySQL
- 核心 API 使用 `async def + AsyncSession`，同步引擎仅供迁移与运维脚本
- 短期 JWT Access Token
- 按设备保存、轮换和撤销的 Refresh Token
- 邮箱或用户名登录
- 统一异常响应与 stdout 日志；生产环境自动输出结构化 JSON
- Pytest 测试和 Ruff 代码检查
- `pyproject.toml` 声明直接依赖，`uv.lock` 跨平台精确锁定完整依赖树
- Docker Compose 本地编排
- React Router、TanStack Query、React Hook Form 和 Zod
- OpenAPI 生成的 TypeScript API 类型和统一错误模型
- ESLint、Prettier、Vitest、Testing Library 和 MSW

## 核心数据模型

```text
User
└── RefreshSession
```

SaaS 组织、开放 API Key、异步任务、文件和审计模型应按项目需要单独添加。

## 快速启动

需要 Python 3.12+、[uv](https://docs.astral.sh/uv/) 和 Node.js 24+。后端持续兼容 Python 3.12 至当前最新稳定版。首次使用先安装依赖：

```bash
cd backend
cp .env.example .env
uv sync --locked --dev
cd ..

npm install
npm --prefix frontend install
```

之后在项目根目录一键启动：

```bash
npm run dev
```

`concurrently` 只负责本地开发进程；生产环境不会使用它。

单独启动后端：

```bash
cd backend
uv run alembic upgrade head
uv run python -m app.initial_data  # 首次需要管理员时显式执行
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

或者在项目根目录运行：

```bash
docker compose --env-file backend/.env up -d
docker compose exec app python -m app.initial_data  # 可选：创建首个管理员
```

- API 文档：http://127.0.0.1:8000/docs
- 健康检查：http://127.0.0.1:8000/api/v1/health
- Web 前端：http://127.0.0.1:5173

## 认证流程

Web 登录只返回短期 JWT `access_token`，前端仅在内存保存；桌面端和移动端登录还会返回长期 `refresh_token`。普通 API 请求只校验 JWT，不查询会话表；仅刷新、退出和安全事件会访问 `RefreshSession`。

客户端只需在登录请求中通过 `X-Client-Type` 和 `X-Device-Name` 标识设备。Refresh Token 每次使用后都会轮换，复用旧令牌会撤销同一设备的整个令牌族。

## 环境变量

复制 [backend/.env.example](backend/.env.example) 后，至少修改：

- `SECRET_KEY`
- `DB_PASSWORD`
- `FIRST_SUPERUSER_PASSWORD`
- `BACKEND_CORS_ORIGINS`

生产环境必须设置 `ENVIRONMENT=production`、`DEBUG=false`，并使用强随机密钥。配置校验会拒绝使用模板默认密钥启动生产环境。

## 项目文档

- [认证设计](docs/authentication.md)
- [配置说明](docs/configuration.md)
- [单机部署](docs/deployment.md)
- [安全基线](docs/security.md)

GitHub Actions 会自动执行代码检查、测试、MySQL 迁移验证、容器构建和依赖安全审计。模板不包含自动部署流程。

后端接口发生变化后运行 `npm run api:generate`，并提交更新后的 `frontend/openapi.json` 与 `frontend/src/api/schema.d.ts`。

## 验证

```bash
cd backend
uv run pytest -q
uv run ruff check .
uv run ruff format --check .

cd ../frontend
npm run lint
npm run format:check
npm test
npm run build  # 包含 TypeScript 类型检查
```

> 此版本是新的精简数据基线。如果本地已有旧版演示数据库，请先备份需要的数据，再重建开发数据库或 Docker 数据卷。
