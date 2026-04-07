import { useState } from "react"
import { BackButton } from "../components/layout/Header"

interface ObjectType {
  id: string
  name: string
  icon: string
  color: string
  bgColor: string
  properties: number
  relations: number
  props: { name: string; type: string; isKey?: boolean }[]
  position?: { x: number; y: number }
}

interface Relationship {
  from: string
  to: string
  name: string
  color: string
}

const objectTypes: ObjectType[] = [
  {
    id: "customer",
    name: "Customer",
    icon: "C",
    color: "var(--brand-primary)",
    bgColor: "rgba(59, 130, 246, 0.1)",
    properties: 12,
    relations: 3,
    props: [
      { name: "customerId", type: "UUID", isKey: true },
      { name: "name", type: "String" },
      { name: "email", type: "String" },
      { name: "tier", type: "Enum" },
      { name: "lifetimeValue", type: "Decimal" },
    ],
    position: { x: 60, y: 120 },
  },
  {
    id: "order",
    name: "Order",
    icon: "O",
    color: "var(--brand-secondary)",
    bgColor: "rgba(139, 92, 246, 0.1)",
    properties: 10,
    relations: 4,
    props: [
      { name: "orderId", type: "UUID", isKey: true },
      { name: "orderDate", type: "DateTime" },
      { name: "totalAmount", type: "Decimal" },
      { name: "status", type: "Enum" },
    ],
    position: { x: 520, y: 100 },
  },
  {
    id: "product",
    name: "Product",
    icon: "P",
    color: "var(--brand-accent)",
    bgColor: "rgba(6, 182, 212, 0.1)",
    properties: 8,
    relations: 2,
    props: [
      { name: "productId", type: "UUID", isKey: true },
      { name: "name", type: "String" },
      { name: "price", type: "Decimal" },
    ],
    position: { x: 780, y: 80 },
  },
  {
    id: "address",
    name: "Address",
    icon: "A",
    color: "var(--status-success)",
    bgColor: "rgba(16, 185, 129, 0.1)",
    properties: 6,
    relations: 1,
    props: [
      { name: "addressId", type: "UUID", isKey: true },
      { name: "street", type: "String" },
      { name: "city", type: "String" },
    ],
    position: { x: 60, y: 380 },
  },
  {
    id: "contact",
    name: "Contact",
    icon: "C",
    color: "var(--status-warning)",
    bgColor: "rgba(245, 158, 11, 0.1)",
    properties: 7,
    relations: 2,
    props: [
      { name: "contactId", type: "UUID", isKey: true },
      { name: "phone", type: "String" },
      { name: "email", type: "String" },
    ],
    position: { x: 320, y: 400 },
  },
]

const relationships: Relationship[] = [
  { from: "customer", to: "order", name: "places", color: "var(--brand-accent)" },
  { from: "order", to: "customer", name: "has", color: "var(--brand-secondary)" },
  { from: "product", to: "order", name: "contains", color: "var(--status-success)" },
]

const selectedObjectProps = [
  { name: "customerId", type: "UUID", isKey: true },
  { name: "name", type: "String", isKey: false },
  { name: "email", type: "String", isKey: false },
  { name: "tier", type: "Enum", isKey: false },
  { name: "lifetimeValue", type: "Decimal", isKey: false },
]

const selectedObjectRelations = [
  { name: "places → Order", type: "1:N" },
  { name: "has → Address", type: "1:N" },
  { name: "hasPrimary → Contact", type: "1:1" },
]

