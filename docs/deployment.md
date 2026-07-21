# 单机部署

模板面向单机 Docker Compose 部署。推荐由 Caddy 或 Nginx 负责 TLS、请求大小限制和入口限流，FastAPI 与 MySQL 只运行在内部网络。

## 首次部署

1. 复制并填写生产配置：

   ```bash
   cp backend/.env.example backend/.env
   ```

2. 至少设置：

   ```text
   ENVIRONMENT=production
   DEBUG=false
   SECRET_KEY=<强随机密钥>
   DB_PASSWORD=<强随机密码>
   BACKEND_CORS_ORIGINS=<真实前端来源>
   ```

3. 构建并启动：

   ```bash
   docker compose --env-file backend/.env up -d --build
   ```

4. 显式创建首个管理员：

   ```bash
   docker compose exec app python -m app.initial_data
   ```

5. 验证健康检查和 API 文档访问策略。

## 数据库迁移

容器入口当前会在启动应用前执行 `alembic upgrade head`，适用于单实例部署。扩展到多个应用实例前，必须把迁移改成独立的一次性部署步骤。

发布数据库变更前：

- 备份数据库；
- 在副本上验证迁移和回滚；
- 确认旧代码与迁移中的过渡结构兼容；
- 不要依赖破坏性自动迁移完成紧急回滚。

## 生产网络

- 不要把 MySQL 端口暴露到公网；
- 使用独立的非 root 数据库用户；
- 只允许反向代理访问应用端口；
- TLS 在反向代理终止，并正确配置可信代理头；
- `/docs`、`/redoc` 和 OpenAPI 是否公开由具体项目决定。

## 备份与恢复

至少建立每日数据库备份和保留策略。备份只有经过恢复演练后才可信，建议定期在隔离环境完成：

1. 创建空数据库；
2. 恢复最近备份；
3. 执行当前 Alembic 迁移；
4. 验证关键用户和会话数据；
5. 记录恢复耗时。

## 发布验证

GitHub Actions 会检查 Ruff、测试、真实 MySQL 迁移和 Docker 镜像构建。自动部署不属于模板范围；具体项目应根据服务器和密钥管理方式单独添加发布流程。
