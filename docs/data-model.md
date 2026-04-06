# OntoAgent 数据模型定义

## 概述

本文档定义 OntoAgent 平台的核心数据模型，基于 **OWL 2 DL** (Web Ontology Language) 标准，支持语义网的正式语义和推理能力。

---

## OWL 2 核心概念映射

```
OWL 2 概念                    OntoAgent 实现
──────────────────────────────────────────────────────
Class (类)                    ObjectType
DatatypeProperty (数据类型属性)   DataProperty
ObjectProperty (对象属性)        ObjectProperty
Individual (个体)               Instance
rdfs:subClassOf                subClassOf (继承关系)
owl:equivalentClass            equivalentTo (等价)
owl:sameAs                     sameAs (同一)
owl:differentFrom               differentFrom (不同)
Cardinality restrictions        minCardinality, maxCardinality, cardinality
Domain/Range                   domain, range
```

---

## 核心实体关系图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                            OWL 2 本体模型                                │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Datasource  │     │   Ontology   │     │   Version    │
│  (数据源)     │──N:1─│   (本体)     │──1:N─│   (版本)     │
└──────────────┘     └──────────────┘     └──────────────┘
                            │ 1:N
                            ▼
┌──────────────────────────────────────────────────────────────────────┐
│                         ObjectType (对象类型)                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                    │
│  │DataProperty │  │ObjectProperty│  │ SubClassOf │                    │
│  │ (数据属性)  │  │ (对象属性)   │  │ (继承关系)  │                    │
│  └─────────────┘  └─────────────┘  └─────────────┘                    │
└──────────────────────────────────────────────────────────────────────┘
                            │
                            │ N:N (通过 Mapping)
                            ▼
┌──────────────┐     ┌──────────────┐
│   Table      │◄──N:1─│   Mapping   │──1:N──► (多个 Datasource)
│   (数据表)    │       │   (映射)     │
└──────────────┘       └──────────────┘
```

---

## 1. Ontology (本体)

本体是 OWL 2 语义域的完整定义。

### OWL 2 对应

- 本体对应 OWL 2 Ontology
- 支持导入其他本体 (owl:imports)
- 支持声明等价公理 (owl:equivalentTo)

### 字段定义

| 字段 | 类型 | 必填 | OWL 2 对应 | 说明 |
|------|------|------|-----------|------|
| id | UUID | 是 | - | 主键 |
| name | String | 是 | rdfs:label | 本体名称 |
| namespace | String | 是 | @base / Ontology URI | 本体命名空间 |
| description | String | 否 | rdfs:comment | 本体描述 |
| status | Enum | 是 | - | draft/published/archived |
| version | String | 是 | owl:versionInfo | 版本号 (OWL 2 支持版本IRI) |
| imports | Array | 否 | owl:imports | 导入的其他本体 ID |
| equivalentTo | Array | 否 | owl:equivalentTo | 等价本体列表 |
| createdAt | DateTime | 是 | - | 创建时间 |
| updatedAt | DateTime | 是 | - | 更新时间 |
| publishedAt | DateTime | 否 | - | 发布时间 |

**OWL 2 序列化示例:**

```xml
<owl:Ontology rdf:about="http://ontoagent.com/ontology/customer360">
  <rdfs:label>客户360</rdfs:label>
  <rdfs:comment>企业客户全景视图</rdfs:comment>
  <owl:versionInfo>v2.1</owl:versionInfo>
  <owl:imports rdf:resource="http://ontoagent.com/ontology/base"/>
