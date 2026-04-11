"""
Ontology Service — Option B 架构

读：列表/计数 → PostgreSQL（快）
    详情/图谱 → Jena（完整数据）

写：Jena（唯一可信源）→ PostgreSQL（轻量索引，同步计数）

所有实体完整数据以 Jena Fuseki 为唯一可信来源。
PostgreSQL 仅存本体元数据 + 实体索引（ID、名称、Jena URI）+ 计数。
"""

from typing import Optional
from src.database import SystemSession
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.ontology import Ontology, EntityIndex
from src.schemas.ontology import (
    OntologyResponse,
    OntologyDetailResponse,
    OntologyClassResponse,
    DataPropertyResponse,
    ObjectPropertyResponse,
    AnnotationPropertyResponse,
    IndividualResponse,
    AxiomResponse,
    DataRangeResponse,
)
from src.services.jena_client import (
    get_jena_client,
    get_jena_client_for_dataset,
    JenaClient,
)
from src.services.ontology_metadata import get_metadata_store, OntologyMetadata
from src.logging_config import get_logger
from src.exceptions import OntologyNotFoundError, EntityNotFoundError

import httpx

logger = get_logger("ontology")


# ============================================================================
# Jena 客户端获取（延迟，运行时）
# ============================================================================

def _get_jena() -> Optional[JenaClient]:
    try:
        return get_jena_client()
    except Exception:
        return None


# ============================================================================
# 读操作：列表/元数据 → PostgreSQL
# ============================================================================

async def list_ontologies() -> list[OntologyResponse]:
    """本体列表：PostgreSQL（毫秒级）"""
    async with SystemSession() as session:
        result = await session.execute(
            select(Ontology).order_by(Ontology.updated_at.desc())
        )
        ontologies = result.scalars().all()

        return [
            OntologyResponse(
                id=o.id,
                name=o.name,
                description=o.description or "",
                version=o.version or "v1.0",
                status=o.status or "draft",
                datasource=None,
                base_iri=o.base_iri,
                imports=[],
                prefix_mappings={
                    "owl": "http://www.w3.org/2002/07/owl#",
                    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                    "xsd": "http://www.w3.org/2001/XMLSchema#",
                },
                object_count=o.class_count or 0,
                data_property_count=o.dp_count or 0,
                object_property_count=o.op_count or 0,
                individual_count=o.individual_count or 0,
                axiom_count=o.axiom_count or 0,
                created_at=o.created_at.isoformat() if o.created_at else "",
                updated_at=o.updated_at.isoformat() if o.updated_at else "",
            )
            for o in ontologies
        ]


async def get_ontology(ontology_id: str) -> Optional[OntologyResponse]:
    """获取本体摘要：PostgreSQL"""
    async with SystemSession() as session:
        result = await session.execute(
            select(Ontology).where(Ontology.id == ontology_id)
        )
        o = result.scalar_one_or_none()
        if not o:
            return None

        return OntologyResponse(
            id=o.id,
            name=o.name,
            description=o.description or "",
            version=o.version or "v1.0",
            status=o.status or "draft",
            datasource=None,
            base_iri=o.base_iri,
            imports=[],
            prefix_mappings={
                "owl": "http://www.w3.org/2002/07/owl#",
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                "xsd": "http://www.w3.org/2001/XMLSchema#",
            },
            object_count=o.class_count or 0,
            data_property_count=o.dp_count or 0,
            object_property_count=o.op_count or 0,
            individual_count=o.individual_count or 0,
            axiom_count=o.axiom_count or 0,
            created_at=o.created_at.isoformat() if o.created_at else "",
            updated_at=o.updated_at.isoformat() if o.updated_at else "",
        )


async def delete_ontology(ontology_id: str) -> bool:
    """删除本体：PostgreSQL + Jena 命名图（不删除数据集）"""
    async with SystemSession() as session:
        result = await session.execute(
            select(Ontology).where(Ontology.id == ontology_id)
        )
        o = result.scalar_one_or_none()
        if not o:
            return False
        
        # 保存命名图 URI（删除本体后无法从 DB 获取）
        tbox_graph_uri = o.tbox_graph_uri
        abox_graph_uri = o.abox_graph_uri
        
        await session.delete(o)
        await session.commit()

    get_metadata_store().delete(ontology_id)

    # 异步删除 Jena 命名图（不删除整个数据集）
    try:
        import asyncio
        jena = _get_jena()
        if jena:
            asyncio.create_task(_jena_delete_named_graphs(tbox_graph_uri, abox_graph_uri))
    except Exception:
        pass

    return True


