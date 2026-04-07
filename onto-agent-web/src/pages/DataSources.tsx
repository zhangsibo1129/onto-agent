import { useState, useEffect } from "react"
import { useNavigate, useLocation } from "react-router-dom"
import { datasourceApi } from "@/services/datasourceApi"
import type { Datasource } from "@/services/datasourceApi"
import "./DataSources.css"

const iconColors: Record<string, { bg: string; color: string }> = {
  "ERP-Production": { bg: "rgba(59, 130, 246, 0.1)", color: "var(--brand-primary)" },
  "CRM-Main": { bg: "rgba(139, 92, 246, 0.1)", color: "var(--brand-secondary)" },
  "SCM-SupplyChain": { bg: "rgba(6, 182, 212, 0.1)", color: "var(--brand-accent)" },
}

interface FormData {
  name: string
  type: string
  host: string
  port: string
  database: string
  schema: string
  username: string
  password: string
  description: string
  sslMode: string
}

interface FormErrors {
  name?: string
  type?: string
  host?: string
  port?: string
  database?: string
  username?: string
  password?: string
}

const initialFormData: FormData = {
  name: "",
  type: "postgresql",
  host: "",
  port: "5432",
  database: "",
  schema: "public",
  username: "",
  password: "",
  description: "",
  sslMode: "prefer",
}

type ConnectionStatus = "idle" | "testing" | "success" | "error"

