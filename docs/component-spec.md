# OntoAgent 组件规格说明

## 概述

本文档定义 OntoAgent 平台的 UI 组件规格，包括组件状态、尺寸、行为规范。

---

## 1. 按钮 (Button)

### 变体 (Variant)

| 变体 | 用途 | 示例 |
|------|------|------|
| Primary | 主要操作 | 提交、保存、执行 |
| Secondary | 次要操作 | 取消、返回 |
| Ghost | 辅助操作 | 筛选、更多操作 |
| Danger | 危险操作 | 删除、禁用 |

### 尺寸 (Size)

| 尺寸 | 高度 | 内边距 | 字号 |
|------|------|--------|------|
| Small (sm) | 28px | 8px 12px | 12px |
| Medium (md) | 36px | 8px 16px | 14px |
| Large (lg) | 44px | 12px 24px | 16px |

### 状态

| 状态 | 说明 | 视觉表现 |
|------|------|---------|
| Normal | 默认状态 | 正常显示 |
| Hover | 悬停状态 | 背景色加深 10% |
| Active | 按下状态 | 背景色加深 15%，轻微下沉 |
| Disabled | 禁用状态 | opacity: 0.5, cursor: not-allowed |
| Loading | 加载状态 | 显示 spinner，禁止点击 |

### 代码示例

```html
<!-- Primary Small -->
<button class="btn btn-primary btn-sm">按钮</button>

<!-- Primary Medium -->
<button class="btn btn-primary">按钮</button>

<!-- Primary Large -->
<button class="btn btn-primary btn-lg">按钮</button>

<!-- Secondary -->
<button class="btn btn-secondary">按钮</button>

<!-- Ghost -->
<button class="btn btn-ghost">按钮</button>

<!-- Danger -->
<button class="btn btn-danger">删除</button>

<!-- Loading -->
<button class="btn btn-primary" disabled>
  <span class="spinner"></span>
  处理中...
</button>

<!-- Icon Button -->
<button class="btn btn-icon btn-ghost">⚙</button>
```

---

## 2. 输入框 (Input)

### 类型

| 类型 | 用途 |
|------|------|
| Text | 单行文本 |
| Password | 密码 |
| Number | 数字 |
| Email | 邮箱 |
| Textarea | 多行文本 |
| Select | 下拉选择 |
| Checkbox | 复选框 |
| Radio | 单选框 |

### 尺寸

| 尺寸 | 高度 | 内边距 | 字号 |
|------|------|--------|------|
| Small | 28px | 4px 8px | 12px |
| Medium | 36px | 8px 12px | 14px |
| Large | 44px | 12px 16px | 16px |

### 状态

| 状态 | 说明 | 视觉表现 |
|------|------|---------|
| Normal | 默认状态 | 边框: 1px solid border-primary |
| Focus | 聚焦状态 | 边框: 1px solid brand-primary, 添加 glow |
| Error | 错误状态 | 边框: 1px solid error, 显示错误信息 |
| Disabled | 禁用状态 | 背景: bg-tertiary, cursor: not-allowed |

### 代码示例

```html
<!-- Text Input -->
<input type="text" class="form-input" placeholder="请输入">

<!-- Textarea -->
<textarea class="form-textarea" placeholder="请输入"></textarea>

<!-- Select -->
<select class="form-select">
  <option>选项 1</option>
  <option>选项 2</option>
</select>

<!-- With Label -->
<div class="form-group">
  <label class="form-label">名称 <span class="required">*</span></label>
  <input type="text" class="form-input">
  <div class="form-hint">辅助说明文字</div>
</div>

<!-- Error State -->
<div class="form-group">
  <input type="text" class="form-input error">
  <div class="form-error">错误信息</div>
</div>
```

---

## 3. 卡片 (Card)

### 结构

```
┌────────────────────────────┐
│         Card Header         │  可选
├────────────────────────────┤
│                            │
│         Card Body           │
│                            │
├────────────────────────────┤
│         Card Footer         │  可选
└────────────────────────────┘
```

### 规格

| 部分 | 内边距 |
|------|--------|
| Header | 16px 20px |
| Body | 20px |
| Footer | 12px 20px |

### 代码示例

```html
<div class="card">
  <div class="card-header">
    <span class="card-title">标题</span>
    <button class="btn btn-ghost btn-sm">操作</button>
  </div>
  <div class="card-body">
    内容区域
  </div>
  <div class="card-footer">
    <button class="btn btn-secondary">取消</button>
    <button class="btn btn-primary">确认</button>
  </div>
</div>
```

