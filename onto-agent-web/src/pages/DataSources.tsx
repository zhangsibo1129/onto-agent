import { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { mockDataSources } from "@/data/mock"
import "./DataSources.css"

interface DataSource {
  id: string
  name: string
  type: string
  status: string
  host: string
  database: string
  tableCount: number
  lastSync: string
  description: string
}

const iconColors: Record<string, { bg: string; color: string }> = {
  "ERP-Production": { bg: "rgba(59, 130, 246, 0.1)", color: "var(--brand-primary)" },
  "CRM-Main": { bg: "rgba(139, 92, 246, 0.1)", color: "var(--brand-secondary)" },
  "SCM-SupplyChain": { bg: "rgba(6, 182, 212, 0.1)", color: "var(--brand-accent)" },
}

interface FormData {
  name: string
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
  host?: string
  port?: string
  database?: string
  username?: string
  password?: string
}

const initialFormData: FormData = {
  name: "",
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
  const [showModal, setShowModal] = useState(false)
  const [formData, setFormData] = useState<FormData>(initialFormData)
  const [errors, setErrors] = useState<FormErrors>({})
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>("idle")
  const [connectionMessage, setConnectionMessage] = useState("")
  const [saveStatus, setSaveStatus] = useState<"idle" | "saving" | "success" | "error">("idle")
  const [saveMessage, setSaveMessage] = useState("")
  const [datasources, setDatasources] = useState<DataSource[]>(mockDataSources)
  const [searchTerm, setSearchTerm] = useState("")
  const [statusFilter, setStatusFilter] = useState("全部状态")

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
    setFormData(initialFormData)
    setErrors({})
    setConnectionStatus("idle")
    setConnectionMessage("")
    setSaveStatus("idle")
    setSaveMessage("")
  }

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {}

    if (!formData.name.trim()) {
      newErrors.name = "请输入数据源名称"
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

    await new Promise((resolve) => setTimeout(resolve, 1500))

    const success = Math.random() > 0.3
    if (success) {
      setConnectionStatus("success")
      setConnectionMessage("连接成功！")
    } else {
      setConnectionStatus("error")
      setConnectionMessage("连接失败：请检查主机地址和端口是否正确")
    }
  }

  const handleSave = async () => {
    if (!validateForm()) return

    setSaveStatus("saving")
    setSaveMessage("")

    await new Promise((resolve) => setTimeout(resolve, 1000))

    const success = Math.random() > 0.2
    if (success) {
      setSaveStatus("success")
      setSaveMessage("数据源创建成功！正在扫描表结构...")

      const newDs: DataSource = {
        id: `ds-${Date.now()}`,
        name: formData.name,
        type: "PostgreSQL",
        description: formData.description || `数据源 ${formData.name}`,
        status: "connected",
        host: formData.host,
        database: formData.database,
        tableCount: Math.floor(Math.random() * 50) + 10,
        lastSync: "刚刚",
      }

      setDatasources([...datasources, newDs])

      setTimeout(() => {
        handleCloseModal()
      }, 1500)
    } else {
      setSaveStatus("error")
      setSaveMessage("保存失败：请稍后重试")
    }
  }

  const handleInputChange = (field: keyof FormData, value: string) => {
    setFormData({ ...formData, [field]: value })
    if (errors[field as keyof FormErrors]) {
      setErrors({ ...errors, [field]: undefined })
    }
  }

  const filteredDatasources = datasources.filter((ds) => {
    const matchesSearch = ds.name.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus =
      statusFilter === "全部状态" ||
      (statusFilter === "已连接" && ds.status === "connected") ||
      (statusFilter === "连接失败" && ds.status === "error")
    return matchesSearch && matchesStatus
  })

  const totalTables = datasources.reduce((sum, ds) => sum + ds.tableCount, 0)
  const connectedCount = datasources.filter((ds) => ds.status === "connected").length

  return (
    <>
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">数据源总数</div>
          <div className="stat-value">{datasources.length}</div>
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
        <div className="toolbar-right">
          <button className="btn btn-ghost btn-sm">卡片视图</button>
          <button className="btn btn-ghost btn-sm">列表视图</button>
          <button className="btn btn-primary" onClick={() => setShowModal(true)}>+ 添加数据源</button>
        </div>
      </div>

      <div className="datasource-grid">
        {filteredDatasources.map((ds) => (
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
        <div className="modal-overlay" onClick={(e) => e.target === e.currentTarget && handleCloseModal()}>
          <div className="modal">
            <div className="modal-header">
              <h3 className="modal-title">添加数据源</h3>
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
                  <label className="form-label">密码 <span className="required">*</span></label>
                  <input
                    type="password"
                    className={`form-input ${errors.password ? "error" : ""}`}
                    placeholder="••••••••"
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
                {saveStatus === "saving" ? "保存中..." : "保存并扫描"}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}