</owl:Ontology>
```

---

## 2. ObjectType (对象类型 / OWL Class)

对象类型对应 OWL 2 的 **Class**，表示一类实体的概念。

### OWL 2 对应

- Class 声明 → ObjectType 定义
- rdfs:subClassOf → ObjectType.subClassOf
- owl:equivalentClass → ObjectType.equivalentTo
- owl:hasKey → ObjectType.hasKey

### 字段定义

| 字段 | 类型 | 必填 | OWL 2 对应 | 说明 |
|------|------|------|-----------|------|
| id | UUID | 是 | - | 主键 |
| ontologyId | UUID | 是 | - | 所属本体 |
| name | String | 是 | rdfs:label | 类名 (CamelCase) |
| displayName | String | 否 | rdfs:label (多语言) | 显示名称 |
| description | String | 否 | rdfs:comment | 类描述 |
| subClassOf | String | 否 | rdfs:subClassOf | 父类名称 |
| equivalentTo | Array | 否 | owl:equivalentTo | 等价类列表 |
| hasKey | Array | 否 | owl:hasKey | 唯一键属性列表 |
| disjointWith | Array | 否 | owl:disjointWith | 互斥类列表 |
| dataProperties | Array | 是 | - | 数据属性列表 |
| objectProperties | Array | 否 | - | 对象属性列表 |

**OWL 2 序列化示例:**

```xml
<owl:Class rdf:about="http://ontoagent.com/ontology#Customer">
  <rdfs:label xml:lang="zh">客户</rdfs:label>
  <rdfs:comment>企业客户实体</rdfs:comment>
  <rdfs:subClassOf rdf:resource="http://ontoagent.com/ontology#Party"/>
  <owl:hasKey rdf:parseType="Collection">
    <rdf:Property rdf:about="http://ontoagent.com/ontology#customerId"/>
  </owl:hasKey>
</owl:Class>
```

---

## 3. DataProperty (数据属性)

数据属性对应 OWL 2 的 **DatatypeProperty**，表示实体与字面值之间的关系。

### OWL 2 对应

- DatatypeProperty → DataProperty
- rdfs:domain → DataProperty.domain
- rdfs:range → DataProperty.range
- FunctionalProperty → DataProperty.maxCardinality = 1

### 字段定义

| 字段 | 类型 | 必填 | OWL 2 对应 | 说明 |
|------|------|------|-----------|------|
| name | String | 是 | rdfs:label | 属性名 (camelCase) |
| displayName | String | 否 | rdfs:label | 显示名称 |
| description | String | 否 | rdfs:comment | 属性描述 |
| domain | String | 是 | rdfs:domain | 所属对象类型 |
| range | Enum | 是 | rdfs:range | 数据类型 |
| cardinality | Enum | 否 | owl:cardinality | 基数约束 |
| minCardinality | Integer | 否 | owl:minCardinality | 最小基数 |
| maxCardinality | Integer | 否 | owl:maxCardinality | 最大基数 |
| minValue | Any | 否 | - | 最小值 (数值类型) |
| maxValue | Any | 否 | - | 最大值 (数值类型) |
| pattern | String | 否 | - | 正则表达式 (字符串) |
| enumValues | Array | 否 | - | 枚举值列表 |
| defaultValue | Any | 否 | - | 默认值 |
| isRequired | Boolean | 否 | owl:minCardinality = 1 | 是否必填 |
| isUnique | Boolean | 否 | owl:hasKey | 是否唯一 |
| isFunctional | Boolean | 否 | owl:FunctionalProperty | 是否函数型 |
| indexType | Enum | 否 | - | 索引类型 |

**数据类型 (OWL 2 Datatype Mapping):**

| OWL 2 Datatype | Range 值 | 说明 |
|---------------|----------|------|
| xsd:string | String | 字符串 |
| xsd:integer | Integer | 整数 |
| xsd:decimal | Decimal | 精确小数 |
| xsd:double | Double | 浮点数 |
| xsd:boolean | Boolean | 布尔值 |
| xsd:dateTime | DateTime | 日期时间 |
| xsd:date | Date | 日期 |
| xsd:time | Time | 时间 |
| xsd:duration | Duration | 时间段 |
| xsd:anyURI | URI | URI |
| xsd:hexBinary | Binary | 二进制 |
| rdf:JSON | JSON | JSON 对象 |
| rdf:langString | String | 带语言标签字符串 |

**OWL 2 序列化示例:**

```xml
<owl:DatatypeProperty rdf:about="http://ontoagent.com/ontology#customerId">
  <rdfs:label xml:lang="zh">客户ID</rdfs:label>
  <rdfs:domain rdf:resource="http://ontoagent.com/ontology#Customer"/>
  <rdfs:range rdf:resource="http://www.w3.org/2001/XMLSchema#string"/>
  <owl:cardinality rdf:datatype="http://www.w3.org/2001/XMLSchema#integer">1</owl:cardinality>
  <owl:equivalentProperty rdf:resource="http://example.org#customerIdentifier"/>
