# OntoAgent API 接口文档

## 概述

- **基础 URL**: `https://api.ontoagent.com/v1`
- **认证方式**: API Key (Header: `X-API-Key: your-api-key`)
- **数据格式**: JSON
- **字符编码**: UTF-8

---

## 通用说明

### 请求头

| Header | 必填 | 说明 |
|--------|------|------|
| Content-Type | 是 | application/json |
| X-API-Key | 是 | API 密钥 |
| X-Request-ID | 否 | 请求追踪 ID |

### 通用响应格式

```json
{
  "success": true,
  "data": { },
  "error": null,
  "timestamp": "2024-01-15T10:30:00Z",
  "requestId": "req_abc123"
}
```

### 错误响应格式

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "ONTOLOGY_NOT_FOUND",
    "message": "本体不存在",
    "details": {}
  },
  "timestamp": "2024-01-15T10:30:00Z",
  "requestId": "req_abc123"
}
```

### HTTP 状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 409 | 资源冲突 |
| 500 | 服务器内部错误 |

---

## 数据模型

### 2.1 本体 (Ontology)

```json
{
  "id": "onto_abc123",
  "name": "客户360",
  "description": "企业客户全景视图",
  "status": "published",
  "version": "v2.1",
  "objectTypeCount": 8,
  "propertyCount": 64,
  "relationshipCount": 14,
  "datasourceId": "ds_erp_prod",
  "createdAt": "2023-12-20T09:00:00Z",
  "updatedAt": "2024-01-15T14:30:00Z",
  "publishedAt": "2024-01-15T14:30:00Z",
  "createdBy": "user_admin"
}
```

### 2.2 对象类型 (ObjectType)

```json
{
  "id": "obj_customer",
  "ontologyId": "onto_abc123",
  "name": "Customer",
  "displayName": "客户",
  "description": "企业客户实体",
  "properties": [
    {
      "name": "customerId",
      "displayName": "客户ID",
      "dataType": "UUID",
      "isPrimaryKey": true,
      "isRequired": true
    },
    {
      "name": "name",
      "displayName": "名称",
      "dataType": "String",
      "isRequired": true
    }
  ],
  "relationships": [
    {
      "name": "places",
      "targetType": "Order",
      "cardinality": "1:N"
    }
  ],
  "createdAt": "2023-12-20T09:00:00Z"
}
```

### 2.3 数据源 (Datasource)

```json
{
  "id": "ds_erp_prod",
  "name": "ERP-Production",
  "type": "postgresql",
  "status": "connected",
  "host": "erp-db.internal",
  "port": 5432,
  "database": "erp_prod",
  "schema": "public",
  "tableCount": 68,
  "lastSyncAt": "2024-01-15T10:25:00Z",
  "createdAt": "2023-12-01T00:00:00Z"
}
```

### 2.4 映射 (Mapping)

```json
{
  "id": "map_abc123",
  "ontologyId": "onto_abc123",
  "objectTypeName": "Customer",
  "datasourceId": "ds_erp_prod",
  "tableName": "customers",
  "mappings": [
    {
      "propertyName": "customerId",
      "columnName": "customer_id",
      "transform": null
    },
    {
      "propertyName": "name",
      "columnName": "customer_name",
      "transform": null
    }
  ],
  "status": "completed",
  "verifiedAt": "2024-01-10T12:00:00Z"
}
```

### 2.5 版本 (Version)

```json
{
  "id": "ver_abc123",
  "ontologyId": "onto_abc123",
  "version": "v2.1",
  "status": "published",
  "changeLog": [
    {
      "type": "added",
      "description": "新增对象类型 Segment"
    },
    {
      "type": "modified",
      "description": "Customer 新增 segmentId 属性"
    }
  ],
  "snapshot": {},
  "createdAt": "2024-01-15T14:30:00Z",
  "publishedAt": "2024-01-15T14:30:00Z"
}
```

### 2.6 同步任务 (SyncTask)

```json
{
  "id": "sync_abc123",
  "ontologyId": "onto_abc123",
  "datasourceId": "ds_erp_prod",
  "type": "incremental",
  "mode": "cdc",
  "status": "running",
  "progress": 65,
  "totalRecords": 3789,
  "processedRecords": 2456,
  "startedAt": "2024-01-15T10:25:00Z",
  "completedAt": null
}
```

---

## 接口清单

### 3.1 本体管理

#### 创建本体

```
POST /ontologies
```

**请求体:**
```json
{
  "name": "客户360",
  "description": "企业客户全景视图",
  "datasourceId": "ds_erp_prod"
}
```

**响应 (201):**
```json
{
  "success": true,
  "data": {
    "id": "onto_abc123",
    "name": "客户360",
    "description": "企业客户全景视图",
    "status": "draft",
    "version": "v0.1-draft",
    "createdAt": "2024-01-15T10:30:00Z"
  }
}
```

#### 获取本体列表

```
GET /ontologies
```

**查询参数:**
| 参数 | 类型 | 说明 |
|------|------|------|
| page | int | 页码 (默认 1) |
| pageSize | int | 每页数量 (默认 20) |
| status | string | 筛选状态 (draft/published/archived) |
| search | string | 搜索关键词 |

**响应 (200):**
```json
{
  "success": true,
  "data": {
    "items": [...],
    "total": 5,
    "page": 1,
    "pageSize": 20,
    "totalPages": 1
  }
}
```

#### 获取本体详情

```
GET /ontologies/{ontologyId}
```

#### 更新本体

```
PUT /ontologies/{ontologyId}
```

#### 删除本体

```
DELETE /ontologies/{ontologyId}
```

#### 发布本体

```
POST /ontologies/{ontologyId}/publish
```

**响应 (200):**
```json
{
  "success": true,
  "data": {
    "id": "onto_abc123",
    "version": "v2.1",
    "status": "published",
    "publishedAt": "2024-01-15T14:30:00Z"
  }
}
```

---

### 3.2 对象类型管理

#### 获取对象类型列表

```
GET /ontologies/{ontologyId}/object-types
```

#### 创建对象类型

```
POST /ontologies/{ontologyId}/object-types
```

**请求体:**
```json
{
  "name": "Customer",
  "displayName": "客户",
  "description": "企业客户实体",
  "properties": [
    {
      "name": "customerId",
      "displayName": "客户ID",
      "dataType": "UUID",
      "isPrimaryKey": true,
      "isRequired": true
    },
    {
      "name": "name",
      "displayName": "名称",
      "dataType": "String",
      "isRequired": true
    }
  ]
}
```

#### 更新对象类型

```
PUT /ontologies/{ontologyId}/object-types/{objectTypeName}
```

#### 删除对象类型

```
DELETE /ontologies/{ontologyId}/object-types/{objectTypeName}
```

#### 添加属性

```
POST /ontologies/{ontologyId}/object-types/{objectTypeName}/properties
```

#### 删除属性

```
DELETE /ontologies/{ontologyId}/object-types/{objectTypeName}/properties/{propertyName}
```

#### 添加关系

```
POST /ontologies/{ontologyId}/object-types/{objectTypeName}/relationships
```

**请求体:**
```json
{
  "name": "places",
  "targetType": "Order",
  "cardinality": "1:N",
  "displayName": "下单"
}
```

---

### 3.3 数据源管理

#### 创建数据源

```
POST /datasources
```

**请求体:**
```json
{
  "name": "ERP-Production",
  "type": "postgresql",
  "host": "erp-db.internal",
  "port": 5432,
  "database": "erp_prod",
  "schema": "public",
  "username": "ontoagent_ro",
  "password": "encrypted_password",
  "sslMode": "prefer"
}
```

#### 获取数据源列表

```
GET /datasources
```

#### 获取数据源详情

```
GET /datasources/{datasourceId}
```

#### 更新数据源

```
PUT /datasources/{datasourceId}
```

#### 删除数据源

```
DELETE /datasources/{datasourceId}
```

#### 测试连接

```
POST /datasources/{datasourceId}/test
```

**响应 (200):**
```json
{
  "success": true,
  "data": {
    "connected": true,
    "latency": "45ms",
    "version": "PostgreSQL 15.2",
    "tableCount": 68
  }
}
```

#### 扫描元数据

```
POST /datasources/{datasourceId}/scan
```

**响应 (200):**
```json
{
  "success": true,
  "data": {
    "status": "completed",
    "tables": [
      {
        "name": "customers",
        "columns": 15,
        "rowCount": 12450
      }
    ],
    "scannedAt": "2024-01-15T10:30:00Z"
  }
}
```

#### 获取数据表列表

```
GET /datasources/{datasourceId}/tables
```

#### 获取表结构

```
GET /datasources/{datasourceId}/tables/{tableName}
```

---

### 3.4 数据映射管理

#### 创建映射

```
POST /ontologies/{ontologyId}/mappings
```

**请求体:**
```json
{
  "objectTypeName": "Customer",
  "datasourceId": "ds_erp_prod",
  "tableName": "customers",
  "mappings": [
    {
      "propertyName": "customerId",
      "columnName": "customer_id"
    }
  ]
}
```

#### 获取映射列表

```
GET /ontologies/{ontologyId}/mappings
```

#### 更新映射

```
PUT /ontologies/{ontologyId}/mappings/{mappingId}
```

#### 删除映射

```
DELETE /ontologies/{ontologyId}/mappings/{mappingId}
```

#### 验证映射

```
POST /ontologies/{ontologyId}/mappings/{mappingId}/verify
```

**响应 (200):**
```json
{
  "success": true,
  "data": {
    "valid": true,
    "issues": [],
    "sampleData": [
      {
        "customerId": "uuid-xxx",
        "name": "Apple Inc."
      }
    ]
  }
}
```

#### 自动映射

```
POST /ontologies/{ontologyId}/mappings/auto-map
```

**请求体:**
```json
{
  "objectTypeName": "Customer",
  "datasourceId": "ds_erp_prod",
  "tableName": "customers"
}
```

---

### 3.5 版本管理

#### 获取版本列表

```
GET /ontologies/{ontologyId}/versions
```

#### 获取版本详情

```
GET /ontologies/{ontologyId}/versions/{version}
```

#### 回滚到版本

```
POST /ontologies/{ontologyId}/rollback
```

**请求体:**
```json
{
  "targetVersion": "v2.0"
}
```

#### 比较版本差异

```
GET /ontologies/{ontologyId}/versions/compare
```

**查询参数:**
| 参数 | 说明 |
|------|------|
| from | 源版本 |
| to | 目标版本 |

---

### 3.6 语义查询

#### 执行 SPARQL 查询

```
POST /ontologies/{ontologyId}/query
```

**请求体:**
```json
{
  "query": "SELECT ?name ?tier WHERE { ?c rdf:type onto:Customer ; onto:name ?name ; onto:tier ?tier }",
  "format": "table",
  "limit": 100,
  "offset": 0
}
```

**响应 (200):**
```json
{
  "success": true,
  "data": {
    "columns": ["name", "tier"],
    "rows": [
      ["Apple Inc.", "Gold"],
      ["Microsoft Corp.", "Gold"]
    ],
    "total": 42,
    "executionTime": "234ms"
  }
}
```

#### 解释查询

```
POST /ontologies/{ontologyId}/query/explain
```

#### 格式化 SPARQL

```
POST /ontologies/{ontologyId}/query/format
```

**请求体:**
```json
{
  "query": "SELECT ?name WHERE { ?c rdf:type onto:Customer }"
}
```

---

### 3.7 自然语言查询

#### NL 转 SPARQL 并执行

```
POST /ontologies/{ontologyId}/nl-query
```

**请求体:**
```json
{
  "question": "显示上月消费金额最高的前5个金牌客户",
  "context": null
}
```

**响应 (200):**
```json
{
  "success": true,
  "data": {
    "question": "显示上月消费金额最高的前5个金牌客户",
    " sparql": "PREFIX onto: <http://ontoagent.com/ontology#>\nSELECT ?name ?monthlySpend WHERE {\n  ?c rdf:type onto:Customer ;\n     onto:name ?name ;\n     onto:tier \"Gold\" ;\n     onto:monthlySpend ?monthlySpend .\n}\nORDER BY DESC(?monthlySpend)\nLIMIT 5",
    "results": {
      "columns": ["name", "monthlySpend"],
      "rows": [
        ["Apple Inc.", 342567],
        ["Microsoft Corp.", 289123]
      ],
      "total": 5,
      "executionTime": "1800ms"
    }
  }
}
```

#### 继续对话（追问）

```
POST /ontologies/{ontologyId}/nl-query/continue
```

**请求体:**
```json
{
  "sessionId": "sess_abc123",
  "question": "这些客户分别下了多少订单？"
}
```

---

### 3.8 数据同步

#### 创建同步任务

```
POST /sync-tasks
```

**请求体:**
```json
{
  "ontologyId": "onto_abc123",
  "datasourceId": "ds_erp_prod",
  "type": "incremental",
  "mode": "cdc"
}
```

#### 获取同步任务列表

```
GET /sync-tasks
```

**查询参数:**
| 参数 | 类型 | 说明 |
|------|------|------|
| ontologyId | string | 本体 ID |
| status | string | running/completed/failed |

#### 获取同步任务详情

```
GET /sync-tasks/{taskId}
```

#### 触发同步

```
POST /sync-tasks/{taskId}/trigger
```

#### 暂停同步

```
POST /sync-tasks/{taskId}/pause
```

#### 取消同步

```
DELETE /sync-tasks/{taskId}
```

#### 获取同步日志

```
GET /sync-tasks/{taskId}/logs
```

---

### 3.9 权限管理

#### 获取用户列表

```
GET /users
```

#### 邀请用户

```
POST /users/invite
```

**请求体:**
```json
{
  "email": "zhangsan@company.com",
  "role": "editor"
}
```

#### 更新用户权限

```
PUT /users/{userId}/permissions
```

**请求体:**
```json
{
  "ontologyPermissions": [
    {
      "ontologyId": "onto_abc123",
      "canRead": true,
      "canWrite": true,
      "canPublish": false,
      "canDelete": false,
      "canManage": false
    }
  ],
  "systemPermissions": {
    "manageDatasources": true,
    "manageUsers": false,
    "viewAuditLogs": true
  }
}
```

#### 移除用户

```
DELETE /users/{userId}
```

---

### 3.10 API 密钥管理

#### 创建 API 密钥

```
POST /api-keys
```

**请求体:**
```json
{
  "name": "Production API Key",
  "scopes": ["query", "nl-query"],
  "rateLimit": 5000
}
```

#### 获取 API 密钥列表

```
GET /api-keys
```

#### 删除 API 密钥

```
DELETE /api-keys/{keyId}
```

#### 重新生成 API 密钥

```
POST /api-keys/{keyId}/regenerate
```

---

### 3.11 导入导出

#### 导出本体 (OWL)

```
GET /ontologies/{ontologyId}/export
```

**查询参数:**
| 参数 | 说明 |
|------|------|
| format | owl/rdf/turtle/json |

#### 导入本体

```
POST /ontologies/import
```

**请求体:** Multipart form-data
- file: OWL/RDF 文件
- mode: merge/replace

---

## 错误码

| 错误码 | HTTP 状态码 | 说明 |
|--------|------------|------|
| INVALID_REQUEST | 400 | 请求参数错误 |
| UNAUTHORIZED | 401 | 未授权 |
| FORBIDDEN | 403 | 权限不足 |
| NOT_FOUND | 404 | 资源不存在 |
| CONFLICT | 409 | 资源冲突 |
| INTERNAL_ERROR | 500 | 服务器内部错误 |

### 业务错误码

| 错误码 | 说明 |
|--------|------|
| ONTOLOGY_NOT_FOUND | 本体不存在 |
| ONTOLOGY_NAME_DUPLICATED | 本体名称重复 |
| OBJECT_TYPE_NOT_FOUND | 对象类型不存在 |
| OBJECT_TYPE_NAME_DUPLICATED | 对象类型名称重复 |
| DATASOURCE_CONNECTION_FAILED | 数据源连接失败 |
| DATASOURCE_NOT_FOUND | 数据源不存在 |
| MAPPING_INVALID | 映射配置无效 |
| VERSION_NOT_FOUND | 版本不存在 |
| SYNC_TASK_RUNNING | 同步任务进行中 |
| QUERY_TIMEOUT | 查询超时 |
| QUERY_SYNTAX_ERROR | SPARQL 语法错误 |

---

## 分页格式

```json
{
  "success": true,
  "data": {
    "items": [],
    "total": 100,
    "page": 1,
    "pageSize": 20,
    "totalPages": 5
  }
}
```

---

## 速率限制

| 级别 | 请求限制 | 窗口 |
|------|---------|------|
| 免费版 | 100 | 每分钟 |
| 专业版 | 1,000 | 每分钟 |
| 企业版 | 5,000 | 每分钟 |

**响应头:**
```
X-RateLimit-Limit: 5000
X-RateLimit-Remaining: 4999
X-RateLimit-Reset: 1705312800
```
