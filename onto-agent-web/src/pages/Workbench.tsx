const objectTypes = [
  { name: "Customer", count: 8 },
  { name: "Order", count: 10 },
  { name: "Product", count: 8 },
  { name: "Address", count: 6 },
  { name: "Contact", count: 7 },
  { name: "Invoice", count: 9 },
  { name: "Segment", count: 4 },
  { name: "Interaction", count: 5 },
]

const relations = [
  { name: "places", from: "Customer", to: "Order" },
  { name: "has", from: "Customer", to: "Address" },
  { name: "contains", from: "Order", to: "Product" },
]

const savedQueries = [
  { name: "金牌客户订单统计", ontology: "客户360", time: "昨天" },
  { name: "月度销售趋势", ontology: "客户360", time: "3天前" },
  { name: "高价值客户分析", ontology: "客户360", time: "1周前" },
]

const snippets = [
  { label: "DISTINCT", code: "去重" },
  { label: "COUNT(?x)", code: "计数" },
  { label: "SUM(?val)", code: "求和" },
  { label: "AVG(?val)", code: "平均值" },
  { label: "GROUP BY", code: "分组" },
  { label: "HAVING", code: "分组过滤" },
  { label: "FILTER", code: "条件过滤" },
  { label: "OPTIONAL", code: "可选匹配" },
  { label: "UNION", code: "合并结果" },
]

const resultData = [
  { name: "Apple Inc.", tier: "Gold", amount: "$2,456,789" },
  { name: "Microsoft Corp.", tier: "Gold", amount: "$1,892,345" },
  { name: "Amazon.com", tier: "Gold", amount: "$1,654,230" },
  { name: "Google LLC", tier: "Gold", amount: "$1,234,567" },
  { name: "Meta Platforms", tier: "Gold", amount: "$987,654" },
]

