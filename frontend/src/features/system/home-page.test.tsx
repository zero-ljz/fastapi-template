import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { AppProviders } from '../../app/providers.tsx'

describe('HomePage', () => {
  it('shows the backend health status', async () => {
    window.history.pushState({}, '', '/')
    render(<AppProviders />)

    expect(await screen.findByText('API 状态：正常')).toBeInTheDocument()
  })
})
