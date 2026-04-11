# 本体管理相关页面设计缺陷与完善建议

> 分析时间：2026-04-12

---

## 页面概览

| 页面 | 文件 | 代码行数 | 状态 |
|------|------|----------|------|
| 本体列表 | Ontologies.tsx | 246 | ⚠️ 部分功能缺失 |
| 本体建模 | OntologyModeling.tsx | 1104 | ✅ 刚补全 |
| 版本管理 | Versions.tsx | 572 | ⚠️ 待完善 |
| SPARQL查询 | Query.tsx | 399 | ⚠️ 待完善 |
| 自然语言查询 | NLQuery.tsx | 251 | ⚠️ 待完善 |
| 同步管理 | Sync.tsx | 213 | ❌ Mock |
| 映射管理 | Mapping.tsx | 185 | ❌ Mock |

---

## 1. Ontologies.tsx (本体列表页)

### ✅ 现有能力
- 本体列表展示（卡片形式）
- 搜索 + 状态筛选
- 创建本体（Modal）
- 删除本体
- 状态徽章（已发布/草稿）

### ❌ 设计缺陷

| # | 缺陷 | 严重程度 | 说明 |
|---|------|---------|------|
| 1 | 无编辑本体功能 | P0 | 点击卡片直接跳转详情，无编辑入口 |
| 2 | 删除使用原生confirm | P1 | 不符合设计规范 |
| 3 | 卡片无选中高亮 | P2 | 不可感知当前选中态 |
| 4 | 无排序功能 | P2 | 仅搜索+筛选，无创建时间排序 |
| 5 | baseIri 无校验 | P1 | 输入随意字符串不报错 |
| 6 | 删除无二次确认 | P0 | 直接删除，缺少安全保护 |

### 💡 完善建议

```typescript
// 建议1: 添加编辑功能
// 方案A: 在卡片上添加编辑按钮 → Modal
// 方案B: 点击跳转建模页，顶部有"编辑本体"按钮

// 建议2: 自定义删除确认 Modal
<Modal>
  <div className="confirm-content">
    <h3>确认删除</h3>
    <p>确定要删除 "{ontology.name}" 吗？</p>
    <p className="warning">此操作不可恢复</p>
  </div>
  <button className="btn btn-danger">删除</button>
</Modal>

// 建议3: 卡片选中态
<div 
  className={`ontology-card ${selectedId === o.id ? 'selected' : ''}`}
  onClick={() => setSelectedId(o.id)}
>
```

---

## 2. OntologyModeling.tsx (本体建模页)

### ✅ 现有能力
- 本体图可视化（OntologyGraph）
- 类/属性/关系 管理面板
- 实例列表 + IndividualCard
- 实例搜索
- 刚补全：编辑/删除功能

### ❌ 设计缺陷

| # | 缺陷 | 严重程度 | 说明 |
|---|------|---------|------|
| 1 | 搜索框仅UI无功能 | P1 | Toolbar 有搜索框但无处理逻辑 |
| 2 | 导入导出按钮无功能 | P2 | 仅有点击事件无实际逻辑 |
| 3 | 无批量操作 | P2 | 不可多选批量删除 |
| 4 | 无键盘快捷键 | P2 | Ctrl+E/Delete 等 |
| 5 | 无撤销/重做 | P2 | 操作后不可逆 |
| 6 | 类面板属性列表无分页 | P2 | 属性多时卡顿 |
| 7 | 图谱缩放无边界 | P1 | 可无限放大缩小 |
| 8 | 无当前本体信息展示 | P2 | 标题栏无本体基础信息 |

### 💡 完善建议

```typescript
// 建议1: 搜索功能实现
const handleSearch = (keyword: string) => {
  // 搜索类名/属性名
  const matched = classes.filter(c => 
    c.name.includes(keyword) || c.displayName?.includes(keyword)
  )
  if (matched.length === 1) {
    setSelectedClassId(matched[0].id)  // 自动选中
  }
}

// 建议2: 键盘快捷键
useEffect(() => {
  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key === 'Delete' && selectedClassId) {
      setShowDeleteConfirm(...)
    }
    if ((e.ctrlKey || e.metaKey) && e.key === 'e') {
      e.preventDefault()
      setShowEditModal(...)  // 编辑选中项
    }
  }
  window.addEventListener('keydown', handleKeyDown)
  return () => window.removeEventListener('keydown', handleKeyDown)
}, [selectedClassId])

// 建议3: 导入导出功能
const handleExport = async () => {
  // 导出 turtle/JSON-LD
  const blob = await ontologyApi.exportOntology(id)
  download(blob, `${ontology.name}.ttl`)
}
```

