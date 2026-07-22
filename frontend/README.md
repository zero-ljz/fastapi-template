# Frontend

基于 React、TypeScript 和 Vite 的独立 Web 客户端。模板内置 React Router、TanStack Query、React Hook Form、Zod、OpenAPI 类型客户端、ESLint、Prettier、Vitest、Testing Library 和 MSW。

开发和构建使用 Node.js 24+。

## 本地开发

```bash
cp .env.example .env
npm install
npm run dev
```

后端执行过 `uv sync --locked --dev` 后，也可以直接在仓库根目录运行 `npm run dev`，同时启动前后端。根目录脚本通过 uv 使用 `backend/.venv`，不要求提前激活虚拟环境。

## 常用命令

```bash
npm run api:types      # 根据已导出的 openapi.json 更新 TypeScript 类型
npm run lint
npm run format:check
npm run typecheck
npm test
npm run build
```

`npm run build` 会先执行完整 TypeScript 类型检查，再生成生产构建；可单独运行 `npm run typecheck` 做快速检查。

后端接口发生变化后，应从仓库根目录运行：

```bash
npm run api:generate
```

该命令先由 FastAPI 导出 `frontend/openapi.json`，再生成 `src/api/schema.d.ts`。这两个文件都应提交，CI 会检查它们是否过期。

## 认证边界

Web 客户端登录时发送 `X-Client-Type: web`。后端只返回短期 Access Token，前端仅在内存中保存；不会将 Token 写入 localStorage、sessionStorage、URL 或日志。刷新页面后需要重新登录，收到 `401` 时会清理认证状态和 TanStack Query 缓存。

桌面端和移动端应发送 `desktop` 或 `mobile`，并把 Refresh Token 保存到操作系统安全凭据存储中，不要复用 Web 端的内存实现。

## 环境变量

只有 `VITE_API_BASE_URL` 会进入浏览器构建。所有 `VITE_*` 变量都属于公开信息，禁止放入密钥。启动和构建时会使用 Zod 校验环境变量。

## 独立部署

`Dockerfile` 负责构建静态文件，并由 Nginx 提供 SPA history fallback。FastAPI 不托管前端文件。构建示例：

```bash
docker build --build-arg VITE_API_BASE_URL=https://api.example.com -t app-frontend frontend
```
