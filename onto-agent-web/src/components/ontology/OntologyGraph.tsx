import { useRef, useCallback, useEffect, useState, useMemo } from "react"
import ForceGraph2D, { type ForceGraphMethods, type NodeObject, type LinkObject } from "react-force-graph-2d"
import * as d3 from "d3"

// ============================================================
// Types
// ============================================================

export interface OntologyClass {
  id: string
  name: string
  displayName: string
  description?: string
  subClassOf?: string // parent class id
}

export interface DataProperty {
  id: string
  name: string
  displayName: string
  domainId: string // class id
  rangeType: string // String, Integer, Float, Boolean, Date, etc.
  isRequired?: boolean
}

export interface ObjectProperty {
  id: string
  name: string
  displayName: string
  domainId: string // source class id
  rangeId: string // target class id
  cardinality?: "1:1" | "1:N" | "N:1" | "N:N"
}

export interface OntologyGraphData {
  classes: OntologyClass[]
  dataProperties: DataProperty[]
  objectProperties: ObjectProperty[]
}

// VOWL-inspired color scheme
const COLORS = {
  class: "#6366F1", // indigo - classes
  classHover: "#818CF8",
  classSelected: "#4F46E5",

  dataProp: "#10B981", // emerald - data properties
  objectProp: "#F59E0B", // amber - object properties
  inheritance: "#EC4899", // pink - subClassOf

  nodeBg: "rgba(30, 41, 59, 0.95)",
  nodeBorder: "rgba(255, 255, 255, 0.15)",
  nodeBorderSelected: "#6366F1",

  text: "#F1F5F9",
  textSecondary: "#94A3B8",
  textMuted: "#64748B",

  linkDefault: "#475569",
  linkDataProp: "#10B981",
  linkObjectProp: "#F59E0B",
  linkInheritance: "#EC4899",

  panelBg: "rgba(30, 41, 59, 0.98)",
  panelBorder: "rgba(255, 255, 255, 0.1)",

  graphBg: "#0A0E17",
  gridColor: "rgba(255, 255, 255, 0.03)",
}

// ============================================================
// Graph Node / Link Types (for force-graph)
// ============================================================

interface GraphNode extends NodeObject {
  id: string
  name: string
  displayName: string
  subClassOf?: string
  // computed
  dataProperties?: DataProperty[]
  objectProperties?: ObjectProperty[]
  incomingRelations?: ObjectProperty[]
  classCount?: number
  propertyCount?: number
}

interface GraphLink extends LinkObject {
  propertyId: string
  displayName: string
  type: "data" | "object" | "inheritance"
  sourceClass?: string
  targetClass?: string
}

// ============================================================
// Helpers
// ============================================================

function buildGraphData(data: OntologyGraphData): { nodes: GraphNode[]; links: GraphLink[] } {
  const { classes, dataProperties, objectProperties } = data

  // Group properties by class
  const dataPropsByClass = new Map<string, DataProperty[]>()
  const objPropsByClass = new Map<string, ObjectProperty[]>()
  const incomingByClass = new Map<string, ObjectProperty[]>()

  for (const dp of dataProperties) {
    const list = dataPropsByClass.get(dp.domainId) || []
    list.push(dp)
    dataPropsByClass.set(dp.domainId, list)
  }

  for (const op of objectProperties) {
    const outList = objPropsByClass.get(op.domainId) || []
    outList.push(op)
    objPropsByClass.set(op.domainId, outList)

    const inList = incomingByClass.get(op.rangeId) || []
    inList.push(op)
    incomingByClass.set(op.rangeId, inList)
  }

  const nodes: GraphNode[] = classes.map((cls) => ({
    id: cls.id,
    name: cls.name,
    displayName: cls.displayName || cls.name,
    subClassOf: cls.subClassOf,
    dataProperties: dataPropsByClass.get(cls.id) || [],
    objectProperties: objPropsByClass.get(cls.id) || [],
    incomingRelations: incomingByClass.get(cls.id) || [],
    classCount: classes.length,
    propertyCount: dataProperties.length + objectProperties.length,
  }))

  const links: GraphLink[] = []

  // Object properties as links
  for (const op of objectProperties) {
    links.push({
      source: op.domainId,
      target: op.rangeId,
      propertyId: op.id,
      displayName: op.displayName,
      type: "object",
      sourceClass: op.domainId,
      targetClass: op.rangeId,
    })
  }

  // Inheritance as links
  for (const cls of classes) {
    if (cls.subClassOf) {
      links.push({
        source: cls.id,
        target: cls.subClassOf,
        propertyId: `inherit-${cls.id}`,
        displayName: "rdfs:subClassOf",
        type: "inheritance",
        sourceClass: cls.id,
        targetClass: cls.subClassOf,
      })
    }
  }

  return { nodes, links }
}

