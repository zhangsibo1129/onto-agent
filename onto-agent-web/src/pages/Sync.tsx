const syncTasks = [
  {
    id: 1,
    name: "客户360 - ERP-Production 同步",
    mode: "增量同步",
    modeType: "CDC 模式",
    target: "客户360 v2.1",
    progress: 65,
    processed: 2456,
    total: 3789,
    status: "running",
  },
  {
    id: 2,
    name: "供应商网络 - SCM-SupplyChain 同步",
    mode: "全量同步",
    modeType: "每日 00:00",
    target: "供应商网络 v1.3",
    progress: 100,
    processed: 12450,
    total: 12450,
    status: "success",
  },
  {
    id: 3,
    name: "订单全景 - ERP-Production 同步",
    mode: "增量同步",
    modeType: "时间戳模式",
    target: "订单全景 v1.2",
    progress: 100,
    processed: 8234,
    total: 8234,
    status: "success",
  },
  {
    id: 4,
    name: "库存管理 - ERP-Production 同步",
    mode: "全量同步",
    modeType: "手动触发",
    target: "库存管理 v0.5",
    progress: 0,
    processed: 0,
    total: 0,
    status: "error",
    error: "连接失败",
  },
]

const logs = [
  { time: "14:32:15", level: "info", message: "客户360同步任务已启动" },
  { time: "14:32:16", level: "info", message: "连接数据源 CRM-Main..." },
  { time: "14:32:17", level: "success", message: "连接成功，开始读取变更数据" },
  { time: "14:32:18", level: "info", message: "读取到 456 条新增记录" },
  { time: "14:32:19", level: "info", message: "读取到 1,234 条更新记录" },
  { time: "14:32:20", level: "warning", message: "检测到 3 条数据冲突，已标记待处理" },
  { time: "14:32:21", level: "info", message: "正在写入本体图数据库..." },
  { time: "14:32:25", level: "success", message: "同步完成，成功写入 2,456 条" },
  { time: "13:15:00", level: "info", message: "供应商网络同步任务已启动" },
  { time: "13:15:30", level: "success", message: "全量同步完成，处理 12,450 条" },
  { time: "12:00:00", level: "error", message: "库存管理同步失败: 连接超时" },
]

export default function Sync() {
  return (
    <>
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">同步任务</div>
          <div className="stat-value">4</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">运行中</div>
          <div className="stat-value" style={{ color: "var(--brand-primary)" }}>1</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">今日同步</div>
          <div className="stat-value">12,847</div>
          <div className="stat-change positive">条记录</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">最后同步</div>
          <div className="stat-value text-sm">5 分钟前</div>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 380px", gap: "var(--space-4)" }}>
        <div className="sync-card">
          <div className="sync-card-header">
            <span className="card-title">同步任务</span>
            <button className="btn btn-ghost btn-sm">显示全部</button>
          </div>
          <div className="sync-card-body">
            {syncTasks.map((task) => (
              <div key={task.id} className="sync-item">
                <div
                  className="sync-icon"
                  style={{
                    background:
                      task.status === "running"
                        ? "rgba(59, 130, 246, 0.1)"
                        : task.status === "success"
                        ? "rgba(16, 185, 129, 0.1)"
                        : "rgba(239, 68, 68, 0.1)",
                    color:
                      task.status === "running"
                        ? "var(--brand-primary)"
                        : task.status === "success"
                        ? "var(--status-success)"
                        : "var(--status-error)",
                  }}
                >
                  {task.status === "running" ? "⟳" : task.status === "success" ? "✓" : "!"}
                </div>
                <div className="sync-info">
                  <div className="sync-name">{task.name}</div>
                  <div className="sync-meta">
                    {task.mode} · {task.modeType} · 目标: {task.target}
                  </div>
                </div>
                <div className="sync-progress">
                  <div className="sync-progress-bar">
                    <div
                      className="sync-progress-fill"
                      style={{
                        width: `${task.progress}%`,
                        background:
                          task.status === "error"
                            ? "var(--status-error)"
                            : task.status === "success"
                            ? "var(--status-success)"
                            : "var(--brand-primary)",
                      }}
                    ></div>
                  </div>
                  <div className="sync-progress-text">
                    {task.status === "running"
                      ? `处理中 · ${task.processed.toLocaleString()} / ${task.total.toLocaleString()}`
                      : task.status === "error"
                      ? `错误: ${task.error}`
                      : `已完成 · ${task.processed.toLocaleString()} 条`}
                  </div>
                </div>
                <div className="sync-status">
                  <div className={`sync-status-dot ${task.status}`}></div>
                  <span className="text-sm text-secondary">
                    {task.status === "running" ? "运行中" : task.status === "success" ? "成功" : "失败"}
                  </span>
                </div>
                <button className="btn btn-ghost btn-sm">
                  {task.status === "running" ? "暂停" : task.status === "error" ? "重试" : "立即同步"}
                </button>
              </div>
            ))}

            <div className="sync-schedule">
              <div className="sync-schedule-item">
                <span className="icon">⏰</span>
                <span>下次全量同步:</span>
                <strong>明天 00:00</strong>
              </div>
              <div className="sync-schedule-item">
                <span className="icon">📊</span>
                <span>本周已同步:</span>
                <strong>156,789 条</strong>
              </div>
            </div>
          </div>
        </div>

        <div className="sync-card">
          <div className="sync-card-header">
            <span className="card-title">同步日志</span>
            <button className="btn btn-ghost btn-sm">查看全部</button>
          </div>
          <div className="sync-card-body" style={{ maxHeight: 500, overflowY: "auto" }}>
            {logs.map((log, i) => (
              <div key={i} className="log-entry">
                <span className="log-time">{log.time}</span>
                <span
                  className="log-dot"
                  style={{
                    background:
                      log.level === "success"
                        ? "var(--status-success)"
                        : log.level === "error"
                        ? "var(--status-error)"
                        : log.level === "warning"
                        ? "var(--status-warning)"
                        : "var(--text-tertiary)",
                  }}
                ></span>
                <span className="log-message">{log.message}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </>
  )
}