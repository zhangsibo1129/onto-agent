"""
Phase 7: SPARQL Query 路由
POST /{id}/sparql              执行 SPARQL
GET  /{id}/sparql/history     查询历史
POST /{id}/sparql/saved       保存查询
GET  /{id}/sparql/saved       列表已保存查询
DELETE /{id}/sparql/saved/{sid} 删除已保存查询
POST /{id}/nl-query          NL → SPARQL
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Any, Optional

from src.core.naming import CamelCaseModel
from src.services import query_service

router = APIRouter(prefix="/api/ontologies", tags=["query"])


def success(data: Any = None, **extra):
    r = {"success": True}
    if data is not None:
        r["data"] = data
    r.update(extra)
    return r


class SparqlExecuteRequest(CamelCaseModel):
    query: str
    saveAs: Optional[str] = None  # 可选：同时保存为指定名称


class SaveQueryRequest(CamelCaseModel):
    name: str
    query: str
    description: Optional[str] = None


class UpdateQueryRequest(CamelCaseModel):
    name: Optional[str] = None
    query: Optional[str] = None
    description: Optional[str] = None


class NlQueryRequest(CamelCaseModel):
    text: str


# ============================================================
# SPARQL 执行
# ============================================================

@router.post("/{ontology_id}/sparql")
async def execute_sparql(ontology_id: str, body: SparqlExecuteRequest):
    """
    执行 SPARQL 查询
    支持 SELECT / ASK / CONSTRUCT / DESCRIBE
    如果传了 saveAs，同时保存为命名查询
    """
    result = await query_service.execute_sparql(ontology_id, body.query)

    # 如果要求同时保存
    if body.saveAs and result.get("success"):
        await query_service.save_query(
            ontology_id=ontology_id,
            name=body.saveAs,
            query=body.query,
            description=f"Auto-saved from SPARQL execution"
        )

    return result


# ============================================================
# 查询历史
# ============================================================

@router.get("/{ontology_id}/sparql/history")
async def get_query_history(ontology_id: str, limit: int = 50):
    """获取查询历史"""
    history = await query_service.get_query_history(ontology_id, limit)
    return success(data=history)


# ============================================================
# 保存的查询
# ============================================================

@router.post("/{ontology_id}/sparql/saved")
async def save_query(ontology_id: str, body: SaveQueryRequest):
    """保存查询"""
    result = await query_service.save_query(
        ontology_id=ontology_id,
        name=body.name,
        query=body.query,
        description=body.description,
    )
    return success(data=result)


@router.get("/{ontology_id}/sparql/saved")
async def list_saved_queries(ontology_id: str):
    """列出所有已保存的查询"""
    queries = await query_service.get_saved_queries(ontology_id)
    return success(data=queries)


@router.get("/{ontology_id}/sparql/saved/{query_id}")
async def get_saved_query(ontology_id: str, query_id: str):
    """获取单个已保存查询"""
    query = await query_service.get_saved_query(query_id)
    if not query:
        return {"success": False, "error": "Query not found"}
    return success(data=query)


@router.put("/{ontology_id}/sparql/saved/{query_id}")
async def update_saved_query(ontology_id: str, query_id: str, body: UpdateQueryRequest):
    """更新已保存查询"""
    query = await query_service.update_saved_query(
        query_id=query_id,
        name=body.name,
        query=body.query,
        description=body.description,
    )
    if not query:
        return {"success": False, "error": "Query not found"}
    return success(data=query)


@router.delete("/{ontology_id}/sparql/saved/{query_id}")
async def delete_saved_query(ontology_id: str, query_id: str):
    """删除已保存查询"""
    await query_service.delete_saved_query(query_id)
    return success(success=True)


# ============================================================
# NL → SPARQL
# ============================================================

@router.post("/{ontology_id}/nl-query")
async def nl_to_sparql(ontology_id: str, body: NlQueryRequest):
    """
    自然语言转 SPARQL（简化版）
    生产环境应调用 LLM API
    """
    result = await query_service.nl_to_sparql(ontology_id, body.text)
    return result
