"""
Ontology Service — Option B 架构

读：列表/计数 → PostgreSQL（快）
    详情/图谱 → Jena（完整数据）

写：Jena（唯一可信源）→ PostgreSQL（轻量索引，同步计数）

所有实体完整数据以 Jena Fuseki 为唯一可信来源。
PostgreSQL 仅存本体元数据 + 实体索引（ID、名称、Jena URI）+ 计数。
"""

from typing import Optional
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
from src.services.jena import (
    get_jena_client,
    JenaClient,
)
from src.services.ontology_metadata import get_metadata_store, OntologyMetadata
from src.database import SystemSession
from src.repositories import OntologyRepository, EntityIndexRepository
from src.repositories.ontology import (
    get_ontology_by_id as _get_ontology_by_id,
    list_ontologies as _list_ontologies_repo,
    delete_ontology_by_id as _delete_ontology_by_id,
)
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

def _to_ontology_response(o: Ontology) -> OntologyResponse:
    """将 Ontology 模型转换为响应 DTO"""
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


async def list_ontologies() -> list[OntologyResponse]:
    """本体列表：PostgreSQL（毫秒级）"""
    ontologies, _ = await _list_ontologies_repo(limit=100, offset=0)
    return [_to_ontology_response(o) for o in ontologies]


async def get_ontology(ontology_id: str) -> Optional[OntologyResponse]:
    """获取本体摘要：PostgreSQL"""
    o = await _get_ontology_by_id(ontology_id)
    if not o:
        return None
    return _to_ontology_response(o)


async def delete_ontology(ontology_id: str) -> bool:
    """删除本体：PostgreSQL + Jena 命名图（不删除数据集）"""
    o = await _get_ontology_by_id(ontology_id)
    if not o:
        return False

    base_iri = o.base_iri

    # 删除本体
    await _delete_ontology_by_id(ontology_id)
    get_metadata_store().delete(ontology_id)

    # 同步删除 Jena 所有本体命名图（meta + tbox + abox + 所有 abox@vN）
    try:
        jena = _get_jena()
        if jena:
            jena.graph_delete_all_ontology_graphs(base_iri)
    except Exception as e:
        logger.error(f"delete ontology graphs failed: base_iri={base_iri}, error={e}")

    return True


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
            jena = get_jena_client(dataset)
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
    base_iri, dataset, tbox_graph_uri, _ = await _get_ontology_iri(ontology_id)
    if not base_iri or not dataset:
        return []
    try:
        jena = get_jena_client(dataset)
        return jena.list_classes(base_iri)
    except Exception:
        return []


async def get_data_properties(ontology_id: str) -> list[DataPropertyResponse]:
    """DataProperty 列表：从 Jena 读取"""
    base_iri, dataset, _, _ = await _get_ontology_iri(ontology_id)
    if not base_iri or not dataset:
        return []
    try:
        jena = get_jena_client(dataset)
        return jena.list_datatype_properties(base_iri)
    except Exception:
        return []


async def get_object_properties(ontology_id: str) -> list[ObjectPropertyResponse]:
    """ObjectProperty 列表：从 Jena 读取"""
    base_iri, dataset, _, _ = await _get_ontology_iri(ontology_id)
    if not base_iri or not dataset:
        return []
    try:
        jena = get_jena_client(dataset)
        return jena.list_object_properties(base_iri)
    except Exception:
        return []


async def get_annotation_properties(ontology_id: str) -> list:
    """AnnotationProperty 列表：从 Jena 读取"""
    base_iri, dataset, _, _ = await _get_ontology_iri(ontology_id)
    if not base_iri or not dataset:
        return []
    try:
        jena = get_jena_client(dataset)
        return jena.list_annotation_properties(base_iri)
    except Exception:
        return []


