const users = [
  { id: 1, name: "Admin", email: "admin@company.com", role: "admin", initial: "A" },
  { id: 2, name: "Zhang San", email: "zhangsan@company.com", role: "editor", initial: "Z" },
  { id: 3, name: "Li Si", email: "lisi@company.com", role: "editor", initial: "L" },
  { id: 4, name: "Wang Wu", email: "wangwu@company.com", role: "viewer", initial: "W" },
  { id: 5, name: "Zhao Liu", email: "zhaoliu@company.com", role: "viewer", initial: "Z" },
]

const ontologies = [
  { id: 1, name: "客户360", icon: "C", color: "var(--brand-primary)" },
  { id: 2, name: "供应商网络", icon: "S", color: "var(--brand-secondary)" },
  { id: 3, name: "订单全景", icon: "O", color: "var(--brand-accent)" },
  { id: 4, name: "库存管理", icon: "I", color: "var(--status-success)" },
]

export default function Permissions() {
  return (
    <>
      <div className="page-header">
        <div className="page-header-top">
          <div>
            <h1 className="page-title">权限管理</h1>
            <p className="page-description">管理用户、角色和本体访问权限</p>
          </div>
        </div>
      </div>

      <div className="stats-grid" style={{ gridTemplateColumns: "repeat(5, 1fr)" }}>
        <div className="stat-card">
          <div className="stat-label">用户总数</div>
          <div className="stat-value">24</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">管理员</div>
          <div className="stat-value">2</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">编辑者</div>
          <div className="stat-value">8</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">查看者</div>
          <div className="stat-value">14</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">API 密钥</div>
          <div className="stat-value">6</div>
        </div>
      </div>

      <div className="tabs mb-4">
        <div className="tab active">用户权限</div>
        <div className="tab">角色管理</div>
        <div className="tab">API 密钥</div>
        <div className="tab">审计日志</div>
      </div>

      <div className="permission-grid">
        <div className="permission-sidebar">
          <div className="permission-sidebar-header">
            <span className="font-semibold text-sm">用户</span>
            <button className="btn btn-ghost btn-sm">+ 邀请用户</button>
          </div>
          <div style={{ padding: "var(--space-3)" }}>
            <div className="search-input" style={{ width: "100%" }}>
              <span className="icon">⌕</span>
              <input type="text" placeholder="搜索用户..." style={{ width: "100%" }} />
            </div>
          </div>
          <div className="permission-list">
            {users.map((user) => (
              <div key={user.id} className={`permission-item ${user.id === 1 ? "active" : ""}`}>
                <div
                  className="permission-item-icon"
                  style={{
                    background:
                      user.role === "admin"
                        ? "rgba(239, 68, 68, 0.1)"
                        : user.role === "editor"
                        ? "rgba(59, 130, 246, 0.1)"
                        : "rgba(100, 116, 139, 0.1)",
                    color:
                      user.role === "admin"
                        ? "var(--status-error)"
                        : user.role === "editor"
                        ? "var(--brand-primary)"
                        : "var(--text-tertiary)",
                  }}
                >
                  {user.initial}
                </div>
                <div className="permission-item-info">
                  <div className="permission-item-name">{user.name}</div>
                  <div className="permission-item-meta">{user.email}</div>
                </div>
                <span className={`role-badge ${user.role}`}>
                  {user.role === "admin" ? "管理员" : user.role === "editor" ? "编辑者" : "查看者"}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="permission-content">
          <div className="permission-content-header">
            <div>
              <span className="font-semibold text-base">Admin</span>
              <span className="text-sm text-tertiary" style={{ marginLeft: "var(--space-2)" }}>
                admin@company.com
              </span>
            </div>
            <button className="btn btn-secondary btn-sm">编辑权限</button>
          </div>
          <div className="permission-matrix">
            <div style={{ fontSize: "var(--text-sm)", color: "var(--text-secondary)", marginBottom: "var(--space-4)" }}>
              设置用户对各本体的访问权限
            </div>
            <table>
              <thead>
                <tr>
                  <th>本体</th>
                  <th style={{ textAlign: "center" }}>读取</th>
                  <th style={{ textAlign: "center" }}>写入</th>
                  <th style={{ textAlign: "center" }}>发布</th>
                  <th style={{ textAlign: "center" }}>删除</th>
                  <th style={{ textAlign: "center" }}>管理</th>
                </tr>
              </thead>
              <tbody>
                {ontologies.map((ont) => (
                  <tr key={ont.id}>
                    <td>
                      <div className="permission-ontology">
                        <div
                          className="permission-ontology-icon"
                          style={{ background: `${ont.color}1a`, color: ont.color }}
                        >
                          {ont.icon}
                        </div>
                        <span>{ont.name}</span>
                      </div>
                    </td>
                    <td className="permission-checkbox">
                      <input type="checkbox" defaultChecked disabled />
                    </td>
                    <td className="permission-checkbox">
                      <input type="checkbox" defaultChecked disabled />
                    </td>
                    <td className="permission-checkbox">
                      <input type="checkbox" defaultChecked disabled />
                    </td>
                    <td className="permission-checkbox">
                      <input type="checkbox" defaultChecked disabled />
                    </td>
                    <td className="permission-checkbox">
                      <input type="checkbox" defaultChecked disabled />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="divider"></div>

          <div style={{ padding: "0 var(--space-4) var(--space-4)" }}>
            <div className="property-section-title" style={{ marginBottom: "var(--space-3)" }}>
              其他权限
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: "var(--space-3)" }}>
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  padding: "var(--space-3)",
                  background: "var(--bg-tertiary)",
                  borderRadius: "var(--radius-md)",
                }}
              >
                <div>
                  <div className="text-sm font-medium">管理数据源</div>
                  <div className="text-xs text-tertiary">添加、编辑、删除数据源连接</div>
                </div>
                <input type="checkbox" defaultChecked style={{ width: 18, height: 18, accentColor: "var(--brand-primary)" }} />
              </div>
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  padding: "var(--space-3)",
                  background: "var(--bg-tertiary)",
                  borderRadius: "var(--radius-md)",
                }}
              >
                <div>
                  <div className="text-sm font-medium">管理用户</div>
                  <div className="text-xs text-tertiary">邀请、编辑、删除平台用户</div>
                </div>
                <input type="checkbox" defaultChecked style={{ width: 18, height: 18, accentColor: "var(--brand-primary)" }} />
              </div>
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  padding: "var(--space-3)",
                  background: "var(--bg-tertiary)",
                  borderRadius: "var(--radius-md)",
                }}
              >
                <div>
                  <div className="text-sm font-medium">查看审计日志</div>
                  <div className="text-xs text-tertiary">查看平台操作和查询日志</div>
                </div>
                <input type="checkbox" defaultChecked style={{ width: 18, height: 18, accentColor: "var(--brand-primary)" }} />
              </div>
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  padding: "var(--space-3)",
                  background: "var(--bg-tertiary)",
                  borderRadius: "var(--radius-md)",
                }}
              >
                <div>
                  <div className="text-sm font-medium">导出本体</div>
                  <div className="text-xs text-tertiary">导出 OWL/RDF 格式本体文件</div>
                </div>
                <input type="checkbox" defaultChecked style={{ width: 18, height: 18, accentColor: "var(--brand-primary)" }} />
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}