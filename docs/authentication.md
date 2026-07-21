# 认证设计

模板使用短期 JWT Access Token，并只为桌面端和移动端签发按设备保存的 Refresh Token。Access Token 用于访问普通 API，Refresh Token 只用于续期和撤销会话。

## 登录与续期

主要接口：

```text
POST /api/v1/login/access-token  使用邮箱或用户名登录
POST /api/v1/login/refresh       轮换 Refresh Token
POST /api/v1/login/logout        撤销当前令牌族
POST /api/v1/login/logout-all    撤销用户全部 Refresh Session
```

登录接口接受 OAuth2 表单。`username` 字段可以填写邮箱或用户名。只有登录请求需要通过 `X-Client-Type` 声明 `web`、`desktop` 或 `mobile`；缺失或未知值按 Web 端处理，不签发 Refresh Token。`X-Device-Name` 只用于展示和审计，不能作为安全边界。

Access Token 包含：

- `sub`：用户 ID；
- `type`：固定为 `access`；
- `iat`、`exp`：签发和过期时间；
- `jti`：令牌唯一标识。

Refresh Token 是高熵随机字符串，数据库只保存 SHA-256 哈希。每次刷新都会撤销旧记录并创建同一 `family_id` 下的新记录。已经使用过的旧令牌再次出现时，整个令牌族都会被撤销。

## 客户端存储

- Web：登录响应的 `refresh_token` 为 `null`，只在内存保存 Access Token，不要写入 `localStorage`；刷新页面后需要重新登录。
- 桌面和移动端：使用操作系统提供的安全凭据存储保存 Refresh Token。
- 所有客户端：不要在日志、错误上报、URL 或分析事件中记录 Token。

## 当前撤销语义

修改密码会撤销全部 Refresh Session，但已经签发的 Access Token 仍可使用到过期。禁用用户会因为每次认证都重新读取用户而立即阻止后续请求。

如果项目要求修改密码或退出全部设备后 Access Token 立即失效，应在 `User` 增加 `auth_version`，同时把版本写入 JWT 并在认证依赖中比较。版本增加、密码修改和会话撤销必须位于同一数据库事务。

## 扩展认证前的原则

- OAuth、短信登录、MFA 和 API Key 应作为独立模块加入；
- 对登录、注册和刷新接口实施共享状态限流；
- 对外返回相同的账号不存在和密码错误提示；
- 任何改变认证状态的操作都要有失败回滚和安全测试。
