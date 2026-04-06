# OntoAgent 数据模型定义

## 概述

本文档定义 OntoAgent 平台的核心数据模型，包括实体定义、字段说明、关系约束。

---

## 实体关系图

```
┌─────────────┐       ┌─────────────────┐       ┌─────────────┐
│  Datasource │──1:N──│    Ontology      │──1:N──│ ObjectType  │
└─────────────┘       └─────────────────┘       └──────┬──────┘
                               │                        │
                               │ N:1                    │ N:N
                               ▼                        ▼
                        ┌─────────────┐       ┌─────────────────┐
                        │   Version   │       │    Property     │
                        └─────────────┘       └─────────────────┘
                               │
                               │ N:1
                               ▼
                        ┌─────────────┐
                        │   Mapping   │
                        └──────┬──────┘
                               │
                               │ N:1
                               ▼
                        ┌─────────────┐
                        │  SyncTask   │
                        └─────────────┘
```

---

## 核心实体

### 1. Datasource (数据源)

数据源是连接到外部数据库的配置信息。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | UUID | 是 | 主键，格式: `ds_xxxxxx` |
| name | String | 是 | 数据源名称，如 "ERP-Production" |
| type | Enum | 是 | 数据库类型: `postgresql`, `mysql`, `oracle`, `sqlserver` |
| host | String | 是 | 主机地址 |
| port | Integer | 是 | 端口号，默认 5432 |
| database | String | 是 | 数据库名 |
| schema | String | 否 | Schema，默认 "public" |
| username | String | 是 | 连接用户名 |
| password | String | 是 | 连接密码（加密存储） |
| sslMode | Enum | 否 | SSL 模式: `disable`, `prefer`, `require`, `verify-ca`, `verify-full` |
| connectionPool | Object | 否 | 连接池配置 {min: 5, max: 20} |
| timeout | Integer | 否 | 连接超时时间（秒），默认 30 |
| status | Enum | 是 | 连接状态: `connected`, `disconnected`, `error` |
| tableCount | Integer | 否 | 表数量 |
| lastSyncAt | DateTime | 否 | 最后同步时间 |
| createdAt | DateTime | 是 | 创建时间 |
| updatedAt | DateTime | 是 | 更新时间 |
| createdBy | String | 是 | 创建人 ID |

**约束:**
- name 在同一类型下唯一
- host + port + database + schema 组合唯一

---

### 2. Ontology (本体)

本体是语义域的核心定义，包含多个对象类型。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | UUID | 是 | 主键，格式: `onto_xxxxxx` |
| name | String | 是 | 本体名称，如 "客户360" |
| description | String | 否 | 本体描述 |
| status | Enum | 是 | 状态: `draft`, `published`, `archived` |
| version | String | 是 | 当前版本号，如 "v2.1" |
| datasourceId | UUID | 否 | 关联数据源 ID |
| objectTypeCount | Integer | 是 | 对象类型数量 |
| propertyCount | Integer | 是 | 属性总数 |
| relationshipCount | Integer | 是 | 关系总数 |
| createdAt | DateTime | 是 | 创建时间 |
| updatedAt | DateTime | 是 | 更新时间 |
| publishedAt | DateTime | 否 | 发布时间 |
| createdBy | String | 是 | 创建人 ID |

**约束:**
- name 在同一项目中唯一
- 只有 status=draft 时才能编辑

---

### 3. ObjectType (对象类型)

对象类型是本体中的实体定义，类似面向对象的类。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | UUID | 是 | 主键，格式: `obj_xxxxxx` |
| ontologyId | UUID | 是 | 所属本体 ID |
| name | String | 是 | 对象类型名称，如 "Customer" |
| displayName | String | 否 | 显示名称，如 "客户" |
| description | String | 否 | 描述 |
| properties | Array | 是 | 属性列表 |
| relationships | Array | 否 | 关系列表 |
| createdAt | DateTime | 是 | 创建时间 |
| updatedAt | DateTime | 是 | 更新时间 |

