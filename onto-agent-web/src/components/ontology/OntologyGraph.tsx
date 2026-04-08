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
  subClassOf?: string
}

export interface DataProperty {
  id: string
  name: string
  displayName: string
  domainId: string
  rangeType: string
  isRequired?: boolean
}

export interface ObjectProperty {
  id: string
  name: string
  displayName: string
  domainId: string
  rangeId: string
  cardinality?: "1:1" | "1:N" | "N:1" | "N:N"
}

export interface OntologyGraphData {
  classes: OntologyClass[]
  dataProperties: DataProperty[]
  objectProperties: ObjectProperty[]
}

const COLORS = {
  class: "#6366F1",
  classHover: "#818CF8",
  classSelected: "#4F46E5",

  dataProp: "#10B981",
  objectProp: "#F59E0B",
  inheritance: "#EC4899",

  nodeBg: "rgba(30, 41, 59, 0.95)",
  nodeBorder: "rgba(255, 255, 255, 0.15)",
  nodeBorderSelected: "#6366F1",

  text: "#F1F5F9",
  textSecondary: "#94A3B8",
  textMuted: "#64748B",

  linkDefault: "#475569",

  panelBg: "rgba(30, 41, 59, 0.98)",
  panelBorder: "rgba(255, 255, 255, 0.1)",

  graphBg: "#0A0E17",
  gridColor: "rgba(255, 255, 255, 0.03)",
}

interface GraphNode extends NodeObject {
  id: string
  name: string
  displayName: string
  subClassOf?: string
  dataProperties?: DataProperty[]
  objectProperties?: ObjectProperty[]
  incomingRelations?: ObjectProperty[]
  classCount?: number
  propertyCount?: number
}

interface GraphLink extends LinkObject {
  propertyId: string
  displayName: string
  type: "data" | "object" | "bidirectional" | "inheritance"
  sourceClass?: string
  targetClass?: string
}

// ============================================================
// Graph Data Builder
// ============================================================

