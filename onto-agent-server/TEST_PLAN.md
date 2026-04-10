# Onto-Agent 修改方案测试计划

## 测试环境准备

### 1. 依赖检查

```bash
cd /Users/zhangsibo/Projects/onto-agent/onto-agent-server
source .venv/bin/activate
pip list | grep -E "pytest|sqlalchemy|httpx|SPARQLWrapper|rdflib"
```

### 2. 启动必要服务

#### PostgreSQL
```bash
docker run -d --name onto-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=onto_agent \
  -p 5432:5432 postgres:15
```

#### Apache Jena Fuseki
```bash
docker run -d --name onto-fuseki \
  -p 3030:3030 \
  -e ADMIN_PASSWORD=admin \
  jasperklee/fuseki:latest

curl http://localhost:3030/$/ping
```

---

## 第一阶段：单元测试

### 测试 1.1：模型定义测试

```bash
source .venv/bin/activate
python -c "
from src.models.ontology import (
    Ontology, OntologyVersion, EntityIndex, 
    OperationLog, EntityStatus, OperationType
)
print('OK: All models imported')
"
```

### 测试 1.2：Jena Named Graph

```bash
source .venv/bin/activate
python -c "
from src.services.jena_named_graph import get_jena_client_for_default_dataset
jena = get_jena_client_for_default_dataset()
print(f'dataset: {jena.dataset}')
"
```

### 测试 1.3：Saga 事务

```bash
source .venv/bin/activate
pytest tests/test_named_graph.py::TestNamedGraph -v -k "not integration"
pytest tests/test_named_graph.py::TestSagaManager -v
pytest tests/test_named_graph.py::TestTransactionConsistency -v
```

---

## 第二阶段：集成测试

### 测试 2.1：数据库迁移

```bash
cd onto-agent-server
python migrations/versions/002_update_ontology_named_graphs.py

# 验证
psql -U postgres -d onto_agent -c "\dt"
```

### 测试 2.2：本体创建

```bash
curl -X POST http://localhost:8000/api/v1/ontologies \
  -H "Content-Type: application/json" \
  -d '{"name": "TestCompany", "description": "Test"}'
```

验证：
```bash
psql -U postgres -d onto_agent -c "SELECT name, tbox_graph_uri, dataset FROM ontologies;"
# 预期: dataset = '/onto-agent'
```

### 测试 2.3：类创建（Saga）

```bash
curl -X POST "http://localhost:8000/api/v1/ontologies/{id}/classes" \
  -H "Content-Type: application/json" \
  -d '{"name": "Customer", "displayName": "客户"}'
```

查询 Saga 状态：
```bash
curl "http://localhost:8000/api/v1/ontologies/debug/saga/{saga_id}"
```

### 测试 2.4：版本发布

```bash
curl -X POST "http://localhost:8000/api/v1/ontologies/{id}/versions" \
  -H "Content-Type: application/json" \
  -d '{"change_log": [{"type": "added", "category": "class", "name": "Customer"}]}'
```

---

## 测试检查清单

| 测试项 | 状态 |
|--------|------|
| 模型定义导入 | ⬜ |
| Named Graph 方法 | ⬜ |
| Saga 事务 | ⬜ |
| 故障补偿 | ⬜ |
| 数据库迁移 | ⬜ |
| 本体创建 | ⬜ |
| 类创建(Saga) | ⬜ |
| 版本发布 | ⬜ |

---

## 回滚方案

```bash
cd onto-agent-server
python -c "
from sqlalchemy import create_engine, text
import os
engine = create_engine(os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/onto_agent'))
with engine.connect() as conn:
    conn.execute(text('DROP TABLE IF EXISTS operation_logs'))
    conn.execute(text('DROP TABLE IF EXISTS ontology_versions'))
    conn.execute(text('ALTER TABLE entity_index DROP COLUMN IF EXISTS graph_uri'))
    conn.commit()
print('Rolled back')
"

# Jena 回滚
curl -X POST "http://localhost:3030/onto-agent/update" \
  -H "Content-Type: application/sparql-update" \
  -d "DROP SILENT GRAPH <http://onto-agent.com/ontology/TestCompany#tbox>"
```