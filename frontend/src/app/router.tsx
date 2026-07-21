import { createBrowserRouter } from 'react-router'

import { ProtectedRoute } from '../auth/protected-route.tsx'
import { AccountPage } from '../features/account/account-page.tsx'
import { LoginPage } from '../features/auth/login-page.tsx'
import { HomePage } from '../features/system/home-page.tsx'
import { NotFoundPage } from '../features/system/not-found-page.tsx'
import { RootLayout } from '../layouts/root-layout.tsx'

export const router = createBrowserRouter([
  {
    element: <RootLayout />,
    children: [
      { index: true, element: <HomePage /> },
      { path: 'login', element: <LoginPage /> },
      {
        element: <ProtectedRoute />,
        children: [{ path: 'account', element: <AccountPage /> }],
      },
      { path: '*', element: <NotFoundPage /> },
    ],
  },
])