// ============================================================
// Custom Node Canvas Rendering (VOWL-style compact card)
// ============================================================

function renderNodeCanvas(
  ctx: CanvasRenderingContext2D,
  node: GraphNode,
  _width: number,
  _height: number,
  transform: { x: number; y: number; k: number },
  selectedId: string | null,
  hoveredId: string | null
) {
  const isSelected = node.id === selectedId
  const isHovered = node.id === hoveredId
  const isHighlighted = isSelected || isHovered

  const nodeWidth = Math.max(140, node.displayName.length * 9 + 80)
  const headerHeight = 36
  const propLineHeight = 18
  const maxVisibleProps = 5
  const visibleDataProps = (node.dataProperties || []).slice(0, maxVisibleProps)
  const nodeHeight = headerHeight + visibleDataProps.length * propLineHeight + 16

  // Node position (center)
  const px = (node.x || 0) * transform.k + transform.x
  const py = (node.y || 0) * transform.k + transform.y

  ctx.save()

  // Glow effect for selected/hovered
  if (isHighlighted) {
    ctx.shadowColor = isSelected ? COLORS.classSelected : COLORS.classHover
    ctx.shadowBlur = 20 * transform.k
  } else {
    ctx.shadowColor = "rgba(0,0,0,0.5)"
    ctx.shadowBlur = 8 * transform.k
  }

  // Card background
  ctx.beginPath()
  const radius = 8 * transform.k
  _roundRect(ctx, px - nodeWidth / 2, py - nodeHeight / 2, nodeWidth, nodeHeight, radius)
  ctx.fillStyle = COLORS.nodeBg
  ctx.fill()

  // Border
  ctx.strokeStyle = isSelected ? COLORS.nodeBorderSelected : isHovered ? COLORS.classHover : COLORS.nodeBorder
  ctx.lineWidth = isHighlighted ? 2 * transform.k : 1 * transform.k
  ctx.stroke()

  ctx.shadowBlur = 0

  // Header background
  ctx.beginPath()
  _roundRectTop(ctx, px - nodeWidth / 2, py - nodeHeight / 2, nodeWidth, headerHeight, radius)
  ctx.fillStyle = isSelected
    ? "rgba(99, 102, 241, 0.3)"
    : isHovered
    ? "rgba(99, 102, 241, 0.15)"
    : "rgba(255, 255, 255, 0.05)"
  ctx.fill()

  // Header divider
  ctx.beginPath()
  ctx.moveTo(px - nodeWidth / 2 + radius, py - nodeHeight / 2 + headerHeight)
  ctx.lineTo(px + nodeWidth / 2 - radius, py - nodeHeight / 2 + headerHeight)
  ctx.strokeStyle = COLORS.nodeBorder
  ctx.lineWidth = 1 * transform.k
  ctx.stroke()

  // Class name
  const fontSize = Math.max(11, 13 * transform.k)
  ctx.font = `600 ${fontSize}px Inter, -apple-system, sans-serif`
  ctx.fillStyle = COLORS.text
  ctx.textAlign = "center"
  ctx.textBaseline = "middle"
  ctx.fillText(
    node.displayName.length > 16 ? node.displayName.slice(0, 14) + "…" : node.displayName,
    px,
    py - nodeHeight / 2 + headerHeight / 2
  )

  // Properties
  let propY = py - nodeHeight / 2 + headerHeight + 10 * transform.k

  // Data properties (green dot)
  for (const dp of visibleDataProps) {
    const propFontSize = Math.max(9, 11 * transform.k)
    ctx.font = `${propFontSize}px Inter, -apple-system, sans-serif`
    ctx.fillStyle = COLORS.dataProp
    ctx.textAlign = "left"
    ctx.textBaseline = "top"
    // dot
    ctx.beginPath()
    ctx.arc(px - nodeWidth / 2 + 10 * transform.k, propY + propFontSize / 2 - 1, 3 * transform.k, 0, Math.PI * 2)
    ctx.fill()
    // text: displayName (type)
    const text = `${dp.displayName} (${dp.rangeType})`
    ctx.fillStyle = COLORS.textSecondary
    ctx.fillText(text.length > 22 ? text.slice(0, 20) + "…" : text, px - nodeWidth / 2 + 20 * transform.k, propY)
    propY += propLineHeight * transform.k
  }

  // Property overflow indicator (only data properties shown in card)
  const totalDataProps = node.dataProperties?.length || 0
  const shownProps = visibleDataProps.length
  if (totalDataProps > shownProps) {
    const moreFontSize = Math.max(9, 10 * transform.k)
    ctx.font = `400 ${moreFontSize}px Inter, sans-serif`
    ctx.fillStyle = COLORS.textMuted
    ctx.textAlign = "center"
    ctx.fillText(`+${totalDataProps - shownProps} more…`, px, propY + 4 * transform.k)
  }

  ctx.restore()
}

