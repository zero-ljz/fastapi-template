import { render, screen } from '@testing-library/react'
import { HttpResponse, http } from 'msw'
import { describe, expect, it } from 'vitest'

import { AppProviders } from '../../app/providers.tsx'
import { server } from '../../test/server.ts'

describe('HomePage', () => {
  it('shows the backend health status', async () => {
    server.use(
      http.get('*/api/v1/health', ({ request }) => {
        expect(request.headers.get('X-Client-Type')).toBeNull()
        return HttpResponse.json({ status: 'ok', version: '1.0.0' })
      }),
    )
    window.history.pushState({}, '', '/')
    render(<AppProviders />)

    expect(await screen.findByText('API 状态：正常')).toBeInTheDocument()
  })
})
