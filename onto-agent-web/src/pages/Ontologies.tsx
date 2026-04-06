import { useNavigate } from "react-router-dom"
import { mockOntologies } from "@/data/mock"
import "./Ontologies.css"

const colorMap: Record<number, { bg: string; color: string }> = {
  1: { bg: "rgba(59, 130, 246, 0.1)", color: "var(--brand-primary)" },
  2: { bg: "rgba(139, 92, 246, 0.1)", color: "var(--brand-secondary)" },
  3: { bg: "rgba(6, 182, 212, 0.1)", color: "var(--brand-accent)" },
  4: { bg: "rgba(16, 185, 129, 0.1)", color: "var(--status-success)" },
  5: { bg: "rgba(245, 158, 11, 0.1)", color: "var(--status-warning)" },
}

const statusBadgeClass: Record<string, string> = {
  published: "badge badge-published",
  draft: "badge badge-draft",
  archived: "badge badge-archived",
}

const statusText: Record<string, string> = {
  published: "已发布",
  draft: "草稿",
  archived: "已归档",
}

export default function Ontologies() {
  const navigate = useNavigate()

  const publishedCount = mockOntologies.filter((o) => o.status === "published").length
  const draftCount = mockOntologies.filter((o) => o.status === "draft").length
  const archivedCount = mockOntologies.filter((o) => o.status === "archived").length

  return (
    <>
      <div className="page-header">
        <div className="page-header-top">
          <div>
            <h1 className="page-title">本体管理</h1>
            <p className="page-description">创建和管理企业本体语义模型</p>
          </div>
          <div className="page-actions">
            <button className="btn btn-ghost">导入本体</button>
            <button className="btn btn-primary">+ 创建本体</button>
          </div>
        </div>
      </div>

      <div className="stats-grid" style={{ gridTemplateColumns: "repeat(4, 1fr)", marginBottom: "var(--space-6)" }}>
        <div className="stat-card">
          <div className="stat-label">本体总数</div>
          <div className="stat-value">{mockOntologies.length}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">已发布</div>
          <div className="stat-value" style={{ color: "var(--status-success)" }}>{publishedCount}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">草稿</div>
          <div className="stat-value" style={{ color: "var(--text-tertiary)" }}>{draftCount}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">已归档</div>
          <div className="stat-value" style={{ color: "var(--text-tertiary)" }}>{archivedCount}</div>
        </div>
      </div>

      <div className="toolbar">
        <div className="toolbar-left">
          <div className="search-input">
            <span className="icon">⌕</span>
            <input type="text" placeholder="搜索本体名称..." />
          </div>
          <select className="form-select" style={{ width: 120 }}>
            <option>全部状态</option>
            <option>已发布</option>
            <option>草稿</option>
            <option>已归档</option>
          </select>
          <select className="form-select" style={{ width: 140 }}>
            <option>全部数据源</option>
            <option>ERP-Production</option>
            <option>CRM-Main</option>
            <option>SCM-SupplyChain</option>
          </select>
        </div>
        <div className="toolbar-right">
          <button className="btn btn-ghost btn-sm">卡片视图</button>
          <button className="btn btn-ghost btn-sm">列表视图</button>
        </div>
      </div>

      <div className="ontology-grid">
        {mockOntologies.map((ontology) => (
          <div
            key={ontology.id}
            className={`ontology-card ${ontology.status === "archived" ? "archived" : ""}`}
            onClick={() => navigate(`/ontologies/${ontology.id}`)}
          >
            <div className="ontology-card-header">
              <div className="ontology-card-title-row">
                <div
                  className="ontology-card-icon"
                  style={{
                    background: colorMap[ontology.colorIndex]?.bg,
                    color: colorMap[ontology.colorIndex]?.color,
                  }}
                >
                  {ontology.initial}
                </div>
                <div className="ontology-card-info">
                  <div className="ontology-card-name">{ontology.name}</div>
                  <div className="ontology-card-desc">{ontology.description}</div>
                </div>
              </div>
              <span className={statusBadgeClass[ontology.status]}>
                {statusText[ontology.status]}
              </span>
            </div>
            <div className="ontology-card-body">
              <div className="ontology-card-stats">
                <div className="ontology-stat">
                  <div className="ontology-stat-value">{ontology.objectCount}</div>
                  <div className="ontology-stat-label">对象类型</div>
                </div>
                <div className="ontology-stat">
                  <div className="ontology-stat-value">{ontology.propertyCount}</div>
                  <div className="ontology-stat-label">属性</div>
                </div>
                <div className="ontology-stat">
                  <div className="ontology-stat-value">{ontology.relationCount}</div>
                  <div className="ontology-stat-label">关系</div>
                </div>
              </div>
            </div>
            <div className="ontology-card-footer">
              <div className="ontology-card-version">
                {ontology.version} · <span>{ontology.datasource}</span> · 更新于 {ontology.updatedAt}
              </div>
              <div className="flex gap-2">
                <button className="btn btn-ghost btn-sm" onClick={(e) => e.stopPropagation()}>查询</button>
                <button className="btn btn-ghost btn-sm" onClick={(e) => e.stopPropagation()}>编辑</button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </>
  )
}
