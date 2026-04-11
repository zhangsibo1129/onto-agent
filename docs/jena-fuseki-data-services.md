# Jena Fuseki 数据服务 API 调研文档

> 调研日期：2026-04-11
> 调研目的：列出 Jena Fuseki 的所有数据服务 API

---

## 1. 概述

Apache Jena Fuseki 是一个 SPARQL 服务器，可作为独立服务器运行或嵌入应用程序中。Fuseki 提供：

- SPARQL 1.1 查询和更新协议
- SPARQL Graph Store 协议 (HTTP RDF 操作)
- TDB/TDB2 持久化存储层
- 文本查询支持

---

## 2. SPARQL Protocol API

用于 RDF 数据查询和更新。

| 端点 | 方法 | 描述 |
|------|------|------|
| `/{dataset}/sparql` | GET/POST | SPARQL 查询 |
| `/{dataset}/query` | GET/POST | SPARQL 查询 (别名) |
| `/{dataset}/update` | POST | SPARQL Update 更新 |

### 使用示例

```bash
# SPARQL 查询
curl -G "http://localhost:3030/dataset/sparql" --data-urlencode "query=SELECT * WHERE { ?s ?p ?o } LIMIT 10"

# SPARQL 更新
curl -X POST "http://localhost:3030/dataset/update" --data-urlencode "query=INSERT DATA { <http://example.org> <http://example.org/name> \"Test\" }"
```

---

## 3. SPARQL Graph Store Protocol API

用于通过 HTTP 直接操作 RDF 图 (无需 SPARQL 语法)。

| 端点 | 方法 | 描述 |
|------|------|------|
| `/{dataset}/data` | GET | 获取默认图 |
| `/{dataset}/data` | POST | 添加 RDF 三元组 |
| `/{dataset}/data` | PUT | 替换默认图 |
| `/{dataset}/data` | DELETE | 删除默认图 |
| `/{dataset}/data?graph={uri}` | GET | 获取指定命名图 |
| `/{dataset}/data?graph={uri}` | POST | 添加到指定命名图 |
| `/{dataset}/data?graph={uri}` | PUT | 替换指定命名图 |
| `/{dataset}/data?graph={uri}` | DELETE | 删除指定命名图 |

### 使用示例

```bash
# 获取默认图
curl "http://localhost:3030/dataset/data"

# 添加数据 (Turtle 格式)
curl -X POST "http://localhost:3030/dataset/data" \
  -H "Content-Type: text/turtle" \
  -d '<http://example.org> <http://example.org/name> "Test" .'

# 操作指定命名图
curl "http://localhost:3030/dataset/data?graph=http://example.org/graph1"
```

---

## 4. 文件上传 API

| 端点 | 方法 | 描述 |
|------|------|------|
| `/{dataset}/upload` | POST | 上传 RDF 文件 |

支持多种 RDF 格式 (TTL, RDF/XML, N-Triples, N-Quads 等)。

---

## 5. 管理 API ($/ 前缀)

所有管理操作使用 `/$` 前缀避免与数据集名称冲突。

### 5.1 基础运营

| 端点 | 方法 | 描述 |
|------|------|------|
| `/$/ping` | GET/POST | 服务存活检查 |
| `/$/server` | GET | 获取服务器基本信息 |
| `/$/status` | GET | 服务器状态 (同 server) |

### 5.2 数据集管理

| 端点 | 方法 | 描述 |
|------|------|------|
| `/$/datasets` | GET | 列出所有数据集 |
| `/$/datasets` | POST | 创建新数据集 |
| `/$/datasets/{name}` | GET | 获取数据集信息 |
| `/$/datasets/{name}` | DELETE | 删除数据集 |

**创建数据集参数**：
- `dbType`: `mem` | `tdb` | `tdb1` | `tdb2`
- `dbName`: 数据集名称

### 5.3 备份与恢复

| 端点 | 方法 | 描述 |
|------|------|------|
| `/$/backup/{name}` | POST | 备份数据集 |
| `/$/backups-list` | GET | 列出备份文件 |

