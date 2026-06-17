# FastAPI Template

这是一个 FastAPI 全栈模板项目，当前后端骨架已经就绪，前端目录预留给 React + TypeScript + Vite 应用。

## 项目结构

```text
.
├── backend/              # FastAPI 后端
├── frontend/             # 前端应用目录
└── docker-compose.yml    # 本地容器编排
```

## 后端能力

- FastAPI API 服务
- SQLAlchemy 2.0 ORM 模型
- Alembic 数据库迁移
- MySQL 持久化
- JWT 登录认证
- SQLAdmin 后台管理
- 统一异常响应
- Loguru 日志
- Pytest 测试
- Ruff 代码规范检查

## 快速启动

```bash
cd backend
cp .env.example .env
pip install -r requirements.txt
pip install -r requirements-dev.txt
alembic upgrade head
python app/initial_data.py
python run.py
```

或者使用 Docker Compose：

```bash
docker-compose up -d
```

后端默认访问地址：

- API 文档: http://127.0.0.1:8000/docs
- 后台管理: http://127.0.0.1:8000/admin

## 环境变量

后端环境变量模板位于 `backend/.env.example`。复制为 `backend/.env` 后，至少修改：

- `SECRET_KEY`
- `DB_PASSWORD`
- `FIRST_SUPERUSER_PASSWORD`
- `BACKEND_CORS_ORIGINS`

生产环境必须使用强随机密钥，并关闭 `DEBUG`。