function buildGraphData(data: OntologyGraphData): { nodes: GraphNode[]; links: GraphLink[] } {
  const { classes, dataProperties, objectProperties } = data

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

  for (const op of objectProperties) {
    const reverseOp = objectProperties.find(p => p.domainId === op.rangeId && p.rangeId === op.domainId)
    if (reverseOp && op.id < reverseOp.id) continue

    if (reverseOp) {
      links.push({
        source: op.domainId,
        target: op.rangeId,
        propertyId: `${op.id}|${reverseOp.id}`,
        displayName: `${op.displayName}|${reverseOp.displayName}`,
        type: "bidirectional",
        sourceClass: op.domainId,
        targetClass: op.rangeId,
      })
    } else {
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
  }

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
// Node Dimensions (in screen pixels, scaled by globalScale)
// ============================================================

interface NodeDims {
  w: number
  h: number
  hw: number
  hh: number
}

function getNodeDims(node: GraphNode, globalScale: number): NodeDims {
  const baseWidth = Math.max(80, node.displayName.length * 5 + 40)
  const headerH = 20
  const propLineH = 10
  const maxVisibleProps = 5
  const visibleCount = Math.min(maxVisibleProps, node.dataProperties?.length || 0)
  const baseHeight = headerH + visibleCount * propLineH + 8

  return {
    w: baseWidth * globalScale,
    h: baseHeight * globalScale,
    hw: baseWidth * globalScale / 2,
    hh: baseHeight * globalScale / 2,
  }
}

// ============================================================
// Edge Intersection Math
// ============================================================

function lineRectIntersect(
  sx: number, sy: number,
  tx: number, ty: number,
  rcx: number, rcy: number,
  hw: number, hh: number
): [number, number] {
  const dx = tx - sx
  const dy = ty - sy

  let tmin = 0
  let tmax = 1

  const rcLeft = rcx - hw
  const rcRight = rcx + hw
  const rcTop = rcy - hh
  const rcBottom = rcy + hh

  if (dx !== 0) {
    const t1 = (rcLeft - sx) / dx
    const t2 = (rcRight - sx) / dx
    tmin = Math.max(tmin, Math.min(t1, t2))
    tmax = Math.min(tmax, Math.max(t1, t2))
  }

  if (dy !== 0) {
    const t1 = (rcTop - sy) / dy
    const t2 = (rcBottom - sy) / dy
    tmin = Math.max(tmin, Math.min(t1, t2))
    tmax = Math.min(tmax, Math.max(t1, t2))
  }

  if (tmin > tmax || tmin < 0 || tmin > 1) {
    return [rcx, rcy]
  }

  return [sx + dx * tmin, sy + dy * tmin]
}

// ============================================================
// Canvas Helpers
// ============================================================

function roundRect(
  ctx: CanvasRenderingContext2D,
  x: number, y: number, w: number, h: number, r: number
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

function roundRectTop(
  ctx: CanvasRenderingContext2D,
  x: number, y: number, w: number, h: number, r: number
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
// Node Rendering
// ============================================================

function renderNode(
  ctx: CanvasRenderingContext2D,
  node: GraphNode,
  globalScale: number,
  selectedId: string | null,
  hoveredId: string | null
) {
  const isSelected = node.id === selectedId
  const isHovered = node.id === hoveredId
  const isHighlighted = isSelected || isHovered

  const { w, h, hw, hh } = getNodeDims(node, globalScale)
  const headerH = 14 * globalScale
  const propLineH = 10 * globalScale
  const maxVisibleProps = 5
  const visibleDataProps = (node.dataProperties || []).slice(0, maxVisibleProps)

  const px = node.x || 0
  const py = node.y || 0

  ctx.save()

  if (isHighlighted) {
    ctx.shadowColor = isSelected ? COLORS.classSelected : COLORS.classHover
    ctx.shadowBlur = 20 * globalScale
  } else {
    ctx.shadowColor = "rgba(0,0,0,0.5)"
    ctx.shadowBlur = 8 * globalScale
  }

  ctx.beginPath()
  roundRect(ctx, px - hw, py - hh, w, h, 4 * globalScale)
  ctx.fillStyle = COLORS.nodeBg
  ctx.fill()

  ctx.strokeStyle = isSelected ? COLORS.nodeBorderSelected : isHovered ? COLORS.classHover : COLORS.nodeBorder
  ctx.lineWidth = isHighlighted ? 2 * globalScale : 1 * globalScale
  ctx.stroke()

  ctx.shadowBlur = 0

  ctx.beginPath()
  roundRectTop(ctx, px - hw, py - hh, w, headerH, 4 * globalScale)
  ctx.fillStyle = isSelected
    ? "rgba(99, 102, 241, 0.3)"
    : isHovered
    ? "rgba(99, 102, 241, 0.15)"
    : "rgba(255, 255, 255, 0.05)"
  ctx.fill()

  ctx.beginPath()
  ctx.moveTo(px - hw + 4 * globalScale, py - hh + headerH)
  ctx.lineTo(px + hw - 4 * globalScale, py - hh + headerH)
  ctx.strokeStyle = COLORS.nodeBorder
  ctx.lineWidth = 1 * globalScale
  ctx.stroke()

  const fontSize = Math.max(6, 7 * globalScale)
  ctx.font = `600 ${fontSize}px Inter, -apple-system, sans-serif`
  ctx.fillStyle = COLORS.text
  ctx.textAlign = "center"
  ctx.textBaseline = "middle"
  ctx.fillText(
    node.displayName.length > 16 ? node.displayName.slice(0, 14) + "…" : node.displayName,
    px,
    py - hh + headerH / 2
  )

  let propY = py - hh + headerH + 6 * globalScale

  for (const dp of visibleDataProps) {
    const propFontSize = Math.max(5, 6 * globalScale)
    ctx.font = `${propFontSize}px Inter, -apple-system, sans-serif`
    ctx.fillStyle = COLORS.dataProp
    ctx.textAlign = "left"
    ctx.textBaseline = "top"
    ctx.beginPath()
    ctx.arc(px - hw + 6 * globalScale, propY + propFontSize / 2 - 1, 2 * globalScale, 0, Math.PI * 2)
    ctx.fill()
    const text = `${dp.displayName} (${dp.rangeType})`
    ctx.fillStyle = COLORS.textSecondary
    ctx.fillText(
      text.length > 22 ? text.slice(0, 20) + "…" : text,
      px - hw + 12 * globalScale,
      propY
    )
    propY += propLineH
  }

  const totalDataProps = node.dataProperties?.length || 0
  const shownProps = visibleDataProps.length
  if (totalDataProps > shownProps) {
    const moreFontSize = Math.max(5, 6 * globalScale)
    ctx.font = `400 ${moreFontSize}px Inter, sans-serif`
    ctx.fillStyle = COLORS.textMuted
    ctx.textAlign = "center"
    ctx.fillText(`+${totalDataProps - shownProps} more…`, px, propY + 4 * globalScale)
  }

  ctx.restore()
}

// ============================================================
// Link Rendering (edge-to-edge with arrow)
// ============================================================

function renderLink(
  ctx: CanvasRenderingContext2D,
  link: GraphLink,
  sourceNode: GraphNode,
  targetNode: GraphNode,
  globalScale: number,
  selectedClassId: string | null
) {
  const sx = sourceNode.x || 0
  const sy = sourceNode.y || 0
  const tx = targetNode.x || 0
  const ty = targetNode.y || 0

  const { hw: shw, hh: shh } = getNodeDims(sourceNode, globalScale)
  const { hw: thw, hh: thh } = getNodeDims(targetNode, globalScale)

  const isHighlighted =
    sourceNode.id === selectedClassId || targetNode.id === selectedClassId

  const linkColor = isHighlighted ? COLORS.objectProp : COLORS.linkDefault
  const linkWidth = isHighlighted ? 2.5 * globalScale : 1.5 * globalScale

  const dx = tx - sx
  const dy = ty - sy
  const dist = Math.sqrt(dx * dx + dy * dy) || 1
  const nx = dx / dist
  const ny = dy / dist

  const extendBack = 5000
  const [ex2, ey2] = lineRectIntersect(
    tx + nx * extendBack, ty + ny * extendBack,
    sx, sy,
    sx, sy, shw, shh
  )
  const [ex1, ey1] = lineRectIntersect(
    sx - nx * extendBack, sy - ny * extendBack,
    tx, ty,
    tx, ty, thw, thh
  )

  const arrowSize = 8 * globalScale

  ctx.save()

  ctx.beginPath()
  ctx.moveTo(ex2, ey2)
  ctx.lineTo(ex1, ey1)
  ctx.strokeStyle = linkColor
  ctx.lineWidth = linkWidth
  if (link.type === "inheritance") {
    ctx.setLineDash([])
  } else if (link.type === "data") {
    ctx.setLineDash([6 * globalScale, 4 * globalScale])
  }
  ctx.stroke()
  ctx.setLineDash([])

  if (link.type === "object") {
    const angle = Math.atan2(dy, dx)
    ctx.beginPath()
    ctx.moveTo(ex1, ey1)
    ctx.lineTo(
      ex1 - arrowSize * Math.cos(angle - Math.PI / 7),
      ey1 - arrowSize * Math.sin(angle - Math.PI / 7)
    )
    ctx.lineTo(
      ex1 - arrowSize * Math.cos(angle + Math.PI / 7),
      ey1 - arrowSize * Math.sin(angle + Math.PI / 7)
    )
    ctx.closePath()
    ctx.fillStyle = linkColor
    ctx.fill()
  }

  if (link.type === "bidirectional") {
    const linkAngle = Math.atan2(dy, dx)
    ctx.beginPath()
    ctx.moveTo(ex1, ey1)
    ctx.lineTo(
      ex1 - arrowSize * Math.cos(linkAngle - Math.PI / 7),
      ey1 - arrowSize * Math.sin(linkAngle - Math.PI / 7)
    )
    ctx.lineTo(
      ex1 - arrowSize * Math.cos(linkAngle + Math.PI / 7),
      ey1 - arrowSize * Math.sin(linkAngle + Math.PI / 7)
    )
    ctx.closePath()
    ctx.fillStyle = linkColor
    ctx.fill()

    ctx.beginPath()
    ctx.moveTo(ex2, ey2)
    ctx.lineTo(
      ex2 + arrowSize * Math.cos(linkAngle - Math.PI / 7),
      ey2 + arrowSize * Math.sin(linkAngle - Math.PI / 7)
    )
    ctx.lineTo(
      ex2 + arrowSize * Math.cos(linkAngle + Math.PI / 7),
      ey2 + arrowSize * Math.sin(linkAngle + Math.PI / 7)
    )
    ctx.closePath()
    ctx.fillStyle = linkColor
    ctx.fill()

    const fontSize = Math.max(5, 6 * globalScale)
    ctx.font = `400 ${fontSize}px Inter, sans-serif`
    const labels = link.displayName.split("|")

    const mx = (ex1 + ex2) / 2
    const my = (ey1 + ey2) / 2
    const linkLen = Math.sqrt((ex2 - ex1) ** 2 + (ey2 - ey1) ** 2)
    const labelGap = Math.min(20 * globalScale, linkLen / 4)

    ctx.save()
    ctx.translate(mx - nx * labelGap, my - ny * labelGap)
    ctx.fillStyle = isHighlighted ? "#E2E8F0" : COLORS.textSecondary
    ctx.textAlign = "center"
    ctx.textBaseline = "middle"
    ctx.fillText(labels[0], 0, 0)
    ctx.restore()

    ctx.save()
    ctx.translate(mx + nx * labelGap, my + ny * labelGap)
    ctx.fillStyle = isHighlighted ? "#E2E8F0" : COLORS.textSecondary
    ctx.textAlign = "center"
    ctx.textBaseline = "middle"
    ctx.fillText(labels[1], 0, 0)
    ctx.restore()
  }

  if (link.type === "inheritance") {
    const propLen = 8 * globalScale
    const px2 = tx - nx * (thh + propLen)
    const py2 = ty - ny * (thh + propLen)
    const perpX = -ny
    const perpY = nx
    ctx.beginPath()
    ctx.moveTo(tx - nx * thh, ty - ny * thh)
    ctx.lineTo(px2 + perpX * propLen * 0.6, py2 + perpY * propLen * 0.6)
    ctx.lineTo(px2 - perpX * propLen * 0.6, py2 - perpY * propLen * 0.6)
    ctx.closePath()
    ctx.fillStyle = linkColor
    ctx.fill()
  }

  if (link.type !== "bidirectional") {
    const mx = (ex1 + ex2) / 2
    const my = (ey1 + ey2) / 2
    const fontSize = Math.max(5, 6 * globalScale)
    ctx.font = `400 ${fontSize}px Inter, sans-serif`
    const label = link.type === "inheritance" ? "⊆" : link.displayName

    ctx.fillStyle = isHighlighted ? "#E2E8F0" : COLORS.textSecondary
    ctx.textAlign = "center"
    ctx.textBaseline = "middle"
    ctx.fillText(label, mx, my)
  }

  ctx.restore()
}

// ============================================================
// Component
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
  const hoveredIdRef = useRef<string | null>(null)
  const [dimensions, setDimensions] = useState({ width, height })
  const [zoomLevel, setZoomLevel] = useState(1)

  useEffect(() => {
    if (graphRef.current) {
      setTimeout(() => graphRef.current?.zoomToFit(0, 100), 100)
    }
  }, [data])

  useEffect(() => {
    if (!graphRef.current) return
    graphRef.current.d3Force("charge", d3.forceManyBody().strength(-400).distanceMax(400))
    graphRef.current.d3Force("link", d3.forceLink().strength(0.05))
    graphRef.current.d3Force("center", d3.forceCenter(0, 0).strength(0.05))
    graphRef.current.d3Force("collision", d3.forceCollide().strength(0.8).radius((node: any) => {
      const n = node as GraphNode
      const w = Math.max(80, n.displayName.length * 5 + 40)
      const headerH = 20
      const propH = Math.min(5, n.dataProperties?.length || 0) * 10 + 8
      const h = headerH + propH + 8
      return Math.max(w, h) * 0.6
    }))
    graphRef.current.d3ReheatSimulation()
  }, [])

  useEffect(() => {
    if (!graphRef.current) return
    graphRef.current.d3Force("collision", d3.forceCollide().strength(0.8).radius((node: any) => {
      const n = node as GraphNode
      const w = Math.max(80, n.displayName.length * 5 + 40)
      const headerH = 20
      const propH = Math.min(5, n.dataProperties?.length || 0) * 10 + 8
      const h = headerH + propH + 8
      return Math.max(w, h) * 0.6 * zoomLevel
    }))
    graphRef.current.d3ReheatSimulation()
  }, [zoomLevel])

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
      renderNode(ctx, node, globalScale, selectedClassId ?? null, hoveredIdRef.current)
    },
    [selectedClassId]
  )

  const nodePointerAreaPaint = useCallback(
    (node: any, color: string, ctx: CanvasRenderingContext2D, globalScale: number) => {
      const { w, h, hw, hh } = getNodeDims(node as GraphNode, globalScale)
      ctx.fillStyle = color
      ctx.beginPath()
      roundRect(ctx, (node.x || 0) - hw, (node.y || 0) - hh, w, h, 4 * globalScale)
      ctx.fill()
    },
    []
  )

  const linkCanvasObject = useCallback(
    (link: any, ctx: CanvasRenderingContext2D, globalScale: number) => {
      const source = link.source as GraphNode
      const target = link.target as GraphNode
      if (!source || !target || source.x == null || target.x == null) return
      renderLink(ctx, link, source, target, globalScale, selectedClassId ?? null)
    },
    [selectedClassId]
  )

  const onNodeClick = useCallback(
    (node: NodeObject) => {
      onClassSelect?.((node as GraphNode).id)
    },
    [onClassSelect]
  )

  const onNodeHover = useCallback(
    (node: NodeObject | null) => {
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

      <ForceGraph2D
        ref={graphRef}
        graphData={{ nodes, links }}
        width={dimensions.width}
        height={dimensions.height}
        backgroundColor="transparent"
        nodeCanvasObject={nodeCanvasObject as any}
        nodePointerAreaPaint={nodePointerAreaPaint as any}
        linkCanvasObject={linkCanvasObject as any}
        linkDirectionalArrowLength={0}
        onNodeClick={onNodeClick}
        onNodeHover={onNodeHover}
        onZoom={(transform) => setZoomLevel(transform.k)}
        cooldownTicks={50}
        d3AlphaDecay={0.1}
        d3VelocityDecay={0.5}
        enableNodeDrag={true}
        enableZoomInteraction={true}
        enablePanInteraction={true}
        minZoom={0.4}
        maxZoom={2}
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
    </div>
  )
}
