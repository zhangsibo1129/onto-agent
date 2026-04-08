from fastapi import APIRouter, HTTPException
from src.schemas.ontology import (
    OntologyClassCreate,
    DataPropertyCreate,
    ObjectPropertyCreate,
    OntologyRelationCreate,
)
from src.services import ontology as ontology_service

router = APIRouter(prefix="/ontologies", tags=["ontologies"])


def success_response(data):
    return {"success": True, "data": data}


@router.get("")
async def list_ontologies():
    ontologies = await ontology_service.list_ontologies()
    return success_response([o.model_dump() for o in ontologies])


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
    )
    return success_response(new_class.model_dump())


@router.get("/{ontology_id}/data-properties")
async def get_data_properties(ontology_id: str):
    props = await ontology_service.get_data_properties(ontology_id)
    return success_response([p.model_dump() for p in props])


@router.post("/{ontology_id}/data-properties")
async def create_data_property(ontology_id: str, data: DataPropertyCreate):
    new_prop = await ontology_service.create_data_property(
        ontology_id=ontology_id,
        name=data.name,
        domain_id=data.domain_id,
        range_type=data.range_type,
        display_name=data.display_name,
    )
    return success_response(new_prop.model_dump())


@router.get("/{ontology_id}/object-properties")
async def get_object_properties(ontology_id: str):
    props = await ontology_service.get_object_properties(ontology_id)
    return success_response([p.model_dump() for p in props])


@router.post("/{ontology_id}/object-properties")
async def create_object_property(ontology_id: str, data: ObjectPropertyCreate):
    new_prop = await ontology_service.create_object_property(
        ontology_id=ontology_id,
        name=data.name,
        domain_id=data.domain_id,
        range_id=data.range_id,
        display_name=data.display_name,
    )
    return success_response(new_prop.model_dump())


@router.get("/{ontology_id}/relations")
async def get_relations(ontology_id: str):
    relations = await ontology_service.get_relations(ontology_id)
    return success_response([r.model_dump() for r in relations])


@router.post("/{ontology_id}/relations")
async def create_relation(ontology_id: str, data: OntologyRelationCreate):
    new_rel = await ontology_service.create_relation(
        ontology_id=ontology_id,
        source_id=data.source_id,
        target_id=data.target_id,
        property_id=data.property_id,
    )
    return success_response(new_rel.model_dump())
