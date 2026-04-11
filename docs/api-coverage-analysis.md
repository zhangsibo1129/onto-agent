# 前端 API 覆盖度分析

> 分析时间：2026-04-12
> 分析范围：onto-agent-web/src/pages/ + src/services/

---

## 总览

| 分类 | API 数量 | 已连接前端 | 未连接 | 说明 |
|------|---------|---------|--------|------|
| 本体 Ontology | 5 | 4 | 1 | PUT 缺失 |
| Class | 4 | 2 | 2 | update/delete 无 UI |
| DataProperty | 4 | 2 | 2 | update/delete 无 UI |
| ObjectProperty | 4 | 2 | 2 | update/delete 无 UI |
| Individual | 6 | 2 | 4 | detail/edit/delete 无 UI |
| Version | 8 | 8 | 0 | ✅ 全部连接 |
| Sync | 5 | 0 | 5 | Sync.tsx 为 mock 数据 |
| Mapping | 4 | 0 | 4 | Mapping.tsx 为 mock 数据 |
| Query | 7 | 5 | 2 | saved PUT/DELETE 无 UI |
| Datasource | 9 | 7 | 2 | update 无 modal |
| Admin | 4 | 0 | 4 | 无对应 UI 页面 |
| **合计** | **60** | **~36** | **~24** | |

---

## 详细分析

### 1. Ontologies.tsx ✅

| API | 方法 | 路由 | UI 操作 | 状态 |
|-----|------|------|---------|------|
| list | GET | `/api/ontologies` | 页面加载自动获取 | ✅ |
| createOntology | POST | `/api/ontologies` | "创建本体" 按钮 → modal | ✅ |
| deleteOntology | DELETE | `/api/ontologies/{id}` | 列表删除按钮 | ✅ |
| getOntology (getDetail) | GET | `/api/ontologies/{id}/detail` | 点击本体进入 Modeling | ✅ |
| **updateOntology** | **PUT** | **`/api/ontologies/{id}`** | ❌ 无 UI（未连接到前端）| ⚠️ |

---

### 2. OntologyModeling.tsx ⚠️ 部分连接

#### Class 操作
| API | 方法 | 路由 | UI 操作 | 状态 |
|-----|------|------|---------|------|
| getClasses | GET | `/{id}/classes` | 左侧栏显示 | ✅ |
| createClass | POST | `/{id}/classes` | "添加类" 按钮 | ✅ |
| **updateClass** | **PUT** | **`/{id}/classes/{cid}`** | ❌ 无 UI | ⚠️ |
| **deleteClass** | **DELETE** | **`/{id}/classes/{cid}`** | ❌ 无 UI | ⚠️ |

#### DataProperty 操作
| API | 方法 | 路由 | UI 操作 | 状态 |
|-----|------|------|---------|------|
| getDataProperties | GET | `/{id}/data-properties` | 左侧栏显示 | ✅ |
| createDataProperty | POST | `/{id}/data-properties` | "添加属性" 按钮 | ✅ |
| **updateDataProperty** | **PUT** | **`/{id}/data-properties/{pid}`** | ❌ 无 UI | ⚠️ |
| **deleteDataProperty** | **DELETE** | **`/{id}/data-properties/{pid}`** | ❌ 无 UI | ⚠️ |

#### ObjectProperty 操作
| API | 方法 | 路由 | UI 操作 | 状态 |
|-----|------|------|---------|------|
| getObjectProperties | GET | `/{id}/object-properties` | 左侧栏显示 | ✅ |
| createObjectProperty | POST | `/{id}/object-properties` | "添加关系" 按钮 | ✅ |
| **updateObjectProperty** | **PUT** | **`/{id}/object-properties/{pid}`** | ❌ 无 UI | ⚠️ |
| **deleteObjectProperty** | **DELETE** | **`/{id}/object-properties/{pid}`** | ❌ 无 UI | ⚠️ |

#### Individual 操作
| API | 方法 | 路由 | UI 操作 | 状态 |
|-----|------|------|---------|------|
| getIndividuals | GET | `/{id}/individuals` | 列表加载 | ✅ |
| createIndividual | POST | `/{id}/individuals` | "添加实例" 按钮 | ✅ |
| **getIndividual** | **GET** | **`/{id}/individuals/{iid}`** | ❌ 无详情页/详情 panel | ⚠️ |
| **updateIndividual** | **PUT** | **`/{id}/individuals/{iid}`** | ❌ 无 UI | ⚠️ |
| **deleteIndividual** | **DELETE** | **`/{id}/individuals/{iid}`** | ❌ 无 UI | ⚠️ |