function _roundRect(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  w: number,
  h: number,
  r: number
) {
  ctx.moveTo(x + r, y)
  ctx.lineTo(x + w - r, y)
  ctx.arcTo(x + w, y, x + w, y + r, r)
  ctx.lineTo(x + w, y + h - r)
  ctx.arcTo(x + w, y + h, x + w - r, y + h, r)
  ctx.lineTo(x + r, y + h)
  ctx.arcTo(x, y + h, x, y + h - r, r)
  ctx.lineTo(x, y + r)
  ctx.arcTo(x, y, x + r, y, r)
  ctx.closePath()
}

function _roundRectTop(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  w: number,
  h: number,
  r: number
) {
  ctx.moveTo(x + r, y)
  ctx.lineTo(x + w - r, y)
  ctx.arcTo(x + w, y, x + w, y + r, r)
  ctx.lineTo(x + w, y + h)
  ctx.lineTo(x, y + h)
  ctx.lineTo(x, y + r)
  ctx.arcTo(x, y, x + r, y, r)
  ctx.closePath()
}

// ============================================================
// Main Component
// ============================================================

interface OntologyGraphProps {
  data: OntologyGraphData
  selectedClassId?: string | null
  onClassSelect?: (classId: string | null) => void
  width?: number
  height?: number
}

