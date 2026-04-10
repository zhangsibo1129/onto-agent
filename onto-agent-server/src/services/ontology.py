from datetime import datetime
from typing import Optional
from src.schemas.ontology import (
    OntologyClassResponse,
    DataPropertyResponse,
    ObjectPropertyResponse,
    AnnotationPropertyResponse,
    IndividualResponse,
    AxiomResponse,
    OntologyResponse,
    OntologyDetailResponse,
    DataRangeResponse,
)
from src.models.ontology import (
    Ontology,
    OntologyClass,
    DataProperty,
    ObjectProperty,
    AnnotationProperty,
    Individual,
    Axiom,
    DataRange,
)
from src.services.ontology_metadata import OntologyMetadata, get_metadata_store

# Try to import Jena client, fall back gracefully
try:
    from src.services.jena_client import (
        JenaClient,
        get_jena_client,
        get_jena_client_for_dataset,
        JenaConnectionError,
    )

    JENA_AVAILABLE = True
except ImportError:
    JENA_AVAILABLE = False
    JenaClient = None
    get_jena_client = None
    get_jena_client_for_dataset = None
    JenaConnectionError = Exception

# Global Jena client instance
_jena_client = None


def _get_jena() -> Optional["JenaClient"]:
    """Get Jena client if available"""
    global _jena_client
    if not JENA_AVAILABLE:
        return None
    try:
        if _jena_client is None:
            _jena_client = get_jena_client()
        return _jena_client
    except JenaConnectionError:
        return None





# ============================================================
# 本体 CRUD（单一可信源：PostgreSQL）
# ============================================================


async def list_ontologies() -> list[OntologyResponse]:
    from src.database import async_session_maker
    from sqlalchemy import select, func

    async with async_session_maker() as session:
        result = await session.execute(
            select(Ontology).order_by(Ontology.updated_at.desc())
        )
        ontologies = result.scalars().all()

        responses = []
        for ont in ontologies:
            class_count = await session.scalar(
                select(func.count()).select_from(OntologyClass).where(
                    OntologyClass.ontology_id == ont.id
                )
            )
            dp_count = await session.scalar(
                select(func.count()).select_from(DataProperty).where(
                    DataProperty.ontology_id == ont.id
                )
            )
            op_count = await session.scalar(
                select(func.count()).select_from(ObjectProperty).where(
                    ObjectProperty.ontology_id == ont.id
                )
            )

            responses.append(
                OntologyResponse(
                    id=ont.id,
                    name=ont.name,
                    description=ont.description or "",
                    version=ont.version or "v1.0",
                    status=ont.status or "draft",
                    datasource=None,
                    base_iri=ont.base_iri,
                    imports=[],
                    prefix_mappings={
                        "owl": "http://www.w3.org/2002/07/owl#",
                        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                        "xsd": "http://www.w3.org/2001/XMLSchema#",
                    },
                    object_count=class_count or 0,
                    data_property_count=dp_count or 0,
                    object_property_count=op_count or 0,
                    individual_count=0,
                    axiom_count=0,
                    created_at=ont.created_at.isoformat() if ont.created_at else "",
                    updated_at=ont.updated_at.isoformat() if ont.updated_at else "",
                )
            )

        return responses


async def create_ontology(
    name: str,
    description: str = None,
    base_iri: str = None,
    imports: list = None,
    prefix_mappings: dict = None,
) -> OntologyResponse:
    """创建本体：写入 PostgreSQL + metadata store，可选同步 Jena"""
    from src.database import async_session_maker

    async with async_session_maker() as session:
        async with session.begin():
            import uuid
            new_id = str(uuid.uuid4())[:8]

            if not base_iri:
                base_iri = f"http://onto-agent.com/ontology/{name}#"

            dataset = f"/ontology_{new_id}"

            ontology = Ontology(
                id=new_id,
                name=name,
                description=description,
                base_iri=base_iri,
                dataset=dataset,
                version="v1.0",
                status="draft",
            )
            session.add(ontology)

        await session.commit()

    # 同时写 metadata store（向后兼容）
    from datetime import datetime
    now = datetime.utcnow().isoformat() + "Z"
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

    # 异步创建 Jena dataset（不阻塞响应）
    try:
        import asyncio
        jena = _get_jena()
        if jena:
            asyncio.create_task(_sync_jena_dataset(dataset, base_iri, name, description))
    except Exception:
        pass

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