---

## 4. 表格 (Table)

### 结构

```
┌───┬─────────┬───────┬────────┐
│ # │  名称   │ 状态  │  操作  │
├───┼─────────┼───────┼────────┤
│ 1 │  项目A  │  已发布│ 编辑  │
├───┼─────────┼───────┼────────┤
│ 2 │  项目B  │  草稿  │ 编辑  │
└───┴─────────┴───────┴────────┘
```

### 规格

| 部分 | 样式 |
|------|------|
| 表头 | 背景: bg-tertiary, 字号: 12px, 颜色: text-tertiary, 大写 |
| 表头单元格 | 内边距: 12px 16px, 边框底部 |
| 表格单元格 | 内边距: 12px 16px, 字号: 14px |
| 斑马纹 | 奇数行: transparent, 偶数行: bg-hover |
| Hover | 行悬停: bg-hover |

### 代码示例

```html
<div class="table-container">
  <table class="table">
    <thead>
      <tr>
        <th>#</th>
        <th>名称</th>
        <th>状态</th>
        <th>更新时间</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td class="cell-mono">1</td>
        <td class="cell-primary">Apple Inc.</td>
        <td><span class="badge badge-success">已发布</span></td>
        <td class="text-tertiary">2 小时前</td>
      </tr>
    </tbody>
  </table>
</div>
```

---

## 5. 模态框 (Modal)

### 规格

| 属性 | 值 |
|------|-----|
| 最大宽度 | 560px |
| 内边距 | 24px |
| 圆角 | 12px |
| 遮罩透明度 | 70% |
| 动画时长 | 200ms |
| 缓动函数 | ease-out |

### 结构

```
┌────────────────────────────────────┐
│  Modal Header                      │
│  标题                    ✕ 关闭   │
├────────────────────────────────────┤
│                                    │
│         Modal Body                  │
│         (可滚动)                    │
│                                    │
├────────────────────────────────────┤
│  Modal Footer                      │
│         取消    确认                │
└────────────────────────────────────┘
```

### 交互行为

| 交互 | 行为 |
|------|------|
| 点击遮罩 | 关闭模态框 |
| 点击关闭按钮 | 关闭模态框 |
| 按 ESC 键 | 关闭模态框 |
| 点击确认按钮 | 执行操作并关闭 |
| 点击取消按钮 | 关闭模态框 |

### 代码示例

```html
<div class="modal-overlay" id="myModal">
  <div class="modal">
    <div class="modal-header">
      <h3 class="modal-title">标题</h3>
      <button class="modal-close">✕</button>
    </div>
    <div class="modal-body">
      内容
    </div>
    <div class="modal-footer">
      <button class="btn btn-secondary">取消</button>
      <button class="btn btn-primary">确认</button>
    </div>
  </div>
</div>
```

---

## 6. 标签页 (Tabs)

### 规格

| 属性 | 值 |
|------|-----|
| 高度 | 44px |
| 内边距 | 12px 16px |
| 下划线宽度 | 2px |
| 激活颜色 | brand-primary |

### 交互行为

| 交互 | 行为 |
|------|------|
| 点击 Tab | 切换内容区域 |
| 悬停 | 文字颜色变为 text-primary |
| 激活 | 文字颜色 brand-primary, 显示下划线 |

### 代码示例

```html
<div class="tabs">
  <button class="tab active">Tab 1</button>
  <button class="tab">Tab 2</button>
  <button class="tab">Tab 3</button>
</div>
```

---

## 7. 徽标 (Badge)

### 变体

| 变体 | 用途 | 颜色 |
|------|------|------|
| Success | 成功状态 | green |
| Warning | 警告状态 | yellow |
| Error | 错误状态 | red |
| Info | 信息状态 | blue |
| Draft | 草稿状态 | gray |
| Published | 已发布状态 | green |
| Archived | 已归档状态 | dark gray |

### 规格

| 属性 | 值 |
|------|-----|
| 内边距 | 2px 8px |
| 字号 | 12px |
| 圆角 | full (9999px) |
| 字重 | medium |

### 代码示例

```html
<span class="badge badge-success">已连接</span>
<span class="badge badge-warning">处理中</span>
<span class="badge badge-error">失败</span>
<span class="badge badge-draft">草稿</span>
```

---

## 8. 下拉菜单 (Dropdown)

### 规格

| 属性 | 值 |
|------|-----|
| 最小宽度 | 160px |
| 内边距 | 8px |
| 圆角 | 8px |
| 阴影 | shadow-lg |
| Z-Index | 100 |

### 交互行为

