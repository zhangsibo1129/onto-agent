import { useState, useEffect } from "react"
import {
  executeSparql,
  getQueryHistory,
  getSavedQueries,
  saveQuery,
  deleteSavedQuery,
  type SparqlResult,
  type QueryHistoryItem,
  type SavedQuery,
} from "@/services/queryApi"
import { ontologyApi, type Ontology } from "@/services/ontologyApi"
import "./Query.css"

const DEFAULT_QUERY = `PREFIX : <http://onto-agent.com/ontology#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT *
WHERE {
  ?s ?p ?o .
}
LIMIT 100`

export default function Query() {
  // Ontology selector
  const [ontologies, setOntologies] = useState<Ontology[]>([])
  const [selectedOntologyId, setSelectedOntologyId] = useState<string>("")

  // Editor state
  const [query, setQuery] = useState(DEFAULT_QUERY)
  const [isExecuting, setIsExecuting] = useState(false)
  const [activeTab, setActiveTab] = useState<"sparql" | "visual">("sparql")
  const [resultTab, setResultTab] = useState<"table" | "json" | "raw">("table")

  // Results
  const [result, setResult] = useState<SparqlResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  // History & saved
  const [history, setHistory] = useState<QueryHistoryItem[]>([])
  const [savedQueries, setSavedQueries] = useState<SavedQuery[]>([])
  const [activeSideTab, setActiveSideTab] = useState<"history" | "saved">("history")

  // Save modal
  const [showSaveModal, setShowSaveModal] = useState(false)
  const [saveName, setSaveName] = useState("")
  const [saveDesc, setSaveDesc] = useState("")

  // Load ontologies on mount
  useEffect(() => {
    ontologyApi.list().then(setOntologies).catch(console.error)
  }, [])

  // Load history when ontology changes
  useEffect(() => {
    if (!selectedOntologyId) {
      setHistory([])
      setSavedQueries([])
      return
    }
    getQueryHistory(selectedOntologyId)
      .then(setHistory)
      .catch((e) => console.error("Failed to load history:", e))
    getSavedQueries(selectedOntologyId)
      .then(setSavedQueries)
      .catch((e) => console.error("Failed to load saved queries:", e))
  }, [selectedOntologyId])

  // Run SPARQL query
  const handleExecute = async () => {
    if (!selectedOntologyId) {
      setError("请先选择本体")
      return
    }
    if (!query.trim()) {
      setError("查询不能为空")
      return
    }

    setIsExecuting(true)
    setError(null)
    setResult(null)

    try {
      const res = await executeSparql(selectedOntologyId, query)
      setResult(res)
      if (!res.success) {
        setError(res.error || "查询执行失败")
      }
      // Refresh history
      const hist = await getQueryHistory(selectedOntologyId)
      setHistory(hist)
    } catch (e: any) {
      setError(e.message || "查询执行失败")
    } finally {
      setIsExecuting(false)
    }
  }

  // Save query
  const handleSave = async () => {
    if (!selectedOntologyId || !saveName.trim()) return
    try {
      await saveQuery(selectedOntologyId, saveName.trim(), query, saveDesc.trim() || undefined)
      setShowSaveModal(false)
      setSaveName("")
      setSaveDesc("")
      const saved = await getSavedQueries(selectedOntologyId)
      setSavedQueries(saved)
    } catch (e: any) {
      alert("保存失败: " + e.message)
    }
  }

  // Delete saved query
  const handleDeleteSaved = async (id: string) => {
    if (!confirm("确定要删除这个保存的查询吗？")) return
    try {
      await deleteSavedQuery(selectedOntologyId, id)
      setSavedQueries((prev) => prev.filter((q) => q.id !== id))
    } catch (e: any) {
      alert("删除失败: " + e.message)
    }
  }

  // Load saved query into editor
  const handleLoadSaved = (sq: SavedQuery) => {
    setQuery(sq.queryText)
  }

  // Format time ago
  const timeAgo = (dateStr: string) => {
    const diff = Date.now() - new Date(dateStr).getTime()
    const mins = Math.floor(diff / 60000)
    if (mins < 1) return "刚刚"
    if (mins < 60) return `${mins} 分钟前`
    const hours = Math.floor(mins / 60)
    if (hours < 24) return `${hours} 小时前`
    return `${Math.floor(hours / 24)} 天前`
  }

  // Render SELECT results as table
  const renderSelectResults = () => {
    if (!result || result.queryType !== "SELECT") return null
    const rows = result.results as Record<string, unknown>[]
    if (!Array.isArray(rows) || rows.length === 0) {
      return <div className="empty-state">查询返回 0 条结果</div>
    }
    const columns = Object.keys(rows[0] || {})
    return (
      <div className="result-scroll">
        <table className="result-table">
          <thead>
            <tr>
              <th>#</th>
              {columns.map((col) => (
                <th key={col}>{col}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, i) => (
              <tr key={i}>
                <td className="mono" style={{ color: "var(--text-tertiary)" }}>{i + 1}</td>
                {columns.map((col) => (
                  <td key={col} className="mono">
                    {row[col] !== null && row[col] !== undefined
                      ? String(row[col])
                      : <span style={{ color: "var(--text-tertiary)" }}>null</span>}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    )
  }

  const selectedOntology = ontologies.find((o) => o.id === selectedOntologyId)
  const lineCount = query.split("\n").length

  return (
    <div className="query-layout">
      {/* Top bar: ontology selector */}
      <div className="flex gap-3" style={{ padding: "var(--space-3) var(--space-4)", borderBottom: "1px solid var(--border-primary)" }}>
        <select
          className="select"
          value={selectedOntologyId}
          onChange={(e) => setSelectedOntologyId(e.target.value)}
          style={{ minWidth: 200 }}
        >
          <option value="">— 选择本体 —</option>
          {ontologies.map((o) => (
            <option key={o.id} value={o.id}>{o.name}</option>
          ))}
        </select>
        {selectedOntology && (
          <span className="text-sm text-secondary">
            {selectedOntology.baseIri}
          </span>
        )}
      </div>

      <div className="flex gap-4" style={{ flex: 1, minHeight: 0 }}>
        {/* Left: editor + results */}
        <div style={{ flex: 1, display: "flex", flexDirection: "column", minHeight: 0 }}>
          {/* Editor */}
          <div className="query-editor-area" style={{ flex: selectedOntologyId ? "0 0 300px" : 1, borderBottom: selectedOntologyId ? "1px solid var(--border-primary)" : "none" }}>
            <div className="query-editor-header">
              <div className="query-editor-tabs">
                <div className={`query-editor-tab ${activeTab === "sparql" ? "active" : ""}`} onClick={() => setActiveTab("sparql")}>SPARQL</div>
                <div className={`query-editor-tab ${activeTab === "visual" ? "active" : ""}`} onClick={() => setActiveTab("visual")}>可视化构建</div>
              </div>
              <div className="flex gap-2">
                <button className="btn btn-ghost btn-sm" onClick={() => { setQuery(""); setResult(null); setError(null) }}>清除</button>
                <button className="btn btn-ghost btn-sm" onClick={() => setShowSaveModal(true)} disabled={!selectedOntologyId}>保存查询</button>
              </div>
            </div>
            <textarea
              className="query-textarea"
              spellCheck={false}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => {
                if ((e.ctrlKey || e.metaKey) && e.key === "Enter") handleExecute()
              }}
            />
            <div className="query-footer">
              <div className="query-info">
                {selectedOntology ? (
                  <>
                    <span>本体: {selectedOntology.name}</span>
                    <span style={{ marginLeft: "var(--space-4)" }}>行数: {lineCount}</span>
                    {result && (
                      <>
                        <span style={{ marginLeft: "var(--space-4)" }}>
                          执行: {result.executionTimeMs}ms · {result.resultCount} 条
                        </span>
                      </>
                    )}
                  </>
                ) : (
                  <span style={{ color: "var(--text-tertiary)" }}>请先选择本体</span>
                )}
              </div>
              <div className="flex gap-2">
                <button
                  className="btn btn-primary"
                  onClick={handleExecute}
                  disabled={!selectedOntologyId || isExecuting}
                >
                  {isExecuting ? "执行中..." : "▶ 执行查询"}
                </button>
              </div>
            </div>
          </div>

          {/* Results */}
          {selectedOntologyId && result && (
            <div className="query-result-area" style={{ flex: 1, minHeight: 0 }}>
              <div className="query-result-tabs">
                <div className={`query-result-tab ${resultTab === "table" ? "active" : ""}`} onClick={() => setResultTab("table")}>
                  {result.queryType === "SELECT" ? `表格结果 (${result.resultCount})` : result.queryType === "ASK" ? "ASK 结果" : "Turtle 结果"}
                </div>
                {result.queryType === "SELECT" && (
                  <div className={`query-result-tab ${resultTab === "json" ? "active" : ""}`} onClick={() => setResultTab("json")}>JSON</div>
                )}
              </div>
              <div className="query-result-body">
                {error && <div className="alert alert-error">{error}</div>}
                {result.queryType === "ASK" && (
                  <div className="result-boolean">
                    <span className={`boolean-badge ${result.results ? "true" : "false"}`}>
                      {String(result.results)}
                    </span>
                  </div>
                )}
                {result.queryType === "CONSTRUCT" && (
                  <pre className="result-turtle">{result.results as string}</pre>
                )}
                {result.queryType === "SELECT" && resultTab === "table" && renderSelectResults()}
                {result.queryType === "SELECT" && resultTab === "json" && (
                  <pre className="result-json">{JSON.stringify(result.results, null, 2)}</pre>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Right: history + saved */}
        {selectedOntologyId && (
          <div className="query-history" style={{ width: 320, flexShrink: 0 }}>
            <div className="query-history-header">
              <div className="flex gap-1">
                <button
                  className={`tab-btn ${activeSideTab === "history" ? "active" : ""}`}
                  onClick={() => setActiveSideTab("history")}
                >历史</button>
                <button
                  className={`tab-btn ${activeSideTab === "saved" ? "active" : ""}`}
                  onClick={() => setActiveSideTab("saved")}
                >已保存</button>
              </div>
            </div>

            {activeSideTab === "history" && (
              <div className="query-history-list">
                {history.length === 0 && <div className="empty-state-sm">暂无历史记录</div>}
                {history.map((item) => (
                  <div
                    key={item.id}
                    className="query-history-item"
                    onClick={() => setQuery(item.queryText)}
                    title={item.queryText}
                  >
                    <div className="qhi-type">{item.queryType}</div>
                    <div className="qhi-query">{item.queryText.split("\n")[0].substring(0, 60)}...</div>
                    <div className="qhi-meta">
                      <span>{item.resultCount} 条</span>
                      <span>{item.errorMessage ? "❌" : "✅"}</span>
                      <span>{timeAgo(item.createdAt)}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {activeSideTab === "saved" && (
              <div className="query-history-list">
                {savedQueries.length === 0 && <div className="empty-state-sm">暂无保存的查询</div>}
                {savedQueries.map((sq) => (
                  <div key={sq.id} className="query-history-item">
                    <div className="qhi-type">{sq.queryType}</div>
                    <div className="qhi-query" style={{ cursor: "pointer" }} onClick={() => handleLoadSaved(sq)}>
                      {sq.name}
                    </div>
                    <div className="qhi-meta">
                      <span>{timeAgo(sq.updatedAt)}</span>
                      <button className="btn-link" onClick={() => handleDeleteSaved(sq.id)}>删除</button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Save Modal */}
      {showSaveModal && (
        <div className="modal-overlay" onClick={() => setShowSaveModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>保存查询</h3>
              <button className="btn-close" onClick={() => setShowSaveModal(false)}>×</button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>查询名称 *</label>
                <input
                  className="input"
                  value={saveName}
                  onChange={(e) => setSaveName(e.target.value)}
                  placeholder="例如：金牌客户查询"
                  autoFocus
                />
              </div>
              <div className="form-group">
                <label>描述（可选）</label>
                <input
                  className="input"
                  value={saveDesc}
                  onChange={(e) => setSaveDesc(e.target.value)}
                  placeholder="查询用途说明"
                />
              </div>
              <div className="form-group">
                <label>查询内容</label>
                <textarea
                  className="textarea"
                  value={query}
                  readOnly
                  rows={6}
                  style={{ fontFamily: "var(--font-mono)", fontSize: 12 }}
                />
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn btn-ghost" onClick={() => setShowSaveModal(false)}>取消</button>
              <button className="btn btn-primary" onClick={handleSave} disabled={!saveName.trim()}>保存</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
