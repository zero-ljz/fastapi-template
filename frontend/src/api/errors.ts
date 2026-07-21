type ErrorPayload = {
  code?: unknown
  message?: unknown
  detail?: unknown
  data?: unknown
}

function isErrorPayload(value: unknown): value is ErrorPayload {
  return typeof value === 'object' && value !== null
}

export class ApiError extends Error {
  readonly status: number
  readonly code: string
  readonly details?: unknown
  readonly requestId?: string

  constructor(options: {
    status: number
    code: string
    message: string
    details?: unknown
    requestId?: string
  }) {
    super(options.message)
    this.name = 'ApiError'
    this.status = options.status
    this.code = options.code
    this.details = options.details
    this.requestId = options.requestId
  }

  static async fromResponse(response: Response): Promise<ApiError> {
    const payload: unknown = await response
      .clone()
      .json()
      .catch(() => undefined)
    const body = isErrorPayload(payload) ? payload : undefined
    const detail = body?.detail
    const message =
      typeof body?.message === 'string'
        ? body.message
        : typeof detail === 'string'
          ? detail
          : response.statusText || '请求失败'

    return new ApiError({
      status: response.status,
      code:
        typeof body?.code === 'string' ? body.code : `HTTP_${response.status}`,
      message,
      details: body?.data ?? (Array.isArray(detail) ? detail : undefined),
      requestId: response.headers.get('X-Request-ID') ?? undefined,
    })
  }
}

export function getErrorMessage(error: unknown): string {
  return error instanceof Error ? error.message : '发生未知错误'
}