| 交互 | 行为 |
|------|------|
| 点击触发器 | 展开/收起菜单 |
| 悬停选项 | 背景色变为 bg-hover |
| 点击选项 | 执行操作，收起菜单 |
| 点击外部 | 收起菜单 |

### 代码示例

```html
<div class="dropdown">
  <button class="btn btn-ghost dropdown-trigger">
    操作 ▼
  </button>
  <div class="dropdown-menu">
    <div class="dropdown-item">编辑</div>
    <div class="dropdown-item">复制</div>
    <div class="dropdown-divider"></div>
    <div class="dropdown-item danger">删除</div>
  </div>
</div>
```

---

## 9. 提示 (Tooltip)

### 规格

| 属性 | 值 |
|------|-----|
| 背景色 | bg-tooltip (#0d1117) |
| 文字颜色 | text-primary (#f1f5f9) |
| 内边距 | 4px 8px |
| 字号 | 12px |
| 圆角 | 4px |
| 显示延迟 | 200ms |
| 箭头大小 | 6px |

### 位置

| 位置 | 说明 |
|------|------|
| Top | 显示在元素上方 |
| Bottom | 显示在元素下方 |
| Left | 显示在元素左侧 |
| Right | 显示在元素右侧 |

### 代码示例

```html
<button class="tooltip" data-tooltip="提示文字">hover me</button>
```

---

## 10. 消息提示 (Toast)

### 规格

| 属性 | 值 |
|------|-----|
| 位置 | 右上角 |
| 内边距 | 16px 20px |
| 最小宽度 | 320px |
| 最大宽度 | 420px |
| 圆角 | 8px |
| 阴影 | shadow-lg |
| 动画时长 | 200ms |
| 自动消失 | 5秒 |

### 类型

| 类型 | 图标 | 颜色 |
|------|------|------|
| Success | ✓ | green |
| Error | ✕ | red |
| Warning | ⚠ | yellow |
| Info | ℹ | blue |

### 代码示例

```html
<div class="toast-container">
  <div class="toast">
    <span class="toast-icon">✓</span>
    <div class="toast-content">
      <div class="toast-title">操作成功</div>
      <div class="toast-message">本体已发布</div>
    </div>
    <button class="toast-close">✕</button>
  </div>
</div>
```

---

## 11. 空状态 (Empty State)

### 结构

```
┌────────────────────────────┐
│                            │
│           [ 图标 ]           │
│                            │
│          标题文字            │
│                            │
│         描述说明文字         │
│                            │
│        [ 操作按钮 ]         │
│                            │
└────────────────────────────┘
```

### 代码示例

```html
<div class="empty-state">
  <div class="empty-icon">📭</div>
  <h3 class="empty-title">暂无数据</h3>
  <p class="empty-description">
    点击下方按钮创建第一个本体
  </p>
  <button class="btn btn-primary">创建本体</button>
</div>
```

---

## 12. 加载状态 (Loading)

### 类型

| 类型 | 用途 |
|------|------|
| Spinner | 按钮内加载、小型加载 |
| Skeleton | 内容区域骨架屏 |
| Progress | 进度条 |
| Overlay | 全屏加载遮罩 |

### Spinner 规格

| 属性 | Small | Medium | Large |
|------|-------|--------|-------|
| 尺寸 | 16px | 20px | 32px |
| 边框宽度 | 2px | 2px | 3px |
| 旋转周期 | 600ms | 600ms | 800ms |

### Skeleton 规格

| 属性 | 值 |
|------|-----|
| 背景色 | bg-tertiary |
| 动画 | shimmer 1.5s infinite |
| 圆角 | 4px |

### 代码示例

```html
<!-- Button Spinner -->
<button class="btn btn-primary" disabled>
  <span class="spinner"></span>
  加载中...
</button>

<!-- Skeleton -->
<div class="skeleton" style="width: 200px; height: 20px;"></div>

<!-- Skeleton Table -->
<div class="skeleton" style="width: 100%; height: 40px;"></div>
<div class="skeleton" style="width: 100%; height: 40px;"></div>
<div class="skeleton" style="width: 80%; height: 40px;"></div>

<!-- Progress Bar -->
<div class="progress-bar">
  <div class="progress-fill" style="width: 65%;"></div>
</div>
```

---

## 13. 分页 (Pagination)

### 规格

| 属性 | 值 |
|------|-----|
| 按钮尺寸 | 32px × 32px |
| 圆角 | 4px |
| 激活背景 | brand-primary |
| 禁用透明度 | 0.5 |

### 代码示例

```html
<div class="pagination">
  <div class="pagination-info">显示 1-20 / 共 100 条</div>
  <div class="pagination-buttons">
    <button class="pagination-btn" disabled>‹</button>
    <button class="pagination-btn active">1</button>
    <button class="pagination-btn">2</button>
    <button class="pagination-btn">3</button>
    <button class="pagination-btn">›</button>
  </div>
</div>
```

---

## 14. 侧边栏 (Sidebar)

### 规格

| 属性 | 值 |
|------|-----|
| 宽度 | 260px |
| 折叠宽度 | 64px |
| 高度 | 100vh |
| 背景色 | bg-secondary |
| 边框 | 右侧 1px border-primary |

### 导航项

| 属性 | 值 |
|------|-----|
| 高度 | 36px |
| 内边距 | 8px 20px |
| 圆角 | 6px |
| 悬停背景 | bg-hover |
| 激活背景 | rgba(brand-primary, 0.1) |
| 激活颜色 | brand-primary |

### 代码示例

```html
<aside class="sidebar">
  <div class="sidebar-logo">
    <div class="logo-icon">O</div>
    <span class="logo-text">OntoAgent</span>
  </div>
  <nav class="sidebar-nav">
    <div class="nav-section">
      <div class="nav-section-title">概览</div>
      <a href="/" class="nav-item active">
        <span class="nav-icon">◉</span>
        <span>仪表盘</span>
      </a>
    </div>
  </nav>
  <div class="sidebar-footer">
    <div class="user-avatar">A</div>
    <div class="user-info">
      <div class="user-name">Admin</div>
      <div class="user-role">系统管理员</div>
    </div>
  </div>
</aside>
```

---

## 15. 颜色系统

### 主色

```css
--brand-primary: #3b82f6;        /* 主蓝 */
--brand-primary-hover: #2563eb;  /* 悬停 */
--brand-primary-active: #1d4ed8; /* 按下 */
--brand-secondary: #8b5cf6;      /* 辅助紫 */
--brand-accent: #06b6d4;         /* 强调青 */
```

### 状态色

```css
--status-success: #10b981;
--status-success-bg: rgba(16, 185, 129, 0.1);

--status-warning: #f59e0b;
--status-warning-bg: rgba(245, 158, 11, 0.1);

--status-error: #ef4444;
--status-error-bg: rgba(239, 68, 68, 0.1);

--status-info: #3b82f6;
--status-info-bg: rgba(59, 130, 246, 0.1);
```

### 背景色

```css
--bg-primary: #0a0e17;
--bg-secondary: #111827;
--bg-tertiary: #1a2234;
--bg-elevated: #1f2937;
--bg-hover: #2a3444;
--bg-active: #374151;
--bg-input: #0d1321;
--bg-card: #161d2e;
```

### 文字色

```css
--text-primary: #f1f5f9;
--text-secondary: #94a3b8;
--text-tertiary: #64748b;
--text-inverse: #0a0e17;
```

---

## 16. 间距系统

```css
--space-1: 4px;
--space-2: 8px;
--space-3: 12px;
--space-4: 16px;
--space-5: 20px;
--space-6: 24px;
--space-8: 32px;
--space-10: 40px;
--space-12: 48px;
--space-16: 64px;
```

---

## 17. 圆角系统

```css
--radius-sm: 4px;
--radius-md: 6px;
--radius-lg: 8px;
--radius-xl: 12px;
--radius-2xl: 16px;
--radius-full: 9999px;
```

---

## 18. 阴影系统

```css
--shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.3);
--shadow-md: 0 4px 6px rgba(0, 0, 0, 0.4);
--shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.5);
--shadow-xl: 0 20px 25px rgba(0, 0, 0, 0.6);
--shadow-glow: 0 0 20px rgba(59, 130, 246, 0.15);
```

---

## 19. 动画规范

```css
--transition-fast: 150ms ease;
--transition-base: 200ms ease;
--transition-slow: 300ms ease;

/* 缓动函数 */
--ease-out: cubic-bezier(0.33, 1, 0.68, 1);
--ease-in-out: cubic-bezier(0.65, 0, 0.35, 1);
--ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
```

---

## 20. 响应式断点

```css
/* 移动端 */
@media (max-width: 768px) {
  --sidebar-width: 0px;
  --header-height: 56px;
}

/* 平板 */
@media (min-width: 769px) and (max-width: 1024px) {
  --sidebar-width: 64px;
}

/* 桌面 */
@media (min-width: 1025px) {
  --sidebar-width: 260px;
}
```
