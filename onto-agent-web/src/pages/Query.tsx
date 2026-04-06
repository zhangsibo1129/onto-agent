import { useState } from "react"
import "./Query.css"

const defaultQuery = `PREFIX onto: <http://ontoagent.com/ontology#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

# 查询所有金牌客户及其订单总额
SELECT ?customerName ?email ?totalOrders ?totalAmount
WHERE {
  ?customer rdf:type onto:Customer ;
            onto:name ?customerName ;
            onto:email ?email ;
            onto:tier "Gold" ;
            onto:lifetimeValue ?totalAmount .
  
  {
    SELECT ?customer (COUNT(?order) AS ?totalOrders)
    WHERE {
      ?customer onto:places ?order .
      ?order rdf:type onto:Order .
    }
    GROUP BY ?customer
  }
  
  FILTER(?totalAmount > 100000)
}
ORDER BY DESC(?totalAmount)
LIMIT 50`

const queryHistory = [
  { query: "SELECT ?name ?tier WHERE { ?c rdf:type onto:Customer ... }", results: 42, time: "2 分钟前" },
  { query: "SELECT ?order ?total WHERE { ?o rdf:type onto:Order ... }", results: 128, time: "15 分钟前" },
  { query: 'ASK { ?c rdf:type onto:Customer ; onto:tier "Platinum" }', results: false, time: "1 小时前" },
  { query: "SELECT ?product ?count WHERE { ?p rdf:type onto:Product ... }", results: 86, time: "3 小时前" },
  { query: "CONSTRUCT { ?c onto:has ?a } WHERE { ?c onto:hasAddress ?a }", results: "图查询", time: "昨天" },
]

const queryResults = [
  { id: 1, name: "Apple Inc.", email: "procurement@apple.com", orders: 1247, amount: "$2,456,789.00" },
  { id: 2, name: "Microsoft Corp.", email: "orders@microsoft.com", orders: 986, amount: "$1,892,345.00" },
  { id: 3, name: "Amazon.com", email: "vendor-relations@amazon.com", orders: 2103, amount: "$1,654,230.00" },
  { id: 4, name: "Google LLC", email: "purchasing@google.com", orders: 756, amount: "$1,234,567.00" },
  { id: 5, name: "Meta Platforms", email: "supply@meta.com", orders: 543, amount: "$987,654.00" },
  { id: 6, name: "Tesla Inc.", email: "procurement@tesla.com", orders: 432, amount: "$876,543.00" },
  { id: 7, name: "Netflix Inc.", email: "vendor@netflix.com", orders: 321, amount: "$654,321.00" },
]

export default function Query() {
  const [query, setQuery] = useState(defaultQuery)
  const [activeTab, setActiveTab] = useState("sparql")
  const [resultTab, setResultTab] = useState("table")

  const lineCount = query.split("\n").length

  return (
    <>
      <div className="query-layout">
        <div className="flex gap-4" style={{ flex: 1, minHeight: 0 }}>
          <div className="query-editor-area" style={{ flex: 1 }}>
            <div className="query-editor-header">
              <div className="query-editor-tabs">
                <div className={`query-editor-tab ${activeTab === "sparql" ? "active" : ""}`} onClick={() => setActiveTab("sparql")}>SPARQL</div>
                <div className={`query-editor-tab ${activeTab === "visual" ? "active" : ""}`} onClick={() => setActiveTab("visual")}>可视化构建</div>
              </div>
              <div className="flex gap-2">
                <button className="btn btn-ghost btn-sm">格式化</button>
                <button className="btn btn-ghost btn-sm">清除</button>
                <button className="btn btn-ghost btn-sm">保存查询</button>
              </div>
            </div>
            <textarea
              className="query-textarea"
              spellCheck={false}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
            <div className="query-footer">
              <div className="query-info">
                <span>本体: 客户360 v2.1</span>
                <span style={{ marginLeft: "var(--space-4)" }}>行数: {lineCount}</span>
                <span style={{ marginLeft: "var(--space-4)" }}>上次执行: 2.3s · 返回 {queryResults.length} 条</span>
              </div>
              <div className="flex gap-2">
                <button className="btn btn-ghost btn-sm">解释查询</button>
                <button className="btn btn-primary">▶ 执行查询</button>
              </div>
            </div>
          </div>

          <div className="query-history">
            <div className="query-history-header">查询历史</div>
            <div className="query-history-list">
              {queryHistory.map((item, index) => (
                <div key={index} className="query-history-item">
                  <div className="qhi-query">{item.query}</div>
                  <div className="qhi-meta">
                    <span>{typeof item.results === "number" ? `${item.results} 条结果` : String(item.results)}</span>
                    <span>{item.time}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="query-result-area">
          <div className="query-result-tabs">
            <div className={`query-result-tab ${resultTab === "table" ? "active" : ""}`} onClick={() => setResultTab("table")}>表格结果 ({queryResults.length})</div>
            <div className={`query-result-tab ${resultTab === "json" ? "active" : ""}`} onClick={() => setResultTab("json")}>JSON</div>
            <div className={`query-result-tab ${resultTab === "chart" ? "active" : ""}`} onClick={() => setResultTab("chart")}>图表</div>
            <div className={`query-result-tab ${resultTab === "plan" ? "active" : ""}`} onClick={() => setResultTab("plan")}>执行计划</div>
          </div>
          <div className="query-result-body">
            <table className="result-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>customerName</th>
                  <th>email</th>
                  <th>totalOrders</th>
                  <th>totalAmount</th>
                </tr>
              </thead>
              <tbody>
                {queryResults.map((row) => (
                  <tr key={row.id}>
                    <td className="mono" style={{ color: "var(--text-tertiary)" }}>{row.id}</td>
                    <td className="cell-primary">{row.name}</td>
                    <td className="mono">{row.email}</td>
                    <td>{row.orders.toLocaleString()}</td>
                    <td className="mono" style={{ color: "var(--status-success)" }}>{row.amount}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="pagination" style={{ padding: "var(--space-3) var(--space-4)", borderTop: "1px solid var(--border-primary)" }}>
            <div className="pagination-info">显示 1-{queryResults.length} / 共 {queryResults.length} 条</div>
            <div className="pagination-buttons">
              <button className="pagination-btn" disabled>‹</button>
              <button className="pagination-btn active">1</button>
              <button className="pagination-btn">2</button>
              <button className="pagination-btn">3</button>
              <button className="pagination-btn">...</button>
              <button className="pagination-btn">6</button>
              <button className="pagination-btn">›</button>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}
