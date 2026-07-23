import { isRouteErrorResponse, useRouteError } from 'react-router'

export function RootErrorBoundary() {
  const error = useRouteError()

  const message = isRouteErrorResponse(error)
    ? error.statusText || '页面加载失败'
    : import.meta.env.DEV && error instanceof Error
      ? error.message
      : '发生意外错误，请稍后重试'

  return (
    <main className="page-container">
      <section>
        <p className="eyebrow">错误</p>
        <h1>页面暂时不可用</h1>
        <p>{message}</p>
        <a href="/">返回首页</a>
      </section>
    </main>
  )
}