---

## 3. Versions.tsx (版本管理页)

### ✅ 现有能力
- 本体选择器
- 版本列表（表格形式）
- 创建版本
- 发布/取消发布
- 回滚
- 版本对比

### ❌ 设计缺陷

| # | 缺陷 | 严重程度 | 说明 |
|---|------|---------|------|
| 1 | 版本详情仅JSON | P1 | 无格式化展示，无树形展开 |
| 2 | 对比结果仅文本 | P1 | diff 文本，无可视化差异 |
| 3 | 回滚无二次确认 | P0 | 直接回滚，风险高 |
| 4 | 发布时间线不直观 | P2 | 纯表格，无时间轴展示 |
| 5 | 版本无标签功能 | P2 | 不可标记重要版本 |

### 💡 完善建议

```typescript
// 建议1: 版本详情优化
<VersionDetailModal>
  {/* 使用可折叠的树形结构 */}
  <TreeView data={versionDetail.classes} />
  <TreeView data={versionDetail.properties} />
  <TreeView data={versionDetail.individuals} />
</VersionDetailModal>

// 建议2: 版本对比可视化
<CompareView>
  <DiffTable
    added={diff.added.map(c => ({...c, status: 'green'}))}
    removed={diff.removed.map(c => ({...c, status: 'red'}))}
    changed={diff.changed.map(c => ({...c, status: 'yellow'}))}
  />
</CompareView>

// 建议3: 回滚二次确认
const handleRollback = async () => {
  if (!confirm(`确定要回滚到 ${version.version} 吗？`)) return
  // 新增：显示影响范围
  const impact = await ontologyApi.previewRollback(id, version.version)
  if (confirm(`将影响 ${impact.deletedCount} 个实例，是否继续？`)) {
    await ontologyApi.rollbackVersion(...)
  }
}
```

---

## 4. Query.tsx (SPARQL查询页)

### ✅ 现有能力
- 本体选择
- SPARQL 编辑器（文本）
- 查询执行
- 结果展示（table/json/raw）
- 查询历史
- 已保存查询

### ❌ 设计缺陷

| # | 缺陷 | 严重程度 | 说明 |
|---|------|---------|------|
| 1 | 无保存查询编辑 | P0 | API 有方法，UI 无入口 |
| 2 | 结果仅table/json | P1 | 无图可视化 |
| 3 | 无导入导出query | P2 | 不可导入.sparql 文件 |
| 4 | 无自动补全 | P2 | SPARQL关键词无提示 |
| 5 | 执行无超时设置 | P1 | 长时间查询无响应 |
| 6 | Visual查询模式无UI | P2 | tab 有但组件空 |

### 💡 完善建议

```typescript
// 建议1: 保存查询编辑 Modal（复用保存弹窗，区分新建/编辑）
<SaveQueryModal mode={isEditing ? 'edit' : 'create'}>
  <input name="name" defaultValue={query.name} />
  <textarea query={query.text} />
</SaveQueryModal>

// 建议2: 超时设置
const handleExecute = async () => {
  const controller = new AbortController()
  setTimeout(() => controller.abort(), 30000)  // 30s 超时
  
  await executeSparql(id, query, { signal: controller.signal })
}

// 建议3: SPARQL 自动补全
// 使用 CodeMirror + sparql-abbrev 插件
<CodeMirror
  extensions={[autocomplete()]}
/>
```

---

## 5. NLQuery.tsx (自然语言查询页)

### ✅ 现有能力
- 本体选择
- 自然语言输入
- 自动转换为SPARQL
- 执行结果展示

### ❌ 设计缺陷

| # | 缺陷 | 严重程度 | 说明 |
|---|------|---------|------|
| 1 | 无历史会话 | P2 | 每次刷新清空 |
| 2 | Chat窗口仅单轮 | P2 | 无多轮对话 |
| 3 | 无保存会话 | P2 | 不可保存对话 |
| 4 | 转换结果不可编辑 | P1 | Sparql 仅展示不可修改 |
| 5 | 无复制SPASQL | P2 | 不可一键复制 |

### 💡 完善建议

```typescript
// 建议1: 历史会话存储
const [conversations, setConversations] = useState<Conversation[]>([])

// 建议2: 会话列表 Sidebar
<div className="chat-sidebar">
  {conversations.map(c => (
    <ChatSession 
      title={c.title} 
      onClick={() => loadConversation(c.id)}
    />
  ))}
</div>

// 建议3: 可编辑的SPARQL
<SparqlEditor 
  value={sparql} 
  onChange={setSparql}
  language="sparql"
/>
```

