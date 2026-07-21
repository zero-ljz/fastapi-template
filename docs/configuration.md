# 配置说明

配置由 `pydantic-settings` 从环境变量和 `backend/.env` 读取。复制 `backend/.env.example` 作为本地起点，不要提交真实 `.env`。

## 应用配置

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `PROJECT_NAME` | `FastAPI Application` | OpenAPI 和日志中的项目名称 |
| `VERSION` | `1.0.0` | 应用版本 |
| `API_V1_STR` | `/api/v1` | API 版本前缀 |
| `ENVIRONMENT` | `development` | `development`、`testing` 或 `production` |
| `DEBUG` | `true` | 调试模式；生产环境必须为 `false` |
| `BACKEND_CORS_ORIGINS` | 本地开发地址 | JSON 数组或逗号分隔的允许来源 |
| `LOG_LEVEL` | `INFO` | 日志等级 |

生产环境日志输出结构化 JSON，其他环境输出便于阅读的文本；所有日志都写入 stdout。

## 认证配置

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `SECRET_KEY` | 模板占位值 | JWT 签名密钥，至少 32 字符 |
| `ALGORITHM` | `HS256` | JWT 签名算法 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Access Token 有效期 |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `30` | 每次轮换后的 Refresh Token 有效期 |

生产环境会拒绝默认 `SECRET_KEY`。修改现有项目的签名密钥会使所有已签发 Access Token 失效。

## 数据库配置

| 变量 | 示例值 | 说明 |
| --- | --- | --- |
| `DB_DRIVER` | `mysql+mysqldb` | 同步引擎和 Alembic 使用的驱动 |
| `DB_HOST` | `127.0.0.1` | 数据库地址 |
| `DB_PORT` | `3306` | 数据库端口 |
| `DB_USER` | `root` | 数据库用户；生产环境应改为受限用户 |
| `DB_PASSWORD` | `change-me` | 数据库密码 |
| `DB_NAME` | `db1` | 数据库名称 |

异步 API 引擎当前固定使用 `mysql+aiomysql`，同步脚本使用 `DB_DRIVER`。修改数据库驱动时必须同时验证 API、Alembic 和初始化脚本。

## 首个管理员

| 变量 | 说明 |
| --- | --- |
| `FIRST_SUPERUSER` | 可选管理员用户名 |
| `FIRST_SUPERUSER_EMAIL` | 管理员邮箱 |
| `FIRST_SUPERUSER_PASSWORD` | 管理员初始密码 |

这些变量不会在应用启动时自动执行。需要时显式运行：

```bash
cd backend
python -m app.initial_data
```

生产环境应在初始化完成后从运行环境移除初始管理员密码。

## Web 前端配置

前端只读取 `VITE_API_BASE_URL`，示例见 `frontend/.env.example`。Vite 会把所有 `VITE_*` 变量打包进浏览器代码，因此只能存放公开配置，不能包含数据库密码、JWT 密钥或第三方服务密钥。
