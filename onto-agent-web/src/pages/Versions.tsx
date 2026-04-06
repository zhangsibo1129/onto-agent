const versions = [
  {
    tag: "v2.2-draft",
    status: "draft",
    date: null,
    description: "正在添加 Interaction 对象类型和新的关系映射",
    objectTypes: 9,
    properties: 68,
    relations: 15,
    isCurrent: false,
    changes: [],
  },
  {
    tag: "v2.1",
    status: "published",
    date: "2024-01-15 14:30",
    description: "新增 Customer 分段属性，优化 Order 关系映射",
    objectTypes: 8,
    properties: 64,
    relations: 14,
    isCurrent: true,
    changes: [
      { type: "added", text: "新增对象类型 Segment" },
      { type: "added", text: "Customer 新增 segmentId 属性" },
      { type: "modified", text: "修改 Customer→Order 关系基数 1:N → 1:*" },
      { type: "modified", text: "更新 Order.totalAmount 映射表达式" },
    ],
  },
  {
    tag: "v2.0",
    status: "published",
    date: "2024-01-08 10:15",
    description: "重大更新：重构 Customer 对象，添加 Invoice 和 Contact 对象",
    objectTypes: 7,
    properties: 58,
    relations: 11,
    isCurrent: false,
    changes: [
      { type: "added", text: "新增对象类型 Invoice" },
      { type: "added", text: "新增对象类型 Contact" },
      { type: "modified", text: "重构 Customer 属性结构" },
    ],
  },
  {
    tag: "v1.0",
    status: "published",
    date: "2023-12-20 09:00",
    description: "初始版本：Customer、Order、Product、Address 四个对象类型",
    objectTypes: 4,
    properties: 32,
    relations: 5,
    isCurrent: false,
    changes: [],
  },
  {
    tag: "v0.9-beta",
    status: "archived",
    date: "2023-12-10 16:45",
    description: "测试版本，已归档",
    objectTypes: 3,
    properties: 24,
    relations: 4,
    isCurrent: false,
    changes: [],
  },
]

export default function Versions() {
  return (
    <>
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">当前版本</div>
          <div className="stat-value" style={{ color: "var(--status-success)" }}>v2.1</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">草稿版本</div>
          <div className="stat-value">1</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">已发布版本</div>
          <div className="stat-value">3</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">已归档版本</div>
          <div className="stat-value">1</div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <span className="card-title">版本历史 - 客户360</span>
        </div>
        <div className="card-body">
          <div className="version-timeline">
            {versions.map((v) => (
              <div key={v.tag} className="version-item">
                <div className={`version-dot ${v.status}`}></div>
                <div className={`version-card ${v.isCurrent ? "current" : ""}`}>
                  <div className="version-header">
                    <div className="version-title">
                      <span className="version-tag">{v.tag}</span>
                      <span className={`badge badge-${v.status}`}>
                        {v.status === "draft" ? "草稿" : v.status === "published" ? "已发布" : "已归档"}
                      </span>
                      {v.isCurrent && (
                        <span className="badge badge-info" style={{ background: "rgba(59, 130, 246, 0.1)", color: "var(--brand-primary)" }}>
                          当前版本
                        </span>
                      )}
                    </div>
                    {v.date && <span className="text-xs text-tertiary">{v.date}</span>}
                    {!v.date && <span className="text-xs text-tertiary">编辑中</span>}
                  </div>
                  <div className="version-desc">{v.description}</div>
                  {v.changes.length > 0 && (
                    <div className="version-changes">
                      {v.changes.map((c, i) => (
                        <div key={i} className={`version-change ${c.type}`}>
                          <span className="vc-icon">{c.type === "added" ? "+" : "~"}</span>
                          <span>{c.text}</span>
                        </div>
                      ))}
                    </div>
                  )}
                  <div className="version-stats">
                    <div className="version-stat">对象类型: <span>{v.objectTypes}</span></div>
                    <div className="version-stat">属性: <span>{v.properties}</span></div>
                    <div className="version-stat">关系: <span>{v.relations}</span></div>
                  </div>
                  <div className="version-actions">
                    {v.status === "draft" && (
                      <>
                        <button className="btn btn-primary btn-sm">发布</button>
                        <button className="btn btn-secondary btn-sm">查看差异</button>
                        <button className="btn btn-ghost btn-sm">放弃草稿</button>
                      </>
                    )}
                    {v.status === "published" && v.isCurrent && (
                      <>
                        <button className="btn btn-secondary btn-sm">查看快照</button>
                        <button className="btn btn-ghost btn-sm">回滚到此版本</button>
                        <button className="btn btn-ghost btn-sm">导出 OWL</button>
                      </>
                    )}
                    {v.status === "published" && !v.isCurrent && (
                      <>
                        <button className="btn btn-secondary btn-sm">查看快照</button>
                        <button className="btn btn-ghost btn-sm">回滚到此版本</button>
                        <button className="btn btn-ghost btn-sm">比较差异</button>
                      </>
                    )}
                    {v.status === "archived" && (
                      <>
                        <button className="btn btn-ghost btn-sm">查看快照</button>
                        <button className="btn btn-ghost btn-sm">恢复</button>
                      </>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </>
  )
}