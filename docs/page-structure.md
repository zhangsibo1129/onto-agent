# OntoAgent 页面结构文档

本文档描述 OntoAgent 平台的页面组织结构、路由设计和响应式策略。

---

## 1. 页面目录结构

```
ui-prototype/
├── index.html                    # 仪表盘（首页）
├── css/
│   ├── design-system.css         # 设计系统样式
│   └── layout.css                # 布局辅助样式
└── pages/
    ├── data-sources.html         # 数据源列表
    ├── datasource-detail.html    # 数据源详情
    ├── ontologies-list.html      # 本体列表
    ├── ontologies.html           # 本体建模画布
    ├── mapping.html              # 数据映射
    ├── versions.html             # 版本管理
    ├── query.html                # 语义查询
    ├── nl-query.html             # 自然语言查询
    ├── workbench.html            # 查询工作台
    ├── sync.html                 # 数据同步
    ├── permissions.html          # 权限管理
    └── api-management.html       # API 管理
```

---

## 2. 页面层级

### 一级页面（直接访问）

| 页面 | 文件 | 说明 |
|------|------|------|
| 仪表盘 | `index.html` | 首页概览 |
| 数据源 | `pages/data-sources.html` | 数据源列表 |
| 本体列表 | `pages/ontologies-list.html` | 本体列表管理 |
| 语义查询 | `pages/query.html` | SPARQL 查询 |
| 自然语言查询 | `pages/nl-query.html` | AI 查询 |
| 版本管理 | `pages/versions.html` | 版本历史 |
| 权限管理 | `pages/permissions.html` | 权限配置 |
| API 管理 | `pages/api-management.html` | API 文档 |

### 二级页面（通过列表页进入）

| 页面 | 父级页面 | 说明 |
|------|----------|------|
| 数据源详情 | 数据源列表 | 数据源详细信息 |
| 本体建模 | 本体列表 | 本体编辑画布 |
| 查询工作台 | 语义查询 | 高级查询界面 |
| 数据同步 | 版本管理 | 同步任务列表 |
| 数据映射 | 本体列表 | 映射配置 |

---

## 3. 布局结构

### 整体布局

```
┌─────────────────────────────────────────────────────┐
│                    Header (56px)                    │
├────────────┬────────────────────────────────────────┤
│            │                                        │
│  Sidebar   │                                        │
│  (260px)   │           Main Content                 │
│            │                                        │
│            │                                        │
│            │                                        │
├────────────┴────────────────────────────────────────┤
│                    (Page Content)                   │
└─────────────────────────────────────────────────────┘
```

### 侧边栏结构

```
┌──────────────────────┐
│      Logo 区域        │  高度: 64px
├──────────────────────┤
│                      │
│    Navigation        │  可滚动区域
│    (flex: 1)         │
│                      │
│                      │
├──────────────────────┤
│    User Footer       │  高度: 72px
└──────────────────────┘
```

### 导航分组

```html
<nav class="sidebar-nav">
  <!-- 分组 1 -->
  <div class="nav-section">
    <div class="nav-section-title">分组标题</div>
    <a href="..." class="nav-item active">
      <span class="nav-icon">◉</span>
      <span>导航项</span>
      <span class="nav-badge">3</span>
    </a>
  </div>
  <!-- 更多分组 -->
</nav>
```

### 用户信息区域

```html
<div class="sidebar-footer">
  <div class="user-avatar">A</div>
  <div class="user-info">
    <div class="user-name">Admin</div>
    <div class="user-role">系统管理员</div>
  </div>
</div>
```

---

## 4. 页面内容区域结构

### 标准页面布局

```
┌─────────────────────────────────────────────────┐
│                   Header (56px)                 │
├─────────────────────────────────────────────────┤
│                                                 │
│   Page Header (可选)                            │
│   - 页面标题 + 描述                              │
│   - 操作按钮                                    │
│                                                 │
├─────────────────────────────────────────────────┤
│                                                 │
│   Stats Grid (可选)                             │
│   - 统计卡片区域                                 │
│                                                 │
├─────────────────────────────────────────────────┤
│                                                 │
│   Toolbar (可选)                                │
│   - 搜索 + 筛选 + 视图切换                       │
│                                                 │
├─────────────────────────────────────────────────┤
│                                                 │
│   Content Area                                  │
│   - 表格 / 卡片 / 表单 / 图表                     │
│                                                 │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## 5. 响应式断点

### 断点定义

| 名称 | 宽度 | 侧边栏 | 说明 |
|------|------|--------|------|
| Mobile | < 768px | 隐藏 | 移动设备 |
| Tablet | 768px - 1024px | 折叠 (64px) | 平板 |
| Desktop | > 1024px | 展开 (260px) | 桌面 |

### 响应式样式

```css
/* 移动端 */
@media (max-width: 768px) {
  :root {
    --sidebar-width: 0px;
    --header-height: 56px;
  }
  
  .sidebar {
    transform: translateX(-100%);
    position: fixed;
    z-index: 100;
  }
  
  .sidebar.open {
    transform: translateX(0);
  }
}