async def _jena_delete_named_graphs(tbox_graph_uri: str, abox_graph_uri: str = None):
    """删除 Jena 中的命名图（不删除数据集）"""
    try:
        jena = _get_jena()
        if jena:
            # 删除 TBox 命名图
            jena.delete_named_graph(tbox_graph_uri)
            # 删除 ABox 命名图（如果存在）
            if abox_graph_uri:
                jena.delete_named_graph(abox_graph_uri)
    except Exception as e:
        logger.error(f"delete named graphs failed: tbox={tbox_graph_uri}, abox={abox_graph_uri}, error={e}")


# ============================================================================
# 读操作：详情/图谱 → Jena（唯一可信源）
# ============================================================================

async def get_ontology_detail(ontology_id: str) -> Optional[OntologyDetailResponse]:
    """
    本体完整详情：直接从 Jena 读取。
    PostgreSQL 只提供 base_iri/dataset 信息。
    """
    async with SystemSession() as session:
        result = await session.execute(
            select(Ontology).where(Ontology.id == ontology_id)
        )
        ont = result.scalar_one_or_none()
        if not ont:
            return None

        base_iri = ont.base_iri
        dataset = ont.dataset

    # Jena 读取完整数据
    jena = None
    if dataset:
        try:
            jena = get_jena_client_for_dataset(dataset)
        except Exception:
            pass

    if not jena:
        # Jena 不可用时，返回空结构
        return OntologyDetailResponse(
            id=ont.id,
            name=ont.name,
            description=ont.description or "",
            version=ont.version or "v1.0",
            status=ont.status or "draft",
            datasource=None,
            base_iri=base_iri,
            imports=[],
            prefix_mappings={
                "owl": "http://www.w3.org/2002/07/owl#",
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                "xsd": "http://www.w3.org/2001/XMLSchema#",
            },
            object_count=0,
            data_property_count=0,
            object_property_count=0,
            individual_count=0,
            axiom_count=0,
            created_at=ont.created_at.isoformat() if ont.created_at else "",
            updated_at=ont.updated_at.isoformat() if ont.updated_at else "",
            classes=[],
            data_properties=[],
            object_properties=[],
            annotation_properties=[],
            individuals=[],
            axioms=[],
            data_ranges=[],
        )

    # 从 Jena 批量读取
    detail = jena.get_ontology_detail(base_iri)

    return OntologyDetailResponse(
        id=ont.id,
        name=detail.get("name", ont.name),
        description=detail.get("description", ont.description or ""),
        version=ont.version or "v1.0",
        status=ont.status or "draft",
        datasource=None,
        base_iri=base_iri,
        imports=[],
        prefix_mappings={
            "owl": "http://www.w3.org/2002/07/owl#",
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
            "xsd": "http://www.w3.org/2001/XMLSchema#",
        },
        object_count=len(detail.get("classes", [])),
        data_property_count=len(detail.get("data_properties", [])),
        object_property_count=len(detail.get("object_properties", [])),
        individual_count=len(detail.get("individuals", [])),
        axiom_count=0,
        created_at=ont.created_at.isoformat() if ont.created_at else "",
        updated_at=ont.updated_at.isoformat() if ont.updated_at else "",
        classes=detail.get("classes", []),
        data_properties=detail.get("data_properties", []),
        object_properties=detail.get("object_properties", []),
        annotation_properties=detail.get("annotation_properties", []),
        individuals=detail.get("individuals", []),
        axioms=[],
        data_ranges=[],
    )


# ============================================================================
# 读操作：各类型实体列表 → Jena
# ============================================================================

async def get_ontology_classes(ontology_id: str) -> list[OntologyClassResponse]:
    """类列表：从 Jena 读取"""
    base_iri, dataset = await _get_ontology_iri(ontology_id)
    if not base_iri or not dataset:
        return []
    try:
        jena = get_jena_client_for_dataset(dataset)
        return jena.list_classes(base_iri)
    except Exception:
        return []


