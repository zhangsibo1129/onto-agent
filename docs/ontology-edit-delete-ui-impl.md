# OntologyModeling 编辑/删除 UI 实现总结

> 实现时间：2026-04-12
> 状态：待评审

---

## 修改文件清单

| 文件 | 变更内容 |
|------|----------|
| `src/services/ontologyApi.ts` | 新增 9 个 API 方法 |
| `src/pages/OntologyModeling.tsx` | 新增状态、handlers、编辑/删除 UI |
| `src/pages/OntologyModeling.css` | 新增按钮样式 |
| `src/components/ontology/IndividualCard.tsx` | 新增 onEdit prop |

---

## API 补全 (`ontologyApi.ts`)

```typescript
// 新增方法
updateOntology(ontologyId, dto)        // PUT /ontologies/{id}
updateClass(ontologyId, classId, dto)  // PUT /properties/{id}/classes/{cid}
deleteClass(ontologyId, classId)       // DELETE /properties/{id}/classes/{cid}
updateDataProperty(...)                // PUT /properties/{id}/data-properties/{pid}
deleteDataProperty(...)                // DELETE /properties/{id}/data-properties/{pid}
updateObjectProperty(...)              // PUT /properties/{id}/object-properties/{pid}
deleteObjectProperty(...)              // DELETE /properties/{id}/object-properties/{pid}
getIndividual(...)                     // GET /ontologies/{id}/individuals/{iid}
updateIndividual(...)                  // PUT /ontologies/{id}/individuals/{iid}
deleteIndividual(...)                  // DELETE /ontologies/{id}/individuals/{iid}
```

---

## UI 变更明细

### 1. 工具栏新增按钮

```
[添加类] [添加属性] [添加关系]
```

- 点击弹出对应的添加模态框（复用原有逻辑）

### 2. 类详情面板 (Entity Panel)

**头部新增按钮：**
- ✏️ 编辑按钮 → 打开编辑类模态框
- 🗑️ 删除按钮 → 打开删除确认模态框

### 3. 数据属性列表

**每行新增操作：**
- ✏️ 编辑按钮 → 打开编辑数据属性模态框
- 🗑️ 删除按钮 → 打开删除确认模态框

**标题栏新增：**
- `+ 添加` 链接 → 打开添加数据属性模态框

### 4. 对象属性面板 (Relation Panel)

**头部新增按钮：**
- ✏️ 编辑按钮 → 打开编辑对象属性模态框
- 🗑️ 删除按钮 → 打开删除确认模态框

### 5. 实例卡片 (IndividualCard)

**新增按钮：**
- `编辑` → 打开编辑实例模态框
- `删除` → 打开删除确认模态框

---

## 模态框设计

### 编辑模态框

复用添加模态框结构，预填充当前值：

| 实体类型 | 可编辑字段 |
|----------|-----------|
| Class | 显示名称、父类、描述 |
| DataProperty | 显示名称、所属类、数据类型 |
| ObjectProperty | 显示名称、源类、目标类 |
| Individual | 显示名称（属性值编辑待后续迭代） |

### 删除确认模态框

```
┌─────────────────────────────────┐
│  确认删除                    ✕  │
├─────────────────────────────────┤
│  确定要删除 "Customer" 吗？     │
│                                 │
│  删除类将同时删除其所有实例和   │
│  子类关系。                     │
├─────────────────────────────────┤
│         [取消]  [删除]          │
└─────────────────────────────────┘
```

---

## 状态管理

```typescript
// 新增状态
const [showEditModal, setShowEditModal] = useState<...>(null)
const [editingEntity, setEditingEntity] = useState<...>(null)
const [showDeleteConfirm, setShowDeleteConfirm] = useState<...>(null)

// 新增 handlers
handleUpdateClass()
handleUpdateDataProperty()
handleUpdateObjectProperty()
handleUpdateIndividual()
handleDeleteClass()
handleDeleteDataProperty()
handleDeleteObjectProperty()
handleDeleteIndividual()
```

---

## CSS 新增样式

```css
/* Panel Actions - 面板头部操作按钮组 */
.panel-actions { ... }

/* Icon Buttons - 图标按钮 */
.btn-icon { ... }
.btn-icon.btn-icon-danger { ... }
.btn-icon.btn-icon-xs { ... }

/* Prop Actions - 属性行操作 */
.prop-actions { ... }
.prop-row:hover .prop-actions { opacity: 1; }

/* Link Buttons - 链接样式按钮 */
.btn-link { ... }
.btn-link.btn-link-xs { ... }

/* Button Group Add - 添加按钮组 */
.btn-group-add { ... }
```

---

## 测试建议

### 手动测试用例

| # | 操作 | 预期结果 |
|---|------|----------|
| 1 | 点击"添加类"按钮 | 弹出添加类模态框 |
| 2 | 点击"添加属性"按钮 | 弹出添加数据属性模态框，所属类默认当前选中类 |
| 3 | 点击"添加关系"按钮 | 弹出添加对象属性模态框 |
| 4 | 选中类 → 点击编辑按钮 | 弹出编辑类模态框，显示当前值 |
| 5 | 选中类 → 点击删除按钮 | 弹出删除确认模态框 |
| 6 | 确认删除类 | 类从列表中移除 |
| 7 | 编辑数据属性 | 属性更新，列表刷新 |
| 8 | 删除数据属性 | 属性从列表中移除 |
| 9 | 点击对象属性连线 → 编辑按钮 | 弹出编辑对象属性模态框 |
| 10 | 点击实例卡片"编辑"按钮 | 弹出编辑实例模态框 |
| 11 | 点击实例卡片"删除"按钮 | 弹出删除确认模态框 |

---

## 后续优化建议

1. **Individual 属性值编辑**：当前只支持修改displayName，属性值编辑需要更复杂的表单
2. **批量操作**：支持多选后批量删除
3. **撤销/重做**：撤销删除操作
4. **键盘快捷键**：Ctrl+E 编辑、Delete 删除
5. **权限控制**：根据用户权限显示/隐藏编辑删除按钮

---

## 待确认事项

1. API 路径是否正确？`/properties/{id}/classes/{cid}` 还是 `/ontologies/{id}/classes/{cid}`？
2. 删除类时是否需要确认其子类和实例的处理逻辑？
3. 编辑操作是否需要乐观更新（先更新 UI，后同步后端）？

---

**请评审后确认是否可以推送代码。**