**约束:**
- name 在同一本体内唯一
- 名称必须为 CamelCase 格式

---

### 4. Property (属性)

属性是对象类型的字段定义。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | String | 是 | 属性名，如 "customerId" |
| displayName | String | 否 | 显示名称 |
| description | String | 否 | 描述 |
| dataType | Enum | 是 | 数据类型 |
| isPrimaryKey | Boolean | 否 | 是否主键 |
| isRequired | Boolean | 否 | 是否必填 |
| isUnique | Boolean | 否 | 是否唯一 |
| defaultValue | Any | 否 | 默认值 |
| enumValues | Array | 否 | 枚举值列表 |
| validationRule | String | 否 | 自定义校验规则 |
| indexType | Enum | 否 | 索引类型: `none`, `btree`, `hash` |

**数据类型枚举:**

| 类型 | 说明 | 示例 |
|------|------|------|
| String | 字符串 | "Hello World" |
| Integer | 32位整数 | 12345 |
| Long | 64位整数 | 9223372036854775807 |
| Decimal | 精确小数 | 123.45 |
| Boolean | 布尔值 | true/false |
| Date | 日期 | 2024-01-15 |
| DateTime | 日期时间 | 2024-01-15T10:30:00Z |
| Time | 时间 | 10:30:00 |
| UUID | 通用唯一标识符 | 550e8400-e29b-41d4-a716-446655440000 |
| JSON | JSON 对象 | {"key": "value"} |
| Array | 数组 | [1, 2, 3] |
| Binary | 二进制数据 | ... |

---

### 5. Relationship (关系)

关系是对象类型之间的关联。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | String | 是 | 关系名，如 "places", "has" |
| displayName | String | 否 | 显示名称，如 "下单" |
| description | String | 否 | 描述 |
| targetType | String | 是 | 目标对象类型名称 |
| cardinality | Enum | 是 | 基数: `1:1`, `1:N`, `N:1`, `N:N` |
| isReversible | Boolean | 否 | 是否可反向 |
| reverseName | String | 否 | 反向关系名 |
| onDelete | Enum | 否 | 删除级联: `cascade`, `restrict`, `set_null` |
| onUpdate | Enum | 否 | 更新级联 |

**示例:**

```json
{
  "name": "places",
  "displayName": "下单",
  "targetType": "Order",
  "cardinality": "1:N",
  "isReversible": true,
  "reverseName": "placedBy",
  "onDelete": "cascade"
}
```

---

### 6. Mapping (映射)

映射定义本体属性与数据源表列的对应关系。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | UUID | 是 | 主键，格式: `map_xxxxxx` |
| ontologyId | UUID | 是 | 所属本体 ID |
| objectTypeName | String | 是 | 对象类型名称 |
| datasourceId | UUID | 是 | 数据源 ID |
| tableName | String | 是 | 表名 |
| mappings | Array | 是 | 字段映射列表 |
| status | Enum | 是 | 状态: `pending`, `completed`, `error` |
| verifiedAt | DateTime | 否 | 最后验证时间 |
| verifiedBy | String | 否 | 验证人 |
| createdAt | DateTime | 是 | 创建时间 |
| updatedAt | DateTime | 是 | 更新时间 |

**映射项结构:**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| propertyName | String | 是 | 本体属性名 |
| columnName | String | 是 | 数据表列名 |
| transform | String | 否 | 转换表达式，如 `UPPER(name)` |
| isDirect | Boolean | 否 | 是否直接映射 |
| aggregation | Enum | 否 | 聚合类型: `none`, `sum`, `count`, `avg`, `min`, `max` |

---

### 7. Version (版本)

版本记录本体的历史快照。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | UUID | 是 | 主键，格式: `ver_xxxxxx` |
| ontologyId | UUID | 是 | 所属本体 ID |
| version | String | 是 | 版本号，如 "v2.1" |
| status | Enum | 是 | 状态: `draft`, `published`, `archived` |
| changeLog | Array | 否 | 变更日志 |
| snapshot | JSON | 是 | 完整快照 |
| createdAt | DateTime | 是 | 创建时间 |
| publishedAt | DateTime | 否 | 发布时间 |
| publishedBy | String | 否 | 发布人 |

