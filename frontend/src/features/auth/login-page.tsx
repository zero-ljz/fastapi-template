import { zodResolver } from '@hookform/resolvers/zod'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { useLocation, useNavigate } from 'react-router'
import { z } from 'zod'

import { api } from '../../api/client.ts'
import { getErrorMessage } from '../../api/errors.ts'
import { useAuth } from '../../auth/use-auth.ts'

const loginSchema = z.object({
  username: z.string().trim().min(1, '请输入用户名或邮箱'),
  password: z.string().min(1, '请输入密码'),
})

type LoginForm = z.infer<typeof loginSchema>

export function LoginPage() {
  const { signIn } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [submitError, setSubmitError] = useState<string | null>(null)
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginForm>({ resolver: zodResolver(loginSchema) })

  const onSubmit = handleSubmit(async (values) => {
    setSubmitError(null)
    try {
      const { data } = await api.POST('/api/v1/login/access-token', {
        body: { ...values, scope: '' },
        bodySerializer(body) {
          return new URLSearchParams({
            username: body.username,
            password: body.password,
            scope: body.scope,
          })
        },
      })
      if (!data?.access_token) {
        throw new Error('登录响应缺少 access token')
      }
      signIn(data.access_token)
      const destination =
        typeof location.state === 'object' &&
        location.state &&
        'from' in location.state &&
        typeof location.state.from === 'object' &&
        location.state.from &&
        'pathname' in location.state.from &&
        typeof location.state.from.pathname === 'string'
          ? location.state.from.pathname
          : '/account'
      navigate(destination, { replace: true })
    } catch (error) {
      setSubmitError(getErrorMessage(error))
    }
  })

  return (
    <section className="form-card">
      <h1>登录</h1>
      <p>Web 端 access token 仅保存在内存中，刷新页面后需要重新登录。</p>
      <form onSubmit={onSubmit} noValidate>
        <label>
          用户名或邮箱
          <input autoComplete="username" {...register('username')} />
        </label>
        {errors.username && (
          <p className="field-error">{errors.username.message}</p>
        )}
        <label>
          密码
          <input
            autoComplete="current-password"
            type="password"
            {...register('password')}
          />
        </label>
        {errors.password && (
          <p className="field-error">{errors.password.message}</p>
        )}
        {submitError && <p className="form-error">{submitError}</p>}
        <button disabled={isSubmitting} type="submit">
          {isSubmitting ? '登录中…' : '登录'}
        </button>
      </form>
    </section>
  )
}
