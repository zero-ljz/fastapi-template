import { useQuery } from '@tanstack/react-query'

import { api } from '../../api/client.ts'
import { getErrorMessage } from '../../api/errors.ts'

export function AccountPage() {
  const currentUser = useQuery({
    queryKey: ['current-user'],
    queryFn: async () => {
      const { data } = await api.GET('/api/v1/users/me')
      if (!data) throw new Error('用户响应为空')
      return data
    },
  })

  if (currentUser.isPending) return <p>正在加载账户…</p>
  if (currentUser.isError)
    return <p>账户加载失败：{getErrorMessage(currentUser.error)}</p>

  return (
    <section>
      <p className="eyebrow">受保护页面</p>
      <h1>
        {currentUser.data.display_name ||
          currentUser.data.username ||
          '我的账户'}
      </h1>
      <dl className="details-list">
        <div>
          <dt>邮箱</dt>
          <dd>{currentUser.data.email}</dd>
        </div>
        <div>
          <dt>账户状态</dt>
          <dd>{currentUser.data.is_active ? '正常' : '停用'}</dd>
        </div>
      </dl>
    </section>
  )
}
