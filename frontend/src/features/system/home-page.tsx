import { useQuery } from '@tanstack/react-query'
import { z } from 'zod'

import { api } from '../../api/client.ts'
import { getErrorMessage } from '../../api/errors.ts'

const healthSchema = z.object({
  status: z.string(),
  version: z.string(),
})

export function HomePage() {
  const health = useQuery({
    queryKey: ['health'],
    queryFn: async () => {
      const { data } = await api.GET('/api/v1/health')
      return healthSchema.parse(data)
    },
  })

  return (
    <section className="hero">
      <p className="eyebrow">React + FastAPI</p>
      <h1>通用应用模板已经就绪</h1>
      <p className="lede">
        路由、服务端状态、表单校验、类型化 API、认证边界与测试基础设施均已连接。
      </p>
      <div className="status-card" aria-live="polite">
        {health.isPending && '正在检查 API…'}
        {health.isError && `API 不可用：${getErrorMessage(health.error)}`}
        {health.data && (
          <>
            <strong>API 状态：正常</strong>
            <span>版本 {health.data.version}</span>
          </>
        )}
      </div>
    </section>
  )
}
