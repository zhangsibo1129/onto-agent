import { Link } from "react-router-dom"
import { mockOntologies, mockActivities, mockDataSources } from "@/data/mock"
import "./Dashboard.css"

const statusBadgeClass: Record<string, string> = {
  published: "badge badge-published",
  draft: "badge badge-draft",
  archived: "badge badge-archived",
}

const statusText: Record<string, string> = {
  published: "已发布",
  draft: "草稿",
  archived: "已归档",
}

const activityDotClass: Record<string, string> = {
  success: "var(--status-success)",
  primary: "var(--brand-primary)",
  secondary: "var(--brand-secondary)",
  accent: "var(--brand-accent)",
  warning: "var(--status-warning)",
}

export default function Dashboard() {
  return (
    <>
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">数据源</div>
          <div className="stat-value">{mockDataSources.length}</div>
          <div className="stat-change positive">↑ 全部连接正常</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">本体总数</div>
          <div className="stat-value">{mockOntologies.length}</div>
          <div className="stat-change positive">↑ 2 个已发布</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">对象类型</div>
          <div className="stat-value">24</div>
          <div className="stat-change positive">↑ 较上周 +3</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">今日查询</div>
          <div className="stat-value">1,247</div>
          <div className="stat-change positive">↑ 12.5% 较昨日</div>
        </div>
      </div>

      <div className="card mb-6">
        <div className="card-header">
          <span className="card-title">快捷操作</span>
        </div>
        <div className="card-body">
          <div className="quick-actions-grid">
            <Link to="/data-sources" className="quick-action">
              <div className="qa-icon" style={{ background: "rgba(59, 130, 246, 0.1)", color: "var(--brand-primary)" }}>⬡</div>
              <span className="qa-title">连接数据源</span>
            </Link>
            <Link to="/ontologies" className="quick-action">
              <div className="qa-icon" style={{ background: "rgba(139, 92, 246, 0.1)", color: "var(--brand-secondary)" }}>◈</div>
              <span className="qa-title">创建本体</span>
            </Link>
            <Link to="/query" className="quick-action">
              <div className="qa-icon" style={{ background: "rgba(6, 182, 212, 0.1)", color: "var(--brand-accent)" }}>⌘</div>
              <span className="qa-title">语义查询</span>
            </Link>
            <Link to="/nl-query" className="quick-action">
              <div className="qa-icon" style={{ background: "rgba(16, 185, 129, 0.1)", color: "var(--status-success)" }}>◉</div>
              <span className="qa-title">AI 对话查询</span>
            </Link>
          </div>
        </div>
      </div>

      <div className="dashboard-grid">
        <div className="card">
          <div className="card-header">
            <span className="card-title">最近本体</span>
            <Link to="/ontologies" className="btn btn-ghost btn-sm">查看全部 →</Link>
          </div>
          <div className="card-body" style={{ padding: 0 }}>
            <div className="table-container">
              <table className="table">
                <thead>
                  <tr>
                    <th>名称</th>
                    <th>状态</th>
                    <th>对象数</th>
                    <th>更新时间</th>
                  </tr>
                </thead>
                <tbody>
                  {mockOntologies.map((ontology) => (
                    <tr key={ontology.id}>
                      <td className="cell-primary">{ontology.name}</td>
                      <td>
                        <span className={statusBadgeClass[ontology.status]}>
                          {statusText[ontology.status]}
                        </span>
                      </td>
                      <td>{ontology.objectCount}</td>
                      <td className="text-tertiary">{ontology.updatedAt}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <span className="card-title">最近活动</span>
            <button className="btn btn-ghost btn-sm">筛选</button>
          </div>
          <div className="card-body">
            {mockActivities.map((activity) => (
              <div key={activity.id} className="activity-item">
                <div className="activity-dot" style={{ background: activityDotClass[activity.type] }}></div>
                <div className="activity-content">
                  <div className="activity-text" dangerouslySetInnerHTML={{ __html: activity.text.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>") }} />
                  <div className="activity-time">{activity.time} · {activity.user}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </>
  )
}
