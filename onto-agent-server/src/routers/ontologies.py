"""
本体管理路由

处理本体的 CRUD、版本、发布等操作
"""

from typing import Any
from fastapi import APIRouter

from src.services import ontology as ontology_service
from src.schemas.ontology import (
    OntologyResponse,
    OntologyDetailResponse,
    OntologyCreate,
)

router = APIRouter(prefix="/api/ontologies", tags=["ontologies"])


def success_response(data: Any):
    return {"success": True, "data": data}


# ==================== 本体 CRUD ====================

@router.get("")
async def list_ontologies():
    """本体列表"""
    ontologies = await ontology_service.list_ontologies()
    return success_response(ontologies)


@router.post("")
async def create_ontology(data: OntologyCreate):
    """创建本体"""
    ontology = await ontology_service.create_ontology(
        name=data.name,
        description=data.description,
        base_iri=data.base_iri,
    )
    return success_response(ontology)


@router.get("/{ontology_id}")
async def get_ontology(ontology_id: str):
    """获取本体"""
    ontology = await ontology_service.get_ontology(ontology_id)
    if not ontology:
        return {"success": False, "error": "Ontology not found"}
    return success_response(ontology)


@router.delete("/{ontology_id}")
async def delete_ontology(ontology_id: str):
    """删除本体"""
    result = await ontology_service.delete_ontology(ontology_id)
    return success_response(result)


@router.get("/{ontology_id}/detail")
async def get_ontology_detail(ontology_id: str):
    """获取本体完整详情"""
    detail = await ontology_service.get_ontology_detail(ontology_id)
    if not detail:
        return {"success": False, "error": "Ontology not found"}
    return success_response(detail)


# ==================== 版本管理 ====================

@router.get("/{ontology_id}/versions")
async def list_versions(ontology_id: str):
    """获取版本列表"""
    versions = await ontology_service.list_versions(ontology_id)
    return success_response(versions)


@router.post("/{ontology_id}/versions")
async def create_version(ontology_id: str, data: dict):
    """创建版本快照"""
    version = data.get("version")
    description = data.get("description")
    change_log = data.get("change_log")
    if not version:
        return {"success": False, "error": "version is required"}
    result = await ontology_service.create_version(
        ontology_id=ontology_id,
        version=version,
        description=description,
        change_log=change_log,
    )
    return success_response(result)


@router.get("/{ontology_id}/versions/{version}")
async def get_version(ontology_id: str, version: str):
    """获取特定版本的详细内容"""
    try:
        result = await ontology_service.get_version(ontology_id, version)
        return success_response(result)
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/{ontology_id}/rollback")
async def rollback_version(ontology_id: str, data: dict):
    """回滚到指定版本"""
    target_version = data.get("target_version") or data.get("version")
    if not target_version:
        return {"success": False, "error": "target_version is required"}
    ok = await ontology_service.rollback_version(ontology_id, target_version)
    return success_response({"success": ok})


@router.get("/{ontology_id}/versions/compare")
async def compare_versions(ontology_id: str, from_ver: str, to_ver: str):
    """对比两个版本"""
    result = await ontology_service.compare_versions(ontology_id, from_ver, to_ver)
    return success_response(result)


@router.post("/{ontology_id}/publish")
async def publish_ontology(ontology_id: str):
    """发布本体（锁定 TBox）"""
    ok = await ontology_service.publish_ontology(ontology_id)
    return success_response({"success": ok})


@router.post("/{ontology_id}/unpublish")
async def unpublish_ontology(ontology_id: str):
    """取消发布（改为草稿状态）"""
    ok = await ontology_service.unpublish_ontology(ontology_id)
    return success_response({"success": ok})


@router.delete("/{ontology_id}/versions/{version}")
async def delete_version(ontology_id: str, version: str):
    """删除指定版本快照"""
    ok = await ontology_service.delete_version(ontology_id, version)
    return success_response({"success": ok})
