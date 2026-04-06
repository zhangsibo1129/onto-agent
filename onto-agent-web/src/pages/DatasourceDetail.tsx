

const tables = [
  { name: "customers", status: "success", cols: 15, rows: 12450, mapped: "客户360", update: "1小时前", pk: "customer_id" },
  { name: "orders", status: "success", cols: 18, rows: 156789, mapped: "订单全景", update: "30分钟前", pk: "order_id" },
  { name: "products", status: "success", cols: 12, rows: 3456, mapped: "订单全景", update: "2小时前", pk: "product_id" },
  { name: "invoices", status: "success", cols: 20, rows: 89234, mapped: "客户360", update: "1小时前", pk: "invoice_id" },
  { name: "addresses", status: "info", cols: 10, rows: 23567, mapped: "6/10 列", update: "3小时前", pk: "address_id" },
  { name: "contacts", status: "warning", cols: 14, rows: 34567, mapped: "-", update: "1天前", pk: "" },
]

const columns = [
  { name: "customer_id", type: "uuid", key: "PK" },
  { name: "customer_name", type: "varchar(255)", key: "NN" },
  { name: "email_address", type: "varchar(255)", key: "UQ" },
  { name: "phone_number", type: "varchar(50)", key: "" },
  { name: "customer_tier", type: "varchar(20)", key: "" },
  { name: "lifetime_value", type: "numeric(15,2)", key: "" },
  { name: "created_at", type: "timestamp", key: "" },
  { name: "updated_at", type: "timestamp", key: "" },
  { name: "status", type: "varchar(20)", key: "" },
]

export default function DatasourceDetail() {
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
      </div>

      <div className="stats-grid" style={{ gridTemplateColumns: "repeat(4, 1fr)", marginBottom: "var(--space-6)" }}>
        <div className="stat-card">
          <div className="stat-label">总表数</div>
          <div className="stat-value">68</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">已映射表</div>
          <div className="stat-value" style={{ color: "var(--status-success)" }}>24</div>
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

      <div className="card">
        <div className="card-header">
          <span className="card-title">数据库表 (68)</span>
          <div style={{ display: "flex", gap: "var(--space-3)" }}>
            <div className="search-input">
              <span className="icon">⌕</span>
              <input type="text" placeholder="搜索表名..." style={{ width: 200 }} />
            </div>
            <select className="form-select" style={{ width: 140 }}>
              <option>全部</option>
              <option>已映射</option>
              <option>未映射</option>
            </select>
          </div>
        </div>
        <div className="card-body">
          <div className="table-grid">
            {tables.map((t) => (
              <div key={t.name} className="table-card">
                <div className="table-card-header">
                  <span className="table-card-name">{t.name}</span>
                  <span className={`badge badge-${t.status === "success" ? "success" : t.status === "warning" ? "warning" : "info"}`}>
                    {t.status === "success" ? "已映射" : t.status === "warning" ? "未映射" : "部分映射"}
                  </span>
                </div>
                <div className="table-card-meta">
                  <div>列数: <span>{t.cols}</span></div>
                  <div>行数: <span>{t.rows.toLocaleString()}</span></div>
                  <div>映射: <span>{t.mapped}</span></div>
                  <div>更新: <span>{t.update}</span></div>
                </div>
                {t.pk && (
                  <div className="table-card-tags">
                    <span className="badge badge-draft">主键: {t.pk}</span>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="card mt-4">
        <div className="card-header">
          <span className="card-title">customers 表结构</span>
          <div className="flex gap-2">
            <button className="btn btn-ghost btn-sm">查看数据</button>
            <button className="btn btn-ghost btn-sm">映射到本体</button>
          </div>
        </div>
        <div className="column-list">
          {columns.map((c) => (
            <div key={c.name} className="column-item">
              <span className="ci-name">{c.name}</span>
              <span className="ci-type">{c.type}</span>
              {c.key === "PK" && <span className="ci-pk">PK</span>}
              {c.key === "NN" && <span className="ci-key">NN</span>}
              {c.key === "UQ" && <span className="ci-key">UQ</span>}
            </div>
          ))}
        </div>
      </div>
    </>
  )
}