**变更类型:**

```json
{
  "type": "added|modified|removed",
  "entity": "object_type|property|relationship",
  "name": "Customer",
  "description": "变更描述"
}
```

---

### 8. SyncTask (同步任务)

同步任务管理本体与数据源之间的数据同步。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | UUID | 是 | 主键，格式: `sync_xxxxxx` |
| ontologyId | UUID | 是 | 所属本体 ID |
| datasourceId | UUID | 是 | 数据源 ID |
| type | Enum | 是 | 同步类型: `full`, `incremental` |
| mode | Enum | 是 | 同步模式: `batch`, `cdc` |
| status | Enum | 是 | 状态: `pending`, `running`, `paused`, `completed`, `failed` |
| progress | Integer | 否 | 进度百分比 (0-100) |
| totalRecords | Integer | 否 | 总记录数 |
| processedRecords | Integer | 否 | 已处理记录数 |
| failedRecords | Integer | 否 | 失败记录数 |
| errorMessage | String | 否 | 错误信息 |
| startedAt | DateTime | 否 | 开始时间 |
| completedAt | DateTime | 否 | 完成时间 |
| scheduledAt | DateTime | 否 | 计划执行时间 |
| cronExpression | String | 否 | Cron 表达式（用于定时同步） |

---

### 9. User (用户)

用户是系统使用者。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | UUID | 是 | 主键，格式: `user_xxxxxx` |
| email | String | 是 | 邮箱（登录账号） |
| name | String | 是 | 显示名称 |
| avatar | String | 否 | 头像 URL |
| role | Enum | 是 | 系统角色: `admin`, `editor`, `viewer` |
| status | Enum | 是 | 状态: `active`, `inactive`, `deleted` |
| lastLoginAt | DateTime | 否 | 最后登录时间 |
| createdAt | DateTime | 是 | 创建时间 |
| updatedAt | DateTime | 是 | 更新时间 |

---

### 10. Permission (权限)

权限定义用户对本体的访问控制。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | UUID | 是 | 主键 |
| userId | UUID | 是 | 用户 ID |
| ontologyId | UUID | 是 | 本体 ID |
| canRead | Boolean | 是 | 读取权限 |
| canWrite | Boolean | 是 | 写入权限 |
| canPublish | Boolean | 是 | 发布权限 |
| canDelete | Boolean | 是 | 删除权限 |
| canManage | Boolean | 是 | 管理权限 |
| createdAt | DateTime | 是 | 创建时间 |
| updatedAt | DateTime | 是 | 更新时间 |

---

### 11. APIKey (API 密钥)

API 密钥用于外部系统访问。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | UUID | 是 | 主键，格式: `key_xxxxxx` |
| name | String | 是 | 密钥名称 |
| keyHash | String | 是 | 密钥哈希值 |
| keyPrefix | String | 是 | 密钥前缀 (显示用) |
| scopes | Array | 是 | 权限范围: `query`, `nl-query`, `admin` |
| rateLimit | Integer | 否 | 速率限制 (请求/分钟) |
| status | Enum | 是 | 状态: `active`, `inactive`, `expired` |
| lastUsedAt | DateTime | 否 | 最后使用时间 |
| expiresAt | DateTime | 否 | 过期时间 |
| createdAt | DateTime | 是 | 创建时间 |
| createdBy | String | 是 | 创建人 |

---

### 12. QueryHistory (查询历史)