/* 平板 */
@media (min-width: 769px) and (max-width: 1024px) {
  :root {
    --sidebar-width: 64px;
  }
  
  .logo-text,
  .nav-section-title,
  .nav-item span:not(.nav-icon):not(.nav-badge),
  .user-info {
    display: none;
  }
  
  .nav-item {
    justify-content: center;
    padding: var(--space-2);
  }
  
  .nav-icon {
    margin-right: 0;
  }
}

/* 桌面 */
@media (min-width: 1025px) {
  :root {
    --sidebar-width: 260px;
  }
}
```

---

## 6. 路由结构（建议）

```json
{
  "/": "index.html",
  "/data-sources": "pages/data-sources.html",
  "/data-sources/:id": "pages/datasource-detail.html",
  "/ontologies": "pages/ontologies-list.html",
  "/ontologies/:id": "pages/ontologies.html",
  "/mapping": "pages/mapping.html",
  "/query": "pages/query.html",
  "/query/workbench": "pages/workbench.html",
  "/query/nl": "pages/nl-query.html",
  "/versions": "pages/versions.html",
  "/sync": "pages/sync.html",
  "/permissions": "pages/permissions.html",
  "/api": "pages/api-management.html"
}
```

---

## 7. 导航链接映射

### 侧边栏导航项

| 菜单分组 | 导航项 | 目标页面 | 图标 |
|----------|--------|----------|------|
| 概览 | 仪表盘 | `index.html` | ◉ |
| 数据管理 | 数据源 | `pages/data-sources.html` | ⬡ |
| 数据管理 | 本体管理 | `pages/ontologies-list.html` | ◈ |
| 数据管理 | 数据映射 | `pages/mapping.html` | ⇄ |
| 查询与分析 | 语义查询 | `pages/query.html` | ⌘ |
| 查询与分析 | 自然语言查询 | `pages/nl-query.html` | ◉ (AI) |
| 查询与分析 | 查询工作台 | `pages/workbench.html` | ⚙ |
| 系统 | 版本管理 | `pages/versions.html` | ⧖ |
| 系统 | 数据同步 | `pages/sync.html` | ⟳ |
| 系统 | 权限管理 | `pages/permissions.html` | ⚿ |
| 系统 | API 管理 | `pages/api-management.html` | ⊞ |

---

## 8. 面包屑层级

### 页面面包屑定义

| 页面 | 面包屑路径 |
|------|-----------|
| 仪表盘 | 首页 / 仪表盘 |
| 数据源 | 首页 / 数据源 / 数据源管理 |
| 数据源详情 | 首页 / 数据源 / 数据源管理 / 数据源名称 |
| 本体列表 | 首页 / 本体 / 本体列表 |
| 本体建模 | 首页 / 本体 / 本体列表 / 本体名称 |
| 数据映射 | 首页 / 本体 / 数据映射 |
| 语义查询 | 首页 / 查询 / 语义查询 |
| 自然语言查询 | 首页 / 查询 / 自然语言查询 |
| 查询工作台 | 首页 / 查询 / 语义查询 / 工作台 |
| 版本管理 | 首页 / 系统 / 版本管理 |
| 数据同步 | 首页 / 系统 / 数据同步 |
| 权限管理 | 首页 / 系统 / 权限管理 |
| API 管理 | 首页 / 系统 / API 管理 |

---

## 9. 模态框使用场景

| 模态框 | 触发位置 | 用途 |
|--------|----------|------|
| 添加数据源 | 数据源列表页 | 新建数据源 |
| 添加本体 | 本体列表页 | 新建本体 |
| 编辑属性 | 本体建模页 | 编辑对象类型属性 |
| 确认删除 | 列表页 | 删除确认 |
| 执行查询 | 查询页 | 查询结果展示 |

---

## 10. 组件可见性规则

### 仪表盘（首页）

- 侧边栏 ✓
- Header ✓
- Page Header ✓
- Stats Grid ✓
- Quick Actions ✓
- Recent Tables ✓
- Recent Activity ✓

### 列表页（数据源、本体）

- 侧边栏 ✓
- Header ✓
- Page Header ✓
- Stats Grid (部分页面)
- Toolbar (搜索/筛选)
- Table / Card Grid

### 详情页（数据源详情）

- 侧边栏 ✓
- Header ✓
- Page Header ✓
- Detail Cards
- Related Tables

### 建模页（本体建模）

- 侧边栏 ✓
- Header ✓
- Canvas Area (主体)
- Property Panel
- Toolbar

### 查询页

- 侧边栏 ✓
- Header ✓
- Query Input
- Results Area
- Query History