async def get_data_properties(ontology_id: str) -> list[DataPropertyResponse]:
    """DataProperty 列表：从 Jena 读取"""
    base_iri, dataset = await _get_ontology_iri(ontology_id)
    if not base_iri or not dataset:
        return []
    try:
        jena = get_jena_client_for_dataset(dataset)
        return jena.list_datatype_properties(base_iri)
    except Exception:
        return []


async def get_object_properties(ontology_id: str) -> list[ObjectPropertyResponse]:
    """ObjectProperty 列表：从 Jena 读取"""
    base_iri, dataset = await _get_ontology_iri(ontology_id)
    if not base_iri or not dataset:
        return []
    try:
        jena = get_jena_client_for_dataset(dataset)
        return jena.list_object_properties(base_iri)
    except Exception:
        return []


async def get_annotation_properties(ontology_id: str) -> list:
    """AnnotationProperty 列表：从 Jena 读取"""
    base_iri, dataset = await _get_ontology_iri(ontology_id)
    if not base_iri or not dataset:
        return []
    try:
        jena = get_jena_client_for_dataset(dataset)
        return jena.list_annotation_properties(base_iri)
    except Exception:
        return []


async def get_individuals(
    ontology_id: str, class_id: str = None, search: str = None
) -> list:
    """Individual 列表：从 Jena 读取"""
    base_iri, dataset = await _get_ontology_iri(ontology_id)
    if not base_iri or not dataset:
        return []
    try:
        jena = get_jena_client_for_dataset(dataset)
        return jena.list_individuals(base_iri, class_id=class_id, search=search)
    except Exception as e:
        logger.warning(f"get_individuals failed: {e}")
        return []


async def get_axioms(ontology_id: str) -> list:
    """Axiom 列表（暂不支持）"""
    return []


async def get_data_ranges(ontology_id: str) -> list[DataRangeResponse]:
    """DataRange 列表（暂不支持）"""
    return []


# ============================================================================
# 写操作：Jena（唯一可信源）→ PostgreSQL（索引）
# ============================================================================

async def create_ontology(
    name: str,
    description: str = None,
    base_iri: str = None,
    imports: list = None,
    prefix_mappings: dict = None,
) -> OntologyResponse:
    """创建本体：写入 Jena + PostgreSQL 元数据"""
    import uuid
    from datetime import datetime

    new_id = str(uuid.uuid4())[:8]
    if not base_iri:
        base_iri = f"http://onto-agent.com/ontology/{name}#"
    # 使用统一 Dataset + Named Graph 架构
    dataset = f"/onto-agent"
    tbox_graph_uri = f"{dataset}/{new_id}/tbox"
    abox_graph_uri = f"{dataset}/{new_id}/abox"
    now = datetime.utcnow().isoformat() + "Z"

    # 1. Jena：创建 dataset + 本体头
    try:
        jena = get_jena_client()
        jena.create_dataset(dataset)
        ds_jena = get_jena_client_for_dataset(dataset)
        ds_jena.create_ontology(name=name, base_iri=base_iri, description=description)
    except Exception as e:
        logger.error(f"create ontology failed: {e}")

    # 2. PostgreSQL：写入本体元数据
    async with SystemSession() as session:
        ont = Ontology(
            id=new_id,
            name=name,
            description=description,
            base_iri=base_iri,
            dataset=dataset,
            tbox_graph_uri=tbox_graph_uri,
            abox_graph_uri=abox_graph_uri,
            version="v1.0",
            status="draft",
            class_count=0,
            dp_count=0,
            op_count=0,
            ap_count=0,
            individual_count=0,
            axiom_count=0,
        )
        session.add(ont)
        await session.commit()

    # 3. metadata store（向后兼容）
    metadata = OntologyMetadata(
        id=new_id,
        name=name,
        base_iri=base_iri,
        dataset=dataset,
        description=description or "",
        version="v1.0",
        status="draft",
        created_at=now,
        updated_at=now,
    )
    get_metadata_store().add(metadata)

    return OntologyResponse(
        id=new_id,
        name=name,
        description=description or "",
        version="v1.0",
        status="draft",
        datasource=None,
        base_iri=base_iri,
        imports=imports or [],
        prefix_mappings=prefix_mappings or {
            "owl": "http://www.w3.org/2002/07/owl#",
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
            "xsd": "http://www.w3.org/2001/XMLSchema#",
        },
        object_count=0,
        data_property_count=0,
        object_property_count=0,
        individual_count=0,
        axiom_count=0,
        created_at=now,
        updated_at=now,
    )