#### 其他
| API | 方法 | 路由 | UI 操作 | 状态 |
|-----|------|------|---------|------|
| getDetail | GET | `/{id}/detail` | 页面加载 | ✅ |
| getAnnotationProperties | GET | `/{id}/annotation-properties` | 左侧栏显示 | ✅ |
| createAnnotationProperty | POST | `/{id}/annotation-properties` | 按钮存在 | ✅ |

---

### 3. Versions.tsx ✅ 全部连接

| API | 方法 | 路由 | UI 操作 | 状态 |
|-----|------|------|---------|------|
| listVersions | GET | `/{id}/versions` | 加载 | ✅ |
| createVersion | POST | `/{id}/versions` | "创建版本" 按钮 | ✅ |
| getVersion | GET | `/{id}/versions/{v}` | 点击版本号查看详情 | ✅ |
| deleteVersion | DELETE | `/{id}/versions/{v}` | 删除按钮 | ✅ |
| rollbackVersion | POST | `/{id}/rollback` | 回滚按钮 | ✅ |
| compareVersions | GET | `/{id}/versions/compare` | 版本对比 | ✅ |
| publishOntology | POST | `/{id}/publish` | 发布按钮 | ✅ |
| unpublishOntology | POST | `/{id}/unpublish` | 取消发布按钮 | ✅ |

---

### 4. Query.tsx ⚠️ 部分连接

| API | 方法 | 路由 | UI 操作 | 状态 |
|-----|------|------|---------|------|
| executeSparql | POST | `/{id}/sparql` | "执行查询" 按钮 | ✅ |
| getQueryHistory | GET | `/{id}/sparql/history` | 右侧历史列表 | ✅ |
| getSavedQueries | GET | `/{id}/sparql/saved` | 右侧已保存列表 | ✅ |
| saveQuery | POST | `/{id}/sparql/saved` | "保存查询" 按钮 → modal | ✅ |
| **updateSavedQuery** | **PUT** | **`/{id}/sparql/saved/{sid}`** | ❌ 无 UI | ⚠️ |
| **deleteSavedQuery** | **DELETE** | **`/{id}/sparql/saved/{sid}`** | ⚠️ 删除按钮存在但未连接 API | ⚠️ |
| nlToSparql | POST | `/{id}/nl-query` | NLQuery.tsx 独立页面 | ✅ |

> ⚠️ `deleteSavedQuery` 在 Query.tsx 中有"删除"文字链接，但未确认是否调用了真实 API

---

### 5. NLQuery.tsx ✅ 已连接

| API | 方法 | 路由 | UI 操作 | 状态 |
|-----|------|------|---------|------|
| nlToSparql | POST | `/{id}/nl-query` | 发送按钮 | ✅ |
| executeSparql | POST | `/{id}/sparql` | 自动触发 | ✅ |
| getSavedQueries | GET | `/{id}/sparql/saved` | 暂未使用 | — |

---

### 6. Sync.tsx ❌ 全部 Mock

| API | 方法 | 路由 | UI 操作 | 状态 |
|-----|------|------|---------|------|
| **getSyncTasks** | **GET** | **`/{id}/sync/tasks`** | ❌ 静态 mock 数据 | ❌ |
| **createSyncTask** | **POST** | **`/{id}/sync/tasks`** | ❌ 无"新建任务"按钮 | ❌ |
| **getSyncTask** | **GET** | **`/{id}/sync/tasks/{tid}`** | ❌ mock | ❌ |
| **getSyncTaskLogs** | **GET** | **`/{id}/sync/tasks/{tid}/logs`** | ❌ mock | ❌ |
| **deleteSyncTask** | **DELETE** | **`/{id}/sync/tasks/{tid}`** | ❌ 无删除按钮 | ❌ |

---

### 7. Mapping.tsx ❌ 全部 Mock

| API | 方法 | 路由 | UI 操作 | 状态 |
|-----|------|------|---------|------|
| **getMappings** | **GET** | **`/{id}/mappings`** | ❌ 静态 mock 数据 | ❌ |
| **createMapping** | **POST** | **`/{id}/mappings`** | ❌ 无 UI | ❌ |
| **getMapping** | **GET** | **`/{id}/mappings/{mid}`** | ❌ 无详情 | ❌ |
| **deleteMapping** | **DELETE** | **`/{id}/mappings/{mid}`** | ❌ 无删除按钮 | ❌ |

---

### 8. DataSources.tsx ✅ 基本完整

