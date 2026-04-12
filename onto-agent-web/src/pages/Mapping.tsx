import { useState, useEffect, useCallback } from "react"
import { useParams } from "react-router-dom"
import { ontologyApi, type Mapping, type DataProperty } from "@/services/ontologyApi"
import "./Mapping.css"

export default function Mapping() {
  const { id: ontologyId } = useParams<{ id: string }>()
  
  const [mappings, setMappings] = useState<Mapping[]>([])
  const [properties, setProperties] = useState<DataProperty[]>([])
  const [loading, setLoading] = useState(true)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [selectedMapping, setSelectedMapping] = useState<Mapping | null>(null)

  // 加载映射和属性
  const fetchData = useCallback(async () => {
    if (!ontologyId) return
    setLoading(true)
    try {
      const [mappingsData, detail] = await Promise.all([
        ontologyApi.listMappings(ontologyId),
        ontologyApi.getDetail(ontologyId),
      ])
      setMappings(mappingsData)
      setProperties(detail.dataProperties)
    } catch (err) {
      console.error("加载失败:", err)
    } finally {
      setLoading(false)
    }
  }, [ontologyId])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  // 创建映射
  const handleCreateMapping = async (propertyName: string, columnName: string, transform?: string) => {
    if (!ontologyId) return
    try {
      await ontologyApi.createMapping(ontologyId, { propertyName, columnName, transform })
      fetchData()
      setShowCreateModal(false)
    } catch (err) {
      console.error("创建映射失败:", err)
    }
  }

  // 删除映射
  const handleDeleteMapping = async (propertyName: string) => {
    if (!ontologyId) return
    if (!confirm(`确定要删除 "${propertyName}" 的映射吗？`)) return
    try {
      await ontologyApi.deleteMapping(ontologyId, propertyName)
      if (selectedMapping?.propertyName === propertyName) {
        setSelectedMapping(null)
      }
      fetchData()
    } catch (err) {
      console.error("删除映射失败:", err)
    }
  }

  // 已映射和未映射
  const mappedProperties = properties.filter(p => mappings.some(m => m.propertyName === p.name))
  const unmappedProperties = properties.filter(p => !mappings.some(m => m.propertyName === p.name))

  if (loading) {
    return <div className="mapping-page"><div className="loading">加载中...</div></div>
  }

  return (
    <div className="mapping-page">
      {/* 头部 */}
      <div className="mapping-header">
        <div className="mapping-stats">
          <span>总属性: <strong>{properties.length}</strong></span>
          <span>已映射: <strong className="mapped-count">{mappedProperties.length}</strong></span>
          <span>未映射: <strong className="unmapped-count">{unmappedProperties.length}</strong></span>
        </div>
        <button className="btn btn-primary btn-sm" onClick={() => setShowCreateModal(true)}>
          + 添加映射
        </button>
      </div>

      <div className="mapping-layout">
        {/* 左侧：属性列表 */}
        <div className="mapping-panel">
          <div className="panel-title">未映射属性</div>
          <div className="property-list">
            {unmappedProperties.length === 0 ? (
              <div className="empty-text">所有属性已映射</div>
            ) : (
              unmappedProperties.map(prop => (
                <div key={prop.name} className="property-item unmapped">
                  <span className="property-name">{prop.displayName || prop.name}</span>
                  <span className="property-type">{prop.rangeType}</span>
                </div>
              ))
            )}
          </div>

          <div className="panel-title" style={{ marginTop: 'var(--space-4)' }}>已映射属性</div>
          <div className="property-list">
            {mappedProperties.length === 0 ? (
              <div className="empty-text">暂无映射</div>
            ) : (
              mappedProperties.map(prop => {
                const mapping = mappings.find(m => m.propertyName === prop.name)
                return (
                  <div key={prop.name} className="property-item mapped">
                    <div className="property-main">
                      <span className="property-name">{prop.displayName || prop.name}</span>
                      <span className="property-type">{prop.rangeType}</span>
                    </div>
                    <div className="property-actions">
                      <button 
                        className="btn-icon btn-icon-xs"
                        title="删除映射"
                        onClick={() => handleDeleteMapping(prop.name)}
                      >
                        ×
                      </button>
                    </div>
                  </div>
                )
              })
            )}
          </div>
        </div>

        {/* 中间：映射编辑器 */}
        <div className="mapping-center">
          <div className="mapping-arrows">
            {mappedProperties.map(prop => {
              const mapping = mappings.find(m => m.propertyName === prop.name)
              return (
                <div key={prop.name} className="mapping-row">
                  <div className="mapping-col source">{mapping?.columnName || '-'}</div>
                  <div className="mapping-arrow">→</div>
                  <div className="mapping-col target">{prop.name}</div>
                </div>
              )
            })}
          </div>
        </div>

        {/* 右侧：数据库列（模拟） */}
        <div className="mapping-panel">
          <div className="panel-title">数据源列</div>
          <div className="column-list">
            {/* 实际应从数据源API获取，这里模拟展示 */}
            {mappings.map(m => (
              <div key={m.columnName} className="column-item">
                <span className="column-name">{m.columnName}</span>
              </div>
            ))}
            {mappings.length === 0 && (
              <div className="empty-text">暂无映射</div>
            )}
          </div>
        </div>
      </div>

      {/* 创建 Modal */}
      {showCreateModal && (
        <MappingCreateModal 
          unmappedProperties={unmappedProperties}
          onClose={() => setShowCreateModal(false)}
          onSubmit={handleCreateMapping}
        />
      )}
    </div>
  )
}

// 创建映射 Modal 组件
function MappingCreateModal({ 
  unmappedProperties, 
  onClose, 
  onSubmit 
}: { 
  unmappedProperties: DataProperty[]
  onClose: () => void
  onSubmit: (propertyName: string, columnName: string, transform?: string) => void
}) {
  const [propertyName, setPropertyName] = useState("")
  const [columnName, setColumnName] = useState("")
  const [transform, setTransform] = useState("")

  const handleSubmit = () => {
    if (propertyName && columnName) {
      onSubmit(propertyName, columnName, transform || undefined)
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h3>添加映射</h3>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>
        <div className="modal-body">
          <div className="form-group">
            <label className="form-label">本体属性 *</label>
            <select 
              className="form-select"
              value={propertyName}
              onChange={e => setPropertyName(e.target.value)}
            >
              <option value="">选择属性</option>
              {unmappedProperties.map(p => (
                <option key={p.id} value={p.name}>
                  {p.displayName || p.name} ({p.rangeType})
                </option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">数据源列 *</label>
            <input 
              type="text" 
              className="form-input"
              placeholder="column_name"
              value={columnName}
              onChange={e => setColumnName(e.target.value)}
            />
          </div>
          <div className="form-group">
            <label className="form-label">转换函数（可选）</label>
            <input 
              type="text" 
              className="form-input"
              placeholder="e.g., TO_DATE({value}, 'YYYY-MM-DD')"
              value={transform}
              onChange={e => setTransform(e.target.value)}
            />
          </div>
        </div>
        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onClose}>取消</button>
          <button 
            className="btn btn-primary" 
            onClick={handleSubmit}
            disabled={!propertyName || !columnName}
          >
            添加
          </button>
        </div>
      </div>
    </div>
  )
}