"""
Phase 7: Query Service
SPARQL 执行 + 历史 + 保存查询
"""
import uuid
import time
from datetime import datetime
from typing import Optional

from sqlalchemy import text

from src.database import SystemSession
from src.services.jena import get_jena_client
from src.logging_config import get_logger

logger = get_logger("query_service")


# ============================================================
# SPARQL 执行
# ============================================================

async def execute_sparql(ontology_id: str, query: str) -> dict:
    """
    执行 SPARQL 查询，记录历史
    """
    import time
    start_ms = int(time.time() * 1000)

    # 1. 获取本体信息
    async with SystemSession() as session:
        result = await session.execute(
            text("SELECT base_iri, dataset FROM ontologies WHERE id = :id"),
            {"id": ontology_id}
        )
        row = result.fetchone()
        if not row:
            return {"success": False, "error": "Ontology not found"}
        base_iri = row.base_iri
        dataset = row.dataset

    # 2. 执行 SPARQL
    history_id = str(uuid.uuid4())
    error_msg = None
    result_count = 0
    results_data = None

    try:
        jena = get_jena_client(dataset)

        # 检测 query type
        query_upper = query.strip().upper()
        if query_upper.startswith("SELECT"):
            query_type = "SELECT"
            rows = jena.query(query)
            # 展开结果
            results_data = _expand_results(rows)
            result_count = len(results_data)
        elif query_upper.startswith("ASK"):
            query_type = "ASK"
            result_bool = jena.query_ask(query)
            results_data = result_bool
            result_count = 1 if result_bool else 0
        elif query_upper.startswith("CONSTRUCT") or query_upper.startswith("DESCRIBE"):
            query_type = "CONSTRUCT"
            turtle = jena.query_construct(query)
            results_data = turtle
            result_count = turtle.count("\n") if turtle else 0
        else:
            return {"success": False, "error": "Unsupported query type"}

    except Exception as e:
        error_msg = str(e)
        query_type = _detect_query_type(query)
        logger.error(f"SPARQL execution failed: {e}")

    execution_ms = int(time.time() * 1000) - start_ms

    # 3. 记录历史
    async with SystemSession() as session:
        await session.execute(
            text("""
                INSERT INTO query_history
                  (id, ontology_id, query_type, query_text, result_count, error_message, execution_time_ms, created_at)
                VALUES
                  (:id, :onto_id, :qtype, :qtext, :rcount, :err, :exec_ms, :now)
            """),
            {
                "id": history_id,
                "onto_id": ontology_id,
                "qtype": query_type,
                "qtext": query,
                "rcount": result_count,
                "err": error_msg,
                "exec_ms": execution_ms,
                "now": datetime.now()
            }
        )
        await session.commit()

    return {
        "success": error_msg is None,
        "queryType": query_type,
        "results": results_data,
        "resultCount": result_count,
        "executionTimeMs": execution_ms,
        "historyId": history_id,
        "error": error_msg
    }


def _detect_query_type(query: str) -> str:
    q = query.strip().upper()
    if q.startswith("SELECT"):
        return "SELECT"
    elif q.startswith("ASK"):
        return "ASK"
    elif q.startswith("CONSTRUCT"):
        return "CONSTRUCT"
    elif q.startswith("DESCRIBE"):
        return "DESCRIBE"
    return "UNKNOWN"


def _expand_results(rows: list) -> list:
    """展开 Jena 返回的 Value 对象为 Python 原生类型"""
    expanded = []
    for row in rows:
        expanded_row = {}
        for key, val in row.items():
            if isinstance(val, dict):
                # Value object: {"type": "literal", "value": "..."}
                expanded_row[key] = val.get("value", val)
            elif hasattr(val, 'value'):
                expanded_row[key] = val.value
            else:
                expanded_row[key] = val
        expanded.append(expanded_row)
    return expanded


# ============================================================
# 查询历史
# ============================================================

async def get_query_history(ontology_id: str, limit: int = 50) -> list[dict]:
    """获取查询历史"""
    async with SystemSession() as session:
        result = await session.execute(
            text("""
                SELECT id, query_type, query_text, result_count, error_message,
                       execution_time_ms, created_at
                FROM query_history
                WHERE ontology_id = :onto_id
                ORDER BY created_at DESC
                LIMIT :lim
            """),
            {"onto_id": ontology_id, "lim": limit}
        )
        return [dict(r._mapping) for r in result.fetchall()]


# ============================================================
# 保存的查询
# ============================================================