记录用户的查询历史。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | UUID | 是 | 主键 |
| userId | UUID | 是 | 用户 ID |
| ontologyId | UUID | 是 | 本体 ID |
| queryType | Enum | 是 | 查询类型: `sparql`, `nl` |
| sparql | String | 否 | SPARQL 查询语句 |
| nlQuestion | String | 否 | 自然语言问题 |
| executionTime | Integer | 否 | 执行时间 (毫秒) |
| resultCount | Integer | 否 | 结果数量 |
| status | Enum | 是 | 状态: `success`, `failed` |
| errorMessage | String | 否 | 错误信息 |
| createdAt | DateTime | 是 | 创建时间 |

---

### 13. AuditLog (审计日志)

记录系统操作日志。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | UUID | 是 | 主键 |
| userId | UUID | 是 | 用户 ID |
| action | String | 是 | 操作类型 |
| entityType | String | 是 | 实体类型 |
| entityId | String | 是 | 实体 ID |
| details | JSON | 否 | 操作详情 |
| ipAddress | String | 否 | IP 地址 |
| userAgent | String | 否 | User Agent |
| createdAt | DateTime | 是 | 操作时间 |

**操作类型示例:**
- `ontology.create`
- `ontology.publish`
- `ontology.delete`
- `mapping.create`
- `mapping.verify`
- `sync.start`
- `sync.complete`
- `user.login`
- `user.logout`

---

## 索引设计

### 必须索引

| 表 | 索引字段 | 类型 | 用途 |
|----|---------|------|------|
| ontology | name | btree | 名称唯一性 |
| ontology | status | btree | 状态筛选 |
| object_type | ontology_id | btree | 本体对象查询 |
| property | object_type_id | btree | 对象属性查询 |
| mapping | ontology_id | btree | 本体映射查询 |
| mapping | datasource_id | btree | 数据源映射查询 |
| version | ontology_id | btree | 本体版本查询 |
| version | version | btree | 版本号查询 |
| sync_task | ontology_id | btree | 本体同步查询 |
| sync_task | status | btree | 状态筛选 |
| permission | user_id | btree | 用户权限查询 |
| query_history | user_id | btree | 用户查询历史 |
| query_history | ontology_id | btree | 本体查询历史 |
| query_history | created_at | btree | 时间范围查询 |
| audit_log | user_id | btree | 用户操作查询 |
| audit_log | created_at | btree | 时间范围查询 |

---

## 附：JSON Schema 摘要

```json
// Ontology
{
  "type": "object",
  "properties": {
    "id": { "type": "string", "pattern": "^onto_[a-z0-9]+$" },
    "name": { "type": "string", "minLength": 1, "maxLength": 100 },
    "description": { "type": "string", "maxLength": 500 },
    "status": { "type": "string", "enum": ["draft", "published", "archived"] },
    "version": { "type": "string", "pattern": "^v\\d+\\.\\d+(-[a-z]+)?$" },
    "datasourceId": { "type": "string" },
    "objectTypeCount": { "type": "integer", "minimum": 0 },
    "propertyCount": { "type": "integer", "minimum": 0 },
    "relationshipCount": { "type": "integer", "minimum": 0 }
  },
  "required": ["id", "name", "status", "version"]
}

// ObjectType
{
  "type": "object",
  "properties": {
    "id": { "type": "string", "pattern": "^obj_[a-z0-9]+$" },
    "ontologyId": { "type": "string" },
    "name": { "type": "string", "pattern": "^[A-Z][a-zA-Z0-9]*$" },
    "displayName": { "type": "string" },
    "properties": {
      "type": "array",
      "items": { "$ref": "#/definitions/Property" }
    }
  },
  "required": ["id", "ontologyId", "name", "properties"]
}

// Property
{
  "type": "object",
  "properties": {
    "name": { "type": "string", "pattern": "^[a-z][a-zA-Z0-9]*$" },
    "displayName": { "type": "string" },
    "dataType": {
      "type": "string",
      "enum": ["String", "Integer", "Long", "Decimal", "Boolean", "Date", "DateTime", "Time", "UUID", "JSON", "Array", "Binary"]
    },
    "isPrimaryKey": { "type": "boolean" },
    "isRequired": { "type": "boolean" }
  },
  "required": ["name", "dataType"]
}
```
