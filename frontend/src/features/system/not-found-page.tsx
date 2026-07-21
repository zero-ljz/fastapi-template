import { Link } from 'react-router'

export function NotFoundPage() {
  return (
    <section>
      <p className="eyebrow">404</p>
      <h1>页面不存在</h1>
      <Link to="/">返回首页</Link>
    </section>
  )
}
