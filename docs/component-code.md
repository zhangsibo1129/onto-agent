# OntoAgent 组件代码手册

本文档为开发团队提供可直接使用的 HTML/CSS 组件代码参考。

---

## 1. 页面布局结构

### 完整页面模板

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>页面标题 - OntoAgent</title>
  <link rel="stylesheet" href="../css/design-system.css">
</head>
<body>
  <div class="app-layout">
    <!-- 侧边栏 -->
    <aside class="sidebar">
      <div class="sidebar-logo">
        <div class="logo-icon">O</div>
        <span class="logo-text">OntoAgent</span>
      </div>
      <nav class="sidebar-nav">
        <div class="nav-section">
          <div class="nav-section-title">概览</div>
          <a href="index.html" class="nav-item active">
            <span class="nav-icon">◉</span>
            <span>仪表盘</span>
          </a>
          <a href="pages/data-sources.html" class="nav-item">
            <span class="nav-icon">⬡</span>
            <span>数据源</span>
            <span class="nav-badge">3</span>
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

    <!-- 主内容区 -->
    <main class="main-content">
      <!-- 页头 -->
      <header class="header">
        <div class="header-left">
          <div class="header-breadcrumb">
            <a href="#">首页</a>
            <span class="separator">/</span>
            <span class="current">当前页面</span>
          </div>
        </div>
        <div class="header-right">
          <div class="header-search">
            <span class="search-icon">⌕</span>
            <input type="text" placeholder="搜索...">
            <span class="search-shortcut">⌘K</span>
          </div>
          <button class="header-icon-btn">◉<span class="badge"></span></button>
          <button class="header-icon-btn">⚙</button>
        </div>
      </header>

      <!-- 页面内容 -->
      <div class="content">
        <!-- 页面标题栏 -->
        <div class="page-header">
          <div class="page-header-top">
            <div>
              <h1 class="page-title">页面标题</h1>
              <p class="page-description">页面描述说明</p>
            </div>
            <div class="page-actions">
              <button class="btn btn-secondary">次要操作</button>
              <button class="btn btn-primary">主要操作</button>
            </div>
          </div>
        </div>

        <!-- 页面具体内容 -->
      </div>
    </main>
  </div>
</body>
</html>
```

---

## 2. 按钮 (Button)

### 基础按钮

```html
<!-- Primary -->
<button class="btn btn-primary">保存</button>

<!-- Secondary -->
<button class="btn btn-secondary">取消</button>

<!-- Ghost -->
<button class="btn btn-ghost">更多</button>

<!-- Danger -->
<button class="btn btn-danger">删除</button>

<!-- Success -->
<button class="btn btn-success">确认</button>
```

### 尺寸变体

```html
<button class="btn btn-primary btn-sm">小按钮</button>
<button class="btn btn-primary">中按钮</button>
<button class="btn btn-primary btn-lg">大按钮</button>
```

### 带图标

```html
<button class="btn btn-primary">+ 新建</button>
<button class="btn btn-secondary">⟳ 刷新</button>
<button class="btn btn-ghost">⋮ 更多</button>
```

### 图标按钮

```html
<button class="btn btn-icon btn-ghost">⚙</button>
<button class="btn btn-icon btn-ghost">✕</button>
```

### 加载状态

```html
<button class="btn btn-primary" disabled>
  <span class="spinner"></span>
  处理中...
</button>

<button class="btn btn-primary" disabled>
  <span class="spinner spinner-sm"></span>
  加载中
</button>
```

### 禁用状态

```html
<button class="btn btn-primary" disabled>禁用按钮</button>
```

---

## 3. 表单组件

### 输入框

```html
<!-- 基础输入框 -->
<input type="text" class="form-input" placeholder="请输入">

<!-- 带标签 -->
<div class="form-group">
  <label class="form-label">名称 <span class="required">*</span></label>
  <input type="text" class="form-input">
  <div class="form-hint">辅助说明文字</div>
</div>

<!-- 错误状态 -->
<div class="form-group">
  <input type="text" class="form-input error">
  <div class="form-error">错误信息</div>
</div>

<!-- 密码输入 -->
<input type="password" class="form-input" placeholder="••••••••">

<!-- 大尺寸输入 -->
<input type="text" class="form-input form-input-lg" placeholder="大输入框">

