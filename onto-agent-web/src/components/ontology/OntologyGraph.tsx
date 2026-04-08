import { useRef, useCallback, useEffect, useState, useMemo } from "react"
import ForceGraph2D, { type ForceGraphMethods, type NodeObject, type LinkObject } from "react-force-graph-2d"
import * as d3 from "d3"

// ============================================================
// Types (OWL 2 aligned)
// ============================================================

export interface OntologyClass {
  id: string
  ontologyId: string
  name: string
  displayName?: string
  description?: string
  labels: Record<string, string>
  comments: Record<string, string>
  equivalentTo: string[]
  disjointWith: string[]
  superClasses: string[]
}

export interface DataProperty {
  id: string
  ontologyId: string
  name: string
  displayName?: string
  description?: string
  labels: Record<string, string>
  comments: Record<string, string>
  domainIds: string[]
  rangeType: string
  characteristics: string[]
  superPropertyId?: string
}

export interface ObjectProperty {
  id: string
  ontologyId: string
  name: string
  displayName?: string
  description?: string
  labels: Record<string, string>
  comments: Record<string, string>
  domainIds: string[]
  rangeIds: string[]
  characteristics: string[]
  superPropertyId?: string
  inverseOfId?: string
  propertyChain: string[]
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
    for (const domainId of dp.domainIds || []) {
      const list = dataPropsByClass.get(domainId) || []
      list.push(dp)
      dataPropsByClass.set(domainId, list)
    }
  }

  for (const op of objectProperties) {
    for (const domainId of op.domainIds || []) {
      const outList = objPropsByClass.get(domainId) || []
      outList.push(op)
      objPropsByClass.set(domainId, outList)
    }
    for (const rangeId of op.rangeIds || []) {
      const inList = incomingByClass.get(rangeId) || []
      inList.push(op)
      incomingByClass.set(rangeId, inList)
    }
  }

  const nodes: GraphNode[] = classes.map((cls) => ({
    id: cls.id,
    name: cls.name,
    displayName: cls.displayName || cls.name,
    subClassOf: cls.superClasses?.[0],
    dataProperties: dataPropsByClass.get(cls.id) || [],
    objectProperties: objPropsByClass.get(cls.id) || [],
    incomingRelations: incomingByClass.get(cls.id) || [],
    classCount: classes.length,
    propertyCount: dataProperties.length + objectProperties.length,
  }))

  const links: GraphLink[] = []

  for (const op of objectProperties) {
    for (const sourceId of op.domainIds || []) {
      for (const targetId of op.rangeIds || []) {
        const reverseOp = objectProperties.find(p => 
          (p.domainIds || []).includes(targetId) && (p.rangeIds || []).includes(sourceId)
        )
        
        if (reverseOp && op.id < reverseOp.id) continue

        if (reverseOp) {
          links.push({
            source: sourceId,
            target: targetId,
            propertyId: `${op.id}|${reverseOp.id}`,
            displayName: `${op.displayName || op.name}|${reverseOp.displayName || reverseOp.name}`,
            type: "bidirectional",
            sourceClass: sourceId,
            targetClass: targetId,
          })
        } else {
          links.push({
            source: sourceId,
            target: targetId,
            propertyId: op.id,
            displayName: op.displayName || op.name,
            type: "object",
            sourceClass: sourceId,
            targetClass: targetId,
          })
        }
      }
    }
  }

  for (const cls of classes) {
    if (cls.superClasses?.[0]) {
      links.push({
        source: cls.id,
        target: cls.superClasses[0],
        propertyId: `inherit-${cls.id}`,
        displayName: "rdfs:subClassOf",
        type: "inheritance",
        sourceClass: cls.id,
        targetClass: cls.superClasses[0],
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
  selectedClassId: string | null,
  hoveredId: string | null
) {
  const sx = sourceNode.x || 0
  const sy = sourceNode.y || 0
  const tx = targetNode.x || 0
  const ty = targetNode.y || 0

  const { hw: shw, hh: shh } = getNodeDims(sourceNode, globalScale)
  const { hw: thw, hh: thh } = getNodeDims(targetNode, globalScale)

  const isHighlighted =
    sourceNode.id === selectedClassId || targetNode.id === selectedClassId ||
    sourceNode.id === hoveredId || targetNode.id === hoveredId

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

  const arrowBack = arrowSize * Math.cos(Math.PI / 7)

  if (link.type === "inheritance") {
    const angle = Math.atan2(dy, dx)
    ctx.setLineDash([5, 3])
    ctx.beginPath()
    ctx.moveTo(ex2, ey2)
    ctx.lineTo(ex1 - arrowBack * Math.cos(angle), ey1 - arrowBack * Math.sin(angle))
    ctx.strokeStyle = linkColor
    ctx.lineWidth = linkWidth
    ctx.stroke()
    ctx.setLineDash([])

    const arrowLen = arrowSize * 1.2
    ctx.beginPath()
    ctx.moveTo(ex1, ey1)
    ctx.lineTo(
      ex1 - arrowLen * Math.cos(angle - Math.PI / 6),
      ey1 - arrowLen * Math.sin(angle - Math.PI / 6)
    )
    ctx.lineTo(
      ex1 - arrowLen * Math.cos(angle + Math.PI / 6),
      ey1 - arrowLen * Math.sin(angle + Math.PI / 6)
    )
    ctx.closePath()
    ctx.strokeStyle = linkColor
    ctx.lineWidth = linkWidth
    ctx.stroke()
  } else if (link.type === "object") {
    const angle = Math.atan2(dy, dx)
    ctx.beginPath()
    ctx.moveTo(ex2, ey2)
    ctx.lineTo(ex1 - arrowBack * Math.cos(angle), ey1 - arrowBack * Math.sin(angle))
    ctx.strokeStyle = linkColor
    ctx.lineWidth = linkWidth
    ctx.stroke()

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
  } else if (link.type === "bidirectional") {
    const linkAngle = Math.atan2(dy, dx)

    // --- 逆向箭头根部（线段起点）和正向箭头根部（线段终点）---
    const revEndX = ex2 + arrowBack * Math.cos(linkAngle)
    const revEndY = ey2 + arrowBack * Math.sin(linkAngle)
    const fwdEndX = ex1 - arrowBack * Math.cos(linkAngle)
    const fwdEndY = ey1 - arrowBack * Math.sin(linkAngle)

    // --- 线段：从逆向箭头根部到正向箭头根部 ---
    ctx.beginPath()
    ctx.moveTo(revEndX, revEndY)
    ctx.lineTo(fwdEndX, fwdEndY)
    ctx.strokeStyle = linkColor
    ctx.lineWidth = linkWidth
    ctx.stroke()

    // --- 正向箭头（尖端在 ex1）---
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

    // --- 逆向箭头（尖端在 ex2，指向源节点，翅膀沿 +linkAngle 方向向后延伸）---
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

    // 正向标签：靠近正向箭头根部 fwdEnd，往 -linkAngle 方向偏移
    ctx.fillStyle = isHighlighted ? "#E2E8F0" : COLORS.textSecondary
    ctx.textAlign = "center"
    ctx.textBaseline = "middle"
    ctx.fillText(labels[0], fwdEndX - nx * 15, fwdEndY - ny * 15)

    // 逆向标签：靠近逆向箭头根部 revEnd，往 +linkAngle 方向偏移
    ctx.fillText(labels[1] || "", revEndX + nx * 15, revEndY + ny * 15)
  }

  if (link.type === "object") {
    const mx = (ex1 + ex2) / 2
    const my = (ey1 + ey2) / 2
    const fontSize = Math.max(5, 6 * globalScale)
    ctx.font = `400 ${fontSize}px Inter, sans-serif`
    const label = link.displayName

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
  onClassSelect,
  width = 800,
  height = 600,
}: OntologyGraphProps) {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const graphRef = useRef<ForceGraphMethods<GraphNode, GraphLink>>(null) as any
  const containerRef = useRef<HTMLDivElement>(null)
  const [dimensions, setDimensions] = useState({ width, height })
  const [zoomLevel, setZoomLevel] = useState(1)
  const [hoveredId, setHoveredId] = useState<string | null>(null)
  const selectedIdRef = useRef<string | null>(null)
  const dragStartPosRef = useRef<{ x: number; y: number } | null>(null)
  const isDraggingRef = useRef(false)

  useEffect(() => {
    if (graphRef.current) {
      setTimeout(() => graphRef.current?.zoomToFit(0, 100), 100)
    }
  }, [data])

  useEffect(() => {
    if (!graphRef.current) return
    graphRef.current.d3Force("charge", d3.forceManyBody().strength(-400).distanceMax(400))
    graphRef.current.d3Force("link", d3.forceLink().strength(0.04))
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
      renderNode(ctx, node, globalScale, selectedIdRef.current, hoveredId)
    },
    [hoveredId]
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
      renderLink(ctx, link, source, target, globalScale, selectedIdRef.current, hoveredId)
    },
    [hoveredId]
  )

  const onNodeClick = useCallback(
    (node: NodeObject) => {
      if (dragStartPosRef.current) return
      const id = (node as GraphNode).id
      selectedIdRef.current = selectedIdRef.current === id ? null : id
      onClassSelect?.(id)
    },
    [onClassSelect]
  )

  const onNodeDrag = useCallback(
    (_node: NodeObject, _translate: { x: number; y: number }) => {
      isDraggingRef.current = true
      if (!dragStartPosRef.current) {
        dragStartPosRef.current = { x: 0, y: 0 }
      }
    },
    []
  )

  const onNodeDragEnd = useCallback(
    (_node: NodeObject) => {
      isDraggingRef.current = false
      dragStartPosRef.current = null
    },
    []
  )

  const onNodeHover = useCallback(
    (node: NodeObject | null) => {
      const id = node ? (node as GraphNode).id : null
      if (!isDraggingRef.current) {
        setHoveredId(id)
      }
      if (containerRef.current) {
        containerRef.current.style.cursor = id ? "pointer" : "grab"
      }
    },
    []
  )

  const onZoom = useCallback((transform: { k: number }) => {
    requestAnimationFrame(() => setZoomLevel(transform.k))
  }, [])

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
        onNodeDrag={onNodeDrag}
        onNodeDragEnd={onNodeDragEnd}
        onZoom={onZoom}
        cooldownTicks={200}
        d3AlphaDecay={0.02}
        d3VelocityDecay={0.4}
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
