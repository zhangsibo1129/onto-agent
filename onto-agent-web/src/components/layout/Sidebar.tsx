import { NavLink } from "react-router-dom"
import { cn } from "@/lib/utils"

const navItems = [
  {
    section: "概览",
    items: [
      { label: "仪表盘", icon: "◉", path: "/" },
    ],
  },
  {
    section: "数据管理",
    items: [
      { label: "数据源", icon: "⬡", path: "/data-sources", badge: "3" },
      { label: "本体管理", icon: "◈", path: "/ontologies" },
      { label: "数据映射", icon: "⇄", path: "/mapping" },
    ],
  },
  {
    section: "查询与分析",
    items: [
      { label: "语义查询", icon: "⌘", path: "/query" },
      { label: "自然语言查询", icon: "◉", path: "/nl-query", badge: "AI" },
      { label: "查询工作台", icon: "⚙", path: "/workbench" },
    ],
  },
  {
    section: "系统",
    items: [
      { label: "版本管理", icon: "⧖", path: "/versions" },
      { label: "数据同步", icon: "⟳", path: "/sync" },
      { label: "权限管理", icon: "⚿", path: "/permissions" },
      { label: "API 管理", icon: "⊞", path: "/api-management" },
    ],
  },
]

export function Sidebar() {
  return (
    <aside className="w-[260px] h-full bg-[var(--bg-secondary)] border-r border-[var(--border-primary)] flex flex-col">
      <div className="h-16 flex items-center px-5 border-b border-[var(--border-primary)]">
        <div className="w-8 h-8 rounded-lg bg-[var(--brand-primary)] flex items-center justify-center text-white font-bold mr-3">
          O
        </div>
        <span className="text-[var(--text-primary)] font-semibold">OntoAgent</span>
      </div>

      <nav className="flex-1 overflow-y-auto py-4">
        {navItems.map((section) => (
          <div key={section.section} className="mb-4">
            <div className="px-5 py-2 text-xs font-semibold text-[var(--text-tertiary)] uppercase tracking-wider">
              {section.section}
            </div>
            {section.items.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  cn(
                    "flex items-center h-9 px-5 mx-2 rounded-md text-sm transition-colors",
                    isActive
                      ? "bg-[rgba(59,130,246,0.1)] text-[var(--brand-primary)]"
                      : "text-[var(--text-secondary)] hover:bg-[var(--bg-hover)] hover:text-[var(--text-primary)]"
                  )
                }
              >
                <span className="mr-3 text-base">{item.icon}</span>
                <span className="flex-1">{item.label}</span>
                {item.badge && (
                  <span className={cn(
                    "text-xs px-1.5 py-0.5 rounded-full",
                    item.badge === "AI"
                      ? "bg-[var(--brand-secondary)] text-white"
                      : "bg-[var(--bg-tertiary)] text-[var(--text-tertiary)]"
                  )}>
                    {item.badge}
                  </span>
                )}
              </NavLink>
            ))}
          </div>
        ))}
      </nav>

      <div className="h-[72px] flex items-center px-5 border-t border-[var(--border-primary)]">
        <div className="w-9 h-9 rounded-full bg-[var(--brand-primary)] flex items-center justify-center text-white font-medium mr-3">
          A
        </div>
        <div>
          <div className="text-sm font-medium text-[var(--text-primary)]">Admin</div>
          <div className="text-xs text-[var(--text-tertiary)]">系统管理员</div>
        </div>
      </div>
    </aside>
  )
}