---

## 6. Sync.tsx (同步管理页) — 最严重

### ❌ 致命问题

| # | 缺陷 | 严重程度 | 说明 |
|---|------|---------|------|
| 1 | **全Mock数据** | P0 | 页面完全不可用 |
| 2 | 无API调用 | P0 | 未连接后端 |
| 3 | 无任务创建UI | P0 | 仅有展示列表 |

### 🔴 需要全面重写

```typescript
// 后端接口参考
// GET    /api/ontologies/{id}/sync/tasks
// POST   /api/ontologies/{id}/sync/tasks
// GET    /api/ontologies/{id}/sync/tasks/{tid}
// DELETE /api/ontologies/{id}/sync/tasks/{tid}
// GET    /api/ontologies/{id}/sync/tasks/{tid}/logs

// 需要实现的 UI
export default function Sync() {
  const [tasks, setTasks] = useState<SyncTask[]>([])
  
  // 加载任务列表
  useEffect(() => {
    ontologyApi.listSyncTasks(ontologyId).then(setTasks)
  }, [ontologyId])
  
  // 创建任务 Modal
  const [showCreateModal, setShowCreateModal] = useState(false)
  
  // 创建任务
  const handleCreate = async (config: SyncConfig) => {
    await ontologyApi.createSyncTask(ontologyId, config)
    refreshTasks()
  }
  
  return (
    <>
      <SyncTaskList tasks={tasks} onCreate={setShowCreateModal} />
      <CreateTaskModal open={showCreateModal} onClose={...} />
    </>
  )
}
```

---

## 7. Mapping.tsx (映射管理页) — 最严重

### ❌ 致命问题

| # | 缺陷 | 严重程度 | 说明 |
|---|------|---------|------|
| 1 | **全Mock数据** | P0 | 页面完全不可用 |
| 2 | 无API调用 | P0 | 未连接后端 |
| 3 | 映射操作无保存 | P0 | 仅展示 |
| 4 | 无新增映射UI | P0 | 不可创建映射 |

### 🔴 需要全面重写

```typescript
// 后端接口参考
// GET    /api/ontologies/{id}/mappings
// POST   /api/ontologies/{id}/mappings
// DELETE /api/ontologies/{id}/mappings/{mid}

export default function Mapping() {
  const [mappings, setMappings] = useState<Mapping[]>([])
  
  // 加载映射
  useEffect(() => {
    ontologyApi.listMappings(ontologyId).then(setMappings)
  }, [ontologyId])
  
  // 可视化映射编辑器
  return (
    <MappingEditor
      sourceColumns={dbColumns}
      targetProperties={ontologyProperties}
      mappings={mappings}
      onSave={handleSaveMapping}
    />
  )
}
```

---

## 优先级排序

### 🔴 P0 - 阻断级

| 页面 | 问题 | 修复建议 |
|-------|------|----------|
| Sync.tsx | 全Mock → **重写** | 连接后端 API + 创建任务 Modal |
| Mapping.tsx | 全Mock → **重写** | 连接后端 API + 映射编辑器 |
| Ontologies.tsx | 无编辑功能 | 添加 updateOntology Modal |
| OntologyModeling.tsx | 回滚无确认 | 添加二次确认 Modal |

### 🟡 P1 - 重要

| 页面 | 问题 | 修复建议 |
|-------|------|----------|
| Versions.tsx | 版本详情无树形 | 使用 TreeView 组件 |
| Versions.tsx | 对比结果文本 | 实现 Diff 可视化 |
| Query.tsx | 结果无图可视化 | 接入图可视化库 |
| NLQuery.tsx | Sparql不可编辑 | 改为 CodeEditor |

### 🟠 P2 - 优化

| 页面 | 问题 | 修复建议 |
|-------|------|----------|
| OntologyModeling.tsx | 搜索无功能 | 实现类/属性搜索 |
| OntologyModeling.tsx | 无键盘快捷键 | 添加快捷键支持 |
| Query.tsx | 无自动补全 | 接入 CodeMirror |
| NLQuery.tsx | 无历史会话 | 添加会话存储 |

---

## 总结

| 严重程度 | 数量 | 占比 |
|---------|------|------|
| 🔴 阻断级 | 4 | 15% |
| 🟡 重要 | 5 | 19% |
| 🟠 优化 | 4 | 15% |
| ⚠️ 次要 | 13 | 50% |

**核心问题：Sync.tsx 和 Mapping.tsx 两个页面需要完全重写，预计工时 3-4 小时。**