async def create_ontology_class(
    ontology_id: str,
    name: str,
    display_name: str = None,
    description: str = None,
    labels: dict = None,
    comments: dict = None,
    equivalent_to: list = None,
    disjoint_with: list = None,
    super_classes: list = None,
) -> OntologyClassResponse:
    """创建类：Jena → PostgreSQL 索引"""
    base_iri, dataset = await _get_ontology_iri(ontology_id)
    if not base_iri:
        raise ValueError(f"Ontology {ontology_id} not found")

    class_uri = f"{base_iri}{name}"
    super_iris = [f"{base_iri}{sc}" for sc in (super_classes or [])]

    # 1. Jena 写入
    jena_result = None
    try:
        jena = get_jena_client_for_dataset(dataset)
        jena_result = jena.create_class(
            ontology_iri=base_iri,
            name=name,
            display_name=display_name,
            description=description,
            super_classes=super_iris if super_iris else None,
        )
    except Exception as e:
        logger.error(f"create class failed: {e}")

    # 2. PostgreSQL 索引
    await _index_entity(ontology_id, "CLASS", name, display_name, class_uri)
    await _increment_count(ontology_id, "class_count")

    return jena_result or OntologyClassResponse(
        id=name,
        ontology_id=ontology_id,
        name=name,
        display_name=display_name,
        description=description,
        labels=labels or {},
        comments=comments or {},
        equivalent_to=equivalent_to or [],
        disjoint_with=disjoint_with or [],
        super_classes=super_classes or [],
    )


async def update_ontology_class(
    ontology_id: str,
    class_id: str,
    name: str = None,
    display_name: str = None,
    description: str = None,
    labels: dict = None,
    comments: dict = None,
    equivalent_to: list = None,
    disjoint_with: list = None,
    super_classes: list = None,
) -> Optional[OntologyClassResponse]:
    """更新类：Jena → PostgreSQL 索引（名称变化时）"""
    base_iri, dataset = await _get_ontology_iri(ontology_id)
    if not base_iri:
        return None

    class_uri = f"{base_iri}{class_id}"

    # Jena 更新
    try:
        jena = get_jena_client_for_dataset(dataset)
        jena.update_class(class_uri, display_name=display_name, description=description)
    except Exception as e:
        logger.error(f"update class failed: {e}")

    # PostgreSQL 索引更新（名称/显示名变化）
    if name or display_name:
        async with SystemSession() as session:
            await session.execute(
                update(EntityIndex)
                .where(
                    EntityIndex.ontology_id == ontology_id,
                    EntityIndex.entity_type == "CLASS",
                    EntityIndex.name == class_id,
                )
                .values(
                    name=name or class_id,
                    display_name=display_name,
                    jena_uri=f"{base_iri}{name}" if name else class_uri,
                )
            )
            await session.commit()

    # 重新从 Jena 读取最新数据
    try:
        jena = get_jena_client_for_dataset(dataset)
        return jena.get_class(class_uri)
    except Exception:
        return None


async def delete_ontology_class(ontology_id: str, class_id: str) -> bool:
    """删除类：Jena + PostgreSQL 索引"""
    base_iri, dataset = await _get_ontology_iri(ontology_id)
    if not base_iri:
        return False

    class_uri = f"{base_iri}{class_id}"

    # 1. Jena 删除
    try:
        jena = get_jena_client_for_dataset(dataset)
        jena.delete_class(class_uri)
    except Exception as e:
        logger.error(f"delete class failed: {e}")

    # 2. PostgreSQL 索引删除
    await _delete_entity_index(ontology_id, "CLASS", class_id)
    await _decrement_count(ontology_id, "class_count")

    return True


