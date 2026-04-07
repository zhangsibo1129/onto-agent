import { Link, useLocation } from "react-router-dom"

interface BreadcrumbItem {
  label: string
  href?: string
}

interface BreadcrumbProps {
  items: BreadcrumbItem[]
}

export function Breadcrumb({ items }: BreadcrumbProps) {
  return (
    <div className="breadcrumb">
      {items.map((item, index) => (
        <span key={index} className="breadcrumb-item">
          {index > 0 && <span className="breadcrumb-separator">/</span>}
          {item.href ? (
            <Link to={item.href} className="breadcrumb-link">
              {item.label}
            </Link>
          ) : (
            <span className="breadcrumb-current">{item.label}</span>
          )}
        </span>
      ))}
    </div>
  )
}

const routeNames: Record<string, string> = {
  "/": "仪表盘",
  "/data-sources": "数据接入",
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

function getDefaultBreadcrumb(pathname: string): BreadcrumbItem[] {
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

  if (pathname.startsWith("/data-sources/") && pathname !== "/data-sources") {
    return [
      { label: "首页", href: "/" },
      { label: "数据接入", href: "/data-sources" },
      { label: "详情" },
    ]
  }

  if (pathname === "/ontologies") {
    return [
      { label: "首页", href: "/" },
      { label: routeNames["/ontologies"] },
    ]
  }

  if (pathname.startsWith("/ontologies/") && pathname !== "/ontologies") {
    return [
      { label: "首页", href: "/" },
      { label: "本体列表", href: "/ontologies" },
      { label: "本体建模" },
    ]
  }

  const crumbs: BreadcrumbItem[] = [
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

export function HeaderBreadcrumb() {
  const location = useLocation()
  const items = getDefaultBreadcrumb(location.pathname)

  return <Breadcrumb items={items} />
}