import { createBrowserRouter } from 'react-router'

import { ProtectedRoute } from '../auth/protected-route.tsx'
import { AccountPage } from '../features/account/account-page.tsx'
import { LoginPage } from '../features/auth/login-page.tsx'
import { HomePage } from '../features/system/home-page.tsx'
import { NotFoundPage } from '../features/system/not-found-page.tsx'
import { RootErrorBoundary } from '../features/system/root-error-boundary.tsx'
import { RootLayout } from '../layouts/root-layout.tsx'

export const router = createBrowserRouter([
  {
    Component: RootLayout,
    ErrorBoundary: RootErrorBoundary,
    children: [
      { index: true, Component: HomePage },
      { path: 'login', Component: LoginPage },
      {
        Component: ProtectedRoute,
        children: [{ path: 'account', Component: AccountPage }],
      },
      { path: '*', Component: NotFoundPage },
    ],
  },
])