async def create_data_property(
    ontology_id: str,
    name: str,
    domain_ids: list,
    range_type: str = "string",
    display_name: str = None,
    description: str = None,
    characteristics: list = None,
    super_property_id: str = None,
) -> DataPropertyResponse:
    """创建 DataProperty：Jena → PostgreSQL 索引"""
    base_iri, dataset = await _get_ontology_iri(ontology_id)
    if not base_iri:
        raise ValueError(f"Ontology {ontology_id} not found")

    domain_iri = f"{base_iri}{domain_ids[0]}" if domain_ids else base_iri

    jena_result = None
    try:
        jena = get_jena_client_for_dataset(dataset)
        jena_result = jena.create_datatype_property(
            ontology_iri=base_iri,
            name=name,
            domain_iri=domain_iri,
            range_type=range_type,
            display_name=display_name,
            characteristics=characteristics,
        )
    except Exception as e:
        logger.error(f"create dataprop failed: {e}")

    prop_uri = f"{base_iri}{name}"
    await _index_entity(ontology_id, "DP", name, display_name, prop_uri)
    await _increment_count(ontology_id, "dp_count")

    return jena_result or DataPropertyResponse(
        id=name,
        ontology_id=ontology_id,
        name=name,
        display_name=display_name,
        description=description,
        labels={},
        comments={},
        domain_ids=domain_ids,
        range_type=range_type,
        characteristics=characteristics or [],
        super_property_id=super_property_id,
    )


async def update_data_property(
    ontology_id: str,
    prop_id: str,
    name: str = None,
    display_name: str = None,
    description: str = None,
    domain_ids: list = None,
    range_type: str = None,
    characteristics: list = None,
    super_property_id: str = None,
) -> Optional[DataPropertyResponse]:
    """更新 DataProperty（暂只支持 display_name/description）"""
    base_iri, dataset = await _get_ontology_iri(ontology_id)
    if not base_iri:
        return None

    try:
        jena = get_jena_client_for_dataset(dataset)
        # 重新创建（简化处理，实际应做 SPARQL DELETE/INSERT）
        jena.delete_datatype_property(f"{base_iri}{prop_id}")
        jena.create_datatype_property(
            ontology_iri=base_iri,
            name=prop_id,
            domain_iri=f"{base_iri}{domain_ids[0]}" if domain_ids else base_iri,
            range_type=range_type or "string",
            display_name=display_name,
            characteristics=characteristics,
        )
    except Exception as e:
        logger.error(f"update dataprop failed: {e}")

    # 索引更新
    if name or display_name:
        async with SystemSession() as session:
            await session.execute(
                update(EntityIndex)
                .where(
                    EntityIndex.ontology_id == ontology_id,
                    EntityIndex.entity_type == "DP",
                    EntityIndex.name == prop_id,
                )
                .values(name=name or prop_id, display_name=display_name)
            )
            await session.commit()

    try:
        jena = get_jena_client_for_dataset(dataset)
        props = jena.list_datatype_properties(base_iri)
        for p in props:
            if p.id == prop_id:
                return p
    except Exception:
        pass
    return None


async def delete_data_property(ontology_id: str, prop_id: str) -> bool:
    """删除 DataProperty：Jena + PostgreSQL"""
    base_iri, dataset = await _get_ontology_iri(ontology_id)
    if not base_iri:
        return False

    try:
        jena = get_jena_client_for_dataset(dataset)
        jena.delete_datatype_property(f"{base_iri}{prop_id}")
    except Exception as e:
        logger.error(f"delete dataprop failed: {e}")

    await _delete_entity_index(ontology_id, "DP", prop_id)
    await _decrement_count(ontology_id, "dp_count")
    return True


