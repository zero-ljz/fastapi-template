# 安全基线

模板提供认证和生产配置基线，但不能替代具体业务的授权设计与上线审查。

## 已实现

- 使用 Argon2 进行密码哈希；
- 短期 JWT Access Token；
- Refresh Token 只保存哈希；
- Refresh Token 轮换和复用检测；
- 修改密码与撤销全部 Refresh Session 在同一事务中完成；
- 生产环境拒绝调试模式和默认 JWT 密钥；
- 日志不记录查询字符串，并为响应生成 `X-Request-ID`；
- 统一处理应用异常、HTTP 异常、请求校验错误和未知异常；
- CI 执行测试、迁移验证、容器构建和依赖审计。

## 上线前必须处理

1. `/uploads` 当前是公开目录。私有文件必须通过鉴权接口或独立对象存储提供。
2. 为登录、注册和刷新接口增加跨 worker 生效的限流。
3. 使用非 root 数据库用户，并停止对公网暴露数据库端口。
4. 如果要求安全事件后 Access Token 立即失效，实现 `auth_version`。
5. 根据部署环境限制 Host、CORS、代理头、请求体大小和超时。

## 日志与敏感数据

禁止记录：

- 密码和密码哈希；
- Access Token、Refresh Token 和 Cookie；
- 数据库连接字符串；
- `.env` 内容；
- 上传文件正文；
- 不必要的个人信息。

生产日志应由容器平台或宿主机收集、限制访问并设置保留期限。

## 依赖与供应链

- Dependabot 每周检查 Python、npm 和 GitHub Actions 更新；
- Security Workflow 每周运行 `pip-audit` 和 `npm audit`；
- 依赖升级必须通过完整 CI；
- Python 直接依赖在 `pyproject.toml` 中约束，完整跨平台依赖树在 `uv.lock` 中精确锁定；
- 不要在 Pull Request 工作流中使用生产密钥。

## 项目级责任

每个新项目仍需单独设计资源授权、多租户隔离、审计、文件访问、支付和隐私策略。模板认证成功只说明“用户是谁”，不代表用户自动拥有业务资源权限。
