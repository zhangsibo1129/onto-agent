from typing import Any
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from src.schemas.ontology import (
    OntologyCreate,
    OntologyClassCreate,
    DataPropertyCreate,
    ObjectPropertyCreate,
    AnnotationPropertyCreate,
    IndividualCreate,
    AxiomCreate,
    DataRangeBase,
)
from src.services import ontology as ontology_service

router = APIRouter(prefix="/ontologies", tags=["ontologies"])


def success_response(data: Any):
    return {"success": True, "data": data}


# ==================== 本体管理 ====================

@router.get("")
async def list_ontologies(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str = Query(None),
    search: str = Query(None),
):
    """本体列表"""
    ontologies = await ontology_service.list_ontologies()
    return success_response([o.model_dump() for o in ontologies])


@router.post("")
async def create_ontology(data: OntologyCreate):
    """创建本体（使用 Named Graph 架构）"""
    new_ontology = await ontology_service.create_ontology(
        name=data.name,
        description=data.description,
        base_iri=data.base_iri,
    )
    return success_response(new_ontology.model_dump())


@router.get("/{ontology_id}")
async def get_ontology(ontology_id: str):
    """获取本体信息"""
    ontology = await ontology_service.get_ontology(ontology_id)
    if not ontology:
        raise HTTPException(status_code=404, detail="Ontology not found")
    return success_response(ontology.model_dump())


@router.delete("/{ontology_id}")
async def delete_ontology(ontology_id: str):
    """删除本体（同时删除 Named Graph）"""
    deleted = await ontology_service.delete_ontology(ontology_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Ontology not found")
    return success_response({"deleted": True})


@router.get("/{ontology_id}/detail")
async def get_ontology_detail(ontology_id: str):
    """获取本体完整详情"""
    detail = await ontology_service.get_ontology_detail(ontology_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Ontology not found")
    return success_response(detail.model_dump())


# ==================== 版本管理 ====================

@router.get("/{ontology_id}/versions")
async def list_versions(ontology_id: str):
    """列出本体所有版本"""
    versions = await ontology_service.list_versions(ontology_id)
    return success_response([v.model_dump() for v in versions])


@router.post("/{ontology_id}/versions")
async def create_version(ontology_id: str, change_log: list[dict] = None):
    """发布新版本（创建快照）"""
    version = await ontology_service.publish_version(ontology_id, change_log)
    return success_response(version.model_dump())


@router.get("/{ontology_id}/versions/{version}")
async def get_version(ontology_id: str, version: str):
    """获取指定版本详情"""
    version = await ontology_service.get_version(ontology_id, version)
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    return success_response(version.model_dump())


@router.post("/{ontology_id}/rollback")
async def rollback_version(ontology_id: str, target_version: str):
    """回滚到指定版本"""
    success = await ontology_service.rollback_to_version(ontology_id, target_version)
    if not success:
        raise HTTPException(status_code=400, detail="Rollback failed")
    return success_response({"rolled_back": True})


@router.get("/{ontology_id}/versions/compare")
async def compare_versions(ontology_id: str, from_ver: str, to_ver: str):
    """比较两个版本差异"""
    diff = await ontology_service.compare_versions(ontology_id, from_ver, to_ver)
    return success_response(diff)


@router.post("/{ontology_id}/publish")
async def publish_ontology(ontology_id: str):
    """发布本体（创建版本快照）"""
    version = await ontology_service.publish_version(ontology_id, None)
    return success_response(version.model_dump())


# ==================== 类管理 ====================

@router.get("/{ontology_id}/classes")
async def get_classes(ontology_id: str):
    classes = await ontology_service.get_ontology_classes(ontology_id)
    return success_response([c.model_dump() for c in classes])


@router.post("/{ontology_id}/classes")
async def create_class(ontology_id: str, data: OntologyClassCreate):
    """创建类（使用 Saga 事务）"""
    new_class, saga_id = await ontology_service.create_ontology_class_saga(
        ontology_id=ontology_id,
        name=data.name,
        display_name=data.display_name,
        description=data.description,
        labels=data.labels,
        comments=data.comments,
        equivalent_to=data.equivalent_to,
        disjoint_with=data.disjoint_with,
        super_classes=data.super_classes,
    )
    return success_response({
        **new_class.model_dump(),
        "saga_id": saga_id  # 返回 Saga ID 供调试
    })


# ==================== 数据属性管理 ====================

@router.get("/{ontology_id}/data-properties")
async def get_data_properties(ontology_id: str):
    props = await ontology_service.get_data_properties(ontology_id)
    return success_response([p.model_dump() for p in props])


@router.post("/{ontology_id}/data-properties")
async def create_data_property(ontology_id: str, data: DataPropertyCreate):
    new_prop, saga_id = await ontology_service.create_data_property_saga(
        ontology_id=ontology_id,
        name=data.name,
        domain_ids=data.domain_ids,
        range_type=data.range_type,
        display_name=data.display_name,
        description=data.description,
        characteristics=data.characteristics,
        super_property_id=data.super_property_id,
    )
    return success_response({
        **new_prop.model_dump(),
        "saga_id": saga_id
    })


# ==================== 对象属性管理 ====================

@router.get("/{ontology_id}/object-properties")
async def get_object_properties(ontology_id: str):
    props = await ontology_service.get_object_properties(ontology_id)
    return success_response([p.model_dump() for p in props])


@router.post("/{ontology_id}/object-properties")
async def create_object_property(ontology_id: str, data: ObjectPropertyCreate):
    new_prop, saga_id = await ontology_service.create_object_property_saga(
        ontology_id=ontology_id,
        name=data.name,
        domain_ids=data.domain_ids,
        range_ids=data.range_ids,
        display_name=data.display_name,
        description=data.description,
        characteristics=data.characteristics,
        super_property_id=data.super_property_id,
        inverse_of_id=data.inverse_of_id,
        property_chain=data.property_chain,
    )
    return success_response({
        **new_prop.model_dump(),
        "saga_id": saga_id
    })


# ==================== 注解属性管理 ====================

@router.get("/{ontology_id}/annotation-properties")
async def get_annotation_properties(ontology_id: str):
    props = await ontology_service.get_annotation_properties(ontology_id)
    return success_response([p.model_dump() for p in props])


@router.post("/{ontology_id}/annotation-properties")
async def create_annotation_property(ontology_id: str, data: AnnotationPropertyCreate):
    new_prop = await ontology_service.create_annotation_property(
        ontology_id=ontology_id,
        name=data.name,
        display_name=data.display_name,
        description=data.description,
        domain_ids=data.domain_ids,
        range_ids=data.range_ids,
        sub_property_of_id=data.sub_property_of_id,
    )
    return success_response(new_prop.model_dump())


# ==================== 个体管理 ====================

@router.get("/{ontology_id}/individuals")
async def get_individuals(
    ontology_id: str,
    class_id: str = None,
    search: str = None,
):
    individuals = await ontology_service.get_individuals(
        ontology_id, 
        class_id=class_id,
        search=search
    )
    return success_response(individuals)


@router.post("/{ontology_id}/individuals")
async def create_individual(ontology_id: str, data: IndividualCreate):
    new_ind = await ontology_service.create_individual(
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
    return success_response(new_ind.model_dump())


# ==================== 公理管理 ====================

@router.get("/{ontology_id}/axioms")
async def get_axioms(ontology_id: str):
    axioms = await ontology_service.get_axioms(ontology_id)
    return success_response([a.model_dump() for a in axioms])


@router.post("/{ontology_id}/axioms")
async def create_axiom(ontology_id: str, data: AxiomCreate):
    new_axiom = await ontology_service.create_axiom(
        ontology_id=ontology_id,
        axiom_type=data.type,
        subject=data.subject,
        assertions=data.assertions,
        annotations=data.annotations,
    )
    return success_response(new_axiom.model_dump())


# ==================== 数据范围 ====================

@router.get("/{ontology_id}/data-ranges")
async def get_data_ranges(ontology_id: str):
    data_ranges = await ontology_service.get_data_ranges(ontology_id)
    return success_response([d.model_dump() for d in data_ranges])


# ==================== Saga 调试接口 ====================

@router.get("/debug/saga/{saga_id}")
async def get_saga_status(saga_id: str):
    """查询 Saga 状态（调试用）"""
    from src.services.saga_manager import SagaManager
    status = await SagaManager.get_saga_status(saga_id)
    if not status:
        raise HTTPException(status_code=404, detail="Saga not found")
    return success_response(status)


@router.get("/debug/saga/pending")
async def list_pending_sagas():
    """列出所有 pending 的 Saga 操作"""
    from src.services.saga_manager import SagaManager
    sags = await SagaManager.get_pending_sagas()
    return success_response(sags)
