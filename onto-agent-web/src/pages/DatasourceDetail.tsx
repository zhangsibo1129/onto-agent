import { useState, useEffect } from "react"
import { useParams } from "react-router-dom"
import { datasourceApi } from "@/services/datasourceApi"
import type { Datasource, TableInfo, ColumnInfo } from "@/services/datasourceApi"

export default function DatasourceDetail() {
  const { id } = useParams<{ id: string }>()
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
      loadTables()
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

  const loadTables = async () => {
    if (!id) return
    try {
      setLoadingTables(true)
      const result = await datasourceApi.getTables(id)
      setTables(result.tables)
    } catch (error) {
      console.error("Failed to load tables:", error)
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

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return "从未"
    const date = new Date(dateStr)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const minutes = Math.floor(diff / 60000)
    if (minutes < 1) return "刚刚"
    if (minutes < 60) return `${minutes} 分钟前`
    const hours = Math.floor(minutes / 60)
    if (hours < 24) return `${hours} 小时前`
    const days = Math.floor(hours / 24)
    if (days < 30) return `${days} 天前`
    return date.toLocaleDateString("zh-CN")
  }

  const totalRows = tables.reduce((sum, t) => sum + t.rowCount, 0)

  return (
    <>
      <div className="datasource-header">
        <div className="datasource-icon-lg">⬡</div>
        <div className="datasource-info">
          {loading ? (
            <h2>加载中...</h2>
          ) : datasource ? (
            <>
              <h2>{datasource.name}</h2>
              <div className="connection-badge">
                <div className="connection-dot" style={{ background: datasource.status === "connected" ? "var(--status-success)" : "var(--status-error)" }}></div>
                <span className="text-sm" style={{ color: datasource.status === "connected" ? "var(--status-success)" : "var(--status-error)" }}>
                  {datasource.status === "connected" ? "已连接" : "连接失败"}
                </span>
                <span className="text-sm text-tertiary">·</span>
                <span className="text-sm text-secondary">{getTypeLabel(datasource.type)}</span>
                {datasource.host && (
                  <>
                    <span className="text-sm text-tertiary">·</span>
                    <span className="text-sm text-secondary">{datasource.host}:{datasource.port}</span>
                  </>
                )}
              </div>
            </>
          ) : (
            <h2>数据源不存在</h2>
          )}
        </div>
        <div style={{ marginLeft: "auto", display: "flex", gap: "var(--space-2)" }}>
          <button className="btn btn-secondary btn-sm">编辑</button>
          <button className="btn btn-primary btn-sm" onClick={loadTables}>⟳ 同步</button>
        </div>
      </div>

      <div className="stats-grid" style={{ gridTemplateColumns: "repeat(4, 1fr)", marginBottom: "var(--space-4)" }}>
        <div className="stat-card">
          <div className="stat-label">总表数</div>
          <div className="stat-value">{loadingTables ? "-" : tables.length}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">同步状态</div>
          <div className="stat-value" style={{ color: datasource?.status === "connected" ? "var(--status-success)" : "var(--status-warning)" }}>
            {datasource?.status === "connected" ? "正常" : "未同步"}
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-label">总记录数</div>
          <div className="stat-value">
            {loadingTables ? "-" : totalRows >= 1000000 ? `${(totalRows / 1000000).toFixed(1)}M` : totalRows >= 1000 ? `${(totalRows / 1000).toFixed(1)}k` : totalRows}
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-label">最后同步</div>
          <div className="stat-value text-sm">{formatDate(datasource?.lastSyncAt || null)}</div>
        </div>
      </div>

      <div className="card" style={{ marginBottom: "var(--space-4)" }}>
        <div className="card-header">
          <span className="card-title">连接信息</span>
        </div>
        <div className="card-body">
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "var(--space-4)" }}>
            <div><div className="text-xs text-tertiary mb-1">主机地址</div><div className="text-sm mono">{datasource?.host || "-"}</div></div>
            <div><div className="text-xs text-tertiary mb-1">端口</div><div className="text-sm mono">{datasource?.port || "-"}</div></div>
            <div><div className="text-xs text-tertiary mb-1">数据库</div><div className="text-sm mono">{datasource?.database || "-"}</div></div>
            <div><div className="text-xs text-tertiary mb-1">Schema</div><div className="text-sm mono">{datasource?.schema || "public"}</div></div>
          </div>
        </div>
      </div>

      <div className="detail-layout">
        <div className="detail-left">
          <div className="detail-left-header">
            <span className="detail-left-title">数据库表 ({loadingTables ? "..." : filteredTables.length})</span>
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
                      <span>·</span>
                      <span>{t.rowCount >= 1000 ? `${(t.rowCount / 1000).toFixed(1)}k` : t.rowCount} 行</span>
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
                      <span className="col-name">{col.name}</span>
                      <span className="col-type">{col.type}</span>
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
