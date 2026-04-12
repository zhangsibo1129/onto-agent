import { useState, useCallback, useEffect, useRef } from "react"
import { useNavigate, useParams } from "react-router-dom"
import { OntologyGraph, IndividualCard } from "@/components/ontology"
import type { OntologyGraphData } from "@/components/ontology"
import {
  ontologyApi,
  type Ontology,
  type OntologyClass,
  type DataProperty,
  type ObjectProperty,
  type Individual,
  type DataType,
} from "@/services/ontologyApi"
import "./OntologyModeling.css"

// 合并两种 ObjectProperty 类型
type ObjectPropertyWithAnyChar = ObjectProperty & { characteristics: string[] }
type EditingEntity = OntologyClass | DataProperty | ObjectPropertyWithAnyChar | Individual

// ============================================================
// Types
// ============================================================

interface OntologyRelation {
  id: string
  sourceId: string
  targetId: string
  propertyId: string
}

const CHARACTERISTIC_LABELS: Record<string, string> = {
  functional: "Func",
  inverseFunctional: "InvFunc",
  transitive: "Trans",
  symmetric: "Sym",
  asymmetric: "Asym",
  reflexive: "Refl",
  irreflexive: "Irrefl",
}

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
  const [loading, setLoading] = useState(true)
  const [selectedClassId, setSelectedClassId] = useState<string | null>(null)
  const [selectedRelation, setSelectedRelation] = useState<ObjectPropertyWithAnyChar | null>(null)
  const [showAddModal, setShowAddModal] = useState<"class" | "dataProperty" | "objectProperty" | null>(null)
  const [showEditModal, setShowEditModal] = useState<"class" | "dataProperty" | "objectProperty" | "individual" | null>(null)
  const [editingEntity, setEditingEntity] = useState<EditingEntity | null>(null)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<{ type: string; id: string; name: string } | null>(null)
  const [individuals, setIndividuals] = useState<Individual[]>([])
  const [individualsLoading, setIndividualsLoading] = useState(false)
  const [individualSearch, setIndividualSearch] = useState("")
  const [graphSearch, setGraphSearch] = useState("")

  // 添加表单状态
  const [addClassForm, setAddClassForm] = useState({ name: "", displayName: "", superClass: "", description: "" })
  const [addDataPropForm, setAddDataPropForm] = useState({ name: "", displayName: "", domainId: "", rangeType: "string" })
  const [addObjPropForm, setAddObjPropForm] = useState({ name: "", displayName: "", sourceId: "", targetId: "" })
  
  // 编辑表单状态
  const [editClassForm, setEditClassForm] = useState({ displayName: "", superClass: "", description: "" })
  const [editDataPropForm, setEditDataPropForm] = useState({ displayName: "", domainId: "", rangeType: "string" })
  const [editObjPropForm, setEditObjPropForm] = useState({ displayName: "", sourceId: "", targetId: "" })
  const [editIndForm, setEditIndForm] = useState({ displayName: "" })
  
  // 同步编辑数据到表单
  useEffect(() => {
    if (editingEntity) {
      if (showEditModal === "class") {
        const cls = editingEntity as OntologyClass
        setEditClassForm({
          displayName: cls.displayName || "",
          superClass: cls.superClasses?.[0] || "",
          description: cls.description || ""
        })
      } else if (showEditModal === "dataProperty") {
        const prop = editingEntity as DataProperty
        setEditDataPropForm({
          displayName: prop.displayName || "",
          domainId: prop.domainIds?.[0] || "",
          rangeType: prop.rangeType || "string"
        })
      } else if (showEditModal === "objectProperty") {
        const prop = editingEntity as ObjectProperty
        setEditObjPropForm({
          displayName: prop.displayName || "",
          sourceId: prop.domainIds?.[0] || "",
          targetId: prop.rangeIds?.[0] || ""
        })
      } else if (showEditModal === "individual") {
        const ind = editingEntity as Individual
        setEditIndForm({ displayName: ind.displayName || "" })
      }
    }
  }, [editingEntity, showEditModal])
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const [debouncedSearch, setDebouncedSearch] = useState("")

  useEffect(() => {
    if (debounceRef.current) {
      clearTimeout(debounceRef.current)
    }
    debounceRef.current = setTimeout(() => {
      setDebouncedSearch(individualSearch)
    }, 300)
    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current)
      }
    }
  }, [individualSearch])

  useEffect(() => {
    if (!id) return
    setLoading(true)
    ontologyApi
      .getDetail(id)
      .then((data) => {
        setOntology(data)
        setClasses(data.classes)
        setDataProperties(data.dataProperties)
        setObjectProperties(data.objectProperties)
      })
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [id])

  // 加载该类的实例（防抖）
  useEffect(() => {
    if (!id || !selectedClassId) {
      setIndividuals([])
      return
    }
    setIndividualsLoading(true)
    ontologyApi
      .getIndividuals(id, { classId: selectedClassId, search: debouncedSearch || undefined })
      .then(setIndividuals)
      .catch(console.error)
      .finally(() => setIndividualsLoading(false))
  }, [id, selectedClassId, debouncedSearch])

  const handleClassSelect = useCallback((classId: string | null) => {
    setSelectedClassId(classId)
  }, [])

  const handleLinkClick = useCallback((link: { propertyId: string } | null) => {
    if (!link) {
      setSelectedRelation(null)
      return
    }
    const propId = link.propertyId.split("|")[0]
    const prop = objectProperties.find(p => p.id === propId)
    setSelectedRelation(prop || null)
  }, [objectProperties])

  const handleCreateClass = useCallback(
    async (name: string, displayName: string, superClass?: string) => {
      if (!id) return
      const newClass = await ontologyApi.createClass(id, { 
        name, 
        displayName,
        superClasses: superClass ? [superClass] : [] 
      })
      setClasses((prev) => [...prev, newClass])
      setShowAddModal(null)
    },
    [id]
  )

  const handleCreateDataProperty = useCallback(
    async (name: string, displayName: string, domainId: string, rangeType: string) => {
      if (!id) return
      const newProp = await ontologyApi.createDataProperty(id, {
        name,
        displayName,
        domainIds: [domainId],
        rangeType: rangeType as DataProperty["rangeType"],
      })
      setDataProperties((prev) => [...prev, newProp])
      setShowAddModal(null)
    },
    [id]
  )

  const handleCreateObjectProperty = useCallback(
    async (name: string, displayName: string, domainId: string, rangeId: string) => {
      if (!id) return
      const newProp = await ontologyApi.createObjectProperty(id!, {
        name,
        displayName,
        domainIds: [domainId],
        rangeIds: [rangeId],
      })
      setObjectProperties((prev) => [...prev, newProp])
      setShowAddModal(null)
    },
    [id]
  )

  // ======== Update Handlers ========

  const handleUpdateClass = useCallback(
    async (classId: string, updates: { displayName?: string; description?: string; superClasses?: string[] }) => {
      if (!id) return
      const updated = await ontologyApi.updateClass(id, classId, updates)
      setClasses((prev) => prev.map((c) => (c.id === classId ? updated : c)))
      setShowEditModal(null)
      setEditingEntity(null)
    },
    [id]
  )

  const handleUpdateDataProperty = useCallback(
    async (propId: string, updates: { displayName?: string; domainIds?: string[]; rangeType?: DataType }) => {
      if (!id) return
      const updated = await ontologyApi.updateDataProperty(id, propId, updates)
      setDataProperties((prev) => prev.map((p) => (p.id === propId ? updated : p)))
      setShowEditModal(null)
      setEditingEntity(null)
    },
    [id]
  )

  const handleUpdateObjectProperty = useCallback(
    async (propId: string, updates: { displayName?: string; domainIds?: string[]; rangeIds?: string[] }) => {
      if (!id) return
      const updated = await ontologyApi.updateObjectProperty(id, propId, updates)
      setObjectProperties((prev) => prev.map((p) => (p.id === propId ? updated : p)))
      setShowEditModal(null)
      setEditingEntity(null)
    },
    [id]
  )

  const handleUpdateIndividual = useCallback(
    async (individualId: string, updates: { displayName?: string; propertyValues?: Record<string, unknown> }) => {
      if (!id) return
      const updated = await ontologyApi.updateIndividual(id, individualId, updates)
      setIndividuals((prev) => prev.map((i) => (i.id === individualId ? updated : i)))
      setShowEditModal(null)
      setEditingEntity(null)
    },
    [id]
  )

  // ======== Delete Handlers ========

  const handleDeleteClass = useCallback(
    async (classId: string) => {
      if (!id) return
      await ontologyApi.deleteClass(id, classId)
      setClasses((prev) => prev.filter((c) => c.id !== classId))
      if (selectedClassId === classId) setSelectedClassId(null)
      setShowDeleteConfirm(null)
    },
    [id, selectedClassId]
  )

  const handleDeleteDataProperty = useCallback(
    async (propId: string) => {
      if (!id) return
      await ontologyApi.deleteDataProperty(id, propId)
      setDataProperties((prev) => prev.filter((p) => p.id !== propId))
      setShowDeleteConfirm(null)
    },
    [id]
  )

  const handleDeleteObjectProperty = useCallback(
    async (propId: string) => {
      if (!id) return
      await ontologyApi.deleteObjectProperty(id, propId)
      setObjectProperties((prev) => prev.filter((p) => p.id !== propId))
      setShowDeleteConfirm(null)
    },
    [id]
  )

  const handleDeleteIndividual = useCallback(
    async (individualId: string) => {
      if (!id) return
      await ontologyApi.deleteIndividual(id, individualId)
      setIndividuals((prev) => prev.filter((i) => i.id !== individualId))
      setShowDeleteConfirm(null)
    },
    [id]
  )

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

  const relations: OntologyRelation[] = objectProperties.flatMap((op) =>
    (op.domainIds || []).flatMap((domainId) =>
      (op.rangeIds || []).map((rangeId) => ({
        id: `${op.id}-${domainId}-${rangeId}`,
        sourceId: domainId,
        targetId: rangeId,
        propertyId: op.id,
      }))
    )
  )

  const getPropertyById = (propId: string) =>
    [...dataProperties, ...objectProperties].find((p) => p.id === propId)

  const getClassById = (classId: string) => classes.find((c) => c.id === classId)

  const selectedClass = classes.find((c) => c.id === selectedClassId)
  const selectedClassDataProperties = dataProperties.filter((p) =>
    p.domainIds?.includes(selectedClassId || "") || false
  )
  const incomingRelations = relations.filter((r) => r.targetId === selectedClassId)
  const outgoingRelations = relations.filter((r) => r.sourceId === selectedClassId)

  const graphData: OntologyGraphData = {
    classes,
    dataProperties,
    objectProperties,
  }

  const DATA_TYPES = [
    "string",
    "boolean",
    "integer",
    "decimal",
    "float",
    "double",
    "dateTime",
    "date",
  ]

  const baseIri = ontology.baseIri

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
              <span className="stat-label">类</span>
              <span className="stat-value">{classes.length}</span>
            </div>
            <div className="stat-group">
              <svg className="stat-icon" viewBox="0 0 16 16" width="14" height="14">
                <circle cx="8" cy="8" r="5" fill="#10B981" />
              </svg>
              <span className="stat-label">数据属性</span>
              <span className="stat-value">{dataProperties.length}</span>
            </div>
            <div className="stat-group">
              <svg className="stat-icon" viewBox="0 0 16 16" width="14" height="14">
                <line x1="1" y1="8" x2="10" y2="8" stroke="#F59E0B" strokeWidth="2" />
                <polygon points="8,4 14,8 8,12" fill="#F59E0B" />
              </svg>
              <span className="stat-label">对象属性</span>
              <span className="stat-value">{objectProperties.length}</span>
            </div>
          </div>

          <div className="search-box">
            <svg className="search-icon" viewBox="0 0 20 20" width="14" height="14">
              <circle cx="8" cy="8" r="5" stroke="currentColor" strokeWidth="1.5" fill="none" />
              <line x1="12" y1="12" x2="16" y2="16" stroke="currentColor" strokeWidth="1.5" />
            </svg>
            <input 
              type="text" 
              placeholder="搜索类/属性..." 
              className="search-input"
              value={graphSearch}
              onChange={(e) => setGraphSearch(e.target.value)}
            />
          </div>
        </div>

        <div className="toolbar-actions">
          <div className="toolbar-right">
            <div className="btn-group-add">
              <button className="btn-toolbar" onClick={() => setShowAddModal("class")}>
                <svg viewBox="0 0 16 16" width="14" height="14">
                  <rect x="2" y="2" width="12" height="12" rx="2" fill="none" stroke="currentColor" strokeWidth="1.2" />
                  <line x1="8" y1="5" x2="8" y2="11" stroke="currentColor" strokeWidth="1.2" />
                  <line x1="5" y1="8" x2="11" y2="8" stroke="currentColor" strokeWidth="1.2" />
                </svg>
                添加类
              </button>
              <button className="btn-toolbar" onClick={() => setShowAddModal("dataProperty")}>
                <svg viewBox="0 0 16 16" width="14" height="14">
                  <circle cx="8" cy="8" r="5" fill="none" stroke="currentColor" strokeWidth="1.2" />
                  <line x1="8" y1="5" x2="8" y2="11" stroke="currentColor" strokeWidth="1.2" />
                </svg>
                添加属性
              </button>
              <button className="btn-toolbar" onClick={() => setShowAddModal("objectProperty")}>
                <svg viewBox="0 0 16 16" width="14" height="14">
                  <line x1="1" y1="8" x2="10" y2="8" stroke="currentColor" strokeWidth="1.2" />
                  <polygon points="8,5 12,8 8,11" fill="currentColor" />
                </svg>
                添加关系
              </button>
            </div>
            <div className="btn-group-secondary">
              <button className="btn-toolbar" onClick={() => alert("导入功能开发中")}>
                <svg viewBox="0 0 16 16" width="14" height="14">
                  <path d="M2 4h5l1 2h6v8H2V4z" fill="none" stroke="currentColor" strokeWidth="1.2" strokeLinejoin="round" />
                </svg>
                导入
              </button>
              <button className="btn-toolbar" onClick={() => alert("导出功能开发中")}>
                <svg viewBox="0 0 16 16" width="14" height="14">
                  <path d="M2 10V12h12v-2" fill="none" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round" />
                  <path d="M8 2v8M5 5l3-3 3 3" fill="none" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
                导出
              </button>
            </div>
            <button className="btn-toolbar btn-toolbar-primary" onClick={() => alert("保存功能开发中")}>
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
        <OntologyGraph data={graphData} selectedClassId={selectedClassId} onClassSelect={handleClassSelect} onLinkClick={handleLinkClick} />

        {/* ---- Relation Panel ---- */}
        <div className={`relation-panel ${selectedRelation ? "active" : ""}`}>
          {selectedRelation && (
            <>
              <div className="panel-header">
                <div className="panel-title">
                  <svg className="panel-icon" viewBox="0 0 16 16" width="16" height="16">
                    <line x1="1" y1="8" x2="10" y2="8" stroke="#F59E0B" strokeWidth="2" />
                    <polygon points="8,4 14,8 8,12" fill="#F59E0B" />
                  </svg>
                  <span className="panel-name">{selectedRelation.displayName || selectedRelation.name}</span>
                </div>
                <div className="panel-actions">
                  <button
                    className="btn-icon"
                    title="编辑关系"
                    onClick={() => {
                      setEditingEntity(selectedRelation)
                      setShowEditModal("objectProperty")
                    }}
                  >
                    <svg viewBox="0 0 24 24" width="14" height="14">
                      <path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z" fill="currentColor"/>
                    </svg>
                  </button>
                  <button
                    className="btn-icon btn-icon-danger"
                    title="删除关系"
                    onClick={() => setShowDeleteConfirm({ type: "objectProperty", id: selectedRelation.id, name: selectedRelation.displayName || selectedRelation.name })}
                  >
                    <svg viewBox="0 0 24 24" width="14" height="14">
                      <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z" fill="currentColor"/>
                    </svg>
                  </button>
                  <button className="panel-close" onClick={() => setSelectedRelation(null)}>
                    <svg viewBox="0 0 24 24" width="14" height="14">
                      <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                    </svg>
                  </button>
                </div>
              </div>
              <div className="panel-body">
                <div className="panel-section">
                  <div className="section-title">基本信息</div>
                  <div className="basic-info">
                    <div className="basic-info-row">
                      <span className="basic-label">URL</span>
                      <span className="basic-value url">{baseIri}{selectedRelation.name}</span>
                    </div>
                    {selectedRelation.description && (
                      <div className="basic-info-row">
                        <span className="basic-label">描述</span>
                        <span className="basic-value">{selectedRelation.description}</span>
                      </div>
                    )}
                  </div>
                </div>
                <div className="panel-section">
                  <div className="section-title">定义域</div>
                  <div className="basic-tags">
                    {(selectedRelation.domainIds || []).map((did) => (
                      <span key={did} className="rel-tag" onClick={() => setSelectedClassId(did)}>
                        {getClassById(did)?.displayName || did}
                      </span>
                    ))}
                  </div>
                </div>
                <div className="panel-section">
                  <div className="section-title">值域</div>
                  <div className="basic-tags">
                    {(selectedRelation.rangeIds || []).map((rid) => (
                      <span key={rid} className="rel-tag" onClick={() => setSelectedClassId(rid)}>
                        {getClassById(rid)?.displayName || rid}
                      </span>
                    ))}
                  </div>
                </div>
                {(selectedRelation.characteristics || []).length > 0 && (
                  <div className="panel-section">
                    <div className="section-title">特性</div>
                    <div className="basic-tags">
                      {(selectedRelation.characteristics || []).map((c) => (
                        <span key={c} className="char-badge">{CHARACTERISTIC_LABELS[c] || c}</span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </>
          )}
        </div>

        {/* ---- Entity Panel ---- */}
        <div className={`entity-panel ${selectedClass ? "active" : ""}`}>
          {selectedClass && (
            <>
              <div className="panel-header">
                <div className="panel-title">
                  <svg className="panel-icon" viewBox="0 0 24 24" width="16" height="16">
                    <circle cx="12" cy="12" r="10" fill="#6366F1" stroke="#1E293B" strokeWidth="2" />
                  </svg>
                  <span className="panel-name">{selectedClass.displayName || selectedClass.name}</span>
                </div>
                <div className="panel-actions">
                  <button 
                    className="btn-icon" 
                    title="编辑类"
                    onClick={() => {
                      setEditingEntity(selectedClass)
                      setShowEditModal("class")
                    }}
                  >
                    <svg viewBox="0 0 24 24" width="14" height="14">
                      <path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z" fill="currentColor"/>
                    </svg>
                  </button>
                  <button 
                    className="btn-icon btn-icon-danger" 
                    title="删除类"
                    onClick={() => setShowDeleteConfirm({ type: "class", id: selectedClass.id, name: selectedClass.displayName || selectedClass.name })}
                  >
                    <svg viewBox="0 0 24 24" width="14" height="14">
                      <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z" fill="currentColor"/>
                    </svg>
                  </button>
                  <button className="panel-close" onClick={() => setSelectedClassId(null)}>
                    <svg viewBox="0 0 24 24" width="14" height="14">
                      <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                    </svg>
                  </button>
                </div>
              </div>

              <div className="panel-body">
                {/* Basic Info */}
                <div className="panel-section">
                  <div className="section-title">基本信息</div>
                  <div className="basic-info">
                    <div className="basic-info-row">
                      <span className="basic-label">URL</span>
                      <span className="basic-value url">{baseIri}{selectedClass.name}</span>
                    </div>
                    {selectedClass.superClasses && selectedClass.superClasses.length > 0 && (
                      <div className="basic-info-row">
                        <span className="basic-label">父类</span>
                        <div className="basic-tags">
                          {selectedClass.superClasses.map((sc) => (
                            <span key={sc} className="rel-tag" onClick={() => setSelectedClassId(sc)}>
                              {getClassById(sc)?.displayName || sc}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                    {selectedClass.description && (
                      <div className="basic-info-row">
                        <span className="basic-label">描述</span>
                        <span className="basic-value">{selectedClass.description}</span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Data Properties */}
                <div className="panel-section">
                  <div className="section-title">
                    属性
                    <button 
                      className="btn-link btn-link-xs" 
                      onClick={() => setShowAddModal("dataProperty")}
                      title="添加属性"
                    >
                      + 添加
                    </button>
                  </div>
                  {selectedClassDataProperties.length > 0 ? (
                    <div className="props-list">
                      {selectedClassDataProperties.map((prop) => (
                        <div key={prop.id} className="prop-row">
                          <span className="prop-name">{prop.displayName || prop.name}</span>
                          <span className="prop-type">{prop.rangeType}</span>
                          <span className="prop-chars">
                            {(prop.characteristics || []).map((c) => (
                              <span key={c} className="char-badge">{CHARACTERISTIC_LABELS[c] || c}</span>
                            ))}
                          </span>
                          <div className="prop-actions">
                            <button 
                              className="btn-icon btn-icon-xs" 
                              title="编辑属性"
                              onClick={() => {
                                setEditingEntity(prop)
                                setShowEditModal("dataProperty")
                              }}
                            >
                              <svg viewBox="0 0 24 24" width="12" height="12">
                                <path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z" fill="currentColor"/>
                              </svg>
                            </button>
                            <button 
                              className="btn-icon btn-icon-xs btn-icon-danger" 
                              title="删除属性"
                              onClick={() => setShowDeleteConfirm({ type: "dataProperty", id: prop.id, name: prop.displayName || prop.name })}
                            >
                              <svg viewBox="0 0 24 24" width="12" height="12">
                                <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z" fill="currentColor"/>
                              </svg>
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="empty-text">暂无属性</div>
                  )}
                </div>

                {/* Relations */}
                <div className="panel-section">
                  <div className="section-title">关系</div>
                  {(incomingRelations.length > 0 || outgoingRelations.length > 0) ? (
                    <div className="relations-list">
                      {outgoingRelations.map((rel) => {
                        const prop = getPropertyById(rel.propertyId)
                        return (
                          <div key={rel.id} className="rel-item">
                            <span className="rel-col">{selectedClass.displayName || selectedClass.name}</span>
                            <span className="rel-col">
                              <span className="obj-prop-tag" onClick={() => prop && handleLinkClick({ propertyId: rel.propertyId })}>
                                {prop?.displayName || rel.propertyId}
                              </span>
                            </span>
                            <span className="rel-col">
                              <span className="rel-tag" onClick={() => setSelectedClassId(rel.targetId)}>
                                {getClassById(rel.targetId)?.displayName || rel.targetId}
                              </span>
                            </span>
                          </div>
                        )
                      })}
                      {incomingRelations.map((rel) => {
                        const prop = getPropertyById(rel.propertyId)
                        return (
                          <div key={rel.id} className="rel-item">
                            <span className="rel-col">
                              <span className="rel-tag" onClick={() => setSelectedClassId(rel.sourceId)}>
                                {getClassById(rel.sourceId)?.displayName || rel.sourceId}
                              </span>
                            </span>
                            <span className="rel-col">
                              <span className="obj-prop-tag" onClick={() => prop && handleLinkClick({ propertyId: rel.propertyId })}>
                                {prop?.displayName || rel.propertyId}
                              </span>
                            </span>
                            <span className="rel-col">{selectedClass.displayName || selectedClass.name}</span>
                          </div>
                        )
                      })}
                    </div>
                  ) : (
                    <div className="empty-text">暂无关系</div>
                  )}
                </div>

                {/* Axioms */}
                {(selectedClass.equivalentTo?.length > 0 || selectedClass.disjointWith?.length > 0) && (
                  <div className="panel-section">
                    <div className="section-title">公理</div>
                    <div className="axioms-list">
                      {selectedClass.equivalentTo?.length > 0 && (
                        <div className="axiom-row">
                          <span className="axiom-label">等价</span>
                          <div className="axiom-tags">
                            {selectedClass.equivalentTo.map((eq) => (
                              <span key={eq} className="link-tag" onClick={() => setSelectedClassId(eq)}>
                                {getClassById(eq)?.displayName || eq}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                      {selectedClass.disjointWith?.length > 0 && (
                        <div className="axiom-row">
                          <span className="axiom-label">不相交</span>
                          <div className="axiom-tags">
                            {selectedClass.disjointWith.map((dw) => (
                              <span key={dw} className="link-tag disjoint" onClick={() => setSelectedClassId(dw)}>
                                {getClassById(dw)?.displayName || dw}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}
                {/* 实例列表 - ABox */}
                <div className="panel-section">
                  <div className="section-title">
                    实例
                    <span className="instance-count">({individuals.length})</span>
                  </div>
                  
                  {/* 搜索框 */}
                  <div className="instance-search">
                    <input
                      type="text"
                      placeholder="搜索实例..."
                      value={individualSearch}
                      onChange={(e) => setIndividualSearch(e.target.value)}
                    />
                  </div>
                  
                  {/* 实例列表 */}
                  <div className="instance-list">
                    {individualsLoading ? (
                      <div className="loading-text">加载中...</div>
                    ) : individuals.length > 0 ? (
                      individuals.map((ind) => (
                        <IndividualCard
                          key={ind.id}
                          individual={ind}
                          dataProperties={dataProperties}
                          objectProperties={objectProperties}
                          onEdit={(ind) => {
                            setEditingEntity(ind)
                            setShowEditModal("individual")
                          }}
                          onDelete={(id) => setShowDeleteConfirm({ type: "individual", id, name: individuals.find(i => i.id === id)?.displayName || id })}
                          onNavigateToIndividual={(targetId) => {
                            alert(`跳转到实例: ${targetId} (功能开发中)`)
                          }}
                        />
                      ))
                    ) : (
                      <div className="empty-text">
                        {individualSearch ? "未找到匹配的实例" : "暂无实例"}
                      </div>
                    )}
                  </div>
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
                {showAddModal === "dataProperty" && "添加数据属性"}
                {showAddModal === "objectProperty" && "添加对象属性"}
              </h3>
              <button className="modal-close" onClick={() => setShowAddModal(null)}>
                ✕
              </button>
            </div>
            <div className="modal-body">
              {showAddModal === "class" && (
                <>
                  <div className="form-group">
                    <label className="form-label">英文名称 *</label>
                    <input 
                      type="text" 
                      className="form-input" 
                      placeholder="Product" 
                      value={addClassForm.name}
                      onChange={(e) => setAddClassForm({ ...addClassForm, name: e.target.value })}
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label">显示名称</label>
                    <input 
                      type="text" 
                      className="form-input" 
                      placeholder="产品" 
                      value={addClassForm.displayName}
                      onChange={(e) => setAddClassForm({ ...addClassForm, displayName: e.target.value })}
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label">父类</label>
                    <select 
                      className="form-select"
                      value={addClassForm.superClass}
                      onChange={(e) => setAddClassForm({ ...addClassForm, superClass: e.target.value })}
                    >
                      <option value="">无（顶层类）</option>
                      {classes.map((c) => (
                        <option key={c.id} value={c.id}>
                          {c.displayName || c.name}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label">描述</label>
                    <input 
                      type="text" 
                      className="form-input" 
                      placeholder="商品或服务实体" 
                      value={addClassForm.description}
                      onChange={(e) => setAddClassForm({ ...addClassForm, description: e.target.value })}
                    />
                  </div>
                </>
              )}

              {showAddModal === "dataProperty" && (
                <>
                  <div className="form-group">
                    <label className="form-label">英文名称 *</label>
                    <input 
                      type="text" 
                      className="form-input" 
                      placeholder="hasName" 
                      value={addDataPropForm.name}
                      onChange={(e) => setAddDataPropForm({ ...addDataPropForm, name: e.target.value })}
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label">显示名称</label>
                    <input 
                      type="text" 
                      className="form-input" 
                      placeholder="名称" 
                      value={addDataPropForm.displayName}
                      onChange={(e) => setAddDataPropForm({ ...addDataPropForm, displayName: e.target.value })}
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label">所属类 *</label>
                    <select 
                      className="form-select"
                      value={addDataPropForm.domainId}
                      onChange={(e) => setAddDataPropForm({ ...addDataPropForm, domainId: e.target.value })}
                    >
                      {classes.map((c) => (
                        <option key={c.id} value={c.id}>
                          {c.displayName || c.name}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label">数据类型</label>
                    <select 
                      className="form-select"
                      value={addDataPropForm.rangeType}
                      onChange={(e) => setAddDataPropForm({ ...addDataPropForm, rangeType: e.target.value })}
                    >
                      {DATA_TYPES.map((t) => (
                        <option key={t} value={t}>
                          {t}
                        </option>
                      ))}
                    </select>
                  </div>
                </>
              )}

              {showAddModal === "objectProperty" && (
                <>
                  <div className="form-group">
                    <label className="form-label">英文名称 *</label>
                    <input 
                      type="text" 
                      className="form-input" 
                      placeholder="belongsTo" 
                      value={addObjPropForm.name}
                      onChange={(e) => setAddObjPropForm({ ...addObjPropForm, name: e.target.value })}
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label">显示名称</label>
                    <input 
                      type="text" 
                      className="form-input" 
                      placeholder="属于" 
                      value={addObjPropForm.displayName}
                      onChange={(e) => setAddObjPropForm({ ...addObjPropForm, displayName: e.target.value })}
                    />
                  </div>
                  <div className="form-row">
                    <div className="form-group">
                      <label className="form-label">源类 *</label>
                      <select 
                        className="form-select"
                        value={addObjPropForm.sourceId}
                        onChange={(e) => setAddObjPropForm({ ...addObjPropForm, sourceId: e.target.value })}
                      >
                        {classes.map((c) => (
                          <option key={c.id} value={c.id}>
                            {c.displayName || c.name}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div className="form-group">
                      <label className="form-label">目标类 *</label>
                      <select 
                        className="form-select"
                        value={addObjPropForm.targetId}
                        onChange={(e) => setAddObjPropForm({ ...addObjPropForm, targetId: e.target.value })}
                      >
                        {classes.map((c) => (
                          <option key={c.id} value={c.id}>
                            {c.displayName || c.name}
                          </option>
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
                    if (addClassForm.name) {
                      handleCreateClass(addClassForm.name, addClassForm.displayName || addClassForm.name, addClassForm.superClass || undefined)
                      setAddClassForm({ name: "", displayName: "", superClass: "", description: "" })
                    }
                  } else if (showAddModal === "dataProperty") {
                    if (addDataPropForm.name && addDataPropForm.domainId) {
                      handleCreateDataProperty(
                        addDataPropForm.name,
                        addDataPropForm.displayName || addDataPropForm.name,
                        addDataPropForm.domainId,
                        addDataPropForm.rangeType
                      )
                      setAddDataPropForm({ name: "", displayName: "", domainId: "", rangeType: "string" })
                    }
                  } else if (showAddModal === "objectProperty") {
                    if (addObjPropForm.name && addObjPropForm.sourceId && addObjPropForm.targetId) {
                      handleCreateObjectProperty(
                        addObjPropForm.name,
                        addObjPropForm.displayName || addObjPropForm.name,
                        addObjPropForm.sourceId,
                        addObjPropForm.targetId
                      )
                      setAddObjPropForm({ name: "", displayName: "", sourceId: "", targetId: "" })
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

      {/* ---- Edit Modal ---- */}
      {showEditModal && editingEntity && (
        <div className="modal-overlay" onClick={() => { setShowEditModal(null); setEditingEntity(null) }}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">
                {showEditModal === "class" && "编辑类"}
                {showEditModal === "dataProperty" && "编辑数据属性"}
                {showEditModal === "objectProperty" && "编辑对象属性"}
                {showEditModal === "individual" && "编辑实例"}
              </h3>
              <button className="modal-close" onClick={() => { setShowEditModal(null); setEditingEntity(null) }}>
                ✕
              </button>
            </div>
            <div className="modal-body">
              {showEditModal === "class" && (
                <>
                  <div className="form-group">
                    <label className="form-label">显示名称</label>
                    <input 
                      type="text" 
                      className="form-input"
                      value={editClassForm.displayName}
                      onChange={(e) => setEditClassForm({ ...editClassForm, displayName: e.target.value })}
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label">父类</label>
                    <select 
                      className="form-select"
                      value={editClassForm.superClass}
                      onChange={(e) => setEditClassForm({ ...editClassForm, superClass: e.target.value })}
                    >
                      <option value="">无（顶层类）</option>
                      {classes.filter((c) => c.id !== (editingEntity as OntologyClass).id).map((c) => (
                        <option key={c.id} value={c.id}>
                          {c.displayName || c.name}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label">描述</label>
                    <input 
                      type="text" 
                      className="form-input"
                      value={editClassForm.description}
                      onChange={(e) => setEditClassForm({ ...editClassForm, description: e.target.value })}
                    />
                  </div>
                </>
              )}

              {showEditModal === "dataProperty" && (
                <>
                  <div className="form-group">
                    <label className="form-label">显示名称</label>
                    <input 
                      type="text" 
                      className="form-input"
                      value={editDataPropForm.displayName}
                      onChange={(e) => setEditDataPropForm({ ...editDataPropForm, displayName: e.target.value })}
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label">所属类</label>
                    <select 
                      className="form-select"
                      value={editDataPropForm.domainId}
                      onChange={(e) => setEditDataPropForm({ ...editDataPropForm, domainId: e.target.value })}
                    >
                      {classes.map((c) => (
                        <option key={c.id} value={c.id}>
                          {c.displayName || c.name}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label">数据类型</label>
                    <select 
                      className="form-select"
                      value={editDataPropForm.rangeType}
                      onChange={(e) => setEditDataPropForm({ ...editDataPropForm, rangeType: e.target.value })}
                    >
                      {DATA_TYPES.map((t) => (
                        <option key={t} value={t}>
                          {t}
                        </option>
                      ))}
                    </select>
                  </div>
                </>
              )}

              {showEditModal === "objectProperty" && (
                <>
                  <div className="form-group">
                    <label className="form-label">显示名称</label>
                    <input 
                      type="text" 
                      className="form-input"
                      value={editObjPropForm.displayName}
                      onChange={(e) => setEditObjPropForm({ ...editObjPropForm, displayName: e.target.value })}
                    />
                  </div>
                  <div className="form-row">
                    <div className="form-group">
                      <label className="form-label">源类</label>
                      <select 
                        className="form-select"
                        value={editObjPropForm.sourceId}
                        onChange={(e) => setEditObjPropForm({ ...editObjPropForm, sourceId: e.target.value })}
                      >
                        {classes.map((c) => (
                          <option key={c.id} value={c.id}>
                            {c.displayName || c.name}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div className="form-group">
                      <label className="form-label">目标类</label>
                      <select 
                        className="form-select"
                        value={editObjPropForm.targetId}
                        onChange={(e) => setEditObjPropForm({ ...editObjPropForm, targetId: e.target.value })}
                      >
                        {classes.map((c) => (
                          <option key={c.id} value={c.id}>
                            {c.displayName || c.name}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                </>
              )}

              {showEditModal === "individual" && (
                <>
                  <div className="form-group">
                    <label className="form-label">显示名称</label>
                    <input 
                      type="text" 
                      className="form-input"
                      value={editIndForm.displayName}
                      onChange={(e) => setEditIndForm({ ...editIndForm, displayName: e.target.value })}
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label">说明</label>
                    <p className="form-hint">实例属性值编辑功能正在开发中...</p>
                  </div>
                </>
              )}
            </div>
            <div className="modal-footer">
              <button className="btn btn-secondary" onClick={() => { setShowEditModal(null); setEditingEntity(null) }}>
                取消
              </button>
              <button
                className="btn btn-primary"
                onClick={() => {
                  if (showEditModal === "class") {
                    handleUpdateClass((editingEntity as OntologyClass).id, {
                      displayName: editClassForm.displayName || undefined,
                      description: editClassForm.description || undefined,
                      superClasses: editClassForm.superClass ? [editClassForm.superClass] : [],
                    })
                  } else if (showEditModal === "dataProperty") {
                    handleUpdateDataProperty((editingEntity as DataProperty).id, {
                      displayName: editDataPropForm.displayName || undefined,
                      domainIds: editDataPropForm.domainId ? [editDataPropForm.domainId] : [],
                      rangeType: editDataPropForm.rangeType as DataType,
                    })
                  } else if (showEditModal === "objectProperty") {
                    handleUpdateObjectProperty((editingEntity as ObjectProperty).id, {
                      displayName: editObjPropForm.displayName || undefined,
                      domainIds: editObjPropForm.sourceId ? [editObjPropForm.sourceId] : [],
                      rangeIds: editObjPropForm.targetId ? [editObjPropForm.targetId] : [],
                    })
                  } else if (showEditModal === "individual") {
                    handleUpdateIndividual((editingEntity as Individual).id, {
                      displayName: editIndForm.displayName || undefined,
                    })
                  }
                }}
              >
                保存
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ---- Delete Confirmation Modal ---- */}
      {showDeleteConfirm && (
        <div className="modal-overlay" onClick={() => setShowDeleteConfirm(null)}>
          <div className="modal modal-sm" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">确认删除</h3>
              <button className="modal-close" onClick={() => setShowDeleteConfirm(null)}>
                ✕
              </button>
            </div>
            <div className="modal-body">
              <p className="confirm-text">
                确定要删除 "{showDeleteConfirm.name}" 吗？
              </p>
              <p className="confirm-hint">
                {showDeleteConfirm.type === "class" && "删除类将同时删除其所有实例和子类关系。"}
                {showDeleteConfirm.type === "dataProperty" && "删除数据属性将移除所有实例上的相关属性值。"}
                {showDeleteConfirm.type === "objectProperty" && "删除对象属性将移除所有实例上的相关关系。"}
                {showDeleteConfirm.type === "individual" && "删除实例将无法恢复。"}
              </p>
            </div>
            <div className="modal-footer">
              <button className="btn btn-secondary" onClick={() => setShowDeleteConfirm(null)}>
                取消
              </button>
              <button
                className="btn btn-danger"
                onClick={() => {
                  if (showDeleteConfirm.type === "class") {
                    handleDeleteClass(showDeleteConfirm.id)
                  } else if (showDeleteConfirm.type === "dataProperty") {
                    handleDeleteDataProperty(showDeleteConfirm.id)
                  } else if (showDeleteConfirm.type === "objectProperty") {
                    handleDeleteObjectProperty(showDeleteConfirm.id)
                  } else if (showDeleteConfirm.type === "individual") {
                    handleDeleteIndividual(showDeleteConfirm.id)
                  }
                }}
              >
                删除
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