| API | 方法 | 路由 | UI 操作 | 状态 |
|-----|------|------|---------|------|
| list | GET | `/api/datasources` | 页面加载 | ✅ |
| create | POST | `/api/datasources` | 添加 modal → 保存 | ✅ |
| delete | DELETE | `/api/datasources/{id}` | 删除按钮 | ✅ |
| testConnection | POST | `/api/datasources/test-connection` | 连接测试按钮 | ✅ |
| update (save) | PUT | `/api/datasources/{id}` | ⚠️ 编辑 modal 复用 create 逻辑，需确认 | ⚠️ |
| test | POST | `/api/datasources/{id}/test` | 保存后自动测试 | ✅ |

---

### 9. DatasourceDetail.tsx ✅ 基本完整

| API | 方法 | 路由 | UI 操作 | 状态 |
|-----|------|------|---------|------|
| get | GET | `/api/datasources/{id}` | 页面加载 | ✅ |
| scan | POST | `/api/datasources/{id}/scan` | "扫描数据源"按钮 | ✅ |
| getTables | GET | `/api/datasources/{id}/tables` | 扫描后显示表列表 | ✅ |
| getColumns | GET | `/api/datasources/{id}/tables/{name}/columns` | 点击表名显示列 | ✅ |

---

### 10. Admin API（无对应页面）❌

| API | 方法 | 路由 | UI 操作 | 状态 |
|-----|------|------|---------|------|
| health | GET | `/api/admin/health` | ❌ 无页面 | ❌ |
| backup | POST | `/api/admin/backup` | ❌ 无页面 | ❌ |
| compact | POST | `/api/admin/compact` | ❌ 无页面 | ❌ |
| stats | GET | `/api/admin/stats` | ❌ 无页面 | ❌ |

---

### 11. 其他页面（全部 Mock）❌

| 页面 | 状态 | 说明 |
|------|------|------|
| Dashboard.tsx | ❌ mock | 静态数据，无 API 调用 |
| Workbench.tsx | ❌ mock | 静态数据，无 API 调用 |
| Permissions.tsx | ❌ mock | 静态数据，无 API 调用 |
| ApiManagement.tsx | ❌ mock | 静态数据，无 API 调用 |

---

## 未连接 API 汇总（按优先级）

### 🔴 P0 - 核心功能缺失
| API | 页面 | 影响 |
|-----|------|------|
| `PUT /ontologies/{id}/classes/{cid}` | OntologyModeling | 无法编辑 Class |
| `DELETE /ontologies/{id}/classes/{cid}` | OntologyModeling | 无法删除 Class |
| `PUT /ontologies/{id}/data-properties/{pid}` | OntologyModeling | 无法编辑属性 |
| `DELETE /ontologies/{id}/data-properties/{pid}` | OntologyModeling | 无法删除属性 |
| `PUT /ontologies/{id}/object-properties/{pid}` | OntologyModeling | 无法编辑关系 |
| `DELETE /ontologies/{id}/object-properties/{pid}` | OntologyModeling | 无法删除关系 |
| `PUT /ontologies/{id}/individuals/{iid}` | OntologyModeling | 无法编辑 Individual |
| `DELETE /ontologies/{id}/individuals/{iid}` | OntologyModeling | 无法删除 Individual |
| `GET /ontologies/{id}/individuals/{iid}` | OntologyModeling | 无法查看 Individual 详情 |

### 🟡 P1 - 重要流程断点
| API | 页面 | 影响 |
|-----|------|------|
| Sync 5 个接口全部 | Sync.tsx | 同步管理页面无法使用 |
| Mapping 4 个接口全部 | Mapping.tsx | 映射管理页面无法使用 |
| `PUT /ontologies/{id}` | Ontologies.tsx | 无法修改本体信息 |

### 🟠 P2 - UI 体验优化
| API | 页面 | 影响 |
|-----|------|------|
| `PUT /{id}/sparql/saved/{sid}` | Query.tsx | 无法编辑已保存的查询 |
| Admin 4 个接口 | 无页面 | 系统管理无入口 |

### 🟢 P3 - 低优先级
| API | 页面 | 影响 |
|-----|------|------|
| Dashboard/Workbench/Permissions/ApiManagement 全部 | 4个页面 | 非核心页面，可后续迭代 |

---

## 下一步建议

1. **Phase 10.1（P0）**：OntologyModeling — 为 Class/Property/Individual 补全 update/delete UI（预计 4h）
2. **Phase 10.2（P1）**：Sync.tsx + Mapping.tsx — 重写连接真实 API（预计 3h）
3. **Phase 10.3（P1）**：Ontologies.tsx — 补全 updateOntology modal（预计 1h）
4. **Phase 10.4（P2）**：Query.tsx — 补全 saved query update UI（预计 1h）
