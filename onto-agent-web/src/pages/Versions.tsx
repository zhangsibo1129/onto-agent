import { useState, useEffect, useCallback } from "react"
import { ontologyApi, type Ontology, type Version, type VersionChange } from "@/services/ontologyApi"

export default function Versions() {
  // State
  const [ontologies, setOntologies] = useState<Ontology[]>([])
  const [selectedOntologyId, setSelectedOntologyId] = useState<string>("")
  const [versions, setVersions] = useState<Version[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Modal states
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showCompareModal, setShowCompareModal] = useState(false)
  const [showDetailModal, setShowDetailModal] = useState(false)
  const [selectedVersion, setSelectedVersion] = useState<Version | null>(null)
  const [compareFrom, setCompareFrom] = useState<string>("")
  const [compareTo, setCompareTo] = useState<string>("")
  const [compareResult, setCompareResult] = useState<string>("")

  // Form state
  const [newVersion, setNewVersion] = useState({
    version: "",
    description: "",
    changeLog: "" as string,
  })

  // Fetch ontologies on mount
  useEffect(() => {
    ontologyApi
      .list()
      .then(setOntologies)
      .catch((e) => setError("加载本体列表失败: " + e.message))
  }, [])

  // Fetch versions when ontology changes
  const fetchVersions = useCallback(async (ontologyId: string) => {
    if (!ontologyId) {
      setVersions([])
      return
    }
    setLoading(true)
    setError(null)
    try {
      const data = await ontologyApi.listVersions(ontologyId)
      setVersions(data)
    } catch (e: any) {
      setError("加载版本列表失败: " + e.message)
      setVersions([])
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchVersions(selectedOntologyId)
  }, [selectedOntologyId, fetchVersions])

  // Get selected ontology info
  const selectedOntology = ontologies.find((o) => o.id === selectedOntologyId)

  // Stats
  const currentVersion = versions.find((v) => v.status === "published")?.version || "-"
  const draftCount = versions.filter((v) => v.status === "draft").length
  const publishedCount = versions.filter((v) => v.status === "published").length
  const archivedCount = versions.filter((v) => v.status === "archived").length

  // Handlers
  const handleCreateVersion = async () => {
    if (!selectedOntologyId || !newVersion.version) return
    try {
      const changeLog: VersionChange[] = newVersion.changeLog
        ? newVersion.changeLog.split("\n").map((line) => ({
            type: line.startsWith("-") ? "deleted" : line.startsWith("~") ? "modified" : "added",
            text: line.replace(/^[+\-~]\s*/, ""),
          }))
        : []

      await ontologyApi.createVersion(selectedOntologyId, {
        version: newVersion.version,
        description: newVersion.description,
        changeLog,
      })
      setShowCreateModal(false)
      setNewVersion({ version: "", description: "", changeLog: "" })
      fetchVersions(selectedOntologyId)
    } catch (e: any) {
      alert("创建版本失败: " + e.message)
    }
  }

  const handlePublish = async (version: Version) => {
    if (!selectedOntologyId) return
    if (!confirm(`确定要发布版本 ${version.version} 吗？`)) return
    try {
      await ontologyApi.publishOntology(selectedOntologyId)
      fetchVersions(selectedOntologyId)
    } catch (e: any) {
      alert("发布失败: " + e.message)
    }
  }

  const handleUnpublish = async () => {
    if (!selectedOntologyId) return
    if (!confirm("确定要取消发布吗？本体将变为草稿状态。")) return
    try {
      await ontologyApi.unpublishOntology(selectedOntologyId)
      fetchVersions(selectedOntologyId)
    } catch (e: any) {
      alert("取消发布失败: " + e.message)
    }
  }

  const handleRollback = async (version: Version) => {
    if (!selectedOntologyId) return
    if (!confirm(`确定要回滚到版本 ${version.version} 吗？\n\n注意：当前数据将被保存为 pre_rollback 快照。`)) return
    try {
      await ontologyApi.rollbackVersion(selectedOntologyId, version.version)
      alert("回滚成功")
      fetchVersions(selectedOntologyId)
    } catch (e: any) {
      alert("回滚失败: " + e.message)
    }
  }

  const handleDelete = async (version: Version) => {
    if (!selectedOntologyId) return
    if (!confirm(`确定要删除版本 ${version.version} 吗？\n\n此操作不可恢复。`)) return
    try {
      await ontologyApi.deleteVersion(selectedOntologyId, version.version)
      fetchVersions(selectedOntologyId)
    } catch (e: any) {
      alert("删除失败: " + e.message)
    }
  }

  const handleCompare = async () => {
    if (!selectedOntologyId || !compareFrom || !compareTo) return
    try {
      const result = await ontologyApi.compareVersions(selectedOntologyId, compareFrom, compareTo)
      setCompareResult(`从 ${result.fromVersion} 到 ${result.toVersion}\n\n${result.fromContent.substring(0, 500)}...`)
    } catch (e: any) {
      alert("对比失败: " + e.message)
    }
  }

  const handleViewDetail = async (version: Version) => {
    if (!selectedOntologyId) return
    try {
      const detail = await ontologyApi.getVersion(selectedOntologyId, version.version)
      setSelectedVersion(version)
      setCompareResult(`版本: ${version.version}\n\nTBox 内容:\n${detail.tboxContent.substring(0, 500)}...\n\nABox 内容:\n${detail.aboxContent.substring(0, 500)}...`)
      setShowDetailModal(true)
    } catch (e: any) {
      alert("获取详情失败: " + e.message)
    }
  }

  const formatDate = (dateStr: string) => {
    if (!dateStr) return "编辑中"
    const date = new Date(dateStr)
    if (isNaN(date.getTime())) return dateStr
    return date.toLocaleString("zh-CN", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    })
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case "draft":
        return "草稿"
      case "published":
        return "已发布"
      case "archived":
        return "已归档"
      default:
        return status
    }
  }

  const isCurrentVersion = (v: Version) => {
    // 已发布的最新版本视为当前版本
    const published = versions.filter((ver) => ver.status === "published")
    if (published.length === 0) return false
    return published[0].version === v.version
  }

  return (
    <div className="versions-page">
      {/* Header with ontology selector */}
      <div className="card" style={{ marginBottom: "1.5rem" }}>
        <div className="card-body" style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: "1rem" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
            <h2 style={{ margin: 0, fontSize: "1.25rem" }}>版本管理</h2>
            <select
              value={selectedOntologyId}
              onChange={(e) => setSelectedOntologyId(e.target.value)}
              className="form-select"
              style={{ minWidth: "200px" }}
            >
              <option value="">选择本体...</option>
              {ontologies.map((o) => (
                <option key={o.id} value={o.id}>
                  {o.name} ({o.status === "published" ? "已发布" : "草稿"})
                </option>
              ))}
            </select>
            {selectedOntology && (
              <span className="text-secondary">
                状态: {getStatusText(selectedOntology.status)}
              </span>
            )}
          </div>
          {selectedOntologyId && (
            <button className="btn btn-primary" onClick={() => setShowCreateModal(true)}>
              + 创建版本
            </button>
          )}
        </div>
      </div>

      {error && (
        <div className="alert alert-error" style={{ marginBottom: "1rem" }}>
          {error}
        </div>
      )}

      {!selectedOntologyId ? (
        <div className="empty-state">
          <p>请选择一个本体以查看版本历史</p>
        </div>
      ) : loading ? (
        <div className="loading">加载中...</div>
      ) : (
        <>
          {/* Stats */}
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-label">当前版本</div>
              <div className="stat-value" style={{ color: "var(--status-success)" }}>
                {currentVersion}
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-label">草稿版本</div>
              <div className="stat-value">{draftCount}</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">已发布版本</div>
              <div className="stat-value">{publishedCount}</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">已归档版本</div>
              <div className="stat-value">{archivedCount}</div>
            </div>
          </div>

          {/* Version Timeline */}
          <div className="card">
            <div className="card-header">
              <span className="card-title">
                版本历史{selectedOntology ? ` - ${selectedOntology.name}` : ""}
              </span>
              {versions.length > 0 && (
                <button
                  className="btn btn-secondary btn-sm"
                  onClick={() => {
                    setCompareFrom(versions[0]?.version || "")
                    setCompareTo(versions[1]?.version || "")
                    setShowCompareModal(true)
                  }}
                >
                  对比版本
                </button>
              )}
            </div>
            <div className="card-body">
              {versions.length === 0 ? (
                <div className="empty-state">
                  <p>暂无版本记录</p>
                  <button className="btn btn-primary" onClick={() => setShowCreateModal(true)}>
                    创建第一个版本
                  </button>
                </div>
              ) : (
                <div className="version-timeline">
                  {versions.map((v) => (
                    <div key={v.version} className="version-item">
                      <div className={`version-dot ${v.status}`}></div>
                      <div className={`version-card ${isCurrentVersion(v) ? "current" : ""}`}>
                        <div className="version-header">
                          <div className="version-title">
                            <span className="version-tag">{v.version}</span>
                            <span className={`badge badge-${v.status}`}>
                              {getStatusText(v.status)}
                            </span>
                            {isCurrentVersion(v) && (
                              <span
                                className="badge badge-info"
                                style={{
                                  background: "rgba(59, 130, 246, 0.1)",
                                  color: "var(--brand-primary)",
                                }}
                              >
                                当前版本
                              </span>
                            )}
                          </div>
                          <span className="text-xs text-tertiary">
                            {formatDate(v.createdAt)}
                            {v.tripleCount !== undefined && (
                              <span style={{ marginLeft: "0.5rem" }}>
                                ({v.tripleCount} triples)
                              </span>
                            )}
                          </span>
                        </div>
                        <div className="version-desc">{v.description || "无描述"}</div>
                        {v.changeLog && v.changeLog.length > 0 && (
                          <div className="version-changes">
                            {v.changeLog.map((c, i) => (
                              <div key={i} className={`version-change ${c.type}`}>
                                <span className="vc-icon">
                                  {c.type === "added" ? "+" : c.type === "deleted" ? "-" : "~"}
                                </span>
                                <span>{c.text}</span>
                              </div>
                            ))}
                          </div>
                        )}
                        <div className="version-actions">
                          {v.status === "draft" && (
                            <>
                              <button
                                className="btn btn-primary btn-sm"
                                onClick={() => handlePublish(v)}
                              >
                                发布
                              </button>
                              <button
                                className="btn btn-secondary btn-sm"
                                onClick={() => handleViewDetail(v)}
                              >
                                查看快照
                              </button>
                              <button
                                className="btn btn-ghost btn-sm"
                                onClick={() => handleDelete(v)}
                              >
                                删除
                              </button>
                            </>
                          )}
                          {v.status === "published" && isCurrentVersion(v) && (
                            <>
                              <button
                                className="btn btn-secondary btn-sm"
                                onClick={() => handleViewDetail(v)}
                              >
                                查看快照
                              </button>
                              <button
                                className="btn btn-ghost btn-sm"
                                onClick={() => handleRollback(v)}
                              >
                                回滚(重新加载)
                              </button>
                              <button className="btn btn-ghost btn-sm" onClick={handleUnpublish}>
                                取消发布
                              </button>
                            </>
                          )}
                          {v.status === "published" && !isCurrentVersion(v) && (
                            <>
                              <button
                                className="btn btn-secondary btn-sm"
                                onClick={() => handleViewDetail(v)}
                              >
                                查看快照
                              </button>
                              <button
                                className="btn btn-ghost btn-sm"
                                onClick={() => handleRollback(v)}
                              >
                                回滚到此版本
                              </button>
                              <button
                                className="btn btn-ghost btn-sm"
                                onClick={() => {
                                  setCompareFrom(v.version)
                                  setCompareTo(versions[0]?.version || "")
                                  setShowCompareModal(true)
                                }}
                              >
                                与当前对比
                              </button>
                            </>
                          )}
                          {v.status === "archived" && (
                            <>
                              <button
                                className="btn btn-ghost btn-sm"
                                onClick={() => handleViewDetail(v)}
                              >
                                查看快照
                              </button>
                              <button
                                className="btn btn-ghost btn-sm"
                                onClick={() => handleRollback(v)}
                              >
                                恢复
                              </button>
                            </>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </>
      )}

      {/* Create Version Modal */}
      {showCreateModal && (
        <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>创建新版本</h3>
              <button className="btn btn-ghost" onClick={() => setShowCreateModal(false)}>
                ✕
              </button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>版本号</label>
                <input
                  type="text"
                  value={newVersion.version}
                  onChange={(e) => setNewVersion({ ...newVersion, version: e.target.value })}
                  placeholder="例如: v1.0, v2.1-beta"
                  className="form-input"
                />
              </div>
              <div className="form-group">
                <label>描述</label>
                <textarea
                  value={newVersion.description}
                  onChange={(e) => setNewVersion({ ...newVersion, description: e.target.value })}
                  placeholder="描述此版本的主要变更..."
                  className="form-textarea"
                  rows={3}
                />
              </div>
              <div className="form-group">
                <label>变更日志（每行一条，+ 新增，- 删除，~ 修改）</label>
                <textarea
                  value={newVersion.changeLog}
                  onChange={(e) => setNewVersion({ ...newVersion, changeLog: e.target.value })}
                  placeholder={"+ 新增 Customer 对象类型\n~ 修改 Order 属性\n- 删除废弃字段"}
                  className="form-textarea"
                  rows={4}
                />
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn btn-secondary" onClick={() => setShowCreateModal(false)}>
                取消
              </button>
              <button className="btn btn-primary" onClick={handleCreateVersion}>
                创建版本
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Compare Modal */}
      {showCompareModal && (
        <div className="modal-overlay" onClick={() => setShowCompareModal(false)}>
          <div className="modal modal-lg" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>版本对比</h3>
              <button className="btn btn-ghost" onClick={() => setShowCompareModal(false)}>
                ✕
              </button>
            </div>
            <div className="modal-body">
              <div style={{ display: "flex", gap: "1rem", marginBottom: "1rem" }}>
                <select
                  value={compareFrom}
                  onChange={(e) => setCompareFrom(e.target.value)}
                  className="form-select"
                >
                  <option value="">选择起始版本</option>
                  {versions.map((v) => (
                    <option key={v.version} value={v.version}>
                      {v.version}
                    </option>
                  ))}
                </select>
                <span>→</span>
                <select
                  value={compareTo}
                  onChange={(e) => setCompareTo(e.target.value)}
                  className="form-select"
                >
                  <option value="">选择目标版本</option>
                  {versions.map((v) => (
                    <option key={v.version} value={v.version}>
                      {v.version}
                    </option>
                  ))}
                </select>
                <button className="btn btn-primary" onClick={handleCompare}>
                  对比
                </button>
              </div>
              {compareResult && (
                <pre
                  style={{
                    background: "var(--bg-secondary)",
                    padding: "1rem",
                    borderRadius: "8px",
                    overflow: "auto",
                    maxHeight: "400px",
                  }}
                >
                  {compareResult}
                </pre>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Detail Modal */}
      {showDetailModal && selectedVersion && (
        <div className="modal-overlay" onClick={() => setShowDetailModal(false)}>
          <div className="modal modal-lg" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>版本详情: {selectedVersion.version}</h3>
              <button className="btn btn-ghost" onClick={() => setShowDetailModal(false)}>
                ✕
              </button>
            </div>
            <div className="modal-body">
              <pre
                style={{
                  background: "var(--bg-secondary)",
                  padding: "1rem",
                  borderRadius: "8px",
                  overflow: "auto",
                  maxHeight: "500px",
                  fontSize: "12px",
                }}
              >
                {compareResult}
              </pre>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