</owl:DatatypeProperty>
```

---

## 4. ObjectProperty (对象属性)

对象属性对应 OWL 2 的 **ObjectProperty**，表示实体之间的关系。

### OWL 2 对应

- ObjectProperty → ObjectProperty
- rdfs:domain → ObjectProperty.domain
- rdfs:range → ObjectProperty.range
- owl:inverseOf → ObjectProperty.inverseOf
- owl:SymmetricProperty → ObjectProperty.isSymmetric
- owl:TransitiveProperty → ObjectProperty.isTransitive
- owl:FunctionalProperty → ObjectProperty.maxCardinality = 1

### 字段定义

| 字段 | 类型 | 必填 | OWL 2 对应 | 说明 |
|------|------|------|-----------|------|
| name | String | 是 | rdfs:label | 属性名 |
| displayName | String | 否 | rdfs:label | 显示名称 |
| description | String | 否 | rdfs:comment | 属性描述 |
| domain | String | 是 | rdfs:domain | 源对象类型 |
| range | String | 是 | rdfs:range | 目标对象类型 |
| cardinality | Enum | 否 | owl:cardinality | 基数约束 |
| minCardinality | Integer | 否 | owl:minCardinality | 最小基数 |
| maxCardinality | Integer | 否 | owl:maxCardinality | 最大基数 |
| inverseOf | String | 否 | owl:inverseOf | 反向属性名 |
| isSymmetric | Boolean | 否 | owl:SymmetricProperty | 是否对称 |
| isTransitive | Boolean | 否 | owl:TransitiveProperty | 是否传递 |
| isReflexive | Boolean | 否 | owl:ReflexiveProperty | 是否自反 |
| isFunctional | Boolean | 否 | owl:FunctionalProperty | 是否函数型 |
| inverseFunctional | Boolean | 否 | owl:InverseFunctionalProperty | 是否逆函数型 |
| subPropertyOf | String | 否 | rdfs:subPropertyOf | 父属性 |
| equivalentTo | Array | 否 | owl:equivalentProperty | 等价属性 |

**OWL 2 序列化示例:**

```xml
<owl:ObjectProperty rdf:about="http://ontoagent.com/ontology#places">
  <rdfs:label xml:lang="zh">下单</rdfs:label>
  <rdfs:domain rdf:resource="http://ontoagent.com/ontology#Customer"/>
  <rdfs:range rdf:resource="http://ontoagent.com/ontology#Order"/>
  <owl:inverseOf rdf:resource="http://ontoagent.com/ontology#placedBy"/>
  <owl:maxCardinality rdf:datatype="http://www.w3.org/2001/XMLSchema#integer">1</owl:maxCardinality>
