import { useState, useEffect } from "react"
import { useParams, useNavigate } from "react-router-dom"
import { datasourceApi } from "@/services/datasourceApi"
import type { Datasource, TableInfo, ColumnInfo } from "@/services/datasourceApi"

export default function DatasourceDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [datasource, setDatasource] = useState<Datasource | null>(null)
  const [tables, setTables] = useState<TableInfo[]>([])
  const [selectedTable, setSelectedTable] = useState<string | null>(null)
  const [columns, setColumns] = useState<ColumnInfo[]>([])
  const [searchTerm, setSearchTerm] = useState("")
  const [loading, setLoading] = useState(true)
  const [loadingTables, setLoadingTables] = useState(false)
  const [loadingColumns, setLoadingColumns] = useState(false)

  useEffect(() => {
    if (id) {
      loadDatasource()
    }
  }, [id])

  useEffect(() => {
    if (datasource && datasource.status === "connected" && tables.length === 0) {
      handleScan()
    }
  }, [datasource])

  useEffect(() => {
    if (id && selectedTable) {
      loadColumns(selectedTable)
    }
  }, [selectedTable])

  const loadDatasource = async () => {
    if (!id) return
    try {
      setLoading(true)
      const data = await datasourceApi.get(id)
      setDatasource(data)
    } catch (error) {
      console.error("Failed to load datasource:", error)
    } finally {
      setLoading(false)
    }
  }

  const handleScan = async () => {
    if (!id || datasource?.status !== "connected") return
    try {
      setLoadingTables(true)
      const result = await datasourceApi.scan(id)
      setTables(result.tables)
      setDatasource(prev => prev ? {
        ...prev,
        status: "connected",
        tableCount: result.tables.length,
      } : null)
    } catch (error) {
      console.error("Failed to scan datasource:", error)
      setDatasource(prev => prev ? { ...prev, status: "error" } : null)
    } finally {
      setLoadingTables(false)
    }
  }

  const loadColumns = async (tableName: string) => {
    if (!id) return
    try {
      setLoadingColumns(true)
      const result = await datasourceApi.getColumns(id, tableName)
      setColumns(result.columns)
    } catch (error) {
      console.error("Failed to load columns:", error)
      setColumns([])
    } finally {
      setLoadingColumns(false)
    }
  }

  const filteredTables = tables.filter((t) =>
    t.name.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const getTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      postgresql: "PostgreSQL",
      mysql: "MySQL",
      sqlserver: "SQL Server",
      oracle: "Oracle",
    }
    return labels[type] || type
  }

  return (
    <>
      <div style={{ marginBottom: "var(--space-5)" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "var(--space-3)" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "var(--space-3)" }}>
            <div className="datasource-icon-lg">⬡</div>
            <div>
              {loading ? (
                <h2>加载中...</h2>
              ) : datasource ? (
                <h2 style={{ marginBottom: "var(--space-1)" }}>{datasource.name}</h2>
              ) : (
                <h2>数据源不存在</h2>
              )}
            </div>
          </div>
          <div style={{ display: "flex", gap: "var(--space-2)" }}>
            <button className="btn btn-secondary btn-sm" onClick={() => navigate('/data-sources', { state: { editId: id } })}>编辑</button>
            <button className="btn btn-primary btn-sm" onClick={handleScan} disabled={loadingTables || datasource?.status !== "connected"}>
              {loadingTables ? "同步中..." : "同步"}
            </button>
          </div>
        </div>

        {datasource && (
          <div style={{ display: "flex", flexWrap: "wrap", gap: "var(--space-4)", alignItems: "center", fontSize: "var(--text-sm)", color: "var(--text-secondary)" }}>
            <span style={{ display: "flex", alignItems: "center", gap: "var(--space-2)" }}>
              <span style={{ width: 8, height: 8, borderRadius: "50%", background: datasource.status === "connected" ? "var(--status-success)" : "var(--status-error)" }}></span>
              <span style={{ color: datasource.status === "connected" ? "var(--status-success)" : "var(--status-error)" }}>
                {datasource.status === "connected" ? "已连接" : "连接失败"}
              </span>
            </span>
            <span style={{ color: "var(--text-tertiary)" }}>·</span>
            <span>{getTypeLabel(datasource.type)}</span>
            <span style={{ color: "var(--text-tertiary)" }}>·</span>
            <span className="mono">{datasource.host}:{datasource.port}</span>
            <span style={{ color: "var(--text-tertiary)" }}>·</span>
            <span>{datasource.database}</span>
            {datasource.schema && (
              <>
                <span style={{ color: "var(--text-tertiary)" }}>·</span>
                <span>{datasource.schema}</span>
              </>
            )}
            <span style={{ color: "var(--text-tertiary)" }}>·</span>
            <span>{loadingTables ? "-" : tables.length} 表</span>
          </div>
        )}

        {datasource?.description && (
          <div style={{ marginTop: "var(--space-3)", fontSize: "var(--text-sm)", color: "var(--text-tertiary)" }}>
            {datasource.description}
          </div>
        )}
      </div>

      <div className="detail-layout">
        <div className="detail-left">
          <div className="detail-left-header">
            <span className="detail-left-title">表 ({loadingTables ? "..." : filteredTables.length})</span>
            <div className="detail-left-controls">
              <div className="search-input">
                <span className="icon">⌕</span>
                <input
                  type="text"
                  placeholder="搜索..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
            </div>
          </div>
          <div className="table-list">
            {loadingTables ? (
              <div style={{ padding: "var(--space-4)", textAlign: "center", color: "var(--text-tertiary)" }}>
                加载中...
              </div>
            ) : filteredTables.length === 0 ? (
              <div style={{ padding: "var(--space-4)", textAlign: "center", color: "var(--text-tertiary)" }}>
                {tables.length === 0 ? "点击同步按钮扫描表结构" : "无匹配结果"}
              </div>
            ) : (
              filteredTables.map((t) => {
                const isSelected = selectedTable === t.name
                return (
                  <div
                    key={t.name}
                    className={`table-list-item ${isSelected ? "selected" : ""}`}
                    onClick={() => setSelectedTable(isSelected ? null : t.name)}
                  >
                    <div className="table-list-item-main">
                      <span className="table-list-name">{t.name}</span>
                    </div>
                    <div className="table-list-meta">
                      <span>{t.columns} 列</span>
                    </div>
                  </div>
                )
              })
            )}
          </div>
        </div>

        <div className="detail-right">
          <div className="card" style={{ height: "100%" }}>
            {loadingColumns ? (
              <div className="empty-state">
                <span className="empty-icon">⟳</span>
                <span>加载列信息...</span>
              </div>
            ) : selectedTable ? (
              <>
                <div className="card-header">
                  <span className="card-title">{selectedTable}</span>
                  <span className="text-xs text-tertiary">{columns.length} 列</span>
                </div>
                <div className="column-table">
                  <div className="column-table-header">
                    <span>列名</span>
                    <span>类型</span>
                    <span>键</span>
                  </div>
                  {columns.map((col) => (
                    <div key={col.name} className="column-table-row">
                      <span className="col-name" style={{ fontFamily: "var(--font-mono)", fontSize: "var(--text-xs)" }}>{col.name}</span>
                      <span className="col-type" style={{ fontFamily: "var(--font-mono)", fontSize: "var(--text-xs)", color: "var(--text-secondary)" }}>{col.type}</span>
                      <span>
                        {col.primaryKey && (
                          <span className="badge badge-primary">PK</span>
                        )}
                      </span>
                    </div>
                  ))}
                </div>
              </>
            ) : (
              <div className="empty-state">
                <span className="empty-icon">◈</span>
                <span>点击左侧表名查看表结构</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  )
}
