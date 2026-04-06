const endpoints = [
  { method: "GET", path: "/ontologies/{ontologyId}/query", auth: true, group: "本体查询" },
  { method: "POST", path: "/ontologies/{ontologyId}/nl-query", auth: true, group: "本体查询" },
  { method: "GET", path: "/ontologies/{ontologyId}/objects/{type}", auth: true, group: "本体查询" },
  { method: "POST", path: "/ontologies", auth: true, group: "数据管理" },
  { method: "PUT", path: "/ontologies/{ontologyId}", auth: true, group: "数据管理" },
  { method: "DELETE", path: "/ontologies/{ontologyId}", auth: true, group: "数据管理" },
  { method: "GET", path: "/datasources", auth: true, group: "数据源" },
  { method: "POST", path: "/datasources/{datasourceId}/sync", auth: true, group: "数据源" },
]

const apiKeys = [
  {
    name: "Production API Key",
    status: "active",
    key: "onto_prod_••••••••••••••••••••••••",
    created: "2024-01-15",
    lastUsed: "5 分钟前",
    todayRequests: "8,234",
    rateLimit: "5,000 / 分钟",
  },
  {
    name: "Development API Key",
    status: "info",
    key: "onto_dev_••••••••••••••••••••••••",
    created: "2024-01-10",
    lastUsed: "1 小时前",
    todayRequests: "1,234",
    rateLimit: "1,000 / 分钟",
  },
]

export default function ApiManagement() {
  return (
    <>
      <div className="api-stats-row">
        <div className="api-stat-card">
          <div className="stat-value">24,856</div>
          <div className="stat-label">今日请求</div>
          <div className="stat-change up">↑ 12.5% 较昨日</div>
        </div>
        <div className="api-stat-card">
          <div className="stat-value">156ms</div>
          <div className="stat-label">平均响应时间</div>
          <div className="stat-change down">↓ 8ms 改善</div>
        </div>
        <div className="api-stat-card">
          <div className="stat-value">99.9%</div>
          <div className="stat-label">可用率</div>
          <div className="stat-change up">正常运行</div>
        </div>
        <div className="api-stat-card">
          <div className="stat-value">5,000</div>
          <div className="stat-label">速率限制 (req/min)</div>
          <div className="rate-limit-bar">
            <div className="rate-limit-fill" style={{ width: "42%" }}></div>
          </div>
          <div className="stat-label" style={{ marginTop: "var(--space-1)" }}>
            已用 42%
          </div>
        </div>
      </div>

      <div className="tabs mb-4">
        <div className="tab active">API 密钥</div>
        <div className="tab">接口文档</div>
        <div className="tab">使用统计</div>
        <div className="tab">日志</div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 400px", gap: "var(--space-4)" }}>
        <div>
          <div className="card">
            <div className="card-header">
              <span className="card-title">API 接口</span>
              <button className="btn btn-ghost btn-sm">Swagger 文档</button>
            </div>
            <div className="card-body">
              <div className="text-sm text-secondary mb-4">
                基础 URL: <span className="mono" style={{ color: "var(--brand-accent)" }}>https://api.ontoagent.com/v1</span>
              </div>

              <div className="property-section-title mb-3">本体查询</div>
              {endpoints
                .filter((e) => e.group === "本体查询")
                .map((endpoint, i) => (
                  <div key={i} className="api-endpoint">
                    <span className={`api-method ${endpoint.method.toLowerCase()}`}>{endpoint.method}</span>
                    <span className="api-path">{endpoint.path}</span>
                    <span className="api-auth">🔑 API Key</span>
                  </div>
                ))}

              <div className="property-section-title mb-3" style={{ marginTop: "var(--space-6)" }}>
                数据管理
              </div>
              {endpoints
                .filter((e) => e.group === "数据管理")
                .map((endpoint, i) => (
                  <div key={i} className="api-endpoint">
                    <span className={`api-method ${endpoint.method.toLowerCase()}`}>{endpoint.method}</span>
                    <span className="api-path">{endpoint.path}</span>
                    <span className="api-auth">🔑 API Key</span>
                  </div>
                ))}

              <div className="property-section-title mb-3" style={{ marginTop: "var(--space-6)" }}>
                数据源
              </div>
              {endpoints
                .filter((e) => e.group === "数据源")
                .map((endpoint, i) => (
                  <div key={i} className="api-endpoint">
                    <span className={`api-method ${endpoint.method.toLowerCase()}`}>{endpoint.method}</span>
                    <span className="api-path">{endpoint.path}</span>
                    <span className="api-auth">🔑 API Key</span>
                  </div>
                ))}
            </div>
          </div>
        </div>

        <div>
          {apiKeys.map((key, i) => (
            <div key={i} className="api-key-card" style={{ marginTop: i > 0 ? "var(--space-4)" : 0 }}>
              <div className="api-key-header">
                <span className="font-semibold">{key.name}</span>
                <span className={`badge badge-${key.status}`}>
                  {key.status === "active" ? "活跃" : "开发"}
                </span>
              </div>
              <div className="api-key-value">
                <span className="key masked">{key.key}</span>
                <button className="btn btn-ghost btn-sm">显示</button>
                <button className="btn btn-ghost btn-sm">复制</button>
              </div>
              <div style={{ marginTop: "var(--space-4)" }}>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-tertiary">创建时间</span>
                  <span>{key.created}</span>
                </div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-tertiary">最后使用</span>
                  <span>{key.lastUsed}</span>
                </div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-tertiary">今日请求</span>
                  <span>{key.todayRequests}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-tertiary">速率限制</span>
                  <span>{key.rateLimit}</span>
                </div>
              </div>
              <div className="divider"></div>
              <div className="flex gap-2">
                <button className="btn btn-secondary btn-sm">重新生成</button>
                <button className="btn btn-ghost btn-sm">禁用</button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </>
  )
}