export default function OntologyGraph({
  data,
  selectedClassId,
  onClassSelect,
  width = 800,
  height = 600,
}: OntologyGraphProps) {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const graphRef = useRef<ForceGraphMethods<GraphNode, GraphLink>>(null) as any
  const containerRef = useRef<HTMLDivElement>(null)
  const hoveredIdRef = useRef<string | null>(null) // ref only — avoids re-render → force jitter
  const [dimensions, setDimensions] = useState({ width, height })
  // Auto-fit on data change
  useEffect(() => {
    if (graphRef.current) {
      setTimeout(() => graphRef.current?.zoomToFit(600, 30), 300)
    }
  }, [data])

  // Configure d3 forces after graph mounts
  useEffect(() => {
    if (!graphRef.current) return
    // Increase repulsion and link distance for better spacing
    graphRef.current.d3Force("charge", d3.forceManyBody().strength(-800).distanceMax(500))
    graphRef.current.d3Force("link", d3.forceLink().distance(250).strength(0.3))
    graphRef.current.d3Force("center", d3.forceCenter(0, 0).strength(0.05))
    graphRef.current.d3ReheatSimulation()
  }, [])

  // Responsive resize
  useEffect(() => {
    const el = containerRef.current
    if (!el) return
    const ro = new ResizeObserver((entries) => {
      const { width: w, height: h } = entries[0].contentRect
      setDimensions({ width: w, height: h })
    })
    ro.observe(el)
    return () => ro.disconnect()
  }, [])

  const { nodes, links } = useMemo(() => buildGraphData(data), [data])

  const nodeCanvasObject = useCallback(
    (node: GraphNode, ctx: CanvasRenderingContext2D, globalScale: number) => {
      const transform = { x: 0, y: 0, k: globalScale }
      // Read from ref — never from state — so no re-render triggers
      renderNodeCanvas(ctx, node, dimensions.width, dimensions.height, transform, selectedClassId ?? null, hoveredIdRef.current)
    },
    [selectedClassId, dimensions]
  )

  const onNodeClick = useCallback(
    (node: NodeObject) => {
      onClassSelect?.((node as GraphNode).id)
    },
    [onClassSelect]
  )

  const onNodeHover = useCallback(
    (node: NodeObject | null) => {
      // Update ref only — no React state change, no re-render
      hoveredIdRef.current = node ? (node as GraphNode).id : null
      if (containerRef.current) {
        containerRef.current.style.cursor = node ? "pointer" : "grab"
      }
    },
    []
  )

  return (
    <div
      ref={containerRef}
      style={{
        position: "relative",
        width: "100%",
        height: "100%",
        background: COLORS.graphBg,
        borderRadius: "inherit",
        overflow: "hidden",
      }}
    >
      {/* Grid background */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          backgroundImage: `
            linear-gradient(${COLORS.gridColor} 1px, transparent 1px),
            linear-gradient(90deg, ${COLORS.gridColor} 1px, transparent 1px)
          `,
          backgroundSize: `${24}px ${24}px`,
          pointerEvents: "none",
        }}
      />

      {/* Force Graph */}
      <ForceGraph2D
        ref={graphRef}
        graphData={{ nodes, links }}
        width={dimensions.width}
        height={dimensions.height}
        backgroundColor="transparent"
        nodeCanvasObject={nodeCanvasObject as any}
        nodePointerAreaPaint={(node: any, color: string, ctx: CanvasRenderingContext2D) => {
          const n = node as GraphNode
          const w = Math.max(140, n.displayName.length * 9 + 80)
          const headerH = 36
          const propH = Math.min(5, n.dataProperties?.length || 0) * 18 + 16
          ctx.fillStyle = color
          ctx.beginPath()
          _roundRect(ctx, (n.x || 0) - w / 2, (n.y || 0) - (headerH + propH) / 2, w, headerH + propH, 8)
          ctx.fill()
        }}
        linkDirectionalArrowLength={6}
        linkDirectionalArrowRelPos={0.9}
        linkColor={() => "#F59E0B"}
        linkDirectionalArrowColor={() => "#F59E0B"}
        linkWidth={2}
        onNodeClick={onNodeClick}
        onNodeHover={onNodeHover}
        cooldownTicks={150}
        d3AlphaDecay={0.04}
        d3VelocityDecay={0.4}
        enableNodeDrag={true}
        enableZoomInteraction={true}
        enablePanInteraction={true}
        minZoom={0.15}
        maxZoom={5}
      />

      {/* Controls */}
      <div
        style={{
          position: "absolute",
          bottom: 16,
          right: 16,
          display: "flex",
          flexDirection: "column",
          gap: 8,
        }}
      >
        <button
          onClick={() => graphRef.current?.zoomToFit(600, 30)}
          title="Fit to view"
          style={{
            width: 36,
            height: 36,
            background: COLORS.panelBg,
            border: `1px solid ${COLORS.panelBorder}`,
            borderRadius: 8,
            color: COLORS.textSecondary,
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: 16,
            backdropFilter: "blur(12px)",
            transition: "all 0.15s",
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = "rgba(59, 130, 246, 0.2)"
            e.currentTarget.style.color = COLORS.text
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = COLORS.panelBg
            e.currentTarget.style.color = COLORS.textSecondary
          }}
        >
          ⊡
        </button>
        <button
          onClick={() => graphRef.current?.zoom(graphRef.current.zoom() * 1.3, 300)}
          title="Zoom in"
          style={{
            width: 36,
            height: 36,
            background: COLORS.panelBg,
            border: `1px solid ${COLORS.panelBorder}`,
            borderRadius: 8,
            color: COLORS.textSecondary,
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: 16,
            backdropFilter: "blur(12px)",
            transition: "all 0.15s",
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = "rgba(59, 130, 246, 0.2)"
            e.currentTarget.style.color = COLORS.text
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = COLORS.panelBg
            e.currentTarget.style.color = COLORS.textSecondary
          }}
        >
          +
        </button>
        <button
          onClick={() => graphRef.current?.zoom(graphRef.current.zoom() * 0.7, 300)}
          title="Zoom out"
          style={{
            width: 36,
            height: 36,
            background: COLORS.panelBg,
            border: `1px solid ${COLORS.panelBorder}`,
            borderRadius: 8,
            color: COLORS.textSecondary,
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: 16,
            backdropFilter: "blur(12px)",
            transition: "all 0.15s",
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = "rgba(59, 130, 246, 0.2)"
            e.currentTarget.style.color = COLORS.text
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = COLORS.panelBg
            e.currentTarget.style.color = COLORS.textSecondary
          }}
        >
          −
        </button>
      </div>

      {/* Legend */}
      <div
        style={{
          position: "absolute",
          bottom: 16,
          left: 16,
          background: COLORS.panelBg,
          border: `1px solid ${COLORS.panelBorder}`,
          borderRadius: 10,
          padding: "12px 16px",
          backdropFilter: "blur(12px)",
          minWidth: 160,
        }}
      >
        <div
          style={{
            fontSize: 10,
            fontWeight: 600,
            textTransform: "uppercase",
            letterSpacing: "0.5px",
            color: COLORS.textMuted,
            marginBottom: 8,
          }}
        >
          Legend
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
          <LegendItem color={COLORS.class} shape="circle" label="Class (owl:Class)" />
          <LegendItem color={COLORS.dataProp} shape="dashed" label="Data Property" />
          <LegendItem color={COLORS.objectProp} shape="arrow" label="Object Property" />
          <LegendItem color={COLORS.inheritance} shape="triangle" label="rdfs:subClassOf" />
        </div>
      </div>
    </div>
  )
}

function LegendItem({
  color,
  shape,
  label,
}: {
  color: string
  shape: "circle" | "dashed" | "arrow" | "triangle"
  label: string
}) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
      <svg width="24" height="16" style={{ flexShrink: 0 }}>
        {shape === "circle" && (
          <>
            <circle cx="12" cy="8" r="6" fill={color} stroke="rgba(255,255,255,0.2)" strokeWidth="1" />
          </>
        )}
        {shape === "dashed" && (
          <line x1="2" y1="8" x2="22" y2="8" stroke={color} strokeWidth="2" strokeDasharray="4 3" />
        )}
        {shape === "arrow" && (
          <>
            <line x1="2" y1="8" x2="18" y2="8" stroke={color} strokeWidth="2" />
            <polygon points="16,4 22,8 16,12" fill={color} />
          </>
        )}
        {shape === "triangle" && (
          <>
            <line x1="2" y1="12" x2="12" y2="4" stroke={color} strokeWidth="2" />
            <line x1="12" y1="4" x2="22" y2="12" stroke={color} strokeWidth="2" />
          </>
        )}
      </svg>
      <span style={{ fontSize: 11, color: COLORS.textSecondary }}>{label}</span>
    </div>
  )
}