async def save_query(
    ontology_id: str,
    name: str,
    query: str,
    description: str = None,
) -> dict:
    """保存查询"""
    query_type = _detect_query_type(query)
    qid = str(uuid.uuid4())
    now = datetime.now()

    async with SystemSession() as session:
        await session.execute(
            text("""
                INSERT INTO saved_queries
                  (id, ontology_id, name, description, query_type, query_text, created_at, updated_at)
                VALUES (:id, :onto_id, :name, :desc, :qtype, :qtext, :now, :now)
            """),
            {
                "id": qid,
                "onto_id": ontology_id,
                "name": name,
                "desc": description,
                "qtype": query_type,
                "qtext": query,
                "now": now
            }
        )
        await session.commit()

    return await get_saved_query(qid)


async def get_saved_queries(ontology_id: str) -> list[dict]:
    """获取所有已保存的查询"""
    async with SystemSession() as session:
        result = await session.execute(
            text("""
                SELECT id, name, description, query_type, query_text, created_at, updated_at
                FROM saved_queries
                WHERE ontology_id = :onto_id
                ORDER BY updated_at DESC
            """),
            {"onto_id": ontology_id}
        )
        return [dict(r._mapping) for r in result.fetchall()]


async def get_saved_query(query_id: str) -> Optional[dict]:
    """获取单个已保存查询"""
    async with SystemSession() as session:
        result = await session.execute(
            text("SELECT * FROM saved_queries WHERE id = :id"),
            {"id": query_id}
        )
        row = result.fetchone()
        return dict(row._mapping) if row else None


async def update_saved_query(query_id: str, name: str = None, query: str = None, description: str = None) -> Optional[dict]:
    """更新已保存查询"""
    updates = []
    params = {"id": query_id}
    if name is not None:
        updates.append("name = :name")
        params["name"] = name
    if query is not None:
        updates.append("query_text = :qtext")
        params["qtext"] = query
        updates.append("query_type = :qtype")
        params["qtype"] = _detect_query_type(query)
    if description is not None:
        updates.append("description = :desc")
        params["desc"] = description
    if not updates:
        return await get_saved_query(query_id)

    updates.append("updated_at = :now")
    params["now"] = datetime.now()

    async with SystemSession() as session:
        await session.execute(
            text(f"UPDATE saved_queries SET {', '.join(updates)} WHERE id = :id"),
            params
        )
        await session.commit()

    return await get_saved_query(query_id)


async def delete_saved_query(query_id: str) -> bool:
    """删除已保存查询"""
    async with SystemSession() as session:
        await session.execute(
            text("DELETE FROM saved_queries WHERE id = :id"),
            {"id": query_id}
        )
        await session.commit()
    return True


# ============================================================
# NL → SPARQL（简化版）
# ============================================================

async def nl_to_sparql(ontology_id: str, nl_text: str) -> dict:
    """
    自然语言转 SPARQL（简化版）

    实际生产中应该调用 LLM API，这里用模板 + 启发式规则做简化实现。
    支持常见的 NL 模式：
    - "显示所有 X" → SELECT * WHERE { ?s rdf:type onto:X }
    - "有多少 X" → SELECT COUNT(*) WHERE { ... }
    - "X 的 Y 是多少" → SELECT ?y WHERE { ?x onto:Y ?y }
    """
    nl_lower = nl_text.lower().strip()

    # 获取本体信息用于生成合适的 IRI
    async with SystemSession() as session:
        result = await session.execute(
            text("SELECT base_iri FROM ontologies WHERE id = :id"),
            {"id": ontology_id}
        )
        row = result.fetchone()
        base_iri = row.base_iri if row else "http://example.com/ontology#"

    prefix = f"PREFIX : <{base_iri}>\nPREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\nPREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n"

    # 简单模板匹配
    generated_sparql = None

    # "显示所有 X" / "列出所有 X"
    if any(kw in nl_lower for kw in ["显示所有", "列出所有", "查询所有", "所有"]):
        # 提取类名
        import re
        match = re.search(r'[X类客户订单产品供应商]', nl_lower)
        if match:
            class_name = match.group()
            class_map = {"类": "Thing", "客户": "Customer", "订单": "Order",
                         "产品": "Product", "供应商": "Supplier"}
            cls = class_map.get(class_name, "Thing")
            generated_sparql = f"{prefix}SELECT ?s ?p ?o\nWHERE {{ ?s rdf:type :{cls} ; ?p ?o }}\nLIMIT 100"

    if not generated_sparql:
        # 默认返回简单查询
        generated_sparql = f"""{prefix}SELECT ?s ?p ?o
WHERE {{
  ?s ?p ?o .
}}
LIMIT 50"""

    return {
        "success": True,
        "nlText": nl_text,
        "sparql": generated_sparql,
        "note": "This is a simplified NL→SPARQL converter. For production, use an LLM API."
    }
