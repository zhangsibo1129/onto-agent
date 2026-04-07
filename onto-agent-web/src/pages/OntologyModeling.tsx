import { useState, useRef, useCallback } from "react"
import { useNavigate, useParams } from "react-router-dom"
import ForceGraph2D from "react-force-graph-2d"
import { mockOntologies } from "@/data/mock"
import "./OntologyModeling.css"

interface OntologyClass {
  id: string
  name: string
  displayName: string
  description?: string
}

interface OntologyProperty {
  id: string
  name: string
  displayName: string
  type: "data" | "object"
  domainId: string
  rangeClassId?: string
  rangeType?: string
}

interface OntologyRelation {
  id: string
  sourceId: string
  targetId: string
  propertyId: string
}

interface GraphNode {
  id: string
  name: string
  displayName: string
  val: number
}

interface GraphLink {
  source: string
  target: string
  property: string
  displayName: string
}

export default function OntologyModeling() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const graphRef = useRef<any>(null)

  const ontology = mockOntologies.find((o) => o.id === id)

  const [classes, setClasses] = useState<OntologyClass[]>([
    { id: "Product", name: "Product", displayName: "产品" },
    { id: "Order", name: "Order", displayName: "订单" },
    { id: "Customer", name: "Customer", displayName: "客户" },
  ])

  const [properties, setProperties] = useState<OntologyProperty[]>([
    { id: "p1", name: "hasName", displayName: "名称", type: "data", domainId: "Product", rangeType: "String" },
    { id: "p2", name: "hasName", displayName: "名称", type: "data", domainId: "Order", rangeType: "String" },
    { id: "p3", name: "hasName", displayName: "名称", type: "data", domainId: "Customer", rangeType: "String" },
    { id: "p4", name: "hasPrice", displayName: "价格", type: "data", domainId: "Product", rangeType: "Float" },
    { id: "p5", name: "hasTotal", displayName: "总金额", type: "data", domainId: "Order", rangeType: "Float" },
    { id: "p6", name: "belongsTo", displayName: "属于", type: "object", domainId: "Order", rangeClassId: "Product" },
    { id: "p7", name: "placedBy", displayName: "下单", type: "object", domainId: "Order", rangeClassId: "Customer" },
  ])

  const [relations, setRelations] = useState<OntologyRelation[]>([
    { id: "r1", sourceId: "Order", targetId: "Product", propertyId: "p6" },
    { id: "r2", sourceId: "Order", targetId: "Customer", propertyId: "p7" },
  ])

  const [selectedClassId, setSelectedClassId] = useState<string | null>(null)
  const [showAddModal, setShowAddModal] = useState<"class" | "property" | "relation" | null>(null)

  if (!ontology) {
    return <div>本体不存在</div>
  }

  const getClassById = (classId: string) => classes.find((c) => c.id === classId)
  const getPropertyById = (propId: string) => properties.find((p) => p.id === propId)

  const selectedClass = classes.find((c) => c.id === selectedClassId)
  const selectedClassDataProperties = properties.filter((p) => p.domainId === selectedClassId && p.type === "data")
  const selectedClassObjectProperties = properties.filter((p) => p.domainId === selectedClassId && p.type === "object")
  const incomingRelations = relations.filter((r) => r.targetId === selectedClassId)
  const outgoingRelations = relations.filter((r) => r.sourceId === selectedClassId)

  const handleNodeClick = useCallback((node: any) => {
    setSelectedClassId(node.id)
  }, [])

  const graphData: { nodes: GraphNode[]; links: GraphLink[] } = {
    nodes: classes.map((c) => ({
      id: c.id,
      name: c.name,
      displayName: c.displayName,
      val: 1.5,
    })),
    links: relations.map((rel) => ({
      source: rel.sourceId,
      target: rel.targetId,
      property: rel.propertyId,
      displayName: getPropertyById(rel.propertyId)?.displayName || "",
    })),
  }

  const handleAddClass = (name: string, displayName: string) => {
    const newClass: OntologyClass = { id: name, name, displayName }
    setClasses([...classes, newClass])
    setShowAddModal(null)
  }

  const handleAddProperty = (
    name: string,
    displayName: string,
    type: "data" | "object",
    domainId: string,
    rangeType?: string,
    rangeClassId?: string
  ) => {
    const newProperty: OntologyProperty = {
      id: `p${Date.now()}`,
      name,
      displayName,
      type,
      domainId,
      rangeType,
      rangeClassId,
    }
    setProperties([...properties, newProperty])
    setShowAddModal(null)
  }

  const handleAddRelation = (
    sourceId: string,
    targetId: string,
    propertyName: string,
    propertyDisplayName: string
  ) => {
    const newProperty: OntologyProperty = {
      id: `p${Date.now()}`,
      name: propertyName,
      displayName: propertyDisplayName,
      type: "object",
      domainId: sourceId,
      rangeClassId: targetId,
    }
    const newRelation: OntologyRelation = {
      id: `r${Date.now()}`,
      sourceId,
      targetId,
      propertyId: newProperty.id,
    }
    setProperties([...properties, newProperty])
    setRelations([...relations, newRelation])
    setShowAddModal(null)
  }

  return (
    <div className="ontology-canvas">
      <div className="ontology-toolbar">
        <nav className="breadcrumb">
          <span className="breadcrumb-item" onClick={() => navigate("/ontologies")}>本体</span>
          <span className="breadcrumb-sep">/</span>
          <span className="breadcrumb-item active">{ontology.name}</span>
        </nav>
        <div className="toolbar-actions">
          <button className="btn btn-ghost btn-sm" onClick={() => setShowAddModal("class")}>+ 添加类</button>
          <button className="btn btn-secondary btn-sm">导入</button>
          <button className="btn btn-secondary btn-sm">导出</button>
          <button className="btn btn-primary btn-sm">保存</button>
        </div>
      </div>

      <div className="graph-wrapper">
        <ForceGraph2D
          ref={graphRef}
          graphData={graphData}
          nodeLabel="displayName"
          nodeColor={(node: any) => node.id === selectedClassId ? "#818CF8" : "#4F46E5"}
          nodeRelSize={8}
          linkColor={() => "#475569"}
          linkWidth={2}
          linkLabel="displayName"
          linkDirectionalArrowLength={6}
          linkDirectionalArrowRelPos={0.9}
          onNodeClick={handleNodeClick}
          backgroundColor="#0F172A"
          d3AlphaDecay={0.02}
          d3VelocityDecay={0.3}
          warmupTicks={100}
          cooldownTicks={200}
          nodeCanvasObject={(node: any, ctx: any, globalScale: number) => {
            const label = (node as any).displayName
            const fontSize = 12 / globalScale
            ctx.font = `${fontSize}px Inter, sans-serif`
            ctx.textAlign = "center"
            ctx.textBaseline = "middle"
            ctx.fillStyle = node.id === selectedClassId ? "#818CF8" : "#E2E8F0"
            ctx.fillText(label, (node as any).x, (node as any).y + 16 / globalScale)
          }}
        />

        {selectedClass && (
          <div className="entity-panel">
            <div className="panel-header">
              <div className="panel-title">
                <span className="panel-icon">◉</span>
                <span className="panel-name">{selectedClass.displayName}</span>
              </div>
              <button className="panel-close" onClick={() => setSelectedClassId(null)}>✕</button>
            </div>

            <div className="panel-body">
              <div className="panel-section">
                <div className="section-label">基本信息</div>
                <div className="info-row">
                  <span className="info-key">英文名</span>
                  <span className="info-value">{selectedClass.name}</span>
                </div>
              </div>

              {selectedClassDataProperties.length > 0 && (
                <div className="panel-section">
                  <div className="section-label">数据属性</div>
                  {selectedClassDataProperties.map((prop) => (
                    <div key={prop.id} className="property-row">
                      <span className="prop-badge data">String</span>
                      <span className="prop-name">{prop.displayName}</span>
                    </div>
                  ))}
                </div>
              )}

              {selectedClassObjectProperties.length > 0 && (
                <div className="panel-section">
                  <div className="section-label">对象属性</div>
                  {selectedClassObjectProperties.map((prop) => (
                    <div key={prop.id} className="property-row">
                      <span className="prop-badge object">→</span>
                      <span className="prop-name">{prop.displayName}</span>
                      <span className="prop-range">{getClassById(prop.rangeClassId || "")?.displayName}</span>
                    </div>
                  ))}
                </div>
              )}

              {incomingRelations.length > 0 && (
                <div className="panel-section">
                  <div className="section-label">入向关系</div>
                  {incomingRelations.map((rel) => (
                    <div key={rel.id} className="relation-row">
                      <span className="rel-arrow">←</span>
                      <span className="rel-name">{getPropertyById(rel.propertyId)?.displayName}</span>
                      <span className="rel-from">{getClassById(rel.sourceId)?.displayName}</span>
                    </div>
                  ))}
                </div>
              )}

              {outgoingRelations.length > 0 && (
                <div className="panel-section">
                  <div className="section-label">出向关系</div>
                  {outgoingRelations.map((rel) => (
                    <div key={rel.id} className="relation-row">
                      <span className="rel-arrow">→</span>
                      <span className="rel-name">{getPropertyById(rel.propertyId)?.displayName}</span>
                      <span className="rel-to">{getClassById(rel.targetId)?.displayName}</span>
                    </div>
                  ))}
                </div>
              )}

              <div className="panel-actions">
                <button className="btn btn-ghost btn-sm" onClick={() => setShowAddModal("property")}>+ 数据属性</button>
                <button className="btn btn-ghost btn-sm" onClick={() => setShowAddModal("relation")}>+ 对象属性</button>
              </div>
            </div>
          </div>
        )}

        <div className="graph-hint">
          <span>点击节点查看详情 · 类: {classes.length} · 关系: {relations.length}</span>
        </div>

        <div className="ontology-badge">
          <span className="badge-name">{ontology.name}</span>
          <span className={`badge-status ${ontology.status}`}>
            {ontology.status === "published" ? "●" : "○"}{ontology.status === "published" ? "已发布" : "草稿"}
          </span>
        </div>
      </div>

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
                    </select>
                  </div>
                </>
              )}
              {showAddModal === "relation" && (
                <>
                  <div className="form-group">
                    <label className="form-label">关系名称 *</label>
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
              <button className="btn btn-secondary" onClick={() => setShowAddModal(null)}>取消</button>
              <button
                className="btn btn-primary"
                onClick={() => {
                  if (showAddModal === "class") {
                    const nameInput = document.getElementById("className") as HTMLInputElement
                    const displayNameInput = document.getElementById("classDisplayName") as HTMLInputElement
                    if (nameInput.value) {
                      handleAddClass(nameInput.value, displayNameInput.value || nameInput.value)
                    }
                  } else if (showAddModal === "property") {
                    const nameInput = document.getElementById("propName") as HTMLInputElement
                    const displayNameInput = document.getElementById("propDisplayName") as HTMLInputElement
                    const domainSelect = document.getElementById("propDomain") as HTMLSelectElement
                    const rangeSelect = document.getElementById("propRange") as HTMLSelectElement
                    if (nameInput.value) {
                      handleAddProperty(nameInput.value, displayNameInput.value || nameInput.value, "data", domainSelect.value, rangeSelect.value)
                    }
                  } else if (showAddModal === "relation") {
                    const nameInput = document.getElementById("relName") as HTMLInputElement
                    const displayNameInput = document.getElementById("relDisplayName") as HTMLInputElement
                    const sourceSelect = document.getElementById("relSource") as HTMLSelectElement
                    const targetSelect = document.getElementById("relTarget") as HTMLSelectElement
                    if (nameInput.value) {
                      handleAddRelation(sourceSelect.value, targetSelect.value, nameInput.value, displayNameInput.value || nameInput.value)
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
