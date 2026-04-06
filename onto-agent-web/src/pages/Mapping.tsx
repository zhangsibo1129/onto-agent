import "./Mapping.css"

const ontologyProperties = [
  { name: "customerId", type: "UUID", meta: "主键" },
  { name: "name", type: "String", meta: "必填" },
  { name: "email", type: "String", meta: "" },
  { name: "phone", type: "String", meta: "" },
  { name: "tier", type: "Enum", meta: "" },
  { name: "lifetimeValue", type: "Decimal", meta: "" },
  { name: "createdAt", type: "DateTime", meta: "" },
  { name: "status", type: "Enum", meta: "" },
  { name: "industry", type: "String", meta: "" },
  { name: "website", type: "String", meta: "" },
  { name: "annualRevenue", type: "Decimal", meta: "" },
  { name: "employeeCount", type: "Integer", meta: "" },
]

const sourceColumns = [
  { name: "customer_id", type: "uuid", meta: "PK" },
  { name: "customer_name", type: "varchar(255)", meta: "" },
  { name: "email_address", type: "varchar(255)", meta: "" },
  { name: "phone_number", type: "varchar(50)", meta: "" },
  { name: "customer_tier", type: "varchar(20)", meta: "" },
  { name: "lifetime_value", type: "numeric(15,2)", meta: "" },
  { name: "created_at", type: "timestamp", meta: "" },
  { name: "status", type: "varchar(20)", meta: "" },
  { name: "industry_code", type: "varchar(10)", meta: "" },
  { name: "website_url", type: "varchar(500)", meta: "" },
  { name: "annual_revenue", type: "numeric(15,2)", meta: "" },
  { name: "employee_count", type: "integer", meta: "" },
]

const mappedProperties = [
  { property: "customerId", pType: "UUID", column: "customer_id", cType: "uuid" },
  { property: "name", pType: "String", column: "customer_name", cType: "varchar(255)" },
  { property: "email", pType: "String", column: "email_address", cType: "varchar(255)" },
  { property: "phone", pType: "String", column: "phone_number", cType: "varchar(50)" },
  { property: "tier", pType: "Enum", column: "customer_tier", cType: "varchar(20)" },
  { property: "lifetimeValue", pType: "Decimal", column: "lifetime_value", cType: "numeric(15,2)" },
  { property: "createdAt", pType: "DateTime", column: "created_at", cType: "timestamp" },
  { property: "status", pType: "Enum", column: "status", cType: "varchar(20)" },
]

const unmappedProperties = [
  { property: "industry", pType: "String" },
  { property: "website", pType: "String" },
  { property: "annualRevenue", pType: "Decimal" },
  { property: "employeeCount", pType: "Integer" },
]

export default function Mapping() {
  return (
    <>
      <div className="card mb-4">
        <div className="card-body" style={{ padding: "var(--space-4)" }}>
          <div className="flex items-center gap-4">
            <div className="form-group" style={{ marginBottom: 0, flex: 1 }}>
              <label className="form-label" style={{ marginBottom: "var(--space-1)" }}>本体</label>
              <select className="form-select">
                <option>客户360</option>
                <option>供应商网络</option>
                <option>订单全景</option>
              </select>
            </div>
            <div className="form-group" style={{ marginBottom: 0, flex: 1 }}>
              <label className="form-label" style={{ marginBottom: "var(--space-1)" }}>对象类型</label>
              <select className="form-select">
                <option>Customer</option>
                <option>Order</option>
                <option>Product</option>
                <option>Address</option>
              </select>
            </div>
            <div className="form-group" style={{ marginBottom: 0, flex: 1 }}>
              <label className="form-label" style={{ marginBottom: "var(--space-1)" }}>数据源</label>
              <select className="form-select">
                <option>ERP-Production</option>
                <option>CRM-Main</option>
                <option>SCM-SupplyChain</option>
              </select>
            </div>
            <div className="form-group" style={{ marginBottom: 0, flex: 1 }}>
              <label className="form-label" style={{ marginBottom: "var(--space-1)" }}>数据表</label>
              <select className="form-select">
                <option>customers</option>
                <option>accounts</option>
                <option>client_info</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <div className="mapping-layout">
        {/* Left: Ontology Properties */}
        <div className="mapping-panel-side">
          <div className="mapping-panel-header">
            <span className="mph-title">本体属性</span>
            <span className="badge badge-info">{ontologyProperties.length}</span>
          </div>
          <div style={{ padding: "var(--space-3)" }}>
            <div className="search-input" style={{ width: "100%" }}>
              <span className="icon">⌕</span>
              <input type="text" placeholder="搜索属性..." style={{ width: "100%" }} />
            </div>
          </div>
          <div className="mapping-panel-body">
            {ontologyProperties.map((prop) => (
              <div key={prop.name} className="mapping-table-item">
                <div className="mti-name">{prop.name}</div>
                <div className="mti-meta">{prop.type}{prop.meta ? ` · ${prop.meta}` : ""}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Center: Mapping Grid */}
        <div className="mapping-center">
          <div className="mapping-center-header">
            <span className="font-semibold text-sm">字段映射</span>
            <div className="flex gap-2">
              <button className="btn btn-ghost btn-sm">清除未映射</button>
              <button className="btn btn-ghost btn-sm">智能推荐</button>
            </div>
          </div>
          <div className="mapping-columns">
            {mappedProperties.map((mp) => (
              <div key={mp.property} className="mapping-row mapped">
                <div className="mapping-col">
                  <div className="mc-name">{mp.property}</div>
                  <div className="mc-type">{mp.pType}</div>
                </div>
                <div className="mapping-connector connected">⇄</div>
                <div className="mapping-col">
                  <div className="mc-name">{mp.column}</div>
                  <div className="mc-type">{mp.cType}</div>
                </div>
              </div>
            ))}
            {unmappedProperties.map((mp) => (
              <div key={mp.property} className="mapping-row unmapped">
                <div className="mapping-col">
                  <div className="mc-name">{mp.property}</div>
                  <div className="mc-type">{mp.pType}</div>
                </div>
                <div className="mapping-connector">○</div>
                <div className="mapping-col" style={{ opacity: 0.4 }}>
                  <div className="mc-name">未映射</div>
                </div>
              </div>
            ))}
          </div>
          <div className="mapping-stats">
            <div className="mapping-stat">已映射: <span style={{ color: "var(--status-success)" }}>{mappedProperties.length}</span></div>
            <div className="mapping-stat">未映射: <span style={{ color: "var(--text-warning)" }}>{unmappedProperties.length}</span></div>
            <div className="mapping-stat">映射率: <span>{Math.round(mappedProperties.length / ontologyProperties.length * 100)}%</span></div>
          </div>
        </div>

        {/* Right: Source Columns */}
        <div className="mapping-panel-side">
          <div className="mapping-panel-header">
            <span className="mph-title">表字段</span>
            <span className="badge badge-info">{sourceColumns.length}</span>
          </div>
          <div style={{ padding: "var(--space-3)" }}>
            <div className="text-xs text-tertiary mb-2">CRM-Main.public.customers</div>
            <div className="search-input" style={{ width: "100%" }}>
              <span className="icon">⌕</span>
              <input type="text" placeholder="搜索字段..." style={{ width: "100%" }} />
            </div>
          </div>
          <div className="mapping-panel-body">
            {sourceColumns.map((col) => (
              <div key={col.name} className="mapping-table-item">
                <div className="mti-name">{col.name}</div>
                <div className="mti-meta">{col.type}{col.meta ? ` · ${col.meta}` : ""}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </>
  )
}
