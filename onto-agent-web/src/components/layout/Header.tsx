import { useLocation, Link } from "react-router-dom"

const routeNames: Record<string, string> = {
  "/": "仪表盘",
  "/data-sources": "数据源管理",
  "/data-sources/:id": "数据源详情",
  "/ontologies": "本体列表",
  "/ontologies/:id": "本体建模",
  "/mapping": "数据映射",
  "/query": "语义查询",
  "/nl-query": "自然语言查询",
  "/workbench": "查询工作台",
  "/versions": "版本管理",
  "/sync": "数据同步",
  "/permissions": "权限管理",
  "/api-management": "API 管理",
}

function getBreadcrumb(pathname: string): { label: string; isCurrent: boolean }[] {
  if (pathname === "/") {
    return [
      { label: "首页", isCurrent: false },
      { label: routeNames["/"], isCurrent: true },
    ]
  }

  const segments = pathname.split("/").filter(Boolean)
  const crumbs: { label: string; isCurrent: boolean }[] = [
    { label: "首页", isCurrent: false },
  ]

  let currentPath = ""
  for (const segment of segments) {
    currentPath += `/${segment}`
    const label = routeNames[currentPath] || routeNames[`/${segment}`] || segment
    crumbs.push({ label, isCurrent: currentPath === pathname })
  }

  return crumbs
}

export function Header() {
  const location = useLocation()
  const breadcrumbs = getBreadcrumb(location.pathname)

  return (
    <header className="header">
      <div className="header-left">
        <div className="header-breadcrumb">
          {breadcrumbs.map((crumb, index) => (
            <>
              {index > 0 && <span className="separator">/</span>}
              {index === 0 ? (
                <Link to="/">{crumb.label}</Link>
              ) : (
                <span className={crumb.isCurrent ? "current" : ""}>{crumb.label}</span>
              )}
            </>
          ))}
        </div>
      </div>

      <div className="header-right">
        <div className="header-search">
          <span className="search-icon">⌕</span>
          <input type="text" placeholder="搜索本体、数据源、查询..." />
          <span className="search-shortcut">⌘K</span>
        </div>
        <button className="header-icon-btn">
          ◉
          <span className="badge"></span>
        </button>
        <button className="header-icon-btn">⚙</button>
      </div>
    </header>
  )
}