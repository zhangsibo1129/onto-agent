import { useState, useEffect, useCallback } from "react"
import { useParams } from "react-router-dom"
import { ontologyApi, type SyncTask, type SyncLog } from "@/services/ontologyApi"
import "./Sync.css"

const STATUS_LABELS: Record<string, { text: string; color: string }> = {
  pending: { text: "等待中", color: "var(--status-warning)" },
  running: { text: "运行中", color: "var(--brand-primary)" },
  success: { text: "成功", color: "var(--status-success)" },
  failed: { text: "失败", color: "var(--status-error)" },
}

const LEVEL_COLORS: Record<string, string> = {
  info: "var(--brand-primary)",
  warning: "var(--status-warning)",
  error: "var(--status-error)",
  success: "var(--status-success)",
}

export default function Sync() {
  const { id: ontologyId } = useParams<{ id: string }>()
  
  const [tasks, setTasks] = useState<SyncTask[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedTask, setSelectedTask] = useState<SyncTask | null>(null)
  const [logs, setLogs] = useState<SyncLog[]>([])
  const [logsLoading, setLogsLoading] = useState(false)
  const [showCreateModal, setShowCreateModal] = useState(false)

  // 加载任务列表
  const fetchTasks = useCallback(async () => {
    if (!ontologyId) return
    setLoading(true)
    try {
      const data = await ontologyApi.listSyncTasks(ontologyId)
      setTasks(data)
    } catch (err) {
      console.error("加载同步任务失败:", err)
    } finally {
      setLoading(false)
    }
  }, [ontologyId])

  useEffect(() => {
    fetchTasks()
  }, [fetchTasks])

  // 加载日志
  const fetchLogs = useCallback(async (taskId: string) => {
    if (!ontologyId) return
    setLogsLoading(true)
    try {
      const data = await ontologyApi.getSyncTaskLogs(ontologyId, taskId)
      setLogs(data)
    } catch (err) {
      console.error("加载日志失败:", err)
    } finally {
      setLogsLoading(false)
    }
  }, [ontologyId])

  // 选择任务时加载日志
  useEffect(() => {
    if (selectedTask) {
      fetchLogs(selectedTask.id)
    } else {
      setLogs([])
    }
  }, [selectedTask, fetchLogs])

  // 触发同步
  const handleTriggerSync = async (mode: string) => {
    if (!ontologyId) return
    try {
      const result = await ontologyApi.triggerSync(ontologyId, mode)
      if (result.success) {
        fetchTasks()
        setShowCreateModal(false)
      }
    } catch (err) {
      console.error("触发同步失败:", err)
    }
  }

  // 删除任务
  const handleDelete = async (taskId: string) => {
    if (!ontologyId) return
    if (!confirm("确定要删除这个同步任务吗？")) return
    try {
      await ontologyApi.deleteSyncTask(ontologyId, taskId)
      if (selectedTask?.id === taskId) {
        setSelectedTask(null)
      }
      fetchTasks()
    } catch (err) {
      console.error("删除任务失败:", err)
    }
  }

  // 统计
  const runningCount = tasks.filter(t => t.status === "running").length
  const successCount = tasks.filter(t => t.status === "success").length
  const failedCount = tasks.filter(t => t.status === "failed").length

  if (loading) {
    return <div className="sync-page"><div className="loading">加载中...</div></div>
  }

  return (
    <div className="sync-page">
      {/* 顶部统计 */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">同步任务</div>
          <div className="stat-value">{tasks.length}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">运行中</div>
          <div className="stat-value" style={{ color: "var(--brand-primary)" }}>{runningCount}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">今日同步</div>
          <div className="stat-value">
            {tasks.reduce((sum, t) => sum + (t.processedCount || 0), 0).toLocaleString()}
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-label">失败</div>
          <div className="stat-value" style={{ color: failedCount > 0 ? "var(--status-error)" : "inherit" }}>
            {failedCount}
          </div>
        </div>
      </div>

      <div className="sync-layout">
        {/* 左侧：任务列表 */}
        <div className="sync-list">
          <div className="sync-list-header">
            <h3>同步任务</h3>
            <button className="btn btn-primary btn-sm" onClick={() => setShowCreateModal(true)}>
              + 新建同步
            </button>
          </div>
          
          {tasks.length === 0 ? (
            <div className="empty-state">
              <p>暂无同步任务</p>
              <button className="btn btn-primary" onClick={() => setShowCreateModal(true)}>
                创建第一个任务
              </button>
            </div>
          ) : (
            <div className="task-list">
              {tasks.map(task => (
                <div
                  key={task.id}
                  className={`task-card ${selectedTask?.id === task.id ? 'selected' : ''}`}
                  onClick={() => setSelectedTask(task)}
                >
                  <div className="task-status">
                    <span 
                      className="status-dot"
                      style={{ background: STATUS_LABELS[task.status]?.color }}
                    />
                  </div>
                  <div className="task-info">
                    <div className="task-mode">{task.mode}</div>
                    <div className="task-progress">
                      {task.status === "running" && task.totalCount ? (
                        <div className="progress-bar">
                          <div 
                            className="progress-fill" 
                            style={{ width: `${(task.processedCount || 0) / task.totalCount * 100}%` }}
                          />
                        </div>
                      ) : task.status === "success" ? (
                        <span className="task-count">{task.processedCount?.toLocaleString()} 条</span>
                      ) : task.status === "failed" ? (
                        <span className="task-error">{task.error}</span>
                      ) : null}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* 右侧：任务详情/日志 */}
        <div className="sync-detail">
          {selectedTask ? (
            <>
              <div className="detail-header">
                <h3>任务详情</h3>
                <button 
                  className="btn btn-ghost btn-sm"
                  onClick={() => handleDelete(selectedTask.id)}
                >
                  删除
                </button>
              </div>
              
              <div className="detail-info">
                <div className="detail-row">
                  <span className="detail-label">状态</span>
                  <span className="detail-value" style={{ color: STATUS_LABELS[selectedTask.status]?.color }}>
                    {STATUS_LABELS[selectedTask.status]?.text}
                  </span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">模式</span>
                  <span className="detail-value">{selectedTask.mode}</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">创建时间</span>
                  <span className="detail-value">{selectedTask.createdAt}</span>
                </div>
                {selectedTask.startedAt && (
                  <div className="detail-row">
                    <span className="detail-label">开始时间</span>
                    <span className="detail-value">{selectedTask.startedAt}</span>
                  </div>
                )}
                {selectedTask.completedAt && (
                  <div className="detail-row">
                    <span className="detail-label">完成时间</span>
                    <span className="detail-value">{selectedTask.completedAt}</span>
                  </div>
                )}
              </div>

              <div className="logs-section">
                <h4>执行日志</h4>
                {logsLoading ? (
                  <div className="loading">加载日志...</div>
                ) : logs.length === 0 ? (
                  <div className="empty-logs">暂无日志</div>
                ) : (
                  <div className="logs-list">
                    {logs.map(log => (
                      <div key={log.id} className="log-item">
                        <span className="log-time">{log.createdAt.split("T")[1]?.split(".")[0]}</span>
                        <span className="log-level" style={{ color: LEVEL_COLORS[log.level] }}>
                          [{log.level}]
                        </span>
                        <span className="log-message">{log.message}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </>
          ) : (
            <div className="detail-empty">
              <p>选择一个任务查看详情</p>
            </div>
          )}
        </div>
      </div>

      {/* 创建 Modal */}
      {showCreateModal && (
        <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3>新建同步任务</h3>
              <button className="modal-close" onClick={() => setShowCreateModal(false)}>✕</button>
            </div>
            <div className="modal-body">
              <p className="sync-mode-label">选择同步模式：</p>
              <div className="sync-mode-options">
                <button 
                  className="sync-mode-btn"
                  onClick={() => handleTriggerSync("full")}
                >
                  <div className="mode-title">全量同步</div>
                  <div className="mode-desc">重新同步所有数据</div>
                </button>
                <button 
                  className="sync-mode-btn"
                  onClick={() => handleTriggerSync("incremental")}
                >
                  <div className="mode-title">增量同步</div>
                  <div className="mode-desc">仅同步新增和变更数据</div>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}