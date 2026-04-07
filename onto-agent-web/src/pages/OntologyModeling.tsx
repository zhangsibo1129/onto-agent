import { useState, useRef, useEffect } from "react"
import { useNavigate, useParams } from "react-router-dom"
import * as d3 from "d3"
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

interface GraphNode extends d3.SimulationNodeDatum {
  id: string
  name: string
  displayName: string
}

interface GraphLink extends d3.SimulationLinkDatum<GraphNode> {
  property: string
  displayName: string
  type: "data" | "object"
}

export default function OntologyModeling() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const svgRef = useRef<SVGSVGElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const simulationRef = useRef<d3.Simulation<GraphNode, GraphLink> | null>(null)
  const nodesRef = useRef<GraphNode[]>([])
  const linksRef = useRef<GraphLink[]>([])

  const [dimensions, setDimensions] = useState({ width: 800, height: 600 })
  const [, setRenderTick] = useState(0)

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
  const [hoveredClassId, setHoveredClassId] = useState<string | null>(null)
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

  useEffect(() => {
    const updateDimensions = () => {
      if (containerRef.current) {
        const rect = containerRef.current.getBoundingClientRect()
        setDimensions({ width: rect.width, height: rect.height })
      }
    }
    updateDimensions()
    window.addEventListener("resize", updateDimensions)
    return () => window.removeEventListener("resize", updateDimensions)
  }, [])

  useEffect(() => {
    const nodes: GraphNode[] = classes.map((c) => ({
      id: c.id,
      name: c.name,
      displayName: c.displayName,
    }))

    const links: GraphLink[] = relations.map((rel) => ({
      source: rel.sourceId,
      target: rel.targetId,
      property: rel.propertyId,
      displayName: getPropertyById(rel.propertyId)?.displayName || "",
      type: getPropertyById(rel.propertyId)?.type || "object",
    }))

    nodesRef.current = nodes
    linksRef.current = links

    if (simulationRef.current) {
      simulationRef.current.stop()
    }

    const simulation = d3.forceSimulation<GraphNode>(nodes)
      .force("link", d3.forceLink<GraphNode, GraphLink>(links).id((d) => d.id).distance(180).strength(0.5))
      .force("charge", d3.forceManyBody().strength(-600))
      .force("center", d3.forceCenter(dimensions.width / 2, dimensions.height / 2))
      .force("collision", d3.forceCollide().radius(80))
      .alphaDecay(0.02)

    simulation.on("tick", () => {
      setRenderTick((t) => t + 1)
    })

    simulationRef.current = simulation

    return () => {
      simulation.stop()
    }
  }, [dimensions, classes.length, relations.length])

  const getNodeColor = (nodeId: string) => {
    if (nodeId === selectedClassId) return "#818CF8"
    if (nodeId === hoveredClassId) return "#A78BFA"
    return "#ACF"
  }

  const handleNodeClick = (nodeId: string) => {
    setSelectedClassId(nodeId)
  }

  const handleNodeHover = (nodeId: string | null) => {
    setHoveredClassId(nodeId)
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

  const nodes = nodesRef.current
  const links = linksRef.current

  return (
    <div className="ontology-canvas">
      <div className="ontology-toolbar">
        <div className="toolbar-left">
          <nav className="breadcrumb">
            <span className="breadcrumb-item" onClick={() => navigate("/ontologies")}>本体</span>
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
              属性: {properties.length}
            </span>
            <span className="stat-item">
              <span className="stat-dot relation"></span>
              关系: {relations.length}
            </span>
          </div>
        </div>
        <div className="toolbar-actions">
          <button className="btn btn-ghost btn-sm" onClick={() => setShowAddModal("class")}>+ 类</button>
          <button className="btn btn-ghost btn-sm" onClick={() => setShowAddModal("property")}>+ 属性</button>
          <button className="btn btn-ghost btn-sm" onClick={() => setShowAddModal("relation")}>+ 关系</button>
          <div className="toolbar-divider"></div>
          <button className="btn btn-secondary btn-sm">导入</button>
          <button className="btn btn-secondary btn-sm">导出</button>
          <button className="btn btn-primary btn-sm">保存</button>
        </div>
      </div>

      <div className="graph-wrapper" ref={containerRef}>
        <svg ref={svgRef} className="ontology-svg" width={dimensions.width} height={dimensions.height}>
          <defs>
            <marker
              id="arrowhead"
              markerWidth="10"
              markerHeight="7"
              refX="9"
              refY="3.5"
              orient="auto"
            >
              <polygon points="0 0, 10 3.5, 0 7" fill="#64748B" />
            </marker>
            <marker
              id="arrowhead-selected"
              markerWidth="10"
              markerHeight="7"
              refX="9"
              refY="3.5"
              orient="auto"
            >
              <polygon points="0 0, 10 3.5, 0 7" fill="#818CF8" />
            </marker>
            <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
              <feDropShadow dx="0" dy="2" stdDeviation="3" floodOpacity="0.3"/>
            </filter>
          </defs>

          <g className="links">
            {links.map((link, i) => {
              const sourceNode = link.source as GraphNode
              const targetNode = link.target as GraphNode
              const sourceId = typeof sourceNode === "string" ? sourceNode : sourceNode.id
              const targetId = typeof targetNode === "string" ? targetNode : targetNode.id
              const isHighlighted = sourceId === selectedClassId || targetId === selectedClassId

              const sx = sourceNode.x || 0
              const sy = sourceNode.y || 0
              const tx = targetNode.x || 0
              const ty = targetNode.y || 0
              const dx = tx - sx
              const dy = ty - sy
              const dr = Math.sqrt(dx * dx + dy * dy) * 1.2
              const pathD = `M${sx},${sy}A${dr},${dr} 0 0,1 ${tx},${ty}`

              const midX = (sx + tx) / 2
              const midY = (sy + ty) / 2

              return (
                <g key={`link-${i}`} className={`link-group ${link.type}`}>
                  <path
                    d={pathD}
                    className={`link-path ${link.type === "data" ? "dashed" : ""} ${isHighlighted ? "highlighted" : ""}`}
                    markerEnd={link.type === "object" ? `url(#${isHighlighted ? "arrowhead-selected" : "arrowhead"})` : undefined}
                  />
                  <g className="link-label" transform={`translate(${midX}, ${midY})`}>
                    <rect
                      x="-30"
                      y="-10"
                      width="60"
                      height="20"
                      rx="4"
                      className={`link-label-bg ${isHighlighted ? "highlighted" : ""}`}
                    />
                    <text className={`link-label-text ${isHighlighted ? "highlighted" : ""}`}>
                      {link.displayName}
                    </text>
                  </g>
                </g>
              )
            })}
          </g>

          <g className="nodes">
            {nodes.map((node) => {
              const cx = node.x || 0
              const cy = node.y || 0
              const isSelected = node.id === selectedClassId
              const isHovered = node.id === hoveredClassId

              return (
                <g
                  key={node.id}
                  className={`node-group ${isSelected ? "selected" : ""} ${isHovered ? "hovered" : ""}`}
                  transform={`translate(${cx}, ${cy})`}
                  onClick={() => handleNodeClick(node.id)}
                  onMouseEnter={() => handleNodeHover(node.id)}
                  onMouseLeave={() => handleNodeHover(null)}
                >
                  {(isSelected || isHovered) && (
                    <circle
                      r="58"
                      className="node-halo"
                      fill="none"
                      stroke={isSelected ? "#818CF8" : "#A78BFA"}
                      strokeWidth="2"
                      strokeDasharray="4 2"
                    />
                  )}
                  <circle
                    r="50"
                    className="node-circle"
                    fill={getNodeColor(node.id)}
                    stroke={isSelected ? "#818CF8" : "#1E293B"}
                    strokeWidth={isSelected ? 3 : 2}
                    filter="url(#shadow)"
                  />
                  <text
                    className="node-label"
                    textAnchor="middle"
                    dominantBaseline="middle"
                    fill="#1E293B"
                    fontSize="13"
                    fontWeight="500"
                  >
                    {node.displayName.length > 10
                      ? node.displayName.substring(0, 8) + "..."
                      : node.displayName}
                  </text>
                  <title>{node.displayName}</title>
                </g>
              )
            })}
          </g>
        </svg>

        <div className="graph-legend-vowl">
          <div className="legend-title">图例</div>
          <div className="legend-item">
            <span className="legend-circle class"></span>
            <span>类 (OWL Class)</span>
          </div>
          <div className="legend-item">
            <span className="legend-line solid"></span>
            <span>对象属性</span>
          </div>
          <div className="legend-item">
            <span className="legend-line dashed"></span>
            <span>数据属性</span>
          </div>
        </div>

        <div className={`entity-panel ${selectedClass ? "active" : ""}`}>
          {selectedClass && (
            <>
              <div className="panel-header">
                <div className="panel-title">
                  <svg className="panel-icon" viewBox="0 0 24 24" width="20" height="20">
                    <circle cx="12" cy="12" r="10" fill="#ACF" stroke="#1E293B" strokeWidth="2"/>
                  </svg>
                  <span className="panel-name">{selectedClass.displayName}</span>
                </div>
                <button className="panel-close" onClick={() => setSelectedClassId(null)}>
                  <svg viewBox="0 0 24 24" width="16" height="16">
                    <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
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
                  </div>
                </div>

                {selectedClassDataProperties.length > 0 && (
                  <div className="panel-section">
                    <div className="section-header">
                      <span className="section-icon">─</span>
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
                      <span className="section-icon">●</span>
                      <span className="section-title">对象属性</span>
                      <span className="section-count">{selectedClassObjectProperties.length}</span>
                    </div>
                    <div className="property-list">
                      {selectedClassObjectProperties.map((prop) => (
                        <div key={prop.id} className="property-item object">
                          <span className="prop-name">{prop.displayName}</span>
                          <span className="prop-range">→ {getClassById(prop.rangeClassId || "")?.displayName}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {incomingRelations.length > 0 && (
                  <div className="panel-section">
                    <div className="section-header">
                      <span className="section-icon">←</span>
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
                      <span className="section-icon">→</span>
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
                  <button className="btn btn-ghost btn-sm" onClick={() => setShowAddModal("property")}>
                    + 数据属性
                  </button>
                  <button className="btn btn-ghost btn-sm" onClick={() => setShowAddModal("relation")}>
                    + 对象属性
                  </button>
                </div>
              </div>
            </>
          )}
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
