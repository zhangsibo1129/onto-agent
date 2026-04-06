import { NavLink } from "react-router-dom"
import "./Sidebar.css"

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
    <aside className="sidebar">
      <div className="sidebar-logo">
        <div className="logo-icon">O</div>
        <span className="logo-text">OntoAgent</span>
      </div>

      <nav className="sidebar-nav">
        {navItems.map((section) => (
          <div key={section.section} className="nav-section">
            <div className="nav-section-title">{section.section}</div>
            {section.items.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `nav-item ${isActive ? "active" : ""}`
                }
              >
                <span className="nav-icon">{item.icon}</span>
                <span className="nav-label">{item.label}</span>
                {item.badge && <span className={`nav-badge ${item.badge === "AI" ? "nav-badge-ai" : ""}`}>{item.badge}</span>}
              </NavLink>
            ))}
          </div>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="user-avatar">A</div>
        <div className="user-info">
          <div className="user-name">Admin</div>
          <div className="user-role">系统管理员</div>
        </div>
      </div>
    </aside>
  )
}