</owl:ObjectProperty>
```

---

## 5. Datasource (数据源)

数据源是连接到外部数据库的配置，支持多种数据库类型。

### 字段定义

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | UUID | 是 | 主键 |
| name | String | 是 | 数据源名称 |
| type | Enum | 是 | postgresql/mysql/oracle/sqlserver/mongodb |
| host | String | 是 | 主机地址 |
| port | Integer | 是 | 端口号 |
| database | String | 是 | 数据库名 |
| schema | String | 否 | Schema (默认 public) |
| username | String | 是 | 连接用户名 |
| password | String | 是 | 连接密码 (加密) |
| sslMode | Enum | 否 | SSL 模式 |
| connectionPool | Object | 否 | 连接池配置 |
| timeout | Integer | 否 | 超时时间 (秒) |
| status | Enum | 是 | connected/disconnected/error |
| metadata | JSON | 否 | 扩展元数据 |
| createdAt | DateTime | 是 | 创建时间 |
| updatedAt | DateTime | 是 | 更新时间 |

---

## 6. Mapping (映射)

映射定义本体元素与数据源表列的对应关系。

### 设计理念

- **一个本体**可以对应**多个数据源**
- **一个对象类型**可以映射**多个表** (通过 UNION 或 JOIN)
- **一个属性**可以映射到**计算表达式**，而不只是简单列

### 字段定义

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | UUID | 是 | 主键 |
| ontologyId | UUID | 是 | 所属本体 |
| objectTypeName | String | 是 | 对象类型名 |
| datasourceId | UUID | 是 | 数据源 ID |
| tableName | String | 是 | 表名 |
| joinConditions | Array | 否 | 多表连接条件 |
| propertyMappings | Array | 是 | 属性映射列表 |
| status | Enum | 是 | pending/completed/error |
| verifiedAt | DateTime | 否 | 验证时间 |
| createdAt | DateTime | 是 | 创建时间 |
| updatedAt | DateTime | 是 | 更新时间 |

### 属性映射项

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| propertyName | String | 是 | 本体属性名 |
| columnName | String | 是 | 列名 (支持表达式) |
| transform | String | 否 | 转换表达式 |
| aggregation | Enum | 否 | 聚合类型 |
| isPrimaryKey | Boolean | 否 | 是否为主键映射 |

### 多数据源示例

```
本体: 客户360
├── Datasource: CRM-Main
│   └── Mapping: Customer → customers (CRM表)
├── Datasource: ERP-Production
│   └── Mapping: Customer → ar_customers (ERP表)
│   └── Mapping: Customer → customer_transactions (ERP交易表)
└── Datasource: SCM-SupplyChain
    └── Mapping: Customer → supplier_base (供应链表)
