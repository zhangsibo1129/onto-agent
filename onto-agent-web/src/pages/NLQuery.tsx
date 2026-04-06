import { useState } from "react"
import "./NLQuery.css"

const ontologies = ["客户360", "供应商网络", "订单全景"]

const suggestions = [
  "显示所有金牌客户",
  "订单总额超过100万的客户",
  "过去30天新增的客户",
  "按销售额排序的前10名客户",
]

const messages = [
  {
    type: "user",
    content: "显示上月高价值客户",
  },
  {
    type: "assistant",
    title: "已为您生成查询",
    query: `PREFIX onto: <http://ontoagent.com/ontology#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?customerName ?email ?lifetimeValue
WHERE {
  ?customer rdf:type onto:Customer ;
           onto:name ?customerName ;
           onto:email ?email ;
           onto:lifetimeValue ?lifetimeValue ;
           onto:tier ?tier .
  
  FILTER(?tier IN ("Gold", "Platinum"))
  FILTER(?lifetimeValue > 1000000)
}
ORDER BY DESC(?lifetimeValue)
LIMIT 20`,
    results: [
      { name: "Apple Inc.", email: "procurement@apple.com", value: "$2,456,789" },
      { name: "Microsoft Corp.", email: "orders@microsoft.com", value: "$1,892,345" },
      { name: "Amazon.com", email: "vendor@amazon.com", value: "$1,654,230" },
    ],
  },
]

export default function NLQuery() {
  const [input, setInput] = useState("")
  const [selectedOntology, setSelectedOntology] = useState("客户360")
  const [chatMessages, setChatMessages] = useState(messages)

  const handleSend = () => {
    if (!input.trim()) return
    setChatMessages([...chatMessages, { type: "user", content: input }])
    setInput("")
  }

  return (
      <div className="chat-area">
        <div className="chat-header">
          <div className="chat-ontology-select">
            <select
              className="form-select"
              value={selectedOntology}
              onChange={(e) => setSelectedOntology(e.target.value)}
            >
              {ontologies.map((ontology) => (
                <option key={ontology} value={ontology}>{ontology}</option>
              ))}
            </select>
          </div>
        </div>
        <div className="chat-messages">
          {chatMessages.map((msg, index) => (
            <div key={index} className={`chat-msg ${msg.type}`}>
              <div className="chat-avatar">{msg.type === "user" ? "U" : "AI"}</div>
              <div className="chat-bubble">
                {msg.type === "assistant" && <div className="cb-title">{msg.title}</div>}
                <div>{msg.content}</div>
                {msg.query && <div className="cb-query">{msg.query}</div>}
                {msg.results && (
                  <div className="cb-results">
                    <table className="cb-result-table">
                      <thead>
                        <tr>
                          <th>客户名称</th>
                          <th>邮箱</th>
                          <th>客户价值</th>
                        </tr>
                      </thead>
                      <tbody>
                        {msg.results.map((r: any, i: number) => (
                          <tr key={i}>
                            <td>{r.name}</td>
                            <td>{r.email}</td>
                            <td style={{ color: "var(--status-success)" }}>{r.value}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
                {msg.type === "assistant" && (
                  <div className="chat-actions">
                    <button className="btn btn-ghost btn-sm">复制查询</button>
                    <button className="btn btn-ghost btn-sm">查看详情</button>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        <div className="chat-input-area">
          <div className="chat-input-wrapper">
            <textarea
              className="chat-input"
              placeholder="输入您的查询问题..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault()
                  handleSend()
                }
              }}
              rows={1}
            />
            <button className="btn btn-primary" onClick={handleSend}>发送</button>
          </div>
          <div className="suggestions">
            {suggestions.map((s) => (
              <div key={s} className="suggestion-chip" onClick={() => setInput(s)}>
                {s}
              </div>
            ))}
          </div>
        </div>
      </div>
  )
}
