# ABox 显示与查询功能设计方案

## 一、复用策略

### 现有可复用组件

| 组件 | 位置 | 复用方式 |
|------|------|----------|
| `entity-panel` | `OntologyModeling.tsx` | 复用面板结构，添加实例区域 |
| `relation-panel` | `OntologyModeling.tsx` | 复用弹出面板逻辑 |
| `OntologyGraph` | `OntologyGraph.tsx` | 复用图谱交互事件 |
| Class 选择逻辑 | `handleClassSelect` | 扩展为同时加载实例 |

### 复用模式

```
当前: 点击类 → 显示类详情面板 (entity-panel)
                    ├── 基本信息
                    ├── 数据属性
                    └── 关系

新增: 点击类 → 显示类详情 + 实例列表 (entity-panel)
                    ├── 基本信息
                    ├── 数据属性
                    ├── 关系
                    └── 实例列表 ← 新增 ABox 区域
```

---

## 二、UI 设计

### 2.1 扩展 entity-panel

```
┌──────────────────────────────────────────────────────────────┐
│  entity-panel                                                │
├──────────────────────────────────────────────────────────────┤
│  [基本信息]                                                  │
│    URL: http://example.org/Person                           │
│    父类: [Thing]                                           │
│                                                              │
│  [数据属性]                                                  │
│    hasName (string) [Func]                                 │
│    hasAge (integer) [Func]                                 │
│                                                              │
│  [关系]                                                      │
│    knows → Person                                          │
│    worksAt → Organization                                  │
│                                                              │
│  ────────────────────────────────────────────────────────── │
│                                                              │
│  [实例] 🔍 [搜索...]                              [+新建]   │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ 👤 Person_001                                         │ │
│  │    hasName: "张三"                                     │ │
│  │    hasAge: 25                                         │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ 👤 Person_002                                         │ │
│  │    hasName: "李四"                                     │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  [加载更多...]                                              │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 2.2 实例卡片设计

```
┌──────────────────────────────────────────────────────────────┐
│  👤 张三 (Person_001)                           [编辑] [×] │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  数据属性:                                                   │
│  ├─ hasName:  "张三"                                       │
│  ├─ hasAge:   25                                          │
│  └─ hasEmail: "zhangsan@example.com"                       │
│                                                              │
│  对象属性:                                                   │
│  ├─ knows:      👤 李四 (Person_002)                      │
│  └─ worksAt:    🏢 示例公司 (Organization_001)            │
│                                                              │
│  ────────────────────────────────────────────────────────── │
│  最后更新: 2024-01-15 10:30                                │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 2.3 查询功能

```
┌──────────────────────────────────────────────────────────────┐
│  [实例搜索]                                                │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  搜索框: [输入名称或属性值...              ] [🔍 搜索]    │
│                                                              │
│  筛选器:                                                     │
│  ├─ 按属性筛选:                                             │
│  │   hasName  [等于 ▼] ["张三"]                            │
│  │   hasAge   [大于 ▼] [18        ]                        │
│  │   [+ 添加条件]                                          │
│  │                                                            │
│  │   [清除筛选]  [应用筛选]                                │
│                                                              │
│  结果: 2 条                                                  │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ 👤 张三 (Person_001)                        [查看详情]  │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ 👤 张三丰 (Person_003)                     [查看详情]  │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 三、数据流设计

### 3.1 当前数据流

```
getDetail(id) → OntologyDetail
                      ├── classes[]
                      ├── dataProperties[]
                      ├── objectProperties[]
                      ├── annotationProperties[]
                      ├── individuals[]    ← 已支持但未使用
                      └── axioms[]
```

### 3.2 新增数据流

```
点击类 → 加载该类的实例
         │
         ├── GET /ontologies/{id}/individuals?classId={classId}
         │       ↓
         │   Individual[]
         │
         └── 显示在 entity-panel 的实例区域
```

---

## 四、API 设计

### 4.1 新增 API

| API | 方法 | 说明 |
|-----|------|------|
| `/ontologies/{id}/individuals` | GET | 获取所有实例 |
| `/ontologies/{id}/individuals?classId={classId}` | GET | 按类筛选实例 |
| `/ontologies/{id}/individuals?search={keyword}` | GET | 搜索实例 |
| `/ontologies/{id}/individuals/{indId}` | GET | 获取单个实例详情 |
| `/ontologies/{id}/individuals` | POST | 创建实例 |

### 4.2 查询参数

```
GET /ontologies/{id}/individuals?
    classId={classId}      # 按类筛选
    &search={keyword}      # 关键词搜索
    &page=1                # 分页
    &pageSize=20           # 每页数量
