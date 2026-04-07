import { Link } from "react-router-dom"
import "./Breadcrumb.css"

const routeNames: Record<string, string> = {
  "/": "仪表盘",
  "/data-sources": "数据源管理",
  "/ontologies": "本体列表",
  "/mapping": "数据映射",
  "/query": "语义查询",
  "/nl-query": "自然语言查询",
  "/workbench": "查询工作台",
  "/versions": "版本管理",
  "/sync": "数据同步",
  "/permissions": "权限管理",
  "/api-management": "API 管理",
}

function getBreadcrumb(pathname: string) {
  if (pathname === "/") {
    return [
      { label: "首页", href: "/" },
      { label: routeNames["/"] },
    ]
  }

  if (pathname === "/data-sources") {
    return [
      { label: "首页", href: "/" },
      { label: routeNames["/data-sources"] },
    ]
  }

  if (pathname.startsWith("/data-sources/")) {
    return [
      { label: "首页", href: "/" },
      { label: "数据源管理", href: "/data-sources" },
      { label: "数据源详情" },
    ]
  }

  if (pathname === "/ontologies") {
    return [
      { label: "首页", href: "/" },
      { label: routeNames["/ontologies"] },
    ]
  }

  if (pathname.startsWith("/ontologies/")) {
    return [
      { label: "首页", href: "/" },
      { label: "本体列表", href: "/ontologies" },
      { label: "本体建模" },
    ]
  }

  const crumbs: { label: string; href?: string }[] = [
    { label: "首页", href: "/" },
  ]

  const segments = pathname.split("/").filter(Boolean)
  let currentPath = ""
  
  for (const segment of segments) {
    currentPath += `/${segment}`
    const label = routeNames[currentPath] || segment
    crumbs.push({ label })
  }

  return crumbs
}

export function Header() {
  const pathname = window.location.pathname
  const breadcrumbs = getBreadcrumb(pathname)

  return (
    <header className="header">
      <div className="header-left">
        <div className="header-breadcrumb">
          {breadcrumbs.map((crumb, index) => (
            <span key={index}>
              {index > 0 && <span className="separator">/</span>}
              {crumb.href ? (
                <Link to={crumb.href}>{crumb.label}</Link>
              ) : (
                <span className={index === breadcrumbs.length - 1 ? "current" : ""}>{crumb.label}</span>
              )}
            </span>
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

interface BackButtonProps {
  to: string
  label?: string
}

export function BackButton({ to, label = "返回" }: BackButtonProps) {
  return (
    <div className="header-back">
      <Link to={to} className="back-btn">
        ←
      </Link>
      {label && <span className="text-sm text-tertiary">{label}</span>}
    </div>
  )
}