export default function Workbench() {
  return (
    <div className="content" style={{ padding: "var(--space-4)" }}>
      <div className="workbench-layout">
        <div className="workbench-panel">
          <div className="workbench-panel-header">
            <span className="font-semibold text-sm">本体结构</span>
          </div>
          <div style={{ padding: "var(--space-2) var(--space-3)", borderBottom: "1px solid var(--border-primary)" }}>
            <div className="search-input" style={{ width: "100%" }}>
              <span className="icon">⌕</span>
              <input type="text" placeholder="搜索..." style={{ width: "100%" }} />
            </div>
          </div>
          <div className="workbench-panel-body">
            <div style={{ fontSize: "var(--text-xs)", color: "var(--text-tertiary)", marginBottom: "var(--space-2)", textTransform: "uppercase" }}>
              对象类型
            </div>
            {objectTypes.map((ot) => (
              <div key={ot.name} className={`schema-item ${ot.name === "Customer" ? "selected" : ""}`}>
                <span className="si-icon">◈</span>
                <span className="si-name">{ot.name}</span>
                <span className="si-type">{ot.count}</span>
              </div>
            ))}

            <div style={{ marginTop: "var(--space-4)" }}>
              <div style={{ fontSize: "var(--text-xs)", color: "var(--text-tertiary)", marginBottom: "var(--space-2)", textTransform: "uppercase" }}>
                关系
              </div>
              {relations.map((rel) => (
                <div key={rel.name} className="schema-item">
                  <span className="si-icon" style={{ color: "var(--brand-accent)" }}>⇄</span>
                  <span className="si-name">{rel.name}</span>
                  <span className="si-type">{rel.from}→{rel.to}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="workbench-center">
          <div className="query-builder">
            <div className="query-builder-header">
              <div className="query-builder-tab active">可视化构建</div>
              <div className="query-builder-tab">SPARQL 编辑</div>
              <div className="query-builder-tab">历史记录</div>
            </div>
            <div className="visual-builder">
              <div className="vb-canvas">
                <div style={{ display: "flex", alignItems: "center", flexWrap: "wrap" }}>
                  <div className="vb-node selected">
                    <span className="node-icon">◈</span>
                    <span>Customer</span>
                  </div>
                  <div className="vb-operator">⇄</div>
                  <div className="vb-node">
                    <span className="node-icon">◈</span>
                    <span>Order</span>
                  </div>
                  <div className="vb-operator">?</div>
                  <div className="vb-node" style={{ borderStyle: "dashed", opacity: 0.6 }}>
                    <span className="node-icon">◈</span>
                    <span>添加节点</span>
                  </div>
                </div>
                <div style={{ marginTop: "var(--space-4)", paddingTop: "var(--space-4)", borderTop: "1px dashed var(--border-primary)" }}>
                  <div style={{ fontSize: "var(--text-xs)", color: "var(--text-tertiary)", marginBottom: "var(--space-2)" }}>SELECT</div>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: "var(--space-2)" }}>
                    <div style={{ display: "flex", alignItems: "center", padding: "var(--space-1) var(--space-2)", background: "var(--bg-tertiary)", borderRadius: "var(--radius-sm)", fontSize: "var(--text-xs)" }}>
                      <span style={{ color: "var(--brand-primary)" }}>Customer.</span>name
                      <span style={{ marginLeft: "var(--space-2)", color: "var(--text-tertiary)", cursor: "pointer" }}>✕</span>
                    </div>
                    <div style={{ display: "flex", alignItems: "center", padding: "var(--space-1) var(--space-2)", background: "var(--bg-tertiary)", borderRadius: "var(--radius-sm)", fontSize: "var(--text-xs)" }}>
                      <span style={{ color: "var(--brand-primary)" }}>Customer.</span>tier
                      <span style={{ marginLeft: "var(--space-2)", color: "var(--text-tertiary)", cursor: "pointer" }}>✕</span>
                    </div>
                    <div style={{ display: "flex", alignItems: "center", padding: "var(--space-1) var(--space-2)", background: "var(--bg-tertiary)", borderRadius: "var(--radius-sm)", fontSize: "var(--text-xs)" }}>
                      <span style={{ color: "var(--brand-secondary)" }}>Order.</span>totalAmount
                      <span style={{ marginLeft: "var(--space-2)", color: "var(--text-tertiary)", cursor: "pointer" }}>✕</span>
                    </div>
                    <button style={{ padding: "var(--space-1) var(--space-2)", background: "transparent", border: "1px dashed var(--border-secondary)", borderRadius: "var(--radius-sm)", fontSize: "var(--text-xs)", color: "var(--text-tertiary)", cursor: "pointer" }}>+ 添加字段</button>
                  </div>
                </div>
                <div style={{ marginTop: "var(--space-4)", paddingTop: "var(--space-4)", borderTop: "1px dashed var(--border-primary)" }}>
                  <div style={{ fontSize: "var(--text-xs)", color: "var(--text-tertiary)", marginBottom: "var(--space-2)" }}>WHERE</div>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: "var(--space-2)", alignItems: "center" }}>
                    <div style={{ padding: "var(--space-1) var(--space-2)", background: "rgba(59, 130, 246, 0.1)", border: "1px solid var(--brand-primary)", borderRadius: "var(--radius-sm)", fontSize: "var(--text-xs)" }}>
                      <span style={{ color: "var(--brand-primary)" }}>Customer.tier</span> = <span style={{ color: "var(--status-success)" }}>"Gold"</span>
                      <span style={{ marginLeft: "var(--space-2)", color: "var(--text-tertiary)", cursor: "pointer" }}>✕</span>
                    </div>
                    <div style={{ padding: "var(--space-1) var(--space-2)", background: "rgba(139, 92, 246, 0.1)", border: "1px solid var(--brand-secondary)", borderRadius: "var(--radius-sm)", fontSize: "var(--text-xs)" }}>
                      <span style={{ color: "var(--brand-secondary)" }}>Order.status</span> = <span style={{ color: "var(--status-success)" }}>"completed"</span>
                      <span style={{ marginLeft: "var(--space-2)", color: "var(--text-tertiary)", cursor: "pointer" }}>✕</span>
                    </div>
                    <button style={{ padding: "var(--space-1) var(--space-2)", background: "transparent", border: "1px dashed var(--border-secondary)", borderRadius: "var(--radius-sm)", fontSize: "var(--text-xs)", color: "var(--text-tertiary)", cursor: "pointer" }}>+ 添加条件</button>
                  </div>
                </div>
                <div style={{ marginTop: "var(--space-4)", paddingTop: "var(--space-4)", borderTop: "1px dashed var(--border-primary)" }}>
                  <div style={{ fontSize: "var(--text-xs)", color: "var(--text-tertiary)", marginBottom: "var(--space-2)" }}>ORDER BY</div>
                  <div style={{ display: "flex", gap: "var(--space-2)", alignItems: "center" }}>
                    <div style={{ padding: "var(--space-1) var(--space-2)", background: "var(--bg-tertiary)", borderRadius: "var(--radius-sm)", fontSize: "var(--text-xs)" }}>
                      <span style={{ color: "var(--brand-secondary)" }}>Order.totalAmount</span> <span style={{ color: "var(--text-tertiary)" }}>DESC</span>
                      <span style={{ marginLeft: "var(--space-2)", color: "var(--text-tertiary)", cursor: "pointer" }}>✕</span>
                    </div>
                    <button style={{ padding: "var(--space-1) var(--space-2)", background: "transparent", border: "1px dashed var(--border-secondary)", borderRadius: "var(--radius-sm)", fontSize: "var(--text-xs)", color: "var(--text-tertiary)", cursor: "pointer" }}>+ 添加排序</button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="result-panel">
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "var(--space-3) var(--space-4)", borderBottom: "1px solid var(--border-primary)" }}>
              <div className="result-tabs" style={{ borderBottom: "none" }}>
                <div className="result-tab active">表格</div>
                <div className="result-tab">JSON</div>
                <div className="result-tab">图表</div>
              </div>
              <div style={{ fontSize: "var(--text-xs)", color: "var(--text-tertiary)" }}>执行时间: 234ms · 返回 42 条</div>
            </div>
            <div className="result-body">
              <table className="result-table">
                <thead>
                  <tr>
                    <th style={{ textAlign: "left", padding: "var(--space-3) var(--space-4)" }}>Customer.name</th>
                    <th style={{ textAlign: "left", padding: "var(--space-3) var(--space-4)" }}>Customer.tier</th>
                    <th style={{ textAlign: "right", padding: "var(--space-3) var(--space-4)" }}>Order.totalAmount</th>
                  </tr>
                </thead>
                <tbody>
                  {resultData.map((row, i) => (
                    <tr key={i}>
                      <td style={{ padding: "var(--space-3) var(--space-4)", borderBottom: "1px solid var(--border-primary)", color: "var(--text-primary)" }}>{row.name}</td>
                      <td style={{ padding: "var(--space-3) var(--space-4)", borderBottom: "1px solid var(--border-primary)" }}>
                        <span className="badge badge-success">{row.tier}</span>
                      </td>
                      <td style={{ padding: "var(--space-3) var(--space-4)", borderBottom: "1px solid var(--border-primary)", textAlign: "right", fontFamily: "var(--font-mono)", color: "var(--status-success)" }}>{row.amount}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div style={{ padding: "var(--space-3) var(--space-4)", borderTop: "1px solid var(--border-primary)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div style={{ fontSize: "var(--text-xs)", color: "var(--text-tertiary)" }}>显示 1-5 / 共 42 条</div>
              <div style={{ display: "flex", gap: "var(--space-2)" }}>
                <button className="btn btn-ghost btn-sm">导出 CSV</button>
                <button className="btn btn-ghost btn-sm">导出 JSON</button>
                <button className="btn btn-ghost btn-sm">复制查询</button>
              </div>
            </div>
          </div>
        </div>

        <div className="workbench-panel">
          <div className="workbench-panel-header">
            <span className="font-semibold text-sm">已保存查询</span>
          </div>
          <div className="workbench-panel-body">
            {savedQueries.map((q, i) => (
              <div key={i} className="saved-query-item">
                <div className="sq-name">{q.name}</div>
                <div className="sq-meta">{q.ontology} · {q.time}</div>
              </div>
            ))}

            <div style={{ marginTop: "var(--space-6)" }}>
              <div style={{ fontSize: "var(--text-xs)", color: "var(--text-tertiary)", marginBottom: "var(--space-2)", textTransform: "uppercase" }}>
                代码片段
              </div>
              {snippets.map((s, i) => (
                <button key={i} className="snippet-btn">
                  <code>{s.label}</code> {s.code}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}