async def _sync_jena_dataset(dataset: str, base_iri: str, name: str, description: str):
    """后台任务：创建 Jena dataset 并写入本体头"""
    try:
        jena = _get_jena()
        if not jena:
            return
        jena.create_dataset(dataset)
        ds_jena = get_jena_client_for_dataset(dataset)
        if ds_jena:
            ds_jena.create_ontology(name=name, base_iri=base_iri, description=description or "")
    except Exception as e:
        print(f"[JenaSync] Failed to create dataset {dataset}: {e}")


async def get_ontology(ontology_id: str) -> Optional[OntologyResponse]:
    """获取本体（不含详情实体）"""
    from src.database import async_session_maker
    from sqlalchemy import select, func

    async with async_session_maker() as session:
        result = await session.execute(
            select(Ontology).where(Ontology.id == ontology_id)
        )
        ont = result.scalar_one_or_none()
        if not ont:
            return None

        class_count = await session.scalar(
            select(func.count()).select_from(OntologyClass).where(OntologyClass.ontology_id == ontology_id)
        )
        dp_count = await session.scalar(
            select(func.count()).select_from(DataProperty).where(DataProperty.ontology_id == ontology_id)
        )
        op_count = await session.scalar(
            select(func.count()).select_from(ObjectProperty).where(ObjectProperty.ontology_id == ontology_id)
        )

        return OntologyResponse(
            id=ont.id,
            name=ont.name,
            description=ont.description or "",
            version=ont.version or "v1.0",
            status=ont.status or "draft",
            datasource=None,
            base_iri=ont.base_iri,
            imports=[],
            prefix_mappings={
                "owl": "http://www.w3.org/2002/07/owl#",
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                "xsd": "http://www.w3.org/2001/XMLSchema#",
            },
            object_count=class_count or 0,
            data_property_count=dp_count or 0,
            object_property_count=op_count or 0,
            individual_count=0,
            axiom_count=0,
            created_at=ont.created_at.isoformat() if ont.created_at else "",
            updated_at=ont.updated_at.isoformat() if ont.updated_at else "",
        )


async def delete_ontology(ontology_id: str) -> bool:
    """删除本体：PostgreSQL + metadata store + Jena dataset"""
    from src.database import async_session_maker
    from sqlalchemy import select

    async with async_session_maker() as session:
        result = await session.execute(
            select(Ontology).where(Ontology.id == ontology_id)
        )
        ont = result.scalar_one_or_none()
        if not ont:
            return False

        dataset = ont.dataset
        await session.delete(ont)
        await session.commit()

    # 删除 metadata store
    get_metadata_store().delete(ontology_id)

    # 异步删除 Jena dataset
    try:
        import asyncio
        jena = _get_jena()
        if jena and dataset:
            asyncio.create_task(_delete_jena_dataset(dataset))
    except Exception:
        pass

    return True


async def _delete_jena_dataset(dataset: str):
    """后台任务：删除 Jena dataset"""
    try:
        jena = _get_jena()
        if jena:
            jena.delete_dataset(dataset)
    except Exception as e:
        print(f"[JenaSync] Failed to delete dataset {dataset}: {e}")


async def get_ontology_detail(ontology_id: str) -> Optional[OntologyDetailResponse]:
    from src.database import async_session_maker
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    async with async_session_maker() as session:
        result = await session.execute(
            select(Ontology)
            .where(Ontology.id == ontology_id)
            .options(
                selectinload(Ontology.classes),
                selectinload(Ontology.data_properties),
                selectinload(Ontology.object_properties),
                selectinload(Ontology.annotation_properties),
                selectinload(Ontology.individuals),
                selectinload(Ontology.axioms),
                selectinload(Ontology.data_ranges),
            )
        )
        ontology = result.scalar_one_or_none()
        if not ontology:
            return None
        return _build_detail_response(ontology)


