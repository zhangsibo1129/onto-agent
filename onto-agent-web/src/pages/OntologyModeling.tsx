import { useState, useCallback, useEffect } from "react"
import { useNavigate, useParams } from "react-router-dom"
import { OntologyGraph } from "@/components/ontology"
import type { OntologyGraphData } from "@/components/ontology"
import { ontologyApi, type Ontology, type OntologyClass, type DataProperty, type ObjectProperty, type OntologyRelation } from "@/services/ontologyApi"
import "./OntologyModeling.css"

// ============================================================
// Main Component
// ============================================================

export default function OntologyModeling() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()

  const [ontology, setOntology] = useState<Ontology | null>(null)
  const [classes, setClasses] = useState<OntologyClass[]>([])
  const [dataProperties, setDataProperties] = useState<DataProperty[]>([])
  const [objectProperties, setObjectProperties] = useState<ObjectProperty[]>([])
  const [relations, setRelations] = useState<OntologyRelation[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedClassId, setSelectedClassId] = useState<string | null>(null)
  const [showAddModal, setShowAddModal] = useState<"class" | "property" | "relation" | null>(null)

  useEffect(() => {
    if (!id) return
    setLoading(true)
    ontologyApi.getDetail(id)
      .then((data) => {
        setOntology(data)
        setClasses(data.classes)
        setDataProperties(data.dataProperties)
        setObjectProperties(data.objectProperties)
        setRelations(data.relations)
      })
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [id])

  const handleClassSelect = useCallback((classId: string | null) => {
    setSelectedClassId(classId)
  }, [])

  const handleCreateClass = useCallback(async (name: string, displayName: string) => {
    if (!id) return
    const newClass = await ontologyApi.createClass(id, { name, displayName })
    setClasses(prev => [...prev, newClass])
    setShowAddModal(null)
  }, [id])

  const handleCreateDataProperty = useCallback(async (
    name: string,
    displayName: string,
    domainId: string,
    rangeType: string
  ) => {
    if (!id) return
    const newProp = await ontologyApi.createDataProperty(id, { name, displayName, domainId, rangeType })
    setDataProperties(prev => [...prev, newProp])
    setShowAddModal(null)
  }, [id])

  const handleCreateObjectProperty = useCallback(async (
    name: string,
    displayName: string,
    domainId: string,
    rangeId: string
  ) => {
    if (!id) return
    const newProp = await ontologyApi.createObjectProperty(id, { name, displayName, domainId, rangeId })
    setObjectProperties(prev => [...prev, newProp])
    setShowAddModal(null)
  }, [id])

  if (loading) {
    return (
      <div style={{ padding: 24, color: "#F1F5F9" }}>
        加载中...
      </div>
    )
  }

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
          <div className="ontology-stats">
            <div className="stat-group">
              <svg className="stat-icon" viewBox="0 0 20 20" width="14" height="14">
                <rect x="2" y="4" width="16" height="12" rx="3" fill="#6366F1" fillOpacity="0.2" stroke="#6366F1" strokeWidth="1.5" />
                <line x1="2" y1="9" x2="18" y2="9" stroke="#6366F1" strokeWidth="1" />
              </svg>
              <span className="stat-label">对象</span>
              <span className="stat-value">{classes.length}</span>
            </div>
            <div className="stat-group">
              <svg className="stat-icon" viewBox="0 0 16 16" width="14" height="14">
                <circle cx="8" cy="8" r="5" fill="#10B981" />
              </svg>
              <span className="stat-label">属性</span>
              <span className="stat-value">{dataProperties.length + objectProperties.length}</span>
            </div>
            <div className="stat-group">
              <svg className="stat-icon" viewBox="0 0 16 16" width="14" height="14">
                <line x1="1" y1="8" x2="10" y2="8" stroke="#F59E0B" strokeWidth="2" />
                <polygon points="8,4 14,8 8,12" fill="#F59E0B" />
              </svg>
              <span className="stat-label">关系</span>
              <span className="stat-value">{relations.length}</span>
            </div>
          </div>

          <div className="search-box">
            <svg className="search-icon" viewBox="0 0 20 20" width="14" height="14">
              <circle cx="8" cy="8" r="5" stroke="currentColor" strokeWidth="1.5" fill="none" />
              <line x1="12" y1="12" x2="16" y2="16" stroke="currentColor" strokeWidth="1.5" />
            </svg>
            <input type="text" placeholder="搜索..." className="search-input" />
          </div>
        </div>

        <div className="toolbar-actions">
          <div className="toolbar-right">
            <div className="btn-group-secondary">
              <button className="btn-toolbar">
                <svg viewBox="0 0 16 16" width="14" height="14">
                  <path d="M2 4h5l1 2h6v8H2V4z" fill="none" stroke="currentColor" strokeWidth="1.2" strokeLinejoin="round" />
                </svg>
                导入
              </button>
              <button className="btn-toolbar">
                <svg viewBox="0 0 16 16" width="14" height="14">
                  <path d="M2 10V12h12v-2" fill="none" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round" />
                  <path d="M8 2v8M5 5l3-3 3 3" fill="none" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
                导出
              </button>
            </div>
            <button className="btn-toolbar btn-toolbar-primary">
              <svg viewBox="0 0 16 16" width="14" height="14">
                <path d="M2 10V12h12v-2" fill="none" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round" />
                <path d="M4 10V6h4l2 2v2" fill="none" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round" />
                <path d="M8 2v6" fill="none" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" />
              </svg>
              保存
            </button>
          </div>
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
                      handleCreateClass(
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
                      handleCreateDataProperty(
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
                      handleCreateObjectProperty(
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
