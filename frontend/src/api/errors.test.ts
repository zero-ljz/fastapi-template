import { describe, expect, it } from 'vitest'

import { ApiError } from './errors.ts'

describe('ApiError', () => {
  it('normalizes backend errors and keeps the request id', async () => {
    const response = new Response(
      JSON.stringify({
        code: 'FORBIDDEN',
        message: '权限不足',
        details: { role: 'admin' },
      }),
      {
        status: 403,
        headers: {
          'Content-Type': 'application/json',
          'X-Request-ID': 'request-123',
        },
      },
    )

    const error = await ApiError.fromResponse(response)

    expect(error).toMatchObject({
      status: 403,
      code: 'FORBIDDEN',
      message: '权限不足',
      details: { role: 'admin' },
      requestId: 'request-123',
    })
  })

  it('keeps the error contract when the response header is absent', async () => {
    const response = new Response(
      JSON.stringify({
        code: 'VALIDATION_ERROR',
        message: '请求数据校验失败',
        details: [{ location: ['body', 'email'], code: 'missing' }],
      }),
      { status: 422 },
    )

    const error = await ApiError.fromResponse(response)

    expect(error.code).toBe('VALIDATION_ERROR')
    expect(error.details).toEqual([
      { location: ['body', 'email'], code: 'missing' },
    ])
    expect(error.requestId).toBeUndefined()
  })
})