```

---

## 7. Version (版本)

版本记录本体的历史快照，支持 OWL 2 版本管理。

### OWL 2 对应

- owl:versionInfo → Version.version
- owl:priorVersion → Version.priorVersion
- owl:backwardCompatibleWith → Version.backwardCompatible
- owl:incompatibleWith → Version.incompatible

### 字段定义

| 字段 | 类型 | 必填 | OWL 2 对应 | 说明 |
|------|------|------|-----------|------|
| id | UUID | 是 | - | 主键 |
| ontologyId | UUID | 是 | - | 所属本体 |
| version | String | 是 | owl:versionInfo | 版本号 |
| status | Enum | 是 | - | draft/published/archived |
| priorVersion | String | 否 | owl:priorVersion | 前一版本 |
| backwardCompatible | String | 否 | owl:backwardCompatibleWith | 兼容版本 |
| incompatibleWith | Array | 否 | owl:incompatibleWith | 不兼容版本列表 |
| changeLog | Array | 否 | - | 变更日志 |
| snapshot | JSON | 是 | - | 完整本体快照 |
| createdAt | DateTime | 是 | - | 创建时间 |
| publishedAt | DateTime | 否 | - | 发布时间 |

### 变更类型

```json
{
  "type": "added|modified|removed",
  "category": "class|property|relationship|annotation",
  "name": "Customer",
  "details": {
    "property": "tier",
    "oldValue": "String",
    "newValue": "Enum"
  }
}
```

---

## 8. SyncTask (同步任务)

同步任务管理本体实例与源数据库之间的数据同步。

### 字段定义

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | UUID | 是 | 主键 |
| ontologyId | UUID | 是 | 所属本体 |
| datasourceId | UUID | 是 | 数据源 ID |
| type | Enum | 是 | full/incremental |
| mode | Enum | 是 | batch/cdc |
| status | Enum | 是 | pending/running/paused/completed/failed |
| filter | JSON | 否 | 同步过滤条件 |
| mappingIds | Array | 否 | 要同步的映射 ID 列表 |
| progress | Integer | 否 | 进度 (0-100) |
| totalRecords | Integer | 否 | 总记录数 |
| processedRecords | Integer | 否 | 已处理数 |
| failedRecords | Integer | 否 | 失败数 |
| errorMessage | String | 否 | 错误信息 |
| lastSyncAt | DateTime | 否 | 最后同步时间 |
| startedAt | DateTime | 否 | 开始时间 |
| completedAt | DateTime | 否 | 完成时间 |
| scheduledAt | DateTime | 否 | 计划执行时间 |
| cronExpression | String | 否 | Cron 表达式 |

---

## 9. Instance (实例)

实例是对象类型的具体实体，对应 OWL 2 的 Individual。

### 字段定义

| 字段 | 类型 | 必填 | OWL 2 对应 | 说明 |
|------|------|------|-----------|------|
| id | UUID | 是 | - | 主键 |
| ontologyId | UUID | 是 | - | 所属本体 |
| objectTypeName | String | 是 | rdf:type | 对象类型 |
| identifier | String | 是 | OWL Named Individual | 实例标识符 |
| dataPropertyValues | JSON | 否 | DatatypeProperty 值 | 数据属性值 |
| objectPropertyValues | JSON | 否 | ObjectProperty 值 | 对象属性值 |
| sameAs | Array | 否 | owl:sameAs | 等同实例 |
| differentFrom | Array | 否 | owl:differentFrom | 不同实例 |
| createdAt | DateTime | 是 | - | 创建时间 |
| updatedAt | DateTime | 是 | - | 更新时间 |

---

## 10. QueryHistory (查询历史)

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | UUID | 是 | 主键 |
| userId | UUID | 是 | 用户 ID |
| ontologyId | UUID | 是 | 本体 ID |
| queryType | Enum | 是 | sparql/nl |
| sparql | String | 否 | SPARQL 语句 |
| nlQuestion | String | 否 | 自然语言问题 |
| executionTime | Integer | 否 | 执行时间 (ms) |
| resultCount | Integer | 否 | 结果数量 |
| status | Enum | 是 | success/failed |
| errorMessage | String | 否 | 错误信息 |
| createdAt | DateTime | 是 | 创建时间 |

---

## 11. User (用户)

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | UUID | 是 | 主键 |
| email | String | 是 | 邮箱 (唯一) |
| name | String | 是 | 显示名称 |
| avatar | String | 否 | 头像 URL |
| role | Enum | 是 | admin/editor/viewer |
| status | Enum | 是 | active/inactive/deleted |
| lastLoginAt | DateTime | 否 | 最后登录 |
| createdAt | DateTime | 是 | 创建时间 |
| updatedAt | DateTime | 是 | 更新时间 |

---

## 12. Permission (权限)

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | UUID | 是 | 主键 |
| userId | UUID | 是 | 用户 ID |
| ontologyId | UUID | 是 | 本体 ID (null 表示全局) |
| resourceType | Enum | 是 | ontology/datasource/mapping |
| resourceId | String | 否 | 资源 ID |
| canRead | Boolean | 是 | 读取权限 |
| canWrite | Boolean | 是 | 写入权限 |
| canPublish | Boolean | 是 | 发布权限 |
| canDelete | Boolean | 是 | 删除权限 |
| canManage | Boolean | 是 | 管理权限 |
| createdAt | DateTime | 是 | 创建时间 |
| updatedAt | DateTime | 是 | 更新时间 |

---

## 13. APIKey (API 密钥)

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | UUID | 是 | 主键 |
| name | String | 是 | 密钥名称 |
| keyHash | String | 是 | 密钥哈希 |
| keyPrefix | String | 是 | 显示前缀 |
| scopes | Array | 是 | 权限范围 |
| rateLimit | Integer | 否 | 速率限制 |
| status | Enum | 是 | active/inactive/expired |
| lastUsedAt | DateTime | 否 | 最后使用 |
| expiresAt | DateTime | 否 | 过期时间 |
| createdAt | DateTime | 是 | 创建时间 |

---

## 14. AuditLog (审计日志)

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

---

## 数据类型完整映射表

| OWL 2 / XSD | Java Type | JavaScript Type | 说明 |
|-------------|-----------|-----------------|------|
| xsd:string | String | string | 字符串 |
| xsd:normalizedString | String | string | 规范化字符串 |
| xsd:token | String | string | 令牌 |
| xsd:integer | BigInteger | number | 任意精度整数 |
| xsd:int | Integer | number | 32位整数 |
| xsd:long | Long | number | 64位整数 |
| xsd:decimal | BigDecimal | number | 精确小数 |
| xsd:float | Float | number | 32位浮点 |
| xsd:double | Double | number | 64位浮点 |
| xsd:boolean | Boolean | boolean | 布尔值 |
| xsd:date | LocalDate | string (YYYY-MM-DD) | 日期 |
| xsd:dateTime | Instant | string (ISO 8601) | 日期时间 |
| xsd:time | LocalTime | string (HH:mm:ss) | 时间 |
| xsd:duration | Duration | string | 时间段 |
| xsd:gYear | Year | number | 年份 |
| xsd:gMonth | Month | number | 月份 |
| xsd:anyURI | URI | string | URI |
| xsd:hexBinary | byte[] | string | 十六进制 |
| xsd:base64Binary | byte[] | string | Base64 |
| rdf:JSON | JsonNode | object | JSON 对象 |
| rdf:langString | String | string | 带语言标签 |

---

## 约束定义

### OWL 2 DL 约束支持

| 约束类型 | 支持 | 说明 |
|---------|------|------|
| rdfs:subClassOf | ✅ | 类继承 |
| owl:equivalentClass | ✅ | 等价类 |
| owl:disjointWith | ✅ | 互斥类 |
| owl:hasKey | ✅ | 唯一键 |
| owl:cardinality | ✅ | 精确基数 |
| owl:minCardinality | ✅ | 最小基数 |
| owl:maxCardinality | ✅ | 最大基数 |
| owl:someValuesFrom | ✅ | 存在量化 |
| owl:allValuesFrom | ✅ | 全称量化 |
| owl:inverseOf | ✅ | 属性逆 |
| owl:SymmetricProperty | ✅ | 对称属性 |
| owl:TransitiveProperty | ✅ | 传递属性 |
| owl:FunctionalProperty | ✅ | 函数型属性 |
| owl:InverseFunctionalProperty | ✅ | 逆函数型属性 |

---

## 索引设计

| 表 | 索引字段 | 类型 | 用途 |
|---|---------|------|------|
| ontology | name | btree | 名称唯一性 |
| ontology | namespace | btree | 命名空间唯一性 |
| ontology | status | btree | 状态筛选 |
| object_type | ontology_id | btree | 本体对象查询 |
| object_type | name + ontology_id | btree | 对象唯一性 |
| data_property | domain + name | btree | 属性唯一性 |
| object_property | domain + name | btree | 属性唯一性 |
| mapping | ontology_id | btree | 本体映射查询 |
| mapping | datasource_id | btree | 数据源映射查询 |
| mapping | object_type_name + datasource_id | btree | 映射唯一性 |
| version | ontology_id + version | btree | 版本唯一性 |
| sync_task | ontology_id | btree | 本体同步查询 |
| sync_task | status | btree | 状态筛选 |
| sync_task | scheduled_at | btree | 定时任务调度 |
| permission | user_id | btree | 用户权限查询 |
| query_history | user_id | btree | 用户查询历史 |
| query_history | created_at | btree | 时间范围查询 |
| audit_log | user_id | btree | 用户操作查询 |
| audit_log | entity_type + entity_id | btree | 实体操作查询 |
| audit_log | created_at | btree | 时间范围查询 |