export default function DataSources() {
  const navigate = useNavigate()
  const location = useLocation()
  const [showModal, setShowModal] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [formData, setFormData] = useState<FormData>(initialFormData)
  const [errors, setErrors] = useState<FormErrors>({})
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>("idle")
  const [connectionMessage, setConnectionMessage] = useState("")
  const [saveStatus, setSaveStatus] = useState<"idle" | "saving" | "success" | "error">("idle")
  const [saveMessage, setSaveMessage] = useState("")
  const [datasources, setDatasources] = useState<Datasource[]>([])
  const [searchTerm, setSearchTerm] = useState("")
  const [statusFilter, setStatusFilter] = useState("全部状态")
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDatasources()
  }, [])

  useEffect(() => {
    const editId = location.state?.editId as string | undefined
    if (editId) {
      const ds = datasources.find(d => d.id === editId)
      if (ds) {
        handleOpenEdit(ds)
      }
      navigate(location.pathname, { replace: true })
    }
  }, [location.state, datasources])

  const loadDatasources = async () => {
    try {
      setLoading(true)
      const data = await datasourceApi.list()
      setDatasources(data)
    } catch (error) {
      console.error("Failed to load datasources:", error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === "Escape" && showModal) {
        handleCloseModal()
      }
    }
    document.addEventListener("keydown", handleEscape)
    return () => document.removeEventListener("keydown", handleEscape)
  }, [showModal])

  const handleCloseModal = () => {
    setShowModal(false)
    setEditingId(null)
    setFormData(initialFormData)
    setErrors({})
    setConnectionStatus("idle")
    setConnectionMessage("")
    setSaveStatus("idle")
    setSaveMessage("")
  }

  const handleOpenAdd = () => {
    setEditingId(null)
    setFormData(initialFormData)
    setShowModal(true)
  }

  const handleOpenEdit = (ds: Datasource) => {
    setEditingId(ds.id)
    setFormData({
      name: ds.name,
      type: ds.type,
      host: ds.host || "",
      port: ds.port?.toString() || "5432",
      database: ds.database || "",
      schema: ds.schema || "public",
      username: ds.username || "",
      password: "",
      description: ds.description || "",
      sslMode: ds.sslMode || "prefer",
    })
    setConnectionStatus("idle")
    setConnectionMessage("")
    setSaveStatus("idle")
    setSaveMessage("")
    setShowModal(true)
  }

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation()
    if (!confirm("确定要删除这个数据源吗？")) return
    try {
      await datasourceApi.delete(id)
      setDatasources(datasources.filter(ds => ds.id !== id))
    } catch (error) {
      console.error("Failed to delete datasource:", error)
      alert("删除失败，请重试")
    }
  }

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {}

    if (!formData.name.trim()) {
      newErrors.name = "请输入数据源名称"
    }
    if (!formData.type) {
      newErrors.type = "请选择数据库类型"
    }
    if (!formData.host.trim()) {
      newErrors.host = "请输入主机地址"
    }
    if (!formData.port.trim()) {
      newErrors.port = "请输入端口"
    } else if (isNaN(Number(formData.port)) || Number(formData.port) < 1 || Number(formData.port) > 65535) {
      newErrors.port = "端口号无效"
    }
    if (!formData.database.trim()) {
      newErrors.database = "请输入数据库名"
    }
    if (!formData.username.trim()) {
      newErrors.username = "请输入用户名"
    }
    if (!formData.password) {
      newErrors.password = "请输入密码"
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleTestConnection = async () => {
    if (!validateForm()) return

    setConnectionStatus("testing")
    setConnectionMessage("")

    try {
      const result = await datasourceApi.testConnection({
        type: formData.type,
        host: formData.host,
        port: parseInt(formData.port),
        database: formData.database,
        schema: formData.schema || undefined,
        username: formData.username,
        password: formData.password,
        sslMode: formData.sslMode,
      })
      if (result.connected) {
        setConnectionStatus("success")
        setConnectionMessage(`连接成功！延迟: ${result.latency || "N/A"}`)
      } else {
        setConnectionStatus("error")
        setConnectionMessage(`连接失败: ${result.error}`)
      }
    } catch (error: any) {
      setConnectionStatus("error")
      setConnectionMessage(`连接失败: ${error.message}`)
    }
  }

  const handleSave = async () => {
    if (!validateForm()) return

    setSaveStatus("saving")
    setSaveMessage("")

    try {
      let savedDs: Datasource

      if (editingId) {
        savedDs = await datasourceApi.update(editingId, {
          name: formData.name,
          type: formData.type as "postgresql" | "mysql" | "sqlserver" | "oracle",
          host: formData.host,
          port: parseInt(formData.port),
          database: formData.database,
          schema: formData.schema || undefined,
          username: formData.username,
          password: formData.password || undefined,
          sslMode: formData.sslMode,
          description: formData.description || undefined,
        })
        setDatasources(datasources.map(ds => ds.id === editingId ? savedDs : ds))
        setSaveMessage("数据源更新成功！")
      } else {
        savedDs = await datasourceApi.create({
          name: formData.name,
          type: formData.type as "postgresql" | "mysql" | "sqlserver" | "oracle",
          host: formData.host,
          port: parseInt(formData.port),
          database: formData.database,
          schema: formData.schema || undefined,
          username: formData.username,
          password: formData.password,
          sslMode: formData.sslMode,
          description: formData.description || undefined,
        })
        const testResult = await datasourceApi.test(savedDs.id)
        savedDs = {
          ...savedDs,
          status: testResult.connected ? "connected" as const : "error" as const,
          tableCount: testResult.tableCount || 0,
        }
        setDatasources([savedDs, ...datasources])
        setSaveMessage("数据源创建成功！")
      }

      setSaveStatus("success")

      setTimeout(() => {
        handleCloseModal()
        loadDatasources()
      }, 1500)
    } catch (error: any) {
      setSaveStatus("error")
      setSaveMessage(`操作失败: ${error.message}`)
    }
  }

  const handleInputChange = (field: keyof FormData, value: string) => {
    const newFormData = { ...formData, [field]: value }
    if (field === "type") {
      const defaultPorts: Record<string, string> = {
        postgresql: "5432",
        mysql: "3306",
        sqlserver: "1433",
        oracle: "1521",
      }
      newFormData.port = defaultPorts[value] || "5432"
    }
    setFormData(newFormData)
    if (errors[field as keyof FormErrors]) {
      setErrors({ ...errors, [field]: undefined })
    }
  }

  const filteredDatasources = datasources.filter((ds) => {
    const matchesSearch = ds.name.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus =
      statusFilter === "全部状态" ||
      (statusFilter === "已连接" && ds.status === "connected") ||
      (statusFilter === "连接失败" && (ds.status === "error" || ds.status === "disconnected"))
    return matchesSearch && matchesStatus
  })

  const totalTables = datasources.reduce((sum, ds) => sum + (ds.tableCount || 0), 0)
  const connectedCount = datasources.filter((ds) => ds.status === "connected").length

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
      <div className="stats-grid" style={{ gridTemplateColumns: "repeat(3, 1fr)" }}>
        <div className="stat-card">
          <div className="stat-label">数据源总数</div>
          <div className="stat-value">{loading ? "-" : datasources.length}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">连接正常</div>
          <div className="stat-value" style={{ color: "var(--status-success)" }}>{loading ? "-" : connectedCount}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">总表数</div>
          <div className="stat-value">{loading ? "-" : totalTables}</div>
        </div>
      </div>

      <div className="toolbar">
        <div className="toolbar-left">
          <div className="search-input">
            <span className="icon">⌕</span>
            <input
              type="text"
              placeholder="搜索数据源名称..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <select
            className="form-select"
            style={{ width: 140 }}
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option>全部状态</option>
            <option>已连接</option>
            <option>连接失败</option>
          </select>
        </div>
      </div>

      <div className="datasource-grid">
        <button
          type="button"
          className="datasource-card add-card"
          onClick={handleOpenAdd}
        >
          <div className="add-icon">+</div>
          <div className="add-text">添加数据源</div>
        </button>
        {loading ? (
          <div className="datasource-card" style={{ opacity: 0.5 }}>
            <div className="text-sm text-tertiary">加载中...</div>
          </div>
        ) : (
          filteredDatasources.map((ds) => (
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
                    <div className="text-xs text-tertiary">{getTypeLabel(ds.type)}</div>
                  </div>
                </div>
                <div className="datasource-card-actions">
                  <button
                    className="btn btn-ghost btn-sm"
                    onClick={(e) => {
                      e.stopPropagation()
                      handleOpenEdit(ds)
                    }}
                    title="编辑"
                  >
                    ✎
                  </button>
                  <button
                    className="btn btn-ghost btn-sm"
                    onClick={(e) => handleDelete(ds.id, e)}
                    title="删除"
                  >
                    ✕
                  </button>
                </div>
              </div>
              <span className={`badge ${ds.status === "connected" ? "badge-success" : "badge-error"}`}>
                {ds.status === "connected" ? "已连接" : "连接失败"}
              </span>
              {ds.description && <div className="text-sm text-secondary mb-2">{ds.description}</div>}
              <div className="datasource-meta">
                <div className="datasource-meta-item">
                  主机: <span>{ds.host ? `${ds.host}:${ds.port}` : "-"}</span>
                </div>
                <div className="datasource-meta-item">
                  数据库: <span>{ds.database || "-"}</span>
                </div>
                <div className="datasource-meta-item">
                  表数: <span>{ds.tableCount >= 0 ? ds.tableCount : "-"}</span>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      <div className={`modal-overlay ${showModal ? "active" : ""}`} onClick={(e) => e.target === e.currentTarget && handleCloseModal()}>
        <div className="modal">
          <div className="modal-header">
            <h3 className="modal-title">{editingId ? "编辑数据源" : "添加数据源"}</h3>
            <button className="modal-close" onClick={handleCloseModal}>✕</button>
          </div>
          <div className="modal-body">
            <div className="form-group">
              <label className="form-label">数据源名称 <span className="required">*</span></label>
              <input
                type="text"
                className={`form-input ${errors.name ? "error" : ""}`}
                placeholder="例如：ERP-Production"
                value={formData.name}
                onChange={(e) => handleInputChange("name", e.target.value)}
              />
              {errors.name && <div className="form-error">{errors.name}</div>}
              <div className="form-hint">用于标识此数据源的名称，建议使用环境+系统名</div>
            </div>
            <div className="form-group">
              <label className="form-label">数据库类型 <span className="required">*</span></label>
              <select
                className={`form-select ${errors.type ? "error" : ""}`}
                value={formData.type}
                onChange={(e) => handleInputChange("type", e.target.value)}
              >
                <option value="postgresql">PostgreSQL</option>
                <option value="mysql">MySQL</option>
                <option value="sqlserver">SQL Server</option>
                <option value="oracle">Oracle</option>
              </select>
              {errors.type && <div className="form-error">{errors.type}</div>}
            </div>
            <div className="form-row">
              <div className="form-group">
                <label className="form-label">主机地址 <span className="required">*</span></label>
                <input
                  type="text"
                  className={`form-input ${errors.host ? "error" : ""}`}
                  placeholder="db.example.com"
                  value={formData.host}
                  onChange={(e) => handleInputChange("host", e.target.value)}
                />
                {errors.host && <div className="form-error">{errors.host}</div>}
              </div>
              <div className="form-group">
                <label className="form-label">端口 <span className="required">*</span></label>
                <input
                  type="number"
                  className={`form-input ${errors.port ? "error" : ""}`}
                  value={formData.port}
                  onChange={(e) => handleInputChange("port", e.target.value)}
                />
                {errors.port && <div className="form-error">{errors.port}</div>}
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label className="form-label">数据库名 <span className="required">*</span></label>
                <input
                  type="text"
                  className={`form-input ${errors.database ? "error" : ""}`}
                  placeholder="database_name"
                  value={formData.database}
                  onChange={(e) => handleInputChange("database", e.target.value)}
                />
                {errors.database && <div className="form-error">{errors.database}</div>}
              </div>
              <div className="form-group">
                <label className="form-label">Schema</label>
                <input
                  type="text"
                  className="form-input"
                  value={formData.schema}
                  onChange={(e) => handleInputChange("schema", e.target.value)}
                />
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label className="form-label">用户名 <span className="required">*</span></label>
                <input
                  type="text"
                  className={`form-input ${errors.username ? "error" : ""}`}
                  placeholder="postgres"
                  value={formData.username}
                  onChange={(e) => handleInputChange("username", e.target.value)}
                />
                {errors.username && <div className="form-error">{errors.username}</div>}
              </div>
              <div className="form-group">
                <label className="form-label">密码 {editingId ? "" : <span className="required">*</span>}</label>
                <input
                  type="password"
                  className={`form-input ${errors.password ? "error" : ""}`}
                  placeholder={editingId ? "留空表示不修改密码" : "••••••••"}
                  value={formData.password}
                  onChange={(e) => handleInputChange("password", e.target.value)}
                />
                {errors.password && <div className="form-error">{errors.password}</div>}
              </div>
            </div>
            <div className="form-group">
              <label className="form-label">描述</label>
              <textarea
                className="form-textarea"
                placeholder="数据源用途说明..."
                value={formData.description}
                onChange={(e) => handleInputChange("description", e.target.value)}
              />
            </div>
            <div className="form-group">
              <label className="form-label">SSL 模式</label>
              <select
                className="form-select"
                value={formData.sslMode}
                onChange={(e) => handleInputChange("sslMode", e.target.value)}
              >
                <option value="prefer">prefer</option>
                <option value="require">require</option>
                <option value="disable">disable</option>
                <option value="verify-ca">verify-ca</option>
                <option value="verify-full">verify-full</option>
              </select>
            </div>

            {connectionStatus !== "idle" && (
              <div className={`connection-result ${connectionStatus}`}>
                {connectionStatus === "testing" && (
                  <span className="connection-spinner">⟳</span>
                )}
                {connectionStatus === "success" && <span className="connection-icon">✓</span>}
                {connectionStatus === "error" && <span className="connection-icon">!</span>}
                <span>{connectionMessage}</span>
              </div>
            )}

            {saveStatus === "error" && (
              <div className="save-result error">
                <span className="connection-icon">!</span>
                <span>{saveMessage}</span>
              </div>
            )}
          </div>
          <div className="modal-footer">
            <button className="btn btn-secondary" onClick={handleCloseModal}>取消</button>
            <button
              className="btn btn-ghost"
              onClick={handleTestConnection}
              disabled={connectionStatus === "testing" || saveStatus === "saving"}
            >
              {connectionStatus === "testing" ? "测试中..." : "测试连接"}
            </button>
            <button
              className="btn btn-primary"
              onClick={handleSave}
              disabled={connectionStatus === "testing" || saveStatus === "saving"}
            >
              {saveStatus === "saving" ? "保存中..." : (editingId ? "保存" : "创建")}
            </button>
          </div>
        </div>
      </div>
    </>
  )
}
