import createClient, { type Middleware } from 'openapi-fetch'

import { setAccessToken, getAccessToken } from '../auth/token-store.ts'
import { env } from '../config/env.ts'
import { ApiError } from './errors.ts'
import type { paths } from './schema.d.ts'

const authMiddleware: Middleware = {
  onRequest({ request }) {
    const accessToken = getAccessToken()
    if (accessToken) {
      request.headers.set('Authorization', `Bearer ${accessToken}`)
    }
    return request
  },
  async onResponse({ response }) {
    if (response.status === 401) {
      setAccessToken(null)
    }
    if (!response.ok) {
      throw await ApiError.fromResponse(response)
    }
    return response
  },
}

export const api = createClient<paths>({
  baseUrl: env.VITE_API_BASE_URL,
  fetch: (input) => globalThis.fetch(input),
  headers: {
    'X-Client-Type': 'web',
  },
})

api.use(authMiddleware)
