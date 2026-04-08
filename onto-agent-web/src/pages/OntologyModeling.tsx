import { useState, useCallback } from "react"
import { useNavigate, useParams } from "react-router-dom"
import { OntologyGraph } from "@/components/ontology"
import type { OntologyClass, DataProperty, ObjectProperty, OntologyGraphData } from "@/components/ontology"
import { mockOntologies } from "@/data/mock"
import "./OntologyModeling.css"

// ============================================================
// Types (local aliases for the page)
// ============================================================

interface OntologyRelation {
  id: string
  sourceId: string
  targetId: string
  propertyId: string
}

// ============================================================
// Mock data — in production this comes from the API
// ============================================================

const MOCK_CLASSES: OntologyClass[] = [
  { id: "Product", name: "Product", displayName: "产品", description: "商品实体" },
  { id: "Order", name: "Order", displayName: "订单", description: "订单实体" },
  { id: "Customer", name: "Customer", displayName: "客户", description: "客户实体" },
  { id: "Supplier", name: "Supplier", displayName: "供应商", description: "供应商实体" },
  { id: "Shipment", name: "Shipment", displayName: "货运", description: "货运实体" },
]

const MOCK_DATA_PROPERTIES: DataProperty[] = [
  { id: "p1", name: "productName", displayName: "产品名称", domainId: "Product", rangeType: "String" },
  { id: "p2", name: "price", displayName: "价格", domainId: "Product", rangeType: "Float" },
  { id: "p3", name: "orderDate", displayName: "订单日期", domainId: "Order", rangeType: "Date" },
  { id: "p4", name: "totalAmount", displayName: "总金额", domainId: "Order", rangeType: "Float" },
  { id: "p5", name: "customerName", displayName: "客户名称", domainId: "Customer", rangeType: "String" },
  { id: "p6", name: "tier", displayName: "客户等级", domainId: "Customer", rangeType: "Enum" },
  { id: "p7", name: "supplierName", displayName: "供应商名称", domainId: "Supplier", rangeType: "String" },
  { id: "p8", name: "shipmentDate", displayName: "发货日期", domainId: "Shipment", rangeType: "Date" },
]

const MOCK_OBJECT_PROPERTIES: ObjectProperty[] = [
  { id: "op1", name: "hasProduct", displayName: "包含产品", domainId: "Order", rangeId: "Product" },
  { id: "op2", name: "placedBy", displayName: "下单", domainId: "Order", rangeId: "Customer" },
  { id: "op3", name: "suppliedBy", displayName: "供应方", domainId: "Product", rangeId: "Supplier" },
  { id: "op4", name: "ships", displayName: "发货运", domainId: "Order", rangeId: "Shipment" },
]

const MOCK_RELATIONS: OntologyRelation[] = [
  { id: "r1", sourceId: "Order", targetId: "Product", propertyId: "op1" },
  { id: "r2", sourceId: "Order", targetId: "Customer", propertyId: "op2" },
  { id: "r3", sourceId: "Product", targetId: "Supplier", propertyId: "op3" },
  { id: "r4", sourceId: "Order", targetId: "Shipment", propertyId: "op4" },
]

// ============================================================
// Main Component
// ============================================================

