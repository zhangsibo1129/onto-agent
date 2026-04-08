from pydantic import Field
from typing import Optional
from datetime import datetime
from src.core.naming import CamelCaseModel


class OntologyClassBase(CamelCaseModel):
    name: str
    display_name: Optional[str] = None
    description: Optional[str] = None


class OntologyClassCreate(OntologyClassBase):
    pass


class OntologyClassUpdate(CamelCaseModel):
    name: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None


class OntologyClassResponse(CamelCaseModel):
    id: str
    name: str
    display_name: Optional[str] = None
    description: Optional[str] = None


class DataPropertyBase(CamelCaseModel):
    name: str
    display_name: Optional[str] = None
    domain_id: str
    range_type: str = "String"


class DataPropertyCreate(DataPropertyBase):
    pass


class DataPropertyUpdate(CamelCaseModel):
    name: Optional[str] = None
    display_name: Optional[str] = None
    range_type: Optional[str] = None


class DataPropertyResponse(CamelCaseModel):
    id: str
    name: str
    display_name: Optional[str] = None
    domain_id: str
    range_type: str


class ObjectPropertyBase(CamelCaseModel):
    name: str
    display_name: Optional[str] = None
    domain_id: str
    range_id: str


class ObjectPropertyCreate(ObjectPropertyBase):
    pass


class ObjectPropertyUpdate(CamelCaseModel):
    name: Optional[str] = None
    display_name: Optional[str] = None
    range_id: Optional[str] = None


class ObjectPropertyResponse(CamelCaseModel):
    id: str
    name: str
    display_name: Optional[str] = None
    domain_id: str
    range_id: str


class OntologyRelationCreate(CamelCaseModel):
    source_id: str
    target_id: str
    property_id: str


class OntologyRelationResponse(CamelCaseModel):
    id: str
    source_id: str
    target_id: str
    property_id: str


class OntologyBase(CamelCaseModel):
    name: str
    description: Optional[str] = None
    version: Optional[str] = None
    status: str = "draft"
    datasource: Optional[str] = None


class OntologyCreate(OntologyBase):
    pass


class OntologyUpdate(CamelCaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None
    status: Optional[str] = None
    datasource: Optional[str] = None


class OntologyResponse(CamelCaseModel):
    id: str
    name: str
    description: Optional[str] = None
    status: str
    object_count: int = 0
    property_count: int = 0
    relation_count: int = 0
    updated_at: Optional[str] = None
    version: Optional[str] = None
    datasource: Optional[str] = None


class OntologyDetailResponse(OntologyResponse):
    classes: list[OntologyClassResponse] = []
    data_properties: list[DataPropertyResponse] = []
    object_properties: list[ObjectPropertyResponse] = []
    relations: list[OntologyRelationResponse] = []