async def get_ontology_classes(ontology_id: str) -> list[OntologyClassResponse]:
    from src.database import async_session_maker
    from sqlalchemy import select

    async with async_session_maker() as session:
        result = await session.execute(
            select(OntologyClass).where(OntologyClass.ontology_id == ontology_id)
        )
        classes = result.scalars().all()
        return [_to_class_response(c) for c in classes]


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
    """创建类：写入 PostgreSQL，异步同步 Jena"""
    from src.database import async_session_maker
    import uuid

    async with async_session_maker() as session:
        ont_result = await session.execute(
            select(Ontology).where(Ontology.id == ontology_id)
        )
        if not ont_result.scalar_one_or_none():
            raise ValueError(f"Ontology {ontology_id} not found")

        new_class = OntologyClass(
            id=str(uuid.uuid4())[:12],
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
        session.add(new_class)
        await session.commit()
        await session.refresh(new_class)

    try:
        import asyncio
        asyncio.create_task(_sync_class_to_jena(ontology_id, new_class))
    except Exception:
        pass

    return _to_class_response(new_class)


async def _sync_class_to_jena(ontology_id: str, cls):
    """后台任务：同步类到 Jena"""
    try:
        meta = get_metadata_store().get(ontology_id)
        if not meta:
            return
        jena = get_jena_client_for_dataset(meta.dataset)
        if jena:
            super_iris = [f"{meta.base_iri}{sc}" for sc in (cls.super_classes or [])]
            jena.create_class(
                ontology_iri=meta.base_iri,
                name=cls.name,
                display_name=cls.display_name,
                description=cls.description,
                super_classes=super_iris if super_iris else None,
            )
    except Exception as e:
        print(f"[JenaSync] Failed to sync class {cls.id}: {e}")


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
    from src.database import async_session_maker
    from sqlalchemy import select

    async with async_session_maker() as session:
        result = await session.execute(
            select(OntologyClass).where(
                OntologyClass.id == class_id,
                OntologyClass.ontology_id == ontology_id,
            )
        )
        cls = result.scalar_one_or_none()
        if not cls:
            return None

        if name is not None:
            cls.name = name
        if display_name is not None:
            cls.display_name = display_name
        if description is not None:
            cls.description = description
        if labels is not None:
            cls.labels = labels
        if comments is not None:
            cls.comments = comments
        if equivalent_to is not None:
            cls.equivalent_to = equivalent_to
        if disjoint_with is not None:
            cls.disjoint_with = disjoint_with
        if super_classes is not None:
            cls.super_classes = super_classes

        await session.commit()
        await session.refresh(cls)
        return _to_class_response(cls)


async def delete_ontology_class(ontology_id: str, class_id: str) -> bool:
    from src.database import async_session_maker
    from sqlalchemy import select

    async with async_session_maker() as session:
        result = await session.execute(
            select(OntologyClass).where(
                OntologyClass.id == class_id,
                OntologyClass.ontology_id == ontology_id,
            )
        )
        cls = result.scalar_one_or_none()
        if not cls:
            return False
        await session.delete(cls)
        await session.commit()
        return True


# ============================================================
# DataProperty CRUD
# ============================================================


async def get_data_properties(ontology_id: str) -> list[DataPropertyResponse]:
    from src.database import async_session_maker
    from sqlalchemy import select

    async with async_session_maker() as session:
        result = await session.execute(
            select(DataProperty).where(DataProperty.ontology_id == ontology_id)
        )
        props = result.scalars().all()
        return [_to_dataprop_response(p) for p in props]


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
    from src.database import async_session_maker
    import uuid

    async with async_session_maker() as session:
        ont_result = await session.execute(
            select(Ontology).where(Ontology.id == ontology_id)
        )
        if not ont_result.scalar_one_or_none():
            raise ValueError(f"Ontology {ontology_id} not found")

        new_prop = DataProperty(
            id=str(uuid.uuid4())[:12],
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
        session.add(new_prop)
        await session.commit()
        await session.refresh(new_prop)

    try:
        import asyncio
        asyncio.create_task(_sync_dataprop_to_jena(ontology_id, new_prop))
    except Exception:
        pass

    return _to_dataprop_response(new_prop)


async def _sync_dataprop_to_jena(ontology_id: str, prop):
    try:
        meta = get_metadata_store().get(ontology_id)
        if not meta or not prop.domain_ids:
            return
        jena = get_jena_client_for_dataset(meta.dataset)
        if jena:
            jena.create_datatype_property(
                ontology_iri=meta.base_iri,
                name=prop.name,
                domain_iri=f"{meta.base_iri}{prop.domain_ids[0]}",
                range_type=prop.range_type,
                display_name=prop.display_name,
                characteristics=prop.characteristics,
            )
    except Exception as e:
        print(f"[JenaSync] Failed to sync data property {prop.id}: {e}")


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
    from src.database import async_session_maker
    from sqlalchemy import select

    async with async_session_maker() as session:
        result = await session.execute(
            select(DataProperty).where(
                DataProperty.id == prop_id,
                DataProperty.ontology_id == ontology_id,
            )
        )
        prop = result.scalar_one_or_none()
        if not prop:
            return None

        if name is not None:
            prop.name = name
        if display_name is not None:
            prop.display_name = display_name
        if description is not None:
            prop.description = description
        if domain_ids is not None:
            prop.domain_ids = domain_ids
        if range_type is not None:
            prop.range_type = range_type
        if characteristics is not None:
            prop.characteristics = characteristics
        if super_property_id is not None:
            prop.super_property_id = super_property_id

        await session.commit()
        await session.refresh(prop)
        return _to_dataprop_response(prop)


async def delete_data_property(ontology_id: str, prop_id: str) -> bool:
    from src.database import async_session_maker
    from sqlalchemy import select

    async with async_session_maker() as session:
        result = await session.execute(
            select(DataProperty).where(
                DataProperty.id == prop_id,
                DataProperty.ontology_id == ontology_id,
            )
        )
        prop = result.scalar_one_or_none()
        if not prop:
            return False
        await session.delete(prop)
        await session.commit()
        return True


# ============================================================
# ObjectProperty CRUD
# ============================================================


async def get_object_properties(ontology_id: str) -> list[ObjectPropertyResponse]:
    from src.database import async_session_maker
    from sqlalchemy import select

    async with async_session_maker() as session:
        result = await session.execute(
            select(ObjectProperty).where(ObjectProperty.ontology_id == ontology_id)
        )
        props = result.scalars().all()
        return [_to_objprop_response(p) for p in props]


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
    from src.database import async_session_maker
    import uuid

    async with async_session_maker() as session:
        ont_result = await session.execute(
            select(Ontology).where(Ontology.id == ontology_id)
        )
        if not ont_result.scalar_one_or_none():
            raise ValueError(f"Ontology {ontology_id} not found")

        new_prop = ObjectProperty(
            id=str(uuid.uuid4())[:12],
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
        session.add(new_prop)
        await session.commit()
        await session.refresh(new_prop)

    try:
        import asyncio
        asyncio.create_task(_sync_objprop_to_jena(ontology_id, new_prop))
    except Exception:
        pass

    return _to_objprop_response(new_prop)


async def _sync_objprop_to_jena(ontology_id: str, prop):
    try:
        meta = get_metadata_store().get(ontology_id)
        if not meta or not prop.domain_ids or not prop.range_ids:
            return
        jena = get_jena_client_for_dataset(meta.dataset)
        if jena:
            inverse_of = f"{meta.base_iri}{prop.inverse_of_id}" if prop.inverse_of_id else None
            jena.create_object_property(
                ontology_iri=meta.base_iri,
                name=prop.name,
                domain_iri=f"{meta.base_iri}{prop.domain_ids[0]}",
                range_iri=f"{meta.base_iri}{prop.range_ids[0]}",
                display_name=prop.display_name,
                characteristics=prop.characteristics,
                inverse_of=inverse_of,
            )
    except Exception as e:
        print(f"[JenaSync] Failed to sync object property {prop.id}: {e}")


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
    from src.database import async_session_maker
    from sqlalchemy import select

    async with async_session_maker() as session:
        result = await session.execute(
            select(ObjectProperty).where(
                ObjectProperty.id == prop_id,
                ObjectProperty.ontology_id == ontology_id,
            )
        )
        prop = result.scalar_one_or_none()
        if not prop:
            return None

        if name is not None:
            prop.name = name
        if display_name is not None:
            prop.display_name = display_name
        if description is not None:
            prop.description = description
        if domain_ids is not None:
            prop.domain_ids = domain_ids
        if range_ids is not None:
            prop.range_ids = range_ids
        if characteristics is not None:
            prop.characteristics = characteristics
        if super_property_id is not None:
            prop.super_property_id = super_property_id
        if inverse_of_id is not None:
            prop.inverse_of_id = inverse_of_id
        if property_chain is not None:
            prop.property_chain = property_chain

        await session.commit()
        await session.refresh(prop)
        return _to_objprop_response(prop)


async def delete_object_property(ontology_id: str, prop_id: str) -> bool:
    from src.database import async_session_maker
    from sqlalchemy import select

    async with async_session_maker() as session:
        result = await session.execute(
            select(ObjectProperty).where(
                ObjectProperty.id == prop_id,
                ObjectProperty.ontology_id == ontology_id,
            )
        )
        prop = result.scalar_one_or_none()
        if not prop:
            return False
        await session.delete(prop)
        await session.commit()
        return True


# ============================================================
# AnnotationProperty CRUD
# ============================================================


async def get_annotation_properties(ontology_id: str) -> list[AnnotationPropertyResponse]:
    from src.database import async_session_maker
    from sqlalchemy import select

    async with async_session_maker() as session:
        result = await session.execute(
            select(AnnotationProperty).where(AnnotationProperty.ontology_id == ontology_id)
        )
        props = result.scalars().all()
        return [_to_annprop_response(p) for p in props]


async def create_annotation_property(
    ontology_id: str,
    name: str,
    display_name: str = None,
    description: str = None,
    domain_ids: list = None,
    range_ids: list = None,
    sub_property_of_id: str = None,
) -> AnnotationPropertyResponse:
    from src.database import async_session_maker
    import uuid

    async with async_session_maker() as session:
        new_prop = AnnotationProperty(
            id=str(uuid.uuid4())[:12],
            ontology_id=ontology_id,
            name=name,
            display_name=display_name,
            description=description,
            labels={},
            comments={},
            domain_ids=domain_ids or [],
            range_ids=range_ids or [],
            sub_property_of_id=sub_property_of_id,
        )
        session.add(new_prop)
        await session.commit()
        await session.refresh(new_prop)
        return _to_annprop_response(new_prop)


# ============================================================
# Individual CRUD
# ============================================================


async def get_individuals(ontology_id: str) -> list[IndividualResponse]:
    from src.database import async_session_maker
    from sqlalchemy import select

    async with async_session_maker() as session:
        result = await session.execute(
            select(Individual).where(Individual.ontology_id == ontology_id)
        )
        individuals = result.scalars().all()
        return [_to_individual_response(i) for i in individuals]


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
    from src.database import async_session_maker
    import uuid

    async with async_session_maker() as session:
        new_ind = Individual(
            id=str(uuid.uuid4())[:12],
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
        session.add(new_ind)
        await session.commit()
        await session.refresh(new_ind)
        return _to_individual_response(new_ind)


# ============================================================
# Axiom CRUD
# ============================================================


async def get_axioms(ontology_id: str) -> list[AxiomResponse]:
    from src.database import async_session_maker
    from sqlalchemy import select

    async with async_session_maker() as session:
        result = await session.execute(
            select(Axiom).where(Axiom.ontology_id == ontology_id)
        )
        axioms = result.scalars().all()
        return [_to_axiom_response(a) for a in axioms]


async def create_axiom(
    ontology_id: str,
    axiom_type: str,
    subject: str = None,
    assertions: dict = None,
    annotations: list = None,
) -> AxiomResponse:
    from src.database import async_session_maker
    import uuid

    async with async_session_maker() as session:
        new_axiom = Axiom(
            id=str(uuid.uuid4())[:12],
            ontology_id=ontology_id,
            type=axiom_type,
            subject=subject,
            assertions=assertions or {},
            annotations=annotations or [],
        )
        session.add(new_axiom)
        await session.commit()
        await session.refresh(new_axiom)
        return _to_axiom_response(new_axiom)


# ============================================================
# DataRange CRUD
# ============================================================


async def get_data_ranges(ontology_id: str) -> list[DataRangeResponse]:
    from src.database import async_session_maker
    from sqlalchemy import select

    async with async_session_maker() as session:
        result = await session.execute(
            select(DataRange).where(DataRange.ontology_id == ontology_id)
        )
        ranges = result.scalars().all()
        return [_to_datarange_response(r) for r in ranges]


# ============================================================
# ORM → Response 模型转换（辅助函数）
# ============================================================


def _build_detail_response(ont: Ontology) -> OntologyDetailResponse:
    return OntologyDetailResponse(
        id=ont.id,
        name=ont.name,
        description=ont.description or "",
        version=ont.version or "v1.0",
        status=ont.status or "draft",
        datasource=None,
        base_iri=ont.base_iri,
        imports=[],
        prefix_mappings={
            "owl": "http://www.w3.org/2002/07/owl#",
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
            "xsd": "http://www.w3.org/2001/XMLSchema#",
        },
        object_count=len(ont.classes) if ont.classes else 0,
        data_property_count=len(ont.data_properties) if ont.data_properties else 0,
        object_property_count=len(ont.object_properties) if ont.object_properties else 0,
        individual_count=len(ont.individuals) if ont.individuals else 0,
        axiom_count=len(ont.axioms) if ont.axioms else 0,
        created_at=ont.created_at.isoformat() if ont.created_at else "",
        updated_at=ont.updated_at.isoformat() if ont.updated_at else "",
        classes=[_to_class_response(c) for c in (ont.classes or [])],
        data_properties=[_to_dataprop_response(p) for p in (ont.data_properties or [])],
        object_properties=[_to_objprop_response(p) for p in (ont.object_properties or [])],
        annotation_properties=[_to_annprop_response(p) for p in (ont.annotation_properties or [])],
        individuals=[_to_individual_response(i) for i in (ont.individuals or [])],
        axioms=[_to_axiom_response(a) for a in (ont.axioms or [])],
        data_ranges=[_to_datarange_response(d) for d in (ont.data_ranges or [])],
    )


def _to_class_response(c) -> OntologyClassResponse:
    return OntologyClassResponse(
        id=c.id,
        ontology_id=c.ontology_id,
        name=c.name,
        display_name=c.display_name,
        description=c.description,
        labels=c.labels if isinstance(c.labels, dict) else {},
        comments=c.comments if isinstance(c.comments, dict) else {},
        equivalent_to=c.equivalent_to if isinstance(c.equivalent_to, list) else [],
        disjoint_with=c.disjoint_with if isinstance(c.disjoint_with, list) else [],
        super_classes=c.super_classes if isinstance(c.super_classes, list) else [],
    )


def _to_dataprop_response(p) -> DataPropertyResponse:
    return DataPropertyResponse(
        id=p.id,
        ontology_id=p.ontology_id,
        name=p.name,
        display_name=p.display_name,
        description=p.description,
        labels=p.labels if isinstance(p.labels, dict) else {},
        comments=p.comments if isinstance(p.comments, dict) else {},
        domain_ids=p.domain_ids if isinstance(p.domain_ids, list) else [],
        range_type=p.range_type or "string",
        characteristics=p.characteristics if isinstance(p.characteristics, list) else [],
        super_property_id=p.super_property_id,
    )


def _to_objprop_response(p) -> ObjectPropertyResponse:
    return ObjectPropertyResponse(
        id=p.id,
        ontology_id=p.ontology_id,
        name=p.name,
        display_name=p.display_name,
        description=p.description,
        labels=p.labels if isinstance(p.labels, dict) else {},
        comments=p.comments if isinstance(p.comments, dict) else {},
        domain_ids=p.domain_ids if isinstance(p.domain_ids, list) else [],
        range_ids=p.range_ids if isinstance(p.range_ids, list) else [],
        characteristics=p.characteristics if isinstance(p.characteristics, list) else [],
        super_property_id=p.super_property_id,
        inverse_of_id=p.inverse_of_id,
        property_chain=p.property_chain if isinstance(p.property_chain, list) else [],
    )


def _to_annprop_response(p) -> AnnotationPropertyResponse:
    return AnnotationPropertyResponse(
        id=p.id,
        ontology_id=p.ontology_id,
        name=p.name,
        display_name=p.display_name,
        description=p.description,
        domain_ids=p.domain_ids if isinstance(p.domain_ids, list) else [],
        range_ids=p.range_ids if isinstance(p.range_ids, list) else [],
        sub_property_of_id=p.sub_property_of_id,
    )


def _to_individual_response(i) -> IndividualResponse:
    return IndividualResponse(
        id=i.id,
        ontology_id=i.ontology_id,
        name=i.name,
        display_name=i.display_name,
        description=i.description,
        types=i.types if isinstance(i.types, list) else [],
        labels=i.labels if isinstance(i.labels, dict) else {},
        comments=i.comments if isinstance(i.comments, dict) else {},
        data_property_assertions=i.data_property_assertions if isinstance(i.data_property_assertions, list) else [],
        object_property_assertions=i.object_property_assertions if isinstance(i.object_property_assertions, list) else [],
    )


def _to_axiom_response(a) -> AxiomResponse:
    return AxiomResponse(
        id=a.id,
        ontology_id=a.ontology_id,
        type=a.type,
        subject=a.subject,
        assertions=a.assertions if isinstance(a.assertions, dict) else {},
        annotations=a.annotations if isinstance(a.annotations, list) else [],
    )


def _to_datarange_response(d) -> DataRangeResponse:
    return DataRangeResponse(
        id=d.id,
        ontology_id=d.ontology_id,
        type=d.type,
        values=d.values,
        base_type=d.base_type,
        facets=d.facets,
    )

async def get_data_ranges(ontology_id: str) -> list[DataRangeResponse]:
    from src.database import async_session_maker
    from sqlalchemy import select

    async with async_session_maker() as session:
        result = await session.execute(
            select(DataRange).where(DataRange.ontology_id == ontology_id)
        )
        ranges = result.scalars().all()
        return [_to_datarange_response(r) for r in ranges]


# ============================================================
# ORM → Response 模型转换（辅助函数）
# ============================================================


def _build_detail_response(ont: Ontology) -> OntologyDetailResponse:
    return OntologyDetailResponse(
        id=ont.id,
        name=ont.name,
        description=ont.description or "",
        version=ont.version or "v1.0",
        status=ont.status or "draft",
        datasource=None,
        base_iri=ont.base_iri,
        imports=[],
        prefix_mappings={
            "owl": "http://www.w3.org/2002/07/owl#",
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
            "xsd": "http://www.w3.org/2001/XMLSchema#",
        },
        object_count=len(ont.classes) if ont.classes else 0,
        data_property_count=len(ont.data_properties) if ont.data_properties else 0,
        object_property_count=len(ont.object_properties) if ont.object_properties else 0,
        individual_count=len(ont.individuals) if ont.individuals else 0,
        axiom_count=len(ont.axioms) if ont.axioms else 0,
        created_at=ont.created_at.isoformat() if ont.created_at else "",
        updated_at=ont.updated_at.isoformat() if ont.updated_at else "",
        classes=[_to_class_response(c) for c in (ont.classes or [])],
        data_properties=[_to_dataprop_response(p) for p in (ont.data_properties or [])],
        object_properties=[_to_objprop_response(p) for p in (ont.object_properties or [])],
        annotation_properties=[_to_annprop_response(p) for p in (ont.annotation_properties or [])],
        individuals=[_to_individual_response(i) for i in (ont.individuals or [])],
        axioms=[_to_axiom_response(a) for a in (ont.axioms or [])],
        data_ranges=[_to_datarange_response(d) for d in (ont.data_ranges or [])],
    )


def _to_class_response(c) -> OntologyClassResponse:
    return OntologyClassResponse(
        id=c.id,
        ontology_id=c.ontology_id,
        name=c.name,
        display_name=c.display_name,
        description=c.description,
        labels=c.labels if isinstance(c.labels, dict) else {},
        comments=c.comments if isinstance(c.comments, dict) else {},
        equivalent_to=c.equivalent_to if isinstance(c.equivalent_to, list) else [],
        disjoint_with=c.disjoint_with if isinstance(c.disjoint_with, list) else [],
        super_classes=c.super_classes if isinstance(c.super_classes, list) else [],
    )


def _to_dataprop_response(p) -> DataPropertyResponse:
    return DataPropertyResponse(
        id=p.id,
        ontology_id=p.ontology_id,
        name=p.name,
        display_name=p.display_name,
        description=p.description,
        labels=p.labels if isinstance(p.labels, dict) else {},
        comments=p.comments if isinstance(p.comments, dict) else {},
        domain_ids=p.domain_ids if isinstance(p.domain_ids, list) else [],
        range_type=p.range_type or "string",
        characteristics=p.characteristics if isinstance(p.characteristics, list) else [],
        super_property_id=p.super_property_id,
    )


def _to_objprop_response(p) -> ObjectPropertyResponse:
    return ObjectPropertyResponse(
        id=p.id,
        ontology_id=p.ontology_id,
        name=p.name,
        display_name=p.display_name,
        description=p.description,
        labels=p.labels if isinstance(p.labels, dict) else {},
        comments=p.comments if isinstance(p.comments, dict) else {},
        domain_ids=p.domain_ids if isinstance(p.domain_ids, list) else [],
        range_ids=p.range_ids if isinstance(p.range_ids, list) else [],
        characteristics=p.characteristics if isinstance(p.characteristics, list) else [],
        super_property_id=p.super_property_id,
        inverse_of_id=p.inverse_of_id,
        property_chain=p.property_chain if isinstance(p.property_chain, list) else [],
    )


def _to_annprop_response(p) -> AnnotationPropertyResponse:
    return AnnotationPropertyResponse(
        id=p.id,
        ontology_id=p.ontology_id,
        name=p.name,
        display_name=p.display_name,
        description=p.description,
        domain_ids=p.domain_ids if isinstance(p.domain_ids, list) else [],
        range_ids=p.range_ids if isinstance(p.range_ids, list) else [],
        sub_property_of_id=p.sub_property_of_id,
    )


def _to_individual_response(i) -> IndividualResponse:
    return IndividualResponse(
        id=i.id,
        ontology_id=i.ontology_id,
        name=i.name,
        display_name=i.display_name,
        description=i.description,
        types=i.types if isinstance(i.types, list) else [],
        labels=i.labels if isinstance(i.labels, dict) else {},
        comments=i.comments if isinstance(i.comments, dict) else {},
        data_property_assertions=i.data_property_assertions if isinstance(i.data_property_assertions, list) else [],
        object_property_assertions=i.object_property_assertions if isinstance(i.object_property_assertions, list) else [],
    )


def _to_axiom_response(a) -> AxiomResponse:
    return AxiomResponse(
        id=a.id,
        ontology_id=a.ontology_id,
        type=a.type,
        subject=a.subject,
        assertions=a.assertions if isinstance(a.assertions, dict) else {},
        annotations=a.annotations if isinstance(a.annotations, list) else [],
    )


def _to_datarange_response(d) -> DataRangeResponse:
    return DataRangeResponse(
        id=d.id,
        ontology_id=d.ontology_id,
        type=d.type,
        values=d.values,
        base_type=d.base_type,
        facets=d.facets,
    )
