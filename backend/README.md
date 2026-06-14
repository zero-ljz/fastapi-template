# 快速开始


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
自动生成迁移脚本:   
alembic revision --autogenerate -m "描述"

执行迁移脚本将表结构同步到数据库:   
alembic upgrade head


# 软件设计说明
系统架构与模块描述  
后端: 采用经典的分层架构并结合依赖注入机制
前端: 采用基于组件化与状态分离的现代架构

核心技术栈  
后端: FastAPI + SQLAlchemy + Alembic + MySQL
前端: React + TypeScript + Vite + Zustand + shadcn/ui

核心业务步骤描述  

数据库核心表设计  
14个
Dictionary, System_Config, Permission, 
User, Workspace, Role, 
Role_Permission, User_Role, Workspace_User, 
Notification, Operation_Log, Node, Item
FileAsset

Auth & RBAC: User, Role, Permission, RolePermission, UserRole
System: Dictionary, SystemConfig, OperationLog
Workspace: Workspace, WorkspaceUser
Business: Node, Item, Notification, FileAsset

接口设计规范  
采用 HTTP 状态驱动的原生 RESTful 风格，遵守 FastAPI 默认的 HTTPException 错误格式