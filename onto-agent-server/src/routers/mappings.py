"""
Phase 6: 映射管理路由
GET    /api/ontologies/{id}/mappings              → 列表
POST   /api/ontologies/{id}/mappings              → 创建/批量创建
GET    /api/ontologies/{id}/mappings/{prop}       → 单个详情
DELETE /api/ontologies/{id}/mappings/{prop}      → 删除
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Any, Optional

from src.core.naming import CamelCaseModel
from src.services import mapping_service

router = APIRouter(prefix="/api/ontologies", tags=["mappings"])


def success(data: Any = None, **extra):
    r = {"success": True}
    if data is not None:
        r["data"] = data
    r.update(extra)
    return r


class MappingItem(CamelCaseModel):
    property_local_name: str
    source_table: str
    source_column: str
    instance_id_column: str
    filter_condition: Optional[str] = None


class MappingCreateRequest(CamelCaseModel):
    property_local_name: str
    source_table: str
    source_column: str
    instance_id_column: str
    filter_condition: Optional[str] = None


# ============================================================
# 属性映射
# ============================================================

@router.get("/{ontology_id}/mappings")
async def list_mappings(ontology_id: str):
    """列出属性映射"""
    mappings = await mapping_service.list_mappings(ontology_id)
    return success(data=mappings)


@router.post("/{ontology_id}/mappings")
async def create_mapping(ontology_id: str, body: MappingCreateRequest | list[MappingCreateRequest]):
    """
    创建或更新属性映射
    支持单条或批量（传入 list）
    """
    if isinstance(body, list):
        mappings = [m.model_dump() for m in body]
        count = await mapping_service.bulk_create_mappings(ontology_id, mappings)
        return success(count=count)
    else:
        data = body.model_dump()
        result = await mapping_service.create_or_update_mapping(ontology_id, **data)
        return success(data=result)


@router.get("/{ontology_id}/mappings/{property_name}")
async def get_mapping(ontology_id: str, property_name: str):
    """获取单个属性映射"""
    mapping = await mapping_service.get_mapping(ontology_id, property_name)
    if not mapping:
        return {"success": False, "error": "Mapping not found"}
    return success(data=mapping)


@router.delete("/{ontology_id}/mappings/{property_name}")
async def delete_mapping(ontology_id: str, property_name: str):
    """删除属性映射"""
    await mapping_service.delete_mapping(ontology_id, property_name)
    return success(success=True)