<!-- 小尺寸输入 -->
<input type="text" class="form-input form-input-sm" placeholder="小输入框">
```

### 多行文本

```html
<textarea class="form-textarea" placeholder="请输入描述..."></textarea>
```

### 下拉选择

```html
<select class="form-select">
  <option>选项 1</option>
  <option>选项 2</option>
  <option>选项 3</option>
</select>
```

### 复选框和单选框

```html
<label class="checkbox">
  <input type="checkbox">
  <span class="checkmark"></span>
  选项文字
</label>

<label class="radio">
  <input type="radio" name="group">
  <span class="radio-mark"></span>
  选项 1
</label>
<label class="radio">
  <input type="radio" name="group">
  <span class="radio-mark"></span>
  选项 2
</label>
```

---

## 4. 卡片 (Card)

### 基础卡片

```html
<div class="card">
  <div class="card-header">
    <span class="card-title">卡片标题</span>
    <button class="btn btn-ghost btn-sm">操作</button>
  </div>
  <div class="card-body">
    卡片内容区域
  </div>
  <div class="card-footer">
    <button class="btn btn-secondary">取消</button>
    <button class="btn btn-primary">确认</button>
  </div>
</div>
```

### 仅内容卡片

```html
<div class="card">
  <div class="card-body">
    纯内容卡片
  </div>
</div>
```

### 带 Header 卡片

```html
<div class="card">
  <div class="card-header">
    <span class="card-title">标题</span>
  </div>
  <div class="card-body">
    内容
  </div>
</div>
```

---

## 5. 表格 (Table)

### 基础表格

```html
<div class="table-container">
  <table class="table">
    <thead>
      <tr>
        <th>#</th>
        <th>名称</th>
        <th>状态</th>
        <th>更新时间</th>
        <th>操作</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td class="cell-mono">1</td>
        <td class="cell-primary">Apple Inc.</td>
        <td><span class="badge badge-success">已发布</span></td>
        <td class="text-tertiary">2 小时前</td>
        <td><button class="btn btn-ghost btn-sm">编辑</button></td>
      </tr>
      <tr>
        <td class="cell-mono">2</td>
        <td class="cell-primary">Microsoft</td>
        <td><span class="badge badge-draft">草稿</span></td>
        <td class="text-tertiary">昨天</td>
        <td><button class="btn btn-ghost btn-sm">编辑</button></td>
      </tr>
    </tbody>
  </table>
</div>
```

---

## 6. 徽标 (Badge)

```html
<span class="badge badge-success">已连接</span>
<span class="badge badge-warning">处理中</span>
<span class="badge badge-error">失败</span>
<span class="badge badge-info">进行中</span>
<span class="badge badge-draft">草稿</span>
<span class="badge badge-published">已发布</span>
<span class="badge badge-archived">已归档</span>
```

---

## 7. 模态框 (Modal)

### 基础模态框

```html
<!-- 触发按钮 -->
<button class="btn btn-primary" onclick="document.getElementById('myModal').classList.add('active')">
  打开模态框
</button>

<!-- 模态框结构 -->
<div class="modal-overlay" id="myModal" onclick="if(event.target === this) this.classList.remove('active')">
  <div class="modal">
    <div class="modal-header">
      <h3 class="modal-title">标题</h3>
      <button class="modal-close" onclick="document.getElementById('myModal').classList.remove('active')">✕</button>
    </div>
    <div class="modal-body">
      <p>模态框内容</p>
    </div>
    <div class="modal-footer">
      <button class="btn btn-secondary" onclick="document.getElementById('myModal').classList.remove('active')">取消</button>
      <button class="btn btn-primary">确认</button>
    </div>
  </div>
</div>
```

### 表单模态框

```html
<div class="modal-overlay" id="formModal" onclick="if(event.target === this) this.classList.remove('active')">
  <div class="modal">
    <div class="modal-header">
      <h3 class="modal-title">添加数据源</h3>
      <button class="modal-close" onclick="document.getElementById('formModal').classList.remove('active')">✕</button>
    </div>
    <div class="modal-body">
      <div class="form-group">
        <label class="form-label">名称 <span class="required">*</span></label>
        <input type="text" class="form-input" placeholder="请输入">
      </div>
      <div class="form-row">
        <div class="form-group">
          <label class="form-label">主机</label>
          <input type="text" class="form-input" placeholder="db.example.com">
        </div>
        <div class="form-group">
          <label class="form-label">端口</label>
          <input type="number" class="form-input" value="5432">
        </div>
      </div>
    </div>
    <div class="modal-footer">
      <button class="btn btn-secondary" onclick="document.getElementById('formModal').classList.remove('active')">取消</button>
      <button class="btn btn-primary">保存</button>
    </div>
  </div>
</div>
```

---

## 8. 标签页 (Tabs)

```html
<div class="tabs">
  <button class="tab active">Tab 1</button>
  <button class="tab">Tab 2</button>
  <button class="tab">Tab 3</button>
</div>
```

---

## 9. 下拉菜单 (Dropdown)

```html
<div class="dropdown">
  <button class="btn btn-ghost dropdown-trigger">操作 ▼</button>
  <div class="dropdown-menu">
    <div class="dropdown-item">编辑</div>
    <div class="dropdown-item">复制</div>
    <div class="dropdown-divider"></div>
    <div class="dropdown-item danger">删除</div>
  </div>
</div>
```

---

## 10. 加载状态

### Spinner

```html
<span class="spinner"></span>
<span class="spinner spinner-sm"></span>
<span class="spinner spinner-lg"></span>
```

### Skeleton 骨架屏

```html
<div class="skeleton" style="width: 200px; height: 20px;"></div>
<div class="skeleton" style="width: 100%; height: 40px;"></div>
<div class="skeleton" style="width: 80%; height: 40px;"></div>
```

### 按钮加载状态

```html
<button class="btn btn-primary" disabled>
  <span class="spinner"></span>
  加载中...
</button>
```

---

## 11. 空状态

```html
<div class="empty-state">
  <div class="empty-icon">📭</div>
  <h3 class="empty-title">暂无数据</h3>
  <p class="empty-description">点击下方按钮创建第一个本体</p>
  <button class="btn btn-primary">创建本体</button>
</div>
```

---

## 12. 消息提示 (Toast)

```html
<div class="toast-container">
  <div class="toast toast-success">
    <span class="toast-icon">✓</span>
    <div class="toast-content">
      <div class="toast-title">操作成功</div>
      <div class="toast-message">本体已发布</div>
    </div>
    <button class="toast-close">✕</button>
  </div>
</div>

<div class="toast toast-error">
  <span class="toast-icon">✕</span>
  <div class="toast-content">
    <div class="toast-title">操作失败</div>
    <div class="toast-message">请稍后重试</div>
  </div>
  <button class="toast-close">✕</button>
</div>
```

---

## 13. 统计卡片

```html
<div class="stats-grid">
  <div class="stat-card">
    <div class="stat-label">数据源</div>
    <div class="stat-value">3</div>
    <div class="stat-change positive">↑ 全部连接正常</div>
  </div>
  <div class="stat-card">
    <div class="stat-label">本体总数</div>
    <div class="stat-value">5</div>
    <div class="stat-change positive">↑ 2 个已发布</div>
  </div>
</div>
```

---

## 14. 工具栏

```html
<div class="toolbar">
  <div class="toolbar-left">
    <div class="search-input">
      <span class="icon">⌕</span>
      <input type="text" placeholder="搜索...">
    </div>
    <select class="form-select" style="width: 140px;">
      <option>全部状态</option>
      <option>已连接</option>
    </select>
  </div>
  <div class="toolbar-right">
    <button class="btn btn-ghost btn-sm">卡片视图</button>
    <button class="btn btn-ghost btn-sm">列表视图</button>
  </div>
</div>
```

---

## 15. 分页

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

## 16. 页面头部面包屑

```html
<div class="header-breadcrumb">
  <a href="#">首页</a>
  <span class="separator">/</span>
  <a href="#">数据管理</a>
  <span class="separator">/</span>
  <span class="current">数据源</span>
</div>
```

---

## 17. 页面标题栏

```html
<div class="page-header">
  <div class="page-header-top">
    <div>
      <h1 class="page-title">页面标题</h1>
      <p class="page-description">页面描述说明文字</p>
    </div>
    <div class="page-actions">
      <button class="btn btn-secondary">次要操作</button>
      <button class="btn btn-primary">主要操作</button>
    </div>
  </div>
</div>
```
