from typing import Any
from fastapi import APIRouter, HTTPException
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


@router.get("")
async def list_ontologies():
    ontologies = await ontology_service.list_ontologies()
    return success_response([o.model_dump() for o in ontologies])


@router.post("")
async def create_ontology(data: OntologyCreate):
    new_ontology = await ontology_service.create_ontology(
        name=data.name,
        description=data.description,
        base_iri=data.base_iri,
        imports=data.imports,
        prefix_mappings=data.prefix_mappings,
    )
    return success_response(new_ontology.model_dump())


@router.get("/{ontology_id}")
async def get_ontology(ontology_id: str):
    ontology = await ontology_service.get_ontology(ontology_id)
    if not ontology:
        raise HTTPException(status_code=404, detail="Ontology not found")
    return success_response(ontology.model_dump())


@router.get("/{ontology_id}/detail")
async def get_ontology_detail(ontology_id: str):
    detail = await ontology_service.get_ontology_detail(ontology_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Ontology not found")
    return success_response(detail.model_dump())


# ==================== Classes ====================


@router.get("/{ontology_id}/classes")
async def get_classes(ontology_id: str):
    classes = await ontology_service.get_ontology_classes(ontology_id)
    return success_response([c.model_dump() for c in classes])


@router.post("/{ontology_id}/classes")
async def create_class(ontology_id: str, data: OntologyClassCreate):
    new_class = await ontology_service.create_ontology_class(
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
    return success_response(new_class.model_dump())


# ==================== Data Properties ====================


@router.get("/{ontology_id}/data-properties")
async def get_data_properties(ontology_id: str):
    props = await ontology_service.get_data_properties(ontology_id)
    return success_response([p.model_dump() for p in props])


@router.post("/{ontology_id}/data-properties")
async def create_data_property(ontology_id: str, data: DataPropertyCreate):
    new_prop = await ontology_service.create_data_property(
        ontology_id=ontology_id,
        name=data.name,
        domain_ids=data.domain_ids,
        range_type=data.range_type,
        display_name=data.display_name,
        description=data.description,
        characteristics=data.characteristics,
        super_property_id=data.super_property_id,
    )
    return success_response(new_prop.model_dump())


# ==================== Object Properties ====================


@router.get("/{ontology_id}/object-properties")
async def get_object_properties(ontology_id: str):
    props = await ontology_service.get_object_properties(ontology_id)
    return success_response([p.model_dump() for p in props])


@router.post("/{ontology_id}/object-properties")
async def create_object_property(ontology_id: str, data: ObjectPropertyCreate):
    new_prop = await ontology_service.create_object_property(
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
    return success_response(new_prop.model_dump())


# ==================== Annotation Properties ====================


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


# ==================== Individuals ====================


@router.get("/{ontology_id}/individuals")
async def get_individuals(ontology_id: str):
    individuals = await ontology_service.get_individuals(ontology_id)
    return success_response([i.model_dump() for i in individuals])


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


# ==================== Axioms ====================


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


# ==================== Data Ranges ====================


@router.get("/{ontology_id}/data-ranges")
async def get_data_ranges(ontology_id: str):
    data_ranges = await ontology_service.get_data_ranges(ontology_id)
    return success_response([d.model_dump() for d in data_ranges])
