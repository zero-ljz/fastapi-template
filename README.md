# fastapi-template
 FastAPI + SQLAlchemy 模板


## 本地安装启动
Windows:  
```shell
.\start.bat
```

Linux/macOS:  
```bash
chmod +x start.sh
./start.sh
```

## 使用 Docker Compose 启动
docker-compose up -d

## 访问接口
交互式文档 (Swagger):   
http://127.0.0.1:8000/docs  
备用文档 (ReDoc):   
http://127.0.0.1:8000/redoc  


## 数据库迁移
### 自动生成迁移脚本: 
alembic revision --autogenerate -m "描述"

### 执行迁移脚本将表结构同步到数据库: 
alembic upgrade head

时区, 日志, 安全性, 数据库迁移, 容器化, 社交账号登录



Router 层：面向“接口调用者”
Router 的划分依据主要是 URL 的层级结构 和 API 的访问频率。
逻辑： 按照资源（Resource）划分。例如 /users、/orders、/products。
目的： 为了让 API 文档（Swagger）清晰，方便前端调用。

Service 层：面向“业务逻辑”
Service 的划分依据是 业务逻辑的内聚性 和 代码复用性。
逻辑： 按照领域（Domain）或功能模块划分。
目的： 为了保证逻辑的一致性，防止代码重复，并使单元测试更容易。