import { render, screen } from '@testing-library/react'
import { createMemoryRouter } from 'react-router'
import { RouterProvider } from 'react-router/dom'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { RootErrorBoundary } from './root-error-boundary.tsx'

function BrokenPage(): never {
  throw new Error('测试渲染错误')
}

describe('RootErrorBoundary', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('renders a fallback when a route component throws', async () => {
    vi.spyOn(console, 'error').mockImplementation(() => undefined)
    const router = createMemoryRouter([
      {
        path: '/',
        Component: BrokenPage,
        ErrorBoundary: RootErrorBoundary,
      },
    ])

    render(<RouterProvider router={router} />)

    expect(
      await screen.findByRole('heading', { name: '页面暂时不可用' }),
    ).toBeInTheDocument()
    expect(screen.getByText('测试渲染错误')).toBeInTheDocument()
  })
})