**说明**：
- 备份文件保存在 `backups/` 目录
- 格式：gzip 压缩的 N-Quads
- 从 4.7.0 版本起，写入临时文件后重命名，保证完整性

### 5.4 数据库压缩

| 端点 | 方法 | 描述 |
|------|------|------|
| `/$/compact/{name}` | POST | 压缩 TDB2 数据库 |
| `/$/compact/{name}?deleteOld=true` | POST | 压缩并删除旧存储 |

**说明**：
- 仅适用于 TDB2 数据集
- 返回任务 ID，可通过 `/$/tasks/{id}` 监控

### 5.5 统计与监控

| 端点 | 方法 | 描述 |
|------|------|------|
| `/$/stats` | GET | 所有数据集请求统计 |
| `/$/stats/{name}` | GET | 指定数据集请求统计 |
| `/$/metrics` | GET | 性能指标 |

### 5.6 后台任务

| 端点 | 方法 | 描述 |
|------|------|------|
| `/$/tasks` | GET | 所有后台任务列表 |
| `/$/tasks/{id}` | GET | 特定任务详情 |
| `/$/sleep` | POST | 休眠服务器 |

**任务响应示例**：
```json
[
  {
    "task": "backup",
    "taskId": "1",
    "started": "2024-05-28T12:52:50.859+01:00",
    "finished": "2024-05-28T12:52:51.860+01:00",
    "success": true
  }
]
```

**任务状态字段**：
- `started`: 任务开始时间
- `finished`: 任务完成时间
- `success`: 是否成功
- `finishPoint`: 完成标记

---

## 6. 数据集配置

Fuseki 支持多种数据集类型：

### 6.1 内存数据集

```
<#dataset> rdf:type ja:MemoryDataset .
```

### 6.2 TDB2 数据集

```
<#dataset> rdf:type tdb2:DatasetTDB2 ;
    tdb2:location "/path/to/db" .
```

### 6.3 TDB1 数据集

```
<#dataset> rdf:type tdb1:DatasetTDB ;
    tdb1:location "/path/to/db" .
```

### 6.4 推理数据集

支持多种推理器：
- Generic Rule Reasoner
- Transitive Reasoner
- RDFS Rule Reasoner
- OWL FB Rule Reasoner
- OWL Mini FB Rule Reasoner
- OWL Micro FB Rule Reasoner

---

## 7. 服务端点配置

在 `config.ttl` 中定义服务：

```turtle
<#service> rdf:type fuseki:Service ;
    fuseki:name "ds" ;
    fuseki:endpoint [
        fuseki:operation fuseki:query ;
        fuseki:name "sparql"
    ] ;
    fuseki:endpoint [
        fuseki:operation fuseki:update ;
        fuseki:name "update"
    ] ;
    fuseki:endpoint [
        fuseki:operation fuseki:gsp_r ;
        fuseki:name "get"
    ] ;
    fuseki:endpoint [
        fuseki:operation fuseki:gsp_rw ;
        fuseki:name "data"
    ] ;
    fuseki:endpoint [
        fuseki:operation fuseki:upload ;
        fuseki:name "upload"
    ] ;
    fuseki:dataset <#dataset> .
```

### 可用操作类型

| 操作 | 描述 |
|------|------|
| `fuseki:query` | SPARQL 查询 |
| `fuseki:update` | SPARQL 更新 |
| `fuseki:gsp_r` | Graph Store 协议 (只读) |
| `fuseki:gsp_rw` | Graph Store 协议 (读写) |
| `fuseki:upload` | 文件上传 |

---

## 8. 默认端口

- 3030 (Fuseki 服务默认端口)

---

## 9. 参考链接

- [Apache Jena Fuseki 官方文档](https://jena.apache.org/documentation/fuseki2/)
- [SPARQL 1.1 Protocol 规范](https://www.w3.org/TR/sparql11-protocol/)
- [SPARQL 1.1 Graph Store Protocol 规范](https://www.w3.org/TR/sparql11-http-rdf-update/)