async def get_individuals(
    ontology_id: str, class_id: str = None, search: str = None
) -> list:
    """Individual 列表：从 Jena 读取"""
    base_iri, dataset, _, _ = await _get_ontology_iri(ontology_id)
    if not base_iri or not dataset:
        return []
    try:
        jena = get_jena_client(dataset)
        return jena.list_individuals(base_iri, class_local_name=class_id, search=search)
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
    # 新命名图架构：统一 Dataset，所有本体共享 /onto-agent
    dataset = "/onto-agent"
    # 注意：tbox_graph_uri / abox_graph_uri 不再从 baseIri 计算，保持向后兼容字段
    tbox_graph_uri = f"{base_iri}/tbox"
    abox_graph_uri = f"{base_iri}/abox"
    now = datetime.utcnow().isoformat() + "Z"

    # 1. Jena：初始化本体三个命名图（meta + tbox + abox）
    try:
        jena = get_jena_client()
        jena.create_dataset(dataset)
        jena.create_ontology(
            name=name,
            base_iri=base_iri,
            description=description,
        )
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
            # 新架构下 tbox/abox URI 由 base_iri 推导，不再存储计算后的 URI
            # 但保留字段以兼容旧代码
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
    base_iri, dataset, _, _ = await _get_ontology_iri(ontology_id)
    if not base_iri:
        raise ValueError(f"Ontology {ontology_id} not found")

    class_uri = f"{base_iri}{name}"
    super_iris = [f"{base_iri}{sc}" for sc in (super_classes or [])]

    # 1. Jena 写入 TBox 图
    jena_ok = False
    try:
        jena = get_jena_client(dataset)
        jena_ok = jena.create_class(
            base_iri,
            name,  # class_local_name
            display_name=display_name,
            description=description,
            super_class_iris=super_iris if super_iris else None,
        )
    except Exception as e:
        logger.error(f"create class failed: {e}")

    # 2. PostgreSQL 索引
    tbox_graph_uri = f"{base_iri}/tbox"
    await _index_entity(ontology_id, "CLASS", name, display_name, class_uri, graph_uri=tbox_graph_uri)
    await _increment_count(ontology_id, "class_count")

    if jena_ok:
        # 从 Jena 重新读取完整数据
        try:
            jena = get_jena_client(dataset)
            classes = jena.list_classes(base_iri)
            for c in classes:
                if c.id == name:
                    return c
        except Exception:
            pass

    # Jena 不可用时构造响应
    return OntologyClassResponse(
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
    base_iri, dataset, _, _ = await _get_ontology_iri(ontology_id)
    if not base_iri:
        return None

    class_uri = f"{base_iri}{class_id}"

    # Jena 更新
    try:
        jena = get_jena_client(dataset)
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
        jena = get_jena_client(dataset)
        classes = jena.list_classes(base_iri)
        for c in classes:
            if c.id == (name or class_id):
                return c
    except Exception:
        pass
    return None


async def delete_ontology_class(ontology_id: str, class_id: str) -> bool:
    """删除类：Jena + PostgreSQL 索引"""
    base_iri, dataset, _, _ = await _get_ontology_iri(ontology_id)
    if not base_iri:
        return False

    class_uri = f"{base_iri}{class_id}"

    # 1. Jena 删除
    try:
        jena = get_jena_client(dataset)
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
    base_iri, dataset, _, _ = await _get_ontology_iri(ontology_id)
    if not base_iri:
        raise ValueError(f"Ontology {ontology_id} not found")

    domain_local_name = domain_ids[0] if domain_ids else None

    jena_ok = False
    try:
        jena = get_jena_client(dataset)
        jena_ok = jena.create_datatype_property(
            base_iri,
            name,  # prop_local_name
            domain_local_name,  # domain_local_name
            range_type=range_type,
            display_name=display_name,
            characteristics=characteristics,
        )
    except Exception as e:
        logger.error(f"create dataprop failed: {e}")

    prop_uri = f"{base_iri}{name}"
    tbox_graph_uri = f"{base_iri}/tbox"
    await _index_entity(ontology_id, "DP", name, display_name, prop_uri, graph_uri=tbox_graph_uri)
    await _increment_count(ontology_id, "dp_count")

    if jena_ok:
        try:
            jena = get_jena_client(dataset)
            props = jena.list_datatype_properties(base_iri)
            for p in props:
                if p.id == name:
                    return p
        except Exception:
            pass

    return DataPropertyResponse(
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
    base_iri, dataset, tbox_graph_uri, _ = await _get_ontology_iri(ontology_id)
    if not base_iri:
        return None

    prop_uri = f"{base_iri}{prop_id}"
    domain_local_name = domain_ids[0] if domain_ids else None

    try:
        jena = get_jena_client(dataset)
        # 重新创建（简化处理，实际应做 SPARQL DELETE/INSERT）
        jena.delete_datatype_property(prop_uri)
        jena.create_datatype_property(
            base_iri,
            prop_id,  # prop_local_name
            domain_local_name,
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
        jena = get_jena_client(dataset)
        props = jena.list_datatype_properties(base_iri)
        for p in props:
            if p.id == prop_id:
                return p
    except Exception:
        pass
    return None


async def delete_data_property(ontology_id: str, prop_id: str) -> bool:
    """删除 DataProperty：Jena + PostgreSQL"""
    base_iri, dataset, _, _ = await _get_ontology_iri(ontology_id)
    if not base_iri:
        return False

    try:
        jena = get_jena_client(dataset)
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
    base_iri, dataset, _, _ = await _get_ontology_iri(ontology_id)
    if not base_iri:
        raise ValueError(f"Ontology {ontology_id} not found")

    domain_local_name = domain_ids[0] if domain_ids else None
    range_local_name = range_ids[0] if range_ids else None

    jena_ok = False
    try:
        jena = get_jena_client(dataset)
        jena_ok = jena.create_object_property(
            base_iri,
            name,  # prop_local_name
            domain_local_name,
            range_local_name,
            display_name=display_name,
            characteristics=characteristics,
            inverse_of_local_name=inverse_of_id,
        )
    except Exception as e:
        logger.error(f"create objprop failed: {e}")

    prop_uri = f"{base_iri}{name}"
    tbox_graph_uri = f"{base_iri}/tbox"
    await _index_entity(ontology_id, "OP", name, display_name, prop_uri, graph_uri=tbox_graph_uri)
    await _increment_count(ontology_id, "op_count")

    if jena_ok:
        try:
            jena = get_jena_client(dataset)
            props = jena.list_object_properties(base_iri)
            for p in props:
                if p.id == name:
                    return p
        except Exception:
            pass

    return ObjectPropertyResponse(
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
    base_iri, dataset, tbox_graph_uri, _ = await _get_ontology_iri(ontology_id)
    if not base_iri:
        return None

    prop_uri = f"{base_iri}{prop_id}"
    domain_local_name = domain_ids[0] if domain_ids else None
    range_local_name = range_ids[0] if range_ids else None

    try:
        jena = get_jena_client(dataset)
        jena.delete_object_property(prop_uri)
        jena.create_object_property(
            base_iri,
            prop_id,  # prop_local_name
            domain_local_name,
            range_local_name,
            display_name=display_name,
            characteristics=characteristics,
            inverse_of_local_name=inverse_of_id,
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
        jena = get_jena_client(dataset)
        props = jena.list_object_properties(base_iri)
        for p in props:
            if p.id == prop_id:
                return p
    except Exception:
        pass
    return None


async def delete_object_property(ontology_id: str, prop_id: str) -> bool:
    """删除 ObjectProperty：Jena + PostgreSQL"""
    base_iri, dataset, _, _ = await _get_ontology_iri(ontology_id)
    if not base_iri:
        return False

    try:
        jena = get_jena_client(dataset)
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
    base_iri, _, _, _ = await _get_ontology_iri(ontology_id)
    if not base_iri:
        raise ValueError(f"Ontology {ontology_id} not found")

    prop_uri = f"{base_iri}{name}"
    tbox_graph_uri = f"{base_iri}/tbox"
    await _index_entity(ontology_id, "AP", name, display_name, prop_uri, graph_uri=tbox_graph_uri)
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
    """创建 Individual：Jena ABox → PostgreSQL 索引"""
    base_iri, dataset, _, _ = await _get_ontology_iri(ontology_id)
    if not base_iri:
        raise ValueError(f"Ontology {ontology_id} not found")

    # 转换类型列表为局部名称
    class_local_names = types or []

    # 转换属性断言中的 URI 为局部名称
    dp_assertions = None
    if data_property_assertions:
        dp_assertions = [
            {"propertyLocalName": p.get("propertyUri", "").split("#")[-1].split("/")[-1],
             "value": p.get("value", "")}
            for p in data_property_assertions
        ]
    op_assertions = None
    if object_property_assertions:
        op_assertions = [
            {"propertyLocalName": p.get("propertyUri", "").split("#")[-1].split("/")[-1],
             "targetLocalName": p.get("targetUri", "").split("#")[-1].split("/")[-1]}
            for p in object_property_assertions
        ]

    # 1. Jena 写入 ABox 图
    try:
        jena = get_jena_client(dataset)
        jena.create_individual(
            base_iri,
            name,  # individual_local_name
            class_local_names,
            display_name=display_name,
            data_property_assertions=dp_assertions,
            object_property_assertions=op_assertions,
        )
    except Exception as e:
        logger.error(f"create individual failed: {e}")

    # 2. PostgreSQL 索引
    ind_uri = f"{base_iri}{name}"
    abox_graph_uri = f"{base_iri}/abox"
    await _index_entity(ontology_id, "INDIVIDUAL", name, display_name, ind_uri, graph_uri=abox_graph_uri)
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
    base_iri, _, _, _ = await _get_ontology_iri(ontology_id)
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

async def _get_ontology_iri(ontology_id: str) -> tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
    """从 PostgreSQL 获取本体的 base_iri, dataset, tbox_graph_uri, abox_graph_uri"""
    async with SystemSession() as session:
        result = await session.execute(
            select(Ontology.base_iri, Ontology.dataset, Ontology.tbox_graph_uri, Ontology.abox_graph_uri).where(Ontology.id == ontology_id)
        )
        row = result.one_or_none()
        if not row:
            return None, None, None, None
        return row[0], row[1], row[2], row[3]


async def _index_entity(
    ontology_id: str,
    entity_type: str,
    name: str,
    display_name: str = None,
    jena_uri: str = None,
    graph_uri: str = None,
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
            graph_uri=graph_uri,
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
