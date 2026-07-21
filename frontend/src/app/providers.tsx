import { QueryClientProvider } from '@tanstack/react-query'
import { RouterProvider } from 'react-router'

import { AuthProvider } from '../auth/auth-provider.tsx'
import { queryClient } from './query-client.ts'
import { router } from './router.tsx'

export function AppProviders() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <RouterProvider router={router} />
      </AuthProvider>
    </QueryClientProvider>
  )
}
