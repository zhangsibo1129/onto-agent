import { useState } from "react"

const allTables = [
  { name: "customers", cols: 15, rows: 12450, update: "1小时前", pk: "customer_id" },
  { name: "orders", cols: 18, rows: 156789, update: "30分钟前", pk: "order_id" },
  { name: "products", cols: 12, rows: 3456, update: "2小时前", pk: "product_id" },
  { name: "invoices", cols: 20, rows: 89234, update: "1小时前", pk: "invoice_id" },
  { name: "addresses", cols: 10, rows: 23567, update: "3小时前", pk: "address_id" },
  { name: "contacts", cols: 14, rows: 34567, update: "1天前", pk: "" },
  { name: "accounts", cols: 8, rows: 5678, update: "2小时前", pk: "account_id" },
  { name: "shipments", cols: 16, rows: 12345, update: "30分钟前", pk: "shipment_id" },
]

const tableColumns: Record<string, { name: string; type: string; key: string }[]> = {
  customers: [
    { name: "customer_id", type: "uuid", key: "PK" },
    { name: "customer_name", type: "varchar(255)", key: "NN" },
    { name: "email_address", type: "varchar(255)", key: "UQ" },
    { name: "phone_number", type: "varchar(50)", key: "" },
    { name: "customer_tier", type: "varchar(20)", key: "" },
    { name: "lifetime_value", type: "numeric(15,2)", key: "" },
    { name: "created_at", type: "timestamp", key: "" },
    { name: "updated_at", type: "timestamp", key: "" },
    { name: "status", type: "varchar(20)", key: "" },
  ],
  orders: [
    { name: "order_id", type: "uuid", key: "PK" },
    { name: "customer_id", type: "uuid", key: "FK" },
    { name: "order_date", type: "timestamp", key: "NN" },
    { name: "total_amount", type: "numeric(15,2)", key: "" },
    { name: "status", type: "varchar(20)", key: "" },
    { name: "shipping_address", type: "uuid", key: "FK" },
  ],
  products: [
    { name: "product_id", type: "uuid", key: "PK" },
    { name: "product_name", type: "varchar(255)", key: "NN" },
    { name: "price", type: "numeric(10,2)", key: "" },
    { name: "category", type: "varchar(100)", key: "" },
  ],
  invoices: [
    { name: "invoice_id", type: "uuid", key: "PK" },
    { name: "order_id", type: "uuid", key: "FK" },
    { name: "invoice_date", type: "date", key: "NN" },
    { name: "amount", type: "numeric(15,2)", key: "" },
  ],
  addresses: [
    { name: "address_id", type: "uuid", key: "PK" },
    { name: "customer_id", type: "uuid", key: "FK" },
    { name: "street", type: "varchar(255)", key: "NN" },
    { name: "city", type: "varchar(100)", key: "" },
    { name: "country", type: "varchar(100)", key: "" },
  ],
  contacts: [
    { name: "contact_id", type: "uuid", key: "PK" },
    { name: "customer_id", type: "uuid", key: "FK" },
    { name: "phone", type: "varchar(50)", key: "" },
    { name: "email", type: "varchar(255)", key: "" },
  ],
  accounts: [
    { name: "account_id", type: "uuid", key: "PK" },
    { name: "account_number", type: "varchar(50)", key: "UQ" },
    { name: "balance", type: "numeric(15,2)", key: "" },
  ],
  shipments: [
    { name: "shipment_id", type: "uuid", key: "PK" },
    { name: "order_id", type: "uuid", key: "FK" },
    { name: "carrier", type: "varchar(100)", key: "" },
    { name: "tracking_number", type: "varchar(100)", key: "" },
  ],
}

export default function DatasourceDetail() {
  const [selectedTable, setSelectedTable] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState("")

  const filteredTables = allTables.filter((t) =>
    t.name.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const currentColumns = selectedTable ? (tableColumns[selectedTable] || []) : []

  return (
    <>
      <div className="datasource-header">
        <div className="datasource-icon-lg">⬡</div>
        <div className="datasource-info">
          <h2>ERP-Production</h2>
          <div className="connection-badge">
            <div className="connection-dot"></div>
            <span className="text-sm" style={{ color: "var(--status-success)" }}>已连接</span>
            <span className="text-sm text-tertiary">·</span>
            <span className="text-sm text-secondary">PostgreSQL 15.2</span>
            <span className="text-sm text-tertiary">·</span>
            <span className="text-sm text-secondary">erp-db.internal:5432</span>
          </div>
        </div>
        <div style={{ marginLeft: "auto", display: "flex", gap: "var(--space-2)" }}>
          <button className="btn btn-secondary btn-sm">编辑</button>
          <button className="btn btn-primary btn-sm">⟳ 同步</button>
        </div>
      </div>

      <div className="stats-grid" style={{ gridTemplateColumns: "repeat(4, 1fr)", marginBottom: "var(--space-4)" }}>
        <div className="stat-card">
          <div className="stat-label">总表数</div>
          <div className="stat-value">{allTables.length}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">同步状态</div>
          <div className="stat-value" style={{ color: "var(--status-success)" }}>正常</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">总记录数</div>
          <div className="stat-value">~2.4M</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">最后同步</div>
          <div className="stat-value text-sm">5 分钟前</div>
        </div>
      </div>

      <div className="card" style={{ marginBottom: "var(--space-4)" }}>
        <div className="card-header">
          <span className="card-title">连接信息</span>
        </div>
        <div className="card-body">
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "var(--space-4)" }}>
            <div><div className="text-xs text-tertiary mb-1">主机地址</div><div className="text-sm mono">erp-db.internal</div></div>
            <div><div className="text-xs text-tertiary mb-1">端口</div><div className="text-sm mono">5432</div></div>
            <div><div className="text-xs text-tertiary mb-1">数据库</div><div className="text-sm mono">erp_prod</div></div>
            <div><div className="text-xs text-tertiary mb-1">Schema</div><div className="text-sm mono">public</div></div>
          </div>
        </div>
      </div>

      <div className="detail-layout">
        <div className="detail-left">
          <div className="detail-left-header">
            <span className="detail-left-title">数据库表 ({filteredTables.length})</span>
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
            {filteredTables.map((t) => {
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
                    <span>{t.cols} 列</span>
                    <span>·</span>
                    <span>{t.rows >= 1000 ? `${(t.rows / 1000).toFixed(1)}k` : t.rows} 行</span>
                    <span>·</span>
                    <span>{t.update}</span>
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        <div className="detail-right">
          <div className="card" style={{ height: "100%" }}>
            {selectedTable ? (
              <>
                <div className="card-header">
                  <span className="card-title">{selectedTable}</span>
                  <span className="text-xs text-tertiary">{currentColumns.length} 列</span>
                </div>
                <div className="column-table">
                  <div className="column-table-header">
                    <span style={{ flex: 2 }}>列名</span>
                    <span style={{ flex: 1 }}>类型</span>
                    <span style={{ flex: 0, width: 60 }}>键</span>
                  </div>
                  {currentColumns.map((col) => (
                    <div key={col.name} className="column-table-row">
                      <span style={{ flex: 2 }} className="col-name">{col.name}</span>
                      <span style={{ flex: 1 }} className="col-type">{col.type}</span>
                      <span style={{ flex: 0, width: 60 }}>
                        {col.key && (
                          <span className={`badge ${col.key === "PK" ? "badge-primary" : col.key === "FK" ? "badge-secondary" : "badge-draft"}`}>
                            {col.key}
                          </span>
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