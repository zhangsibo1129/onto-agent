import { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { ontologyApi, type Ontology, type CreateOntologyDto } from "@/services/ontologyApi"
import { Modal, Button } from "@/components/ui"
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
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [createLoading, setCreateLoading] = useState(false)

  const [formData, setFormData] = useState<CreateOntologyDto>({
    name: "",
    description: "",
    baseIri: "http://onto-agent.com/ontology/",
  })

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

  const handleDelete = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation()
    if (!confirm("确定要删除这个本体吗？")) return
    try {
      await ontologyApi.deleteOntology(id)
      setOntologies((prev) => prev.filter((o) => o.id !== id))
    } catch (err) {
      console.error("删除本体失败:", err)
      alert("删除本体失败")
    }
  }

  const handleCreateOntology = async () => {
    if (!formData.name.trim() || !formData.baseIri.trim()) {
      alert("请填写必填项")
      return
    }

    setCreateLoading(true)
    try {
      const newOntology = await ontologyApi.createOntology(formData)
      setOntologies((prev) => [...prev, newOntology])
      setShowCreateModal(false)
      setFormData({ name: "", description: "", baseIri: "http://onto-agent.com/ontology/" })
    } catch (err) {
      console.error("创建本体失败:", err)
      alert("创建本体失败")
    } finally {
      setCreateLoading(false)
    }
  }

  const handleAutoGenerateIri = () => {
    const slug = formData.name.trim() || "ontology"
    setFormData((prev) => ({
      ...prev,
      baseIri: `http://onto-agent.com/ontology/${slug}#`,
    }))
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
          <button className="btn btn-primary btn-sm" onClick={() => setShowCreateModal(true)}>+ 添加本体</button>
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

      <Modal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        title="创建本体"
        footer={
          <>
            <Button variant="secondary" onClick={() => setShowCreateModal(false)}>
              取消
            </Button>
            <Button onClick={handleCreateOntology} disabled={createLoading}>
              {createLoading ? "创建中..." : "创建"}
            </Button>
          </>
        }
      >
        <div className="form-group">
          <label className="form-label">
            本体名称 <span className="required">*</span>
          </label>
          <input
            type="text"
            className="form-input"
            value={formData.name}
            onChange={(e) => setFormData((prev) => ({ ...prev, name: e.target.value }))}
            placeholder="输入本体名称"
          />
        </div>

        <div className="form-group">
          <label className="form-label">描述</label>
          <textarea
            className="form-textarea"
            value={formData.description}
            onChange={(e) => setFormData((prev) => ({ ...prev, description: e.target.value }))}
            placeholder="输入本体描述"
            rows={3}
          />
        </div>

        <div className="form-group">
          <label className="form-label">
            Base IRI <span className="required">*</span>
          </label>
          <div className="input-with-button">
            <input
              type="text"
              className="form-input"
              value={formData.baseIri}
              onChange={(e) => setFormData((prev) => ({ ...prev, baseIri: e.target.value }))}
              placeholder="http://example.com/ontology/"
            />
            <Button variant="secondary" size="sm" onClick={handleAutoGenerateIri}>
              自动生成
            </Button>
          </div>
        </div>
      </Modal>
    </>
  )
}