export default function OntologyModeling() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()

  const ontology = mockOntologies.find((o) => o.id === id)

  // ---- State ----
  const [classes, setClasses] = useState<OntologyClass[]>(MOCK_CLASSES)
  const [dataProperties, setDataProperties] = useState<DataProperty[]>(MOCK_DATA_PROPERTIES)
  const [objectProperties, setObjectProperties] = useState<ObjectProperty[]>(MOCK_OBJECT_PROPERTIES)
  const [relations] = useState<OntologyRelation[]>(MOCK_RELATIONS)

  const [selectedClassId, setSelectedClassId] = useState<string | null>(null)
  const [showAddModal, setShowAddModal] = useState<"class" | "property" | "relation" | null>(null)

  // ---- Handlers (hooks must be before conditionals) ----
  const handleClassSelect = useCallback((classId: string | null) => {
    setSelectedClassId(classId)
  }, [])

  const handleAddClass = useCallback((name: string, displayName: string) => {
    setClasses(prev => [...prev, { id: name, name, displayName }])
    setShowAddModal(null)
  }, [])

  const handleAddDataProperty = useCallback((
    name: string,
    displayName: string,
    domainId: string,
    rangeType: string
  ) => {
    setDataProperties(prev => [
      ...prev,
      { id: `dp-${Date.now()}`, name, displayName, domainId, rangeType },
    ])
    setShowAddModal(null)
  }, [])

  const handleAddObjectProperty = useCallback((
    name: string,
    displayName: string,
    domainId: string,
    rangeId: string
  ) => {
    setObjectProperties(prev => [
      ...prev,
      { id: `op-${Date.now()}`, name, displayName, domainId, rangeId },
    ])
    setShowAddModal(null)
  }, [])

  if (!ontology) {
    return (
      <div style={{ padding: 24, color: "#F1F5F9" }}>
        本体不存在 — <button onClick={() => navigate("/ontologies")}>返回列表</button>
      </div>
    )
  }

  // ---- Computed ----
  const getPropertyById = (propId: string) =>
    [...dataProperties, ...objectProperties].find((p) => p.id === propId)

  const getClassById = (classId: string) => classes.find((c) => c.id === classId)

  const selectedClass = classes.find((c) => c.id === selectedClassId)
  const selectedClassDataProperties = dataProperties.filter((p) => p.domainId === selectedClassId)
  const selectedClassObjectProperties = objectProperties.filter((p) => p.domainId === selectedClassId)
  const incomingRelations = relations.filter((r) => r.targetId === selectedClassId)
  const outgoingRelations = relations.filter((r) => r.sourceId === selectedClassId)

  // ---- Graph Data ----
  const graphData: OntologyGraphData = {
    classes,
    dataProperties,
    objectProperties,
  }

  return (
    <div className="ontology-canvas">
      {/* ---- Toolbar ---- */}
      <div className="ontology-toolbar">
        <div className="toolbar-left">
          <nav className="breadcrumb">
            <span className="breadcrumb-item" onClick={() => navigate("/ontologies")}>
              本体
            </span>
            <span className="breadcrumb-sep">/</span>
            <span className="breadcrumb-item active">{ontology.name}</span>
          </nav>
          <div className="ontology-stats">
            <span className="stat-item">
              <span className="stat-dot class"></span>
              类: {classes.length}
            </span>
            <span className="stat-item">
              <span className="stat-dot property"></span>
              属性: {dataProperties.length + objectProperties.length}
            </span>
            <span className="stat-item">
              <span className="stat-dot relation"></span>
              关系: {relations.length}
            </span>
          </div>
        </div>
        <div className="toolbar-actions">
          <button className="btn btn-ghost btn-sm" onClick={() => setShowAddModal("class")}>
            + 类
          </button>
          <button className="btn btn-ghost btn-sm" onClick={() => setShowAddModal("property")}>
            + 属性
          </button>
          <button className="btn btn-ghost btn-sm" onClick={() => setShowAddModal("relation")}>
            + 关系
          </button>
          <div className="toolbar-divider"></div>
          <button className="btn btn-secondary btn-sm">导入</button>
          <button className="btn btn-secondary btn-sm">导出</button>
          <button className="btn btn-primary btn-sm">保存</button>
        </div>
      </div>

      {/* ---- Graph + Panel ---- */}
      <div className="graph-wrapper">
        <OntologyGraph
          data={graphData}
          selectedClassId={selectedClassId}
          onClassSelect={handleClassSelect}
        />

        {/* ---- Entity Panel ---- */}
        <div className={`entity-panel ${selectedClass ? "active" : ""}`}>
          {selectedClass && (
            <>
              <div className="panel-header">
                <div className="panel-title">
                  <svg className="panel-icon" viewBox="0 0 24 24" width="20" height="20">
                    <circle cx="12" cy="12" r="10" fill="#6366F1" stroke="#1E293B" strokeWidth="2" />
                  </svg>
                  <span className="panel-name">{selectedClass.displayName}</span>
                </div>
                <button className="panel-close" onClick={() => setSelectedClassId(null)}>
                  <svg viewBox="0 0 24 24" width="16" height="16">
                    <path
                      d="M18 6L6 18M6 6l12 12"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                    />
                  </svg>
                </button>
              </div>

              <div className="panel-body">
                <div className="panel-section">
                  <div className="section-header">
                    <span className="section-icon">ℹ</span>
                    <span className="section-title">基本信息</span>
                  </div>
                  <div className="info-grid">
                    <div className="info-item">
                      <span className="info-label">英文名</span>
                      <span className="info-value mono">{selectedClass.name}</span>
                    </div>
                    <div className="info-item">
                      <span className="info-label">类型</span>
                      <span className="info-value">
                        <span className="type-badge class">owl:Class</span>
                      </span>
                    </div>
                    {selectedClass.description && (
                      <div className="info-item full">
                        <span className="info-label">描述</span>
                        <span className="info-value">{selectedClass.description}</span>
                      </div>
                    )}
                  </div>
                </div>

                {selectedClassDataProperties.length > 0 && (
                  <div className="panel-section">
                    <div className="section-header">
                      <span className="section-icon" style={{ color: "#10B981" }}>─</span>
                      <span className="section-title">数据属性</span>
                      <span className="section-count">{selectedClassDataProperties.length}</span>
                    </div>
                    <div className="property-list">
                      {selectedClassDataProperties.map((prop) => (
                        <div key={prop.id} className="property-item data">
                          <span className="prop-name">{prop.displayName}</span>
                          <span className="prop-type">{prop.rangeType}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {selectedClassObjectProperties.length > 0 && (
                  <div className="panel-section">
                    <div className="section-header">
                      <span className="section-icon" style={{ color: "#F59E0B" }}>●</span>
                      <span className="section-title">对象属性</span>
                      <span className="section-count">{selectedClassObjectProperties.length}</span>
                    </div>
                    <div className="property-list">
                      {selectedClassObjectProperties.map((prop) => (
                        <div key={prop.id} className="property-item object">
                          <span className="prop-name">{prop.displayName}</span>
                          <span className="prop-range">→ {getClassById(prop.rangeId)?.displayName}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {incomingRelations.length > 0 && (
                  <div className="panel-section">
                    <div className="section-header">
                      <span className="section-icon" style={{ color: "#6366F1" }}>←</span>
                      <span className="section-title">入向关系</span>
                      <span className="section-count">{incomingRelations.length}</span>
                    </div>
                    <div className="relation-list">
                      {incomingRelations.map((rel) => (
                        <div key={rel.id} className="relation-item">
                          <span className="rel-arrow">←</span>
                          <span className="rel-name">{getPropertyById(rel.propertyId)?.displayName}</span>
                          <span className="rel-from">← {getClassById(rel.sourceId)?.displayName}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {outgoingRelations.length > 0 && (
                  <div className="panel-section">
                    <div className="section-header">
                      <span className="section-icon" style={{ color: "#6366F1" }}>→</span>
                      <span className="section-title">出向关系</span>
                      <span className="section-count">{outgoingRelations.length}</span>
                    </div>
                    <div className="relation-list">
                      {outgoingRelations.map((rel) => (
                        <div key={rel.id} className="relation-item">
                          <span className="rel-arrow">→</span>
                          <span className="rel-name">{getPropertyById(rel.propertyId)?.displayName}</span>
                          <span className="rel-to">→ {getClassById(rel.targetId)?.displayName}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div className="panel-footer-actions">
                  <button
                    className="btn btn-ghost btn-sm"
                    onClick={() => setShowAddModal("property")}
                  >
                    + 数据属性
                  </button>
                  <button
                    className="btn btn-ghost btn-sm"
                    onClick={() => setShowAddModal("relation")}
                  >
                    + 对象属性
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      </div>

      {/* ---- Add Modal ---- */}
      {showAddModal && (
        <div className="modal-overlay" onClick={() => setShowAddModal(null)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">
                {showAddModal === "class" && "添加类"}
                {showAddModal === "property" && "添加数据属性"}
                {showAddModal === "relation" && "添加对象属性"}
              </h3>
              <button className="modal-close" onClick={() => setShowAddModal(null)}>✕</button>
            </div>
            <div className="modal-body">
              {showAddModal === "class" && (
                <>
                  <div className="form-group">
                    <label className="form-label">英文名称 *</label>
                    <input type="text" className="form-input" placeholder="Product" id="className" />
                  </div>
                  <div className="form-group">
                    <label className="form-label">显示名称</label>
                    <input type="text" className="form-input" placeholder="产品" id="classDisplayName" />
                  </div>
                </>
              )}

              {showAddModal === "property" && (
                <>
                  <div className="form-group">
                    <label className="form-label">英文名称 *</label>
                    <input type="text" className="form-input" placeholder="hasName" id="propName" />
                  </div>
                  <div className="form-group">
                    <label className="form-label">显示名称</label>
                    <input type="text" className="form-input" placeholder="名称" id="propDisplayName" />
                  </div>
                  <div className="form-group">
                    <label className="form-label">所属类 *</label>
                    <select className="form-select" id="propDomain">
                      {classes.map((c) => (
                        <option key={c.id} value={c.id}>{c.displayName}</option>
                      ))}
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label">数据类型</label>
                    <select className="form-select" id="propRange">
                      <option value="String">String</option>
                      <option value="Integer">Integer</option>
                      <option value="Float">Float</option>
                      <option value="Boolean">Boolean</option>
                      <option value="Date">Date</option>
                      <option value="DateTime">DateTime</option>
                      <option value="Enum">Enum</option>
                    </select>
                  </div>
                </>
              )}

              {showAddModal === "relation" && (
                <>
                  <div className="form-group">
                    <label className="form-label">英文名称 *</label>
                    <input type="text" className="form-input" placeholder="belongsTo" id="relName" />
                  </div>
                  <div className="form-group">
                    <label className="form-label">显示名称</label>
                    <input type="text" className="form-input" placeholder="属于" id="relDisplayName" />
                  </div>
                  <div className="form-row">
                    <div className="form-group">
                      <label className="form-label">源类 *</label>
                      <select className="form-select" id="relSource">
                        {classes.map((c) => (
                          <option key={c.id} value={c.id}>{c.displayName}</option>
                        ))}
                      </select>
                    </div>
                    <div className="form-group">
                      <label className="form-label">目标类 *</label>
                      <select className="form-select" id="relTarget">
                        {classes.map((c) => (
                          <option key={c.id} value={c.id}>{c.displayName}</option>
                        ))}
                      </select>
                    </div>
                  </div>
                </>
              )}
            </div>
            <div className="modal-footer">
              <button className="btn btn-secondary" onClick={() => setShowAddModal(null)}>
                取消
              </button>
              <button
                className="btn btn-primary"
                onClick={() => {
                  if (showAddModal === "class") {
                    const nameInput = document.getElementById("className") as HTMLInputElement
                    const displayInput = document.getElementById("classDisplayName") as HTMLInputElement
                    if (nameInput.value) {
                      handleAddClass(
                        nameInput.value,
                        displayInput.value || nameInput.value
                      )
                    }
                  } else if (showAddModal === "property") {
                    const nameInput = document.getElementById("propName") as HTMLInputElement
                    const displayInput = document.getElementById("propDisplayName") as HTMLInputElement
                    const domainSelect = document.getElementById("propDomain") as HTMLSelectElement
                    const rangeSelect = document.getElementById("propRange") as HTMLSelectElement
                    if (nameInput.value) {
                      handleAddDataProperty(
                        nameInput.value,
                        displayInput.value || nameInput.value,
                        domainSelect.value,
                        rangeSelect.value
                      )
                    }
                  } else if (showAddModal === "relation") {
                    const nameInput = document.getElementById("relName") as HTMLInputElement
                    const displayInput = document.getElementById("relDisplayName") as HTMLInputElement
                    const sourceSelect = document.getElementById("relSource") as HTMLSelectElement
                    const targetSelect = document.getElementById("relTarget") as HTMLSelectElement
                    if (nameInput.value) {
                      handleAddObjectProperty(
                        nameInput.value,
                        displayInput.value || nameInput.value,
                        sourceSelect.value,
                        targetSelect.value
                      )
                    }
                  }
                }}
              >
                添加
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
