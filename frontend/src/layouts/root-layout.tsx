import { Link, NavLink, Outlet } from 'react-router'

import { useAuth } from '../auth/use-auth.ts'

export function RootLayout() {
  const { isAuthenticated, signOut } = useAuth()

  return (
    <div className="app-shell">
      <header className="site-header">
        <Link className="brand" to="/">
          FastAPI Template
        </Link>
        <nav aria-label="主导航">
          <NavLink to="/">首页</NavLink>
          {isAuthenticated ? (
            <>
              <NavLink to="/account">账户</NavLink>
              <button className="link-button" onClick={signOut} type="button">
                退出
              </button>
            </>
          ) : (
            <NavLink to="/login">登录</NavLink>
          )}
        </nav>
      </header>
      <main className="page-container">
        <Outlet />
      </main>
    </div>
  )
}
