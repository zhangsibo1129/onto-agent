import { useLocation } from "react-router-dom"
import { Search, Bell, Settings } from "lucide-react"
import { Button } from "@/components/ui/Button"

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
  const segments = pathname.split("/").filter(Boolean)
  const crumbs: { label: string; isCurrent: boolean }[] = [
    { label: "首页", isCurrent: false },
  ]

  if (pathname === "/") {
    crumbs[0].isCurrent = true
    return crumbs
  }

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
    <header className="h-[56px] bg-[var(--bg-secondary)] border-b border-[var(--border-primary)] flex items-center justify-between px-6">
      <div className="flex items-center">
        <div className="flex items-center text-sm">
          {breadcrumbs.map((crumb, index) => (
            <span key={index} className="flex items-center">
              {index > 0 && <span className="mx-2 text-[var(--text-tertiary)]">/</span>}
              <span className={crumb.isCurrent ? "text-[var(--text-primary)]" : "text-[var(--text-tertiary)]"}>
                {crumb.label}
              </span>
            </span>
          ))}
        </div>
      </div>

      <div className="flex items-center gap-3">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--text-tertiary)]" />
          <input
            type="text"
            placeholder="搜索本体、数据源、查询..."
            className="w-64 h-9 pl-9 pr-12 bg-[var(--bg-input)] border border-[var(--border-primary)] rounded-md text-sm text-[var(--text-primary)] placeholder:text-[var(--text-tertiary)] focus:outline-none focus:border-[var(--border-focus)]"
          />
          <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-[var(--text-tertiary)]">
            ⌘K
          </span>
        </div>

        <Button variant="ghost" size="sm" className="relative">
          <Bell className="w-4 h-4" />
          <span className="absolute top-1 right-1 w-2 h-2 bg-[var(--status-error)] rounded-full" />
        </Button>

        <Button variant="ghost" size="sm">
          <Settings className="w-4 h-4" />
        </Button>
      </div>
    </header>
  )
}