export default function OntologyModeling() {
  const [selectedObject, setSelectedObject] = useState<string>("customer")
  const [zoom, setZoom] = useState(100)

  const currentObject = objectTypes.find((o) => o.id === selectedObject)

  return (
    <div className="page-with-back">
      <BackButton to="/ontologies" label="返回本体列表" />
      <div className="ontology-canvas">
      <div className="ontology-sidebar-panel">
        <div className="ontology-sidebar-header">
          <div className="flex items-center justify-between">
            <span>对象类型 ({objectTypes.length})</span>
            <button className="btn btn-primary btn-sm">+</button>
          </div>
        </div>
        <div style={{ padding: "var(--space-3)" }}>
          <div className="search-input" style={{ width: "100%" }}>
            <span className="icon">⌕</span>
            <input type="text" placeholder="搜索对象类型..." style={{ width: "100%" }} />
          </div>
        </div>
        <div className="ontology-list">
          {objectTypes.map((obj) => (
            <div
              key={obj.id}
              className={`ontology-list-item ${selectedObject === obj.id ? "active" : ""}`}
              onClick={() => setSelectedObject(obj.id)}
            >
              <div
                className="oli-icon"
                style={{ background: obj.bgColor, color: obj.color }}
              >
                {obj.icon}
              </div>
              <div className="oli-info">
                <div className="oli-name">{obj.name}</div>
                <div className="oli-count">{obj.properties} 属性 · {obj.relations} 关系</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="canvas-area">
        <div className="canvas-grid-bg"></div>
        <div className="canvas-toolbar">
          <button className="btn tooltip" title="选择">⊹</button>
          <button className="btn tooltip" title="添加对象">+</button>
          <button className="btn tooltip" title="添加关系">⇄</button>
          <div style={{ width: 1, background: "var(--border-primary)", margin: "0 var(--space-1)" }}></div>
          <button className="btn tooltip" title="撤销">↩</button>
          <button className="btn tooltip" title="重做">↪</button>
          <div style={{ width: 1, background: "var(--border-primary)", margin: "0 var(--space-1)" }}></div>
          <button className="btn tooltip" title="自动布局">⊞</button>
          <button className="btn tooltip" title="适应视图">⊡</button>
        </div>
        <div className="canvas-zoom">
          <button className="btn btn-ghost btn-sm" onClick={() => setZoom(Math.max(50, zoom - 10))}>−</button>
          <span>{zoom}%</span>
          <button className="btn btn-ghost btn-sm" onClick={() => setZoom(Math.min(200, zoom + 10))}>+</button>
        </div>

        <svg style={{ position: "absolute", inset: 0, width: "100%", height: "100%", pointerEvents: "none" }}>
          <defs>
            <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
              <polygon points="0 0, 10 3.5, 0 7" fill="var(--brand-accent)" />
            </marker>
          </defs>
          {relationships.map((rel, i) => {
            const fromObj = objectTypes.find((o) => o.id === rel.from)
            const toObj = objectTypes.find((o) => o.id === rel.to)
            if (!fromObj || !toObj || !fromObj.position || !toObj.position) return null
            const x1 = fromObj.position.x + 200
            const y1 = fromObj.position.y + 50
            const x2 = toObj.position.x
            const y2 = toObj.position.y + 50
            const midX = (x1 + x2) / 2
            const midY = (y1 + y2) / 2 - 20
            return (
              <g key={i}>
                <path
                  d={`M ${x1} ${y1} Q ${midX} ${midY} ${x2} ${y2}`}
                  stroke={rel.color}
                  strokeWidth="2"
                  fill="none"
                  markerEnd="url(#arrowhead)"
                />
                <text x={midX} y={midY} fill={rel.color} fontSize="11" textAnchor="middle">{rel.name}</text>
              </g>
            )
          })}
        </svg>

        {objectTypes.map((obj) => (
          <div
            key={obj.id}
            className={`canvas-node ${selectedObject === obj.id ? "selected" : ""}`}
            style={{
              left: obj.position?.x || 0,
              top: obj.position?.y || 0,
              transform: `scale(${zoom / 100})`,
              transformOrigin: "top left",
            }}
            onClick={() => setSelectedObject(obj.id)}
          >
            <div className="canvas-node-header" style={{ background: obj.bgColor }}>
              <div className="node-type-dot" style={{ background: obj.color }}></div>
              <span className="node-title">{obj.name}</span>
            </div>
            <div className="canvas-node-body">
              {obj.props.slice(0, 5).map((prop) => (
                <div key={prop.name} className="canvas-node-prop">
                  <span className="prop-key-icon">{prop.isKey ? "⚿" : ""}</span>
                  <span className="prop-key">{prop.name}</span>
                  <span className="prop-type">{prop.type}</span>
                </div>
              ))}
            </div>
            <div className="canvas-node-footer">{obj.properties} 属性 · {obj.relations} 关系</div>
          </div>
        ))}
      </div>

      <div className="property-panel">
        <div className="property-panel-header">
          <span className="font-semibold text-sm">属性面板</span>
          <button className="btn btn-ghost btn-sm">✕</button>
        </div>
        <div className="property-panel-body">
          <div className="property-section">
            <div className="property-section-title">基本信息</div>
            <div className="form-group">
              <label className="form-label">名称</label>
              <input type="text" className="form-input" value={currentObject?.name || ""} />
            </div>
            <div className="form-group">
              <label className="form-label">显示名称</label>
              <input type="text" className="form-input" value={currentObject?.name === "Customer" ? "客户" : ""} />
            </div>
            <div className="form-group">
              <label className="form-label">描述</label>
              <textarea className="form-textarea" rows={2} defaultValue="企业客户实体，包含客户基本信息、分层和价值数据" />
            </div>
          </div>
          <div className="property-section">
            <div className="property-section-title">属性 ({selectedObjectProps.length})</div>
            {selectedObjectProps.map((prop) => (
              <div key={prop.name} className="property-list-item">
                <span className="pli-icon">{prop.isKey ? "⚿" : "A"}</span>
                <div className="pli-info">
                  <div className="pli-name">{prop.name}</div>
                  <div className="pli-type">{prop.type} · {prop.isKey ? "主键" : "必填"}</div>
                </div>
              </div>
            ))}
            <button className="btn btn-ghost btn-sm w-full mt-2">+ 添加属性</button>
          </div>
          <div className="property-section">
            <div className="property-section-title">关系 ({selectedObjectRelations.length})</div>
            {selectedObjectRelations.map((rel, i) => (
              <div key={i} className="property-list-item">
                <span className="pli-icon" style={{ color: "var(--brand-accent)" }}>⇄</span>
                <div className="pli-info">
                  <div className="pli-name">{rel.name}</div>
                  <div className="pli-type">{rel.type}</div>
                </div>
              </div>
            ))}
            <button className="btn btn-ghost btn-sm w-full mt-2">+ 添加关系</button>
          </div>
          <div className="property-section">
            <div className="property-section-title">约束</div>
            <div className="property-row">
              <span className="pr-label">唯一键</span>
              <span className="pr-value mono">email</span>
            </div>
            <div className="property-row">
              <span className="pr-label">索引</span>
              <span className="pr-value">tier, lifetimeValue</span>
            </div>
          </div>
        </div>
      </div>
      </div>
  </div>
  )
}