# 前后端联调测试报告

**测试日期**: 2026-04-10  
**测试人员**: 土豆 (🥔)

---

## 一、测试环境

### 1.1 Docker 容器

| 容器名 | 端口 | 数据库 | 用途 |
|--------|------|--------|------|
| `postgres-system` | 5432 | system_db | 系统内部数据（本体、实体、Saga） |
| `postgres-onto` | 5433 | onto_agent | 业务数据（数据源等） |
| `fuseki` | 3030 | - | Jena Fuseki RDF 存储 |

### 1.2 服务进程

| 服务 | 端口 | 状态 |
|------|------|------|
| 后端 API | 8000 | ✅ 运行中 |
| 前端开发服务器 | 5173 | ✅ 运行中 |
| PostgreSQL (system) | 5432 | ✅ 运行中 |
| PostgreSQL (onto) | 5433 | ✅ 运行中 |
| Fuseki | 3030 | ✅ 运行中 |

---

## 二、功能测试结果

### 2.1 后端 API 测试

| 功能 | API 端点 | 方法 | 状态 | 备注 |
|------|----------|------|------|------|
| Health Check | `/api/health` | GET | ✅ 通过 | |
| 本体列表 | `/api/ontologies` | GET | ✅ 通过 | 返回 2 个测试本体 |
| 创建本体 | `/api/ontologies` | POST | ✅ 通过 | 支持 TBox/ABox 分离 |
| 本体详情 | `/api/ontologies/{id}` | GET | ✅ 通过 | |
| 数据源列表 | `/api/datasources` | GET | ✅ 通过 | |
| 创建数据源 | `/api/datasources` | POST | ✅ 通过 | ID 类型已修复 |

### 2.2 前端测试

| 功能 | 状态 | 备注 |
|------|------|------|
| 页面加载 | ✅ 通过 | http://localhost:5173 |
| API 代理 | ✅ 通过 | 已配置代理到后端 8000 端口 |
| 本体列表显示 | ✅ 通过 | 连接后端 API 正常 |
| 数据源管理 | ✅ 通过 | 管理界面正常工作 |

### 2.3 数据库测试

| 数据库 | 表 | 状态 |
|--------|-----|------|
| system_db | ontologies | ✅ 2 条记录 |
| system_db | entity_index | ✅ 已创建 |
| system_db | ontology_versions | ✅ 已创建 |
| system_db | operation_logs | ✅ 已创建 |
| onto_agent | datasources | ✅ 1 条记录 |

---

## 三、问题发现与修复

### 3.1 已修复问题

| # | 问题描述 | 严重程度 | 修复方案 |
|---|----------|----------|----------|
| 1 | 缺少 `init_db` 函数 | 🔴 高 | 在 database.py 中添加 async init_db() |
| 2 | 缺少 `get_db` 依赖 | 🔴 高 | 添加 get_db() / get_system_db() 依赖函数 |
| 3 | Datasource 模型使用 UUID 但数据库用 VARCHAR | 🔴 高 | 修改 Datasource 模型使用 String(50) |
| 4 | 创建本体时缺少 `tbox_graph_uri` | 🔴 高 | 在 ontology.py 中添加自动生成逻辑 |
| 5 | 前端代理指向错误端口 3001 | 🟡 中 | 修改 vite.config.ts 指向 8000 端口 |
| 6 | entity_index 表缺少 graph_uri 列 | 🟡 中 | 系统数据库已包含此字段 |

### 3.2 待优化问题

| # | 问题描述 | 严重程度 | 建议 |
|---|----------|----------|------|
| 1 | Jena Fuseki 连接错误 | 🟡 中 | httpx 变量作用域问题，需修复 jena_client.py |
| 2 | Fuseki 可能未正确配置 Dataset | 🟡 中 | 需确认 /onto-agent dataset 是否已创建 |

---

## 四、架构变更记录

### 4.1 双数据库架构 ✅

**变更前**:
- 单一数据库 onto_agent
- 所有表混合存储

**变更后**:
- `system_db`: ontologies, entity_index, ontology_versions, operation_logs
- `onto_agent`: datasources, mappings, sync_tasks 等业务数据

### 4.2 Named Graph 架构 ✅

**变更前**:
- 每个本体独立 Dataset: `/ontology_{id}`

**变更后**:
- 统一 Dataset: `/onto-agent`
- 每个本体使用 Named Graph:
  - TBox: `/onto-agent/{id}/tbox` (owl:Class, owl:Property)
  - ABox: `/onto-agent/{id}/abox` (owl:NamedIndividual)

---

## 五、代码修改清单

| 文件 | 修改内容 |
|------|----------|
| `src/database.py` | ✅ 重写，支持 SystemSession/BusinessSession/LegacySession |
| `src/models/datasource.py` | ✅ 修改 ID 类型为 String |
| `src/services/ontology.py` | ✅ 添加 tbox_graph_uri/abox_graph_uri 生成逻辑 |
| `src/services/saga_manager.py` | ✅ 改用 SystemSession |
| `onto-agent-web/vite.config.ts` | ✅ 修改代理目标端口 |
| `.env` | ✅ 添加新数据库环境变量 |

---

## 六、验证结果

### 6.1 示例数据

```
本体 #1:
- id: 77cc4f03
- name: test-onto-1
- dataset: /onto-agent
- tbox_graph_uri: /onto-agent/77cc4f03/tbox
- abox_graph_uri: /onto-agent/77cc4f03/abox

本体 #2:
- id: 739057cb
- name: test-onto-2
- dataset: /onto-agent
- tbox_graph_uri: /onto-agent/739057cb/tbox
- abox_graph_uri: /onto-agent/739057cb/abox
```

```
数据源 #1:
- id: e281108f-dd5c-4978-a8a0-e733ed99681d
- name: 测试数据库
- type: postgresql
- host: localhost
- port: 5432
- status: disconnected
```

---

## 七、总结

✅ **前后端已打通**  
✅ **双数据库架构运行正常**  
✅ **Named Graph 架构已实现**  
🟡 **Jena Fuseki 集成需优化**

---

## 八、下一步建议

1. **修复 Jena 连接问题**: 检查 jena_client.py 中 httpx 变量作用域
2. **添加本体发布功能**: 实现 TBox/ABox 分离发布
3. **完善 Saga 事务**: 测试故障恢复和补偿机制
4. **前端页面优化**: 添加本体详情图谱展示页面

---

*报告生成时间: 2026-04-10 23:60*