async def create_object_property(
    ontology_id: str,
    name: str,
    domain_ids: list,
    range_ids: list,
    display_name: str = None,
    description: str = None,
    characteristics: list = None,
    super_property_id: str = None,
    inverse_of_id: str = None,
    property_chain: list = None,
) -> ObjectPropertyResponse:
    """创建 ObjectProperty：Jena → PostgreSQL 索引"""
    base_iri, dataset = await _get_ontology_iri(ontology_id)
    if not base_iri:
        raise ValueError(f"Ontology {ontology_id} not found")

    domain_iri = f"{base_iri}{domain_ids[0]}" if domain_ids else base_iri
    range_iri = f"{base_iri}{range_ids[0]}" if range_ids else base_iri
    inverse_of = f"{base_iri}{inverse_of_id}" if inverse_of_id else None

    jena_result = None
    try:
        jena = get_jena_client_for_dataset(dataset)
        jena_result = jena.create_object_property(
            ontology_iri=base_iri,
            name=name,
            domain_iri=domain_iri,
            range_iri=range_iri,
            display_name=display_name,
            characteristics=characteristics,
            inverse_of=inverse_of,
        )
    except Exception as e:
        logger.error(f"create objprop failed: {e}")

    prop_uri = f"{base_iri}{name}"
    await _index_entity(ontology_id, "OP", name, display_name, prop_uri)
    await _increment_count(ontology_id, "op_count")

    return jena_result or ObjectPropertyResponse(
        id=name,
        ontology_id=ontology_id,
        name=name,
        display_name=display_name,
        description=description,
        labels={},
        comments={},
        domain_ids=domain_ids,
        range_ids=range_ids,
        characteristics=characteristics or [],
        super_property_id=super_property_id,
        inverse_of_id=inverse_of_id,
        property_chain=property_chain or [],
    )


async def update_object_property(
    ontology_id: str,
    prop_id: str,
    name: str = None,
    display_name: str = None,
    description: str = None,
    domain_ids: list = None,
    range_ids: list = None,
    characteristics: list = None,
    super_property_id: str = None,
    inverse_of_id: str = None,
    property_chain: list = None,
) -> Optional[ObjectPropertyResponse]:
    """更新 ObjectProperty（简化：delete + recreate）"""
    base_iri, dataset = await _get_ontology_iri(ontology_id)
    if not base_iri:
        return None

    try:
        jena = get_jena_client_for_dataset(dataset)
        jena.delete_object_property(f"{base_iri}{prop_id}")
        jena.create_object_property(
            ontology_iri=base_iri,
            name=prop_id,
            domain_iri=f"{base_iri}{domain_ids[0]}" if domain_ids else base_iri,
            range_iri=f"{base_iri}{range_ids[0]}" if range_ids else base_iri,
            display_name=display_name,
            characteristics=characteristics,
            inverse_of=f"{base_iri}{inverse_of_id}" if inverse_of_id else None,
        )
    except Exception as e:
        logger.error(f"update objprop failed: {e}")

    if name or display_name:
        async with SystemSession() as session:
            await session.execute(
                update(EntityIndex)
                .where(
                    EntityIndex.ontology_id == ontology_id,
                    EntityIndex.entity_type == "OP",
                    EntityIndex.name == prop_id,
                )
                .values(name=name or prop_id, display_name=display_name)
            )
            await session.commit()

    try:
        jena = get_jena_client_for_dataset(dataset)
        props = jena.list_object_properties(base_iri)
        for p in props:
            if p.id == prop_id:
                return p
    except Exception:
        pass
    return None


async def delete_object_property(ontology_id: str, prop_id: str) -> bool:
    """删除 ObjectProperty：Jena + PostgreSQL"""
    base_iri, dataset = await _get_ontology_iri(ontology_id)
    if not base_iri:
        return False

    try:
        jena = get_jena_client_for_dataset(dataset)
        jena.delete_object_property(f"{base_iri}{prop_id}")
    except Exception as e:
        logger.error(f"delete objprop failed: {e}")

    await _delete_entity_index(ontology_id, "OP", prop_id)
    await _decrement_count(ontology_id, "op_count")
    return True


async def create_annotation_property(
    ontology_id: str,
    name: str,
    display_name: str = None,
    description: str = None,
    domain_ids: list = None,
    range_ids: list = None,
    sub_property_of_id: str = None,
) -> AnnotationPropertyResponse:
    """创建 AnnotationProperty（暂不写 Jena，只更新 PostgreSQL 索引）"""
    base_iri, _ = await _get_ontology_iri(ontology_id)
    if not base_iri:
        raise ValueError(f"Ontology {ontology_id} not found")

    prop_uri = f"{base_iri}{name}"
    await _index_entity(ontology_id, "AP", name, display_name, prop_uri)
    await _increment_count(ontology_id, "ap_count")

    return AnnotationPropertyResponse(
        id=name,
        ontology_id=ontology_id,
        name=name,
        display_name=display_name,
        description=description,
        domain_ids=domain_ids or [],
        range_ids=range_ids or [],
        sub_property_of_id=sub_property_of_id,
    )


async def create_individual(
    ontology_id: str,
    name: str,
    display_name: str = None,
    description: str = None,
    types: list = None,
    labels: dict = None,
    comments: dict = None,
    data_property_assertions: list = None,
    object_property_assertions: list = None,
) -> IndividualResponse:
    """创建 Individual（暂只写 PostgreSQL 索引，Jena 个体写入较复杂）"""
    base_iri, _ = await _get_ontology_iri(ontology_id)
    if not base_iri:
        raise ValueError(f"Ontology {ontology_id} not found")

    ind_uri = f"{base_iri}{name}"
    await _index_entity(ontology_id, "INDIVIDUAL", name, display_name, ind_uri)
    await _increment_count(ontology_id, "individual_count")

    return IndividualResponse(
        id=name,
        ontology_id=ontology_id,
        name=name,
        display_name=display_name,
        description=description,
        types=types or [],
        labels=labels or {},
        comments=comments or {},
        data_property_assertions=data_property_assertions or [],
        object_property_assertions=object_property_assertions or [],
    )


async def create_axiom(
    ontology_id: str,
    axiom_type: str,
    subject: str = None,
    assertions: dict = None,
    annotations: list = None,
) -> AxiomResponse:
    """创建 Axiom（暂只写 PostgreSQL 索引）"""
    import uuid
    base_iri, _ = await _get_ontology_iri(ontology_id)
    if not base_iri:
        raise ValueError(f"Ontology {ontology_id} not found")

    new_id = str(uuid.uuid4())[:12]
    await _increment_count(ontology_id, "axiom_count")

    return AxiomResponse(
        id=new_id,
        ontology_id=ontology_id,
        type=axiom_type,
        subject=subject,
        assertions=assertions or {},
        annotations=annotations or [],
    )


# ============================================================================
# 内部辅助函数
# ============================================================================

async def _get_ontology_iri(ontology_id: str) -> tuple[Optional[str], Optional[str]]:
    """从 PostgreSQL 获取本体的 base_iri 和 dataset"""
    async with SystemSession() as session:
        result = await session.execute(
            select(Ontology.base_iri, Ontology.dataset).where(Ontology.id == ontology_id)
        )
        row = result.one_or_none()
        if not row:
            return None, None
        return row[0], row[1]


async def _index_entity(
    ontology_id: str,
    entity_type: str,
    name: str,
    display_name: str = None,
    jena_uri: str = None,
):
    """向 PostgreSQL entity_index 写入一条索引"""
    import uuid
    async with SystemSession() as session:
        idx = EntityIndex(
            id=str(uuid.uuid4())[:12],
            ontology_id=ontology_id,
            entity_type=entity_type,
            name=name,
            display_name=display_name,
            jena_uri=jena_uri,
        )
        session.add(idx)
        await session.commit()


async def _delete_entity_index(ontology_id: str, entity_type: str, name: str):
    """从 PostgreSQL entity_index 删除一条索引"""
    from sqlalchemy import delete as sql_delete
    async with SystemSession() as session:
        await session.execute(
            sql_delete(EntityIndex).where(
                EntityIndex.ontology_id == ontology_id,
                EntityIndex.entity_type == entity_type,
                EntityIndex.name == name,
            )
        )
        await session.commit()


async def _increment_count(ontology_id: str, count_field: str):
    """PostgreSQL ontology 表计数 +1"""
    from sqlalchemy import update
    from sqlalchemy import literal
    async with SystemSession() as session:
        col = getattr(Ontology, count_field)
        await session.execute(
            update(Ontology)
            .where(Ontology.id == ontology_id)
            .values({count_field: col + 1})
        )
        await session.commit()


async def _decrement_count(ontology_id: str, count_field: str):
    """PostgreSQL ontology 表计数 -1（最小为0）"""
    from sqlalchemy import update
    async with SystemSession() as session:
        col = getattr(Ontology, count_field)
        # SQL: GREATEST(0, col - 1)
        from sqlalchemy import case
        new_val = case((col <= 0, 0), else_=col - 1)
        await session.execute(
            update(Ontology)
            .where(Ontology.id == ontology_id)
            .values({count_field: new_val})
        )
        await session.commit()
