import { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { ontologyApi, type Ontology } from "@/services/ontologyApi"
import "./Ontologies.css"

const colorMap: Record<number, { bg: string; color: string }> = {
  0: { bg: "rgba(59, 130, 246, 0.1)", color: "var(--brand-primary)" },
  1: { bg: "rgba(59, 130, 246, 0.1)", color: "var(--brand-primary)" },
  2: { bg: "rgba(139, 92, 246, 0.1)", color: "var(--brand-secondary)" },
  3: { bg: "rgba(6, 182, 212, 0.1)", color: "var(--brand-accent)" },
  4: { bg: "rgba(16, 185, 129, 0.1)", color: "var(--status-success)" },
  5: { bg: "rgba(245, 158, 11, 0.1)", color: "var(--status-warning)" },
}

const getColorIndex = (id: string): number => {
  let hash = 0
  for (let i = 0; i < id.length; i++) {
    hash = ((hash << 5) - hash) + id.charCodeAt(i)
    hash |= 0
  }
  return Math.abs(hash) % 5 + 1
}

const statusBadgeClass: Record<string, string> = {
  published: "badge badge-published",
  draft: "badge badge-draft",
}

const statusText: Record<string, string> = {
  published: "已发布",
  draft: "草稿",
}

export default function Ontologies() {
  const navigate = useNavigate()
  const [ontologies, setOntologies] = useState<Ontology[]>([])
  const [searchTerm, setSearchTerm] = useState("")
  const [statusFilter, setStatusFilter] = useState("全部状态")

  useEffect(() => {
    ontologyApi.list()
      .then(setOntologies)
      .catch(console.error)
  }, [])

  const publishedCount = ontologies.filter((o) => o.status === "published").length

  const filteredOntologies = ontologies.filter((o) => {
    const matchesSearch = o.name.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus =
      statusFilter === "全部状态" ||
      statusText[o.status] === statusFilter
    return matchesSearch && matchesStatus
  })

  const handleDelete = (e: React.MouseEvent, id: string) => {
    e.stopPropagation()
    if (!confirm("确定要删除这个本体吗？")) return
    alert(`删除本体 ${id} 功能开发中`)
  }

  return (
    <>
      <div className="toolbar" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div className="toolbar-left">
          <div className="search-input">
            <span className="icon">⌕</span>
            <input
              type="text"
              placeholder="搜索本体名称..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <select
            className="form-select"
            style={{ width: 120 }}
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option>全部状态</option>
            <option>已发布</option>
            <option>草稿</option>
          </select>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "var(--space-3)" }}>
          <span style={{ display: "flex", alignItems: "center", gap: "var(--space-2)" }}>
            <span style={{ width: 8, height: 8, borderRadius: "50%", background: publishedCount > 0 ? "var(--status-success)" : "var(--status-error)" }}></span>
            <span className="text-sm" style={{ color: "var(--text-secondary)" }}>
              {publishedCount}/{ontologies.length}
            </span>
          </span>
          <button className="btn btn-primary btn-sm" onClick={() => alert("创建本体功能开发中...")}>+ 添加本体</button>
        </div>
      </div>

      <div className="ontology-grid">
        {filteredOntologies.map((ontology) => (
          <div
            key={ontology.id}
            className="ontology-card"
            onClick={() => navigate(`/ontologies/${ontology.id}`)}
          >
            <div className="ontology-card-header">
              <div className="ontology-card-title">
            <div
              className="ontology-card-icon"
              style={{
                background: colorMap[getColorIndex(ontology.id)]?.bg,
                color: colorMap[getColorIndex(ontology.id)]?.color,
              }}
            >
                  {ontology.name.charAt(0)}
                </div>
                <div>
                  <div style={{ display: "flex", alignItems: "center", gap: "var(--space-2)" }}>
                    <div className="ontology-card-name">{ontology.name}</div>
                    <span className={statusBadgeClass[ontology.status]}>
                      {statusText[ontology.status]}
                    </span>
                  </div>
                  <div className="text-xs text-tertiary">{ontology.version}</div>
                </div>
              </div>
              <div className="ontology-card-actions">
                <button className="btn btn-ghost btn-sm" onClick={(e) => { e.stopPropagation(); alert("编辑功能开发中") }} title="编辑">✎</button>
                <button className="btn btn-ghost btn-sm" onClick={(e) => handleDelete(e, ontology.id)} title="删除">✕</button>
              </div>
            </div>
            <div className="ontology-card-description">
              {ontology.description || "暂无描述"}
            </div>
            <div className="ontology-card-meta">
              <span>类: {ontology.objectCount}</span>
              <span>·</span>
              <span>数据属性: {ontology.dataPropertyCount}</span>
              <span>·</span>
              <span>对象属性: {ontology.objectPropertyCount}</span>
            </div>
          </div>
        ))}
      </div>
    </>
  )
}
