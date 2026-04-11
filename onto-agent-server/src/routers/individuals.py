"""
个体管理路由

处理 ABox Individual (owl:NamedIndividual) 的 CRUD
"""

from typing import Any
from fastapi import APIRouter

from src.services import ontology as ontology_service
from src.schemas.ontology import IndividualCreate, IndividualUpdate

router = APIRouter(prefix="/api/ontologies", tags=["individuals"])


def success_response(data: Any):
    return {"success": True, "data": data}


# ==================== 个体管理 ====================

@router.get("/{ontology_id}/individuals")
async def get_individuals(
    ontology_id: str,
    class_id: str = None,
    search: str = None,
):
    """
    获取个体列表
    
    - class_id: 可选，按类筛选
    - search: 可选，搜索名称/标签
    """
    individuals = await ontology_service.get_individuals(
        ontology_id,
        class_id=class_id,
        search=search,
    )
    return success_response(individuals)


@router.post("/{ontology_id}/individuals")
async def create_individual(ontology_id: str, data: IndividualCreate):
    """创建个体"""
    result = await ontology_service.create_individual(
        ontology_id=ontology_id,
        name=data.name,
        display_name=data.display_name,
        description=data.description,
        types=data.types,
        labels=data.labels,
        comments=data.comments,
        data_property_assertions=data.data_property_assertions,
        object_property_assertions=data.object_property_assertions,
    )
    return success_response(result)


@router.get("/{ontology_id}/individuals/{individual_id}")
async def get_individual(ontology_id: str, individual_id: str):
    """获取个体详情"""
    result = await ontology_service.get_individual(ontology_id, individual_id)
    if not result:
        return {"success": False, "error": "Individual not found"}
    return success_response(result)


@router.put("/{ontology_id}/individuals/{individual_id}")
async def update_individual(ontology_id: str, individual_id: str, data: IndividualUpdate):
    """更新个体"""
    result = await ontology_service.update_individual(
        ontology_id=ontology_id,
        individual_id=individual_id,
        display_name=data.display_name,
        description=data.description,
        types=data.types,
        labels=data.labels,
        comments=data.comments,
    )
    if not result:
        return {"success": False, "error": "Individual not found"}
    return success_response(result)


@router.delete("/{ontology_id}/individuals/{individual_id}")
async def delete_individual(ontology_id: str, individual_id: str):
    """删除个体"""
    result = await ontology_service.delete_individual(ontology_id, individual_id)
    return success_response({"success": result})


# ==================== 公理 ====================

@router.get("/{ontology_id}/axioms")
async def get_axioms(ontology_id: str):
    """获取公理列表"""
    axioms = await ontology_service.get_axioms(ontology_id)
    return success_response(axioms)


@router.post("/{ontology_id}/axioms")
async def create_axiom(ontology_id: str, data: dict):
    """创建公理"""
    result = await ontology_service.create_axiom(ontology_id, data)
    return success_response(result)


# ==================== DataRange ====================

@router.get("/{ontology_id}/data-ranges")
async def get_data_ranges(ontology_id: str):
    """获取数据类型列表"""
    data_ranges = await ontology_service.get_data_ranges(ontology_id)
    return success_response(data_ranges)
