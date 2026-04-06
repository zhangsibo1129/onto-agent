import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { mockDataSources } from "@/data/mock"
import "./DataSources.css"

const iconColors: Record<string, { bg: string; color: string }> = {
  "ERP-Production": { bg: "rgba(59, 130, 246, 0.1)", color: "var(--brand-primary)" },
  "CRM-Main": { bg: "rgba(139, 92, 246, 0.1)", color: "var(--brand-secondary)" },
  "SCM-SupplyChain": { bg: "rgba(6, 182, 212, 0.1)", color: "var(--brand-accent)" },
}

export default function DataSources() {
  const navigate = useNavigate()
  const [showModal, setShowModal] = useState(false)

  const totalTables = mockDataSources.reduce((sum, ds) => sum + ds.tableCount, 0)
  const connectedCount = mockDataSources.filter((ds) => ds.status === "connected").length

  return (
    <>
      <div className="page-header">
        <div className="page-header-top">
          <div>
            <h1 className="page-title">数据源管理</h1>
            <p className="page-description">管理 PostgreSQL 数据库连接，自动采集表结构和元数据</p>
          </div>
          <div className="page-actions">
            <button className="btn btn-secondary">⟳ 刷新全部</button>
            <button className="btn btn-primary" onClick={() => setShowModal(true)}>+ 添加数据源</button>
          </div>
        </div>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">数据源总数</div>
          <div className="stat-value">{mockDataSources.length}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">连接正常</div>
          <div className="stat-value" style={{ color: "var(--status-success)" }}>{connectedCount}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">总表数</div>
          <div className="stat-value">{totalTables}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">已映射表</div>
          <div className="stat-value">42</div>
        </div>
      </div>

      <div className="toolbar">
        <div className="toolbar-left">
          <div className="search-input">
            <span className="icon">⌕</span>
            <input type="text" placeholder="搜索数据源名称..." />
          </div>
          <select className="form-select" style={{ width: 140 }}>
            <option>全部状态</option>
            <option>已连接</option>
            <option>连接失败</option>
          </select>
        </div>
        <div className="toolbar-right">
          <button className="btn btn-ghost btn-sm">卡片视图</button>
          <button className="btn btn-ghost btn-sm">列表视图</button>
        </div>
      </div>

      <div className="datasource-grid">
        {mockDataSources.map((ds) => (
          <div
            key={ds.id}
            className="datasource-card"
            onClick={() => navigate(`/data-sources/${ds.id}`)}
          >
            <div className="datasource-card-header">
              <div className="datasource-card-title">
                <div
                  className="datasource-icon"
                  style={{
                    background: iconColors[ds.name]?.bg,
                    color: iconColors[ds.name]?.color,
                  }}
                >
                  ⬡
                </div>
                <div>
                  <div className="datasource-name">{ds.name}</div>
                  <div className="text-xs text-tertiary">{ds.type}</div>
                </div>
              </div>
              <span className={`badge ${ds.status === "connected" ? "badge-success" : "badge-error"}`}>
                {ds.status === "connected" ? "已连接" : "连接失败"}
              </span>
            </div>
            <div className="text-sm text-secondary mb-4">{ds.description}</div>
            <div className="datasource-meta">
              <div className="datasource-meta-item">
                主机: <span>{ds.host}</span>
              </div>
              <div className="datasource-meta-item">
                数据库: <span>{ds.database}</span>
              </div>
              <div className="datasource-meta-item">
                表数: <span>{ds.tableCount}</span>
              </div>
              <div className="datasource-meta-item">
                最后同步: <span>{ds.lastSync}</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={(e) => e.target === e.currentTarget && setShowModal(false)}>
          <div className="modal">
            <div className="modal-header">
              <h3 className="modal-title">添加数据源</h3>
              <button className="modal-close" onClick={() => setShowModal(false)}>✕</button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label className="form-label">数据源名称 <span className="required">*</span></label>
                <input type="text" className="form-input" placeholder="例如：ERP-Production" />
                <div className="form-hint">用于标识此数据源的名称，建议使用环境+系统名</div>
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label className="form-label">主机地址 <span className="required">*</span></label>
                  <input type="text" className="form-input" placeholder="db.example.com" />
                </div>
                <div className="form-group">
                  <label className="form-label">端口 <span className="required">*</span></label>
                  <input type="number" className="form-input" defaultValue="5432" />
                </div>
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label className="form-label">数据库名 <span className="required">*</span></label>
                  <input type="text" className="form-input" placeholder="database_name" />
                </div>
                <div className="form-group">
                  <label className="form-label">Schema</label>
                  <input type="text" className="form-input" defaultValue="public" placeholder="public" />
                </div>
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label className="form-label">用户名 <span className="required">*</span></label>
                  <input type="text" className="form-input" placeholder="postgres" />
                </div>
                <div className="form-group">
                  <label className="form-label">密码 <span className="required">*</span></label>
                  <input type="password" className="form-input" placeholder="••••••••" />
                </div>
              </div>
              <div className="form-group">
                <label className="form-label">描述</label>
                <textarea className="form-textarea" placeholder="数据源用途说明..." />
              </div>
              <div className="form-group">
                <label className="form-label">SSL 模式</label>
                <select className="form-select">
                  <option>prefer</option>
                  <option>require</option>
                  <option>disable</option>
                  <option>verify-ca</option>
                  <option>verify-full</option>
                </select>
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn btn-secondary" onClick={() => setShowModal(false)}>取消</button>
              <button className="btn btn-ghost">测试连接</button>
              <button className="btn btn-primary">保存并扫描</button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
