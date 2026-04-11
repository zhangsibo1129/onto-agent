import { useState, useEffect, useRef } from "react"
import { nlToSparql, executeSparql } from "@/services/queryApi"
import { ontologyApi, type Ontology } from "@/services/ontologyApi"
import "./NLQuery.css"

const SUGGESTIONS = [
  "显示所有客户",
  "有多少个订单",
  "列出所有产品",
  "显示所有供应商",
]

interface ChatMessage {
  id: string
  type: "user" | "assistant"
  content: string
  nlText?: string
  sparql?: string
  results?: unknown[]
  resultCount?: number
  error?: string
}

export default function NLQuery() {
  const [ontologies, setOntologies] = useState<Ontology[]>([])
  const [selectedOntologyId, setSelectedOntologyId] = useState<string>("")
  const [input, setInput] = useState("")
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Load ontologies
  useEffect(() => {
    ontologyApi.list().then(setOntologies).catch(console.error)
  }, [])

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const selectedOntology = ontologies.find((o) => o.id === selectedOntologyId)

  const handleSend = async () => {
    if (!input.trim() || !selectedOntologyId) return
    const nlText = input.trim()
    setInput("")

    // Add user message
    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      type: "user",
      content: nlText,
    }
    setMessages((prev) => [...prev, userMsg])

    setIsLoading(true)

    try {
      // NL → SPARQL
      const nlResult = await nlToSparql(selectedOntologyId, nlText)

      if (!nlResult.success) {
        const errMsg: ChatMessage = {
          id: (Date.now() + 1).toString(),
          type: "assistant",
          content: "抱歉，无法理解您的问题。",
          nlText,
        }
        setMessages((prev) => [...prev, errMsg])
        setIsLoading(false)
        return
      }

      // Execute the generated SPARQL
      const execResult = await executeSparql(selectedOntologyId, nlResult.sparql)

      const assistantMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: "assistant",
        content: execResult.success
          ? `已生成并执行查询，返回 ${execResult.resultCount} 条结果`
          : `已生成查询，但执行失败：${execResult.error}`,
        nlText,
        sparql: nlResult.sparql,
        results: Array.isArray(execResult.results) ? execResult.results as unknown[] : undefined,
        resultCount: execResult.resultCount,
        error: execResult.error,
      }
      setMessages((prev) => [...prev, assistantMsg])
    } catch (e: any) {
      const errMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: "assistant",
        content: "发生错误：" + (e.message || "未知错误"),
        nlText,
      }
      setMessages((prev) => [...prev, errMsg])
    } finally {
      setIsLoading(false)
    }
  }

  // Copy SPARQL to clipboard
  const handleCopySparql = (sparql: string) => {
    navigator.clipboard.writeText(sparql).then(() => {
      alert("SPARQL 已复制到剪贴板")
    })
  }

  return (
    <div className="chat-layout">
      {/* Top bar */}
      <div className="flex gap-3" style={{ padding: "var(--space-3) var(--space-4)", borderBottom: "1px solid var(--border-primary)" }}>
        <select
          className="select"
          value={selectedOntologyId}
          onChange={(e) => setSelectedOntologyId(e.target.value)}
          style={{ minWidth: 200 }}
        >
          <option value="">— 选择本体 —</option>
          {ontologies.map((o) => (
            <option key={o.id} value={o.id}>{o.name}</option>
          ))}
        </select>
        {selectedOntology && (
          <span className="text-sm text-secondary">
            {selectedOntology.baseIri}
          </span>
        )}
      </div>

      {/* Chat messages */}
      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="chat-empty">
            <div className="chat-empty-icon">💬</div>
            <div className="chat-empty-title">自然语言查询</div>
            <div className="chat-empty-desc">
              选择本体后，用自然语言描述您的查询问题
            </div>
          </div>
        )}

        {messages.map((msg) => (
          <div key={msg.id} className={`chat-msg ${msg.type}`}>
            <div className="chat-avatar">
              {msg.type === "user" ? "U" : "AI"}
            </div>
            <div className="chat-bubble">
              {msg.type === "assistant" && (
                <div className="cb-title">已为您生成查询</div>
              )}
              <div className="cb-content">{msg.content}</div>

              {msg.sparql && (
                <div className="cb-query">
                  <div className="cb-query-label">SPARQL</div>
                  <pre className="cb-query-text">{msg.sparql}</pre>
                  <div className="cb-query-actions">
                    <button
                      className="btn btn-ghost btn-sm"
                      onClick={() => handleCopySparql(msg.sparql!)}
                    >
                      📋 复制
                    </button>
                  </div>
                </div>
              )}

              {msg.error && (
                <div className="alert alert-error" style={{ marginTop: 8 }}>
                  {msg.error}
                </div>
              )}

              {msg.results && !msg.error && msg.resultCount !== undefined && msg.resultCount > 0 && (
                <div className="cb-results">
                  {Array.isArray(msg.results) && (msg.results as unknown[]).length > 0 && (
                    <div className="result-note">
                      前 {Math.min(10, (msg.results as unknown[]).length)} 条结果
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="chat-msg assistant">
            <div className="chat-avatar">AI</div>
            <div className="chat-bubble">
              <div className="cb-loading">
                <span className="loading-dot">●</span>
                <span className="loading-dot">●</span>
                <span className="loading-dot">●</span>
                正在理解您的问题...
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <div className="chat-input-area">
        {selectedOntologyId ? (
          <>
            <div className="chat-input-wrapper">
              <textarea
                className="chat-input"
                placeholder="用自然语言描述您的查询，例如：显示所有金牌客户..."
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
              <button
                className="btn btn-primary"
                onClick={handleSend}
                disabled={isLoading || !input.trim()}
              >
                发送
              </button>
            </div>
            <div className="suggestions">
              {SUGGESTIONS.map((s) => (
                <div
                  key={s}
                  className="suggestion-chip"
                  onClick={() => setInput(s)}
                >
                  {s}
                </div>
              ))}
            </div>
          </>
        ) : (
          <div className="chat-select-hint">请先在上方选择一个本体</div>
        )}
      </div>
    </div>
  )
}