```

### 4.3 Individual 数据结构

```typescript
interface Individual {
  id: string
  ontologyId: string
  name: string              // e.g., "Person_001"
  displayName?: string       // e.g., "张三"
  description?: string
  
  // 类的类型
  types: string[]           // ["Person", "Thing"]
  
  // 属性值
  dataPropertyAssertions: {
    propertyId: string
    value: string | number | boolean
  }[]
  
  // 关系
  objectPropertyAssertions: {
    propertyId: string
    targetIndividualId: string
  }[]
}
```

---

## 五、实现计划

### Phase 1: 基础显示 (1天)

| 任务 | 文件 | 说明 |
|------|------|------|
| 获取实例 API | `GET /individuals?classId=x` | 按类获取实例 |
| 前端状态 | `useIndividuals()` hook | 管理实例数据 |
| 实例列表区域 | 修改 entity-panel | 在面板中添加实例列表 |
| 实例卡片组件 | `IndividualCard.tsx` | 显示单个实例 |

### Phase 2: 查询功能 (1天)

| 任务 | 文件 | 说明 |
|------|------|------|
| 搜索 API | `GET /individuals?search=x` | 关键词搜索 |
| 搜索框组件 | `IndividualSearch.tsx` | 搜索输入框 |
| 筛选器组件 | `IndividualFilter.tsx` | 属性筛选器 |

### Phase 3: 实例详情 (1天)

| 任务 | 文件 | 说明 |
|------|------|------|
| 实例详情弹窗 | `IndividualModal.tsx` | 查看/编辑实例 |
| 编辑实例 | `PUT /individuals/{id}` | 更新实例 |
| 删除实例 | `DELETE /individuals/{id}` | 删除实例 |

---

## 六、代码复用示例

### 6.1 扩展 entity-panel

```tsx
// OntologyModeling.tsx 修改

const [individuals, setIndividuals] = useState<Individual[]>([])

// 当选择类时，加载该类的实例
useEffect(() => {
  if (selectedClassId) {
    ontologyApi.getIndividuals(id, { classId: selectedClassId })
      .then(setIndividuals)
  }
}, [selectedClassId])

// 在 entity-panel 中添加实例区域
<div className="entity-panel">
  {/* ... 现有代码 ... */}
  
  {/* 新增: 实例区域 */}
  <div className="panel-section">
    <div className="section-title">
      实例 ({individuals.length})
      <input placeholder="搜索..." />
    </div>
    <IndividualList 
      individuals={individuals}
      onSelect={handleIndividualSelect}
    />
  </div>
</div>
```

### 6.2 复用属性显示逻辑

```tsx
// IndividualCard.tsx - 复用属性显示逻辑

<div className="individual-card">
  <div className="card-header">
    <span className="individual-name">
      {individual.displayName || individual.name}
    </span>
  </div>
  
  {/* 数据属性 - 复用现有属性行样式 */}
  <div className="data-properties">
    {individual.dataPropertyAssertions.map(assertion => {
      const prop = dataProperties.find(p => p.id === assertion.propertyId)
      return (
        <div className="prop-row">
          <span className="prop-name">{prop?.displayName || prop?.name}</span>
          <span className="prop-value">{assertion.value}</span>
        </div>
      )
    })}
  </div>
  
  {/* 对象属性 - 复用关系显示样式 */}
  <div className="object-properties">
    {individual.objectPropertyAssertions.map(assertion => {
      const target = individuals.find(i => i.id === assertion.targetIndividualId)
      return (
        <div className="relation-row">
          <span className="rel-name">{assertion.propertyId}</span>
          <span className="rel-target" onClick={() => selectIndividual(target)}>
            {target?.displayName || target?.name}
          </span>
        </div>
      )
    })}
  </div>
</div>
```

---

## 七、文件变更清单

### 新增文件

| 文件 | 说明 |
|------|------|
| `components/IndividualCard.tsx` | 实例卡片组件 |
| `components/IndividualSearch.tsx` | 搜索组件 |
| `components/IndividualModal.tsx` | 实例详情弹窗 |
| `components/IndividualList.tsx` | 实例列表组件 |

### 修改文件

| 文件 | 修改内容 |
|------|----------|
| `OntologyModeling.tsx` | 添加实例区域 |
| `OntologyModeling.css` | 添加实例样式 |
| `ontologyApi.ts` | 添加实例 API 方法 |
| `types/ontology.ts` | 添加 Individual 相关类型 |

---

## 八、关键设计决策

1. **实例显示在 entity-panel 内** - 不新增大面板，复用现有结构
2. **按需加载** - 选择类时才加载该类的实例，避免一次性加载过多
3. **搜索在服务端** - 避免前端大数据量筛选
4. **复用属性显示样式** - prop-row, relation-row 等已有样式

---

*设计时间: 2026-04-11*
