# 代码审查报告与重构方案

## 一、发现的主要坏味道

### 1. 上帝文件（God Files）

| 文件 | 行数 | 函数数 | 问题 |
|------|------|--------|------|
| `ontology.py` | 981 | 31 | 单文件过大，职责不清 |
| `jena_client.py` | 1007 | 9 | 单文件过大，混合了多个概念的代码 |

### 2. 代码重复（Duplicated Code）

**模式 A：CRUD 操作重复**
```python
# 大量重复的 session.execute + select + commit 模式
result = await session.execute(select(Ontology).where(...))
o = result.scalar_one_or_none()
if not o: return False
await session.delete(o)
await session.commit()
```

**模式 B：Jena 查询结果解析重复**
```python
# _get_label, _get_comment, _get_super_classes 等方法结构相同
```

### 3. 异常处理过宽（Broad Exception）

```python
# 大量 bare except Exception
except Exception:
    pass

# 应该使用具体异常类型
except JenaServiceError as e:
    logger.error(f"Jena service error: {e}")
except ValueError as e:
    raise ValidationError(f"Invalid input: {e}")
```

### 4. 硬编码（Hard-coded Values）

```python
# 分散的端口和主机配置
port=dump.get("port") or 5432  # 重复出现 5 次
host=datasource.host or "localhost"  # 重复出现 5 次

# 应该集中在 config.py
FUSEKI_DEFAULT_PORT = 3030
POSTGRES_DEFAULT_PORT = 5432
```

### 5. 命名图扩展注入副作用（Side Effect Injection）

```python
# jena_named_graph.py 末尾
inject_named_graph_methods(JenaClient)  # 运行时修改类

# 问题：
# 1. 隐式依赖，导入顺序敏感
# 2. 方法注入后 JenaClient 才有这些方法
# 3. 测试困难
```

### 6. 单体路由（Massive Router）

```python
# ontology.py (router) 处理所有本体相关操作
# 1339 行，职责过重
```

### 7. 缺少分层（Missing Layers）

```
当前结构：
├── routers/ontology.py  (路由 + 业务逻辑混合)
├── services/ontology.py (业务逻辑 + 数据访问混合)
├── models/ontology.py   (数据模型)

建议结构：
├── routers/     (路由定义，仅处理请求/响应)
├── services/    (业务逻辑，不直接操作 DB)
├── repositories/(数据访问，封装查询)
├── schemas/     (请求/响应 DTO)
```

---

## 二、重构方案

### 阶段 1：提取 Repository 层（Data Access）

**目标**：解耦数据访问逻辑

```
src/repositories/
├── __init__.py
├── ontology_repository.py   # Ontology CRUD
└── entity_repository.py     # EntityIndex CRUD
```

**示例**：
```python
# 之前
async def delete_ontology(ontology_id: str) -> bool:
    async with SystemSession() as session:
        result = await session.execute(select(Ontology).where(...))
        ...

# 之后
class OntologyRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, ontology_id: str) -> Optional[Ontology]:
        result = await self.session.execute(
            select(Ontology).where(Ontology.id == ontology_id)
        )
        return result.scalar_one_or_none()
    
    async def delete(self, ontology: Ontology) -> bool:
        self.session.delete(ontology)
        await self.session.commit()
```

### 阶段 2：拆分 JenaClient

**目标**：将 JenaClient 按领域拆分

```
src/services/jena/
├── __init__.py
├── client.py              # 基础客户端（HTTP、连接管理）
├── ontology_tbox.py       # TBox 操作（类、属性）
├── ontology_abox.py       # ABox 操作（Individual）
├── named_graph.py         # Named Graph 管理
└── queries.py             # SPARQL 查询模板
```

### 阶段 3：统一异常处理

**目标**：使用具体异常类型

```python
# src/exceptions.py
class OntologyNotFoundError(Exception):
    pass

class JenaQueryError(Exception):
    pass

class ValidationError(Exception):
    pass

# 使用
raise OntologyNotFoundError(f"Ontology {id} not found")
```

### 阶段 4：配置统一管理

**目标**：消除硬编码

```python
# src/config.py
@dataclass
class JenaConfig:
    host: str = "localhost"
    port: int = 3030
    dataset: str = "/onto-agent"
    timeout: int = 30

@dataclass  
class PostgresConfig:
    host: str = "localhost"
    system_port: int = 5432
    business_port: int = 5433
    system_db: str = "system_db"
    business_db: str = "onto_agent"
```

### 阶段 5：路由拆分

**目标**：按资源拆分路由

```
src/routers/
├── __init__.py
├── ontologies.py      # 本体 CRUD
├── classes.py         # 类管理
├── properties.py      # 属性管理
├── individuals.py     # 个体管理
└── datasources.py    # 数据源管理
```

---

## 三、推荐实施顺序

| 阶段 | 任务 | 复杂度 | 风险 |
|------|------|--------|------|
| 1 | 提取 Repository 层 | 中 | 低 |
| 2 | 统一异常处理 | 低 | 低 |
| 3 | 配置统一管理 | 低 | 低 |
| 4 | 拆分 JenaClient | 高 | 中 |
| 5 | 路由拆分 | 中 | 中 |

**建议**：每次重构后运行测试，确保功能不受影响。

---

## 四、立即可做的改进（无需大重构）

1. **添加类型注解**：为缺失类型的函数添加类型
2. **使用日志代替 print**：替换 `print(f"[Jena] ...")` 为 `logger.info(...)`
3. **提取常量**：将 `5432`, `3030` 等提取为命名常量
4. **添加 docstring**：为公开函数添加文档字符串
5. **简化 inject 模式**：将 `jena_named_graph.py` 的注入改为显式调用

---

*审查时间: 2026-04-11*
