"""
类和属性管理路由

处理类、数据属性、对象属性、注解属性的 CRUD
"""

from typing import Any
from fastapi import APIRouter

from src.services import ontology as ontology_service
from src.schemas.ontology import (
    OntologyClassCreate,
    DataPropertyCreate,
    ObjectPropertyCreate,
    AnnotationPropertyCreate,
)

router = APIRouter(prefix="/api/ontologies", tags=["properties"])


def success_response(data: Any):
    return {"success": True, "data": data}


# ==================== 类管理 ====================

@router.get("/{ontology_id}/classes")
async def get_classes(ontology_id: str):
    """获取类列表"""
    classes = await ontology_service.get_ontology_classes(ontology_id)
    return success_response(classes)


@router.post("/{ontology_id}/classes")
async def create_class(ontology_id: str, data: OntologyClassCreate):
    """创建类"""
    result = await ontology_service.create_ontology_class(
        ontology_id=ontology_id,
        name=data.name,
        display_name=data.display_name,
        description=data.description,
        super_classes=data.super_classes,
    )
    return success_response(result)


@router.put("/{ontology_id}/classes/{class_id}")
async def update_class(ontology_id: str, class_id: str, data: OntologyClassCreate):
    """更新类"""
    result = await ontology_service.update_ontology_class(
        ontology_id=ontology_id,
        class_id=class_id,
        display_name=data.display_name,
        description=data.description,
        super_classes=data.super_classes,
    )
    return success_response(result)


@router.delete("/{ontology_id}/classes/{class_id}")
async def delete_class(ontology_id: str, class_id: str):
    """删除类"""
    result = await ontology_service.delete_ontology_class(ontology_id, class_id)
    return success_response(result)


# ==================== 数据属性管理 ====================

@router.get("/{ontology_id}/data-properties")
async def get_data_properties(ontology_id: str):
    """获取数据属性列表"""
    props = await ontology_service.get_data_properties(ontology_id)
    return success_response(props)


@router.post("/{ontology_id}/data-properties")
async def create_data_property(ontology_id: str, data: DataPropertyCreate):
    """创建数据属性"""
    result = await ontology_service.create_data_property(
        ontology_id=ontology_id,
        name=data.name,
        display_name=data.display_name,
        domain_ids=data.domain_ids,
        range_type=str(data.range_type) if data.range_type else "string",
        characteristics=data.characteristics or [],
    )
    return success_response(result)


@router.put("/{ontology_id}/data-properties/{prop_id}")
async def update_data_property(ontology_id: str, prop_id: str, data: DataPropertyCreate):
    """更新数据属性"""
    result = await ontology_service.update_data_property(
        ontology_id=ontology_id,
        prop_id=prop_id,
        display_name=data.display_name,
        description=data.description,
        range_type=data.range_type,
    )
    return success_response(result)


@router.delete("/{ontology_id}/data-properties/{prop_id}")
async def delete_data_property(ontology_id: str, prop_id: str):
    """删除数据属性"""
    result = await ontology_service.delete_data_property(ontology_id, prop_id)
    return success_response(result)


# ==================== 对象属性管理 ====================

@router.get("/{ontology_id}/object-properties")
async def get_object_properties(ontology_id: str):
    """获取对象属性列表"""
    props = await ontology_service.get_object_properties(ontology_id)
    return success_response(props)


@router.post("/{ontology_id}/object-properties")
async def create_object_property(ontology_id: str, data: ObjectPropertyCreate):
    """创建对象属性"""
    result = await ontology_service.create_object_property(
        ontology_id=ontology_id,
        name=data.name,
        display_name=data.display_name,
        domain_ids=data.domain_ids,
        range_ids=data.range_ids,
        characteristics=data.characteristics or [],
        inverse_of_id=data.inverse_of_id,
    )
    return success_response(result)


@router.put("/{ontology_id}/object-properties/{prop_id}")
async def update_object_property(ontology_id: str, prop_id: str, data: ObjectPropertyCreate):
    """更新对象属性"""
    result = await ontology_service.update_object_property(
        ontology_id=ontology_id,
        prop_id=prop_id,
        display_name=data.display_name,
        description=data.description,
    )
    return success_response(result)


@router.delete("/{ontology_id}/object-properties/{prop_id}")
async def delete_object_property(ontology_id: str, prop_id: str):
    """删除对象属性"""
    result = await ontology_service.delete_object_property(ontology_id, prop_id)
    return success_response(result)


# ==================== 注解属性管理 ====================

@router.get("/{ontology_id}/annotation-properties")
async def get_annotation_properties(ontology_id: str):
    """获取注解属性列表"""
    props = await ontology_service.get_annotation_properties(ontology_id)
    return success_response(props)


@router.post("/{ontology_id}/annotation-properties")
async def create_annotation_property(ontology_id: str, data: AnnotationPropertyCreate):
    """创建注解属性"""
    result = await ontology_service.create_annotation_property(
        ontology_id=ontology_id,
        name=data.name,
        display_name=data.display_name,
    )
    return success_response(result)
