from pydantic import Field
from typing import Optional, Any, Literal
from src.core.naming import CamelCaseModel

# ============================================================
# Property Characteristics (属性特性)
# ============================================================

DataPropertyCharacteristic = Literal["functional",]

ObjectPropertyCharacteristic = Literal[
    "functional",
    "inverseFunctional",
    "transitive",
    "symmetric",
    "asymmetric",
    "reflexive",
    "irreflexive",
]

PropertyCharacteristic = Literal[
    "functional",
    "inverseFunctional",
    "transitive",
    "symmetric",
    "asymmetric",
    "reflexive",
    "irreflexive",
]

# ============================================================
# Data Types (OWL 2 Built-in DataTypes)
# ============================================================

DataType = Literal[
    "string",
    "boolean",
    "integer",
    "decimal",
    "float",
    "double",
    "dateTime",
    "date",
    "time",
    "duration",
    "hexBinary",
    "base64Binary",
    "anyURI",
    "normalizedString",
    "token",
    "language",
    "positiveInteger",
    "negativeInteger",
    "nonPositiveInteger",
    "nonNegativeInteger",
]

# ============================================================
# Data Type Facets (数据类型刻面)
# ============================================================

DataTypeFacetType = Literal[
    "length",
    "minLength",
    "maxLength",
    "pattern",
    "minInclusive",
    "maxInclusive",
    "minExclusive",
    "maxExclusive",
    "totalDigits",
    "fractionDigits",
]


class DataTypeFacet(CamelCaseModel):
    type: DataTypeFacetType
    value: str | float | int


# ============================================================
# DataRange (数据范围)
# ============================================================


class DataRangeBase(CamelCaseModel):
    type: Literal["datatype", "enumeration", "restriction", "union", "intersection"]
    values: list[Any] | None = None
    base_type: DataType | None = None
    facets: list[DataTypeFacet] | None = None


class DataRangeResponse(DataRangeBase):
    id: str


# ============================================================
# Annotation (注解)
# ============================================================


class Annotation(CamelCaseModel):
    property_id: str
    value: str


# ============================================================
# OntologyClass (类 - owl:Class)
# ============================================================


class OntologyClassBase(CamelCaseModel):
    name: str
    display_name: Optional[str] = None
    description: Optional[str] = None
    labels: dict[str, str] = Field(default_factory=dict)
    comments: dict[str, str] = Field(default_factory=dict)


class OntologyClassCreate(OntologyClassBase):
    equivalent_to: list[str] = Field(default_factory=list)
    disjoint_with: list[str] = Field(default_factory=list)
    super_classes: list[str] = Field(default_factory=list)


class OntologyClassUpdate(CamelCaseModel):
    name: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    labels: Optional[dict[str, str]] = None
    comments: Optional[dict[str, str]] = None
    equivalent_to: Optional[list[str]] = None
    disjoint_with: Optional[list[str]] = None
    super_classes: Optional[list[str]] = None


class OntologyClassResponse(OntologyClassBase):
    id: str
    ontology_id: Optional[str] = None
    equivalent_to: list[str] = Field(default_factory=list)
    disjoint_with: list[str] = Field(default_factory=list)
    super_classes: list[str] = Field(default_factory=list)


# ============================================================
# DataProperty (数据属性 - owl:DatatypeProperty)
# ============================================================


class DataPropertyBase(CamelCaseModel):
    name: str
    display_name: Optional[str] = None
    description: Optional[str] = None
    labels: dict[str, str] = Field(default_factory=dict)
    comments: dict[str, str] = Field(default_factory=dict)


class DataPropertyCreate(DataPropertyBase):
    domain_ids: list[str] = Field(default_factory=list)
    range_type: DataType = "string"
    characteristics: list[PropertyCharacteristic] = Field(default_factory=list)
    super_property_id: Optional[str] = None


class DataPropertyUpdate(CamelCaseModel):
    name: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    labels: Optional[dict[str, str]] = None
    comments: Optional[dict[str, str]] = None
    domain_ids: Optional[list[str]] = None
    range_type: Optional[DataType] = None
    characteristics: Optional[list[PropertyCharacteristic]] = None
    super_property_id: Optional[str] = None


class DataPropertyResponse(DataPropertyBase):
    id: str
    ontology_id: Optional[str] = None
    domain_ids: list[str] = Field(default_factory=list)
    range_type: DataType
    characteristics: list[PropertyCharacteristic] = Field(default_factory=list)
    super_property_id: Optional[str] = None


# ============================================================
# ObjectProperty (对象属性 - owl:ObjectProperty)
# ============================================================


class ObjectPropertyBase(CamelCaseModel):
    name: str
    display_name: Optional[str] = None
    description: Optional[str] = None
    labels: dict[str, str] = Field(default_factory=dict)
    comments: dict[str, str] = Field(default_factory=dict)


class ObjectPropertyCreate(ObjectPropertyBase):
    domain_ids: list[str] = Field(default_factory=list)
    range_ids: list[str] = Field(default_factory=list)
    characteristics: list[PropertyCharacteristic] = Field(default_factory=list)
    super_property_id: Optional[str] = None
    inverse_of_id: Optional[str] = None
    property_chain: list[str] = Field(default_factory=list)


class ObjectPropertyUpdate(CamelCaseModel):
    name: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    labels: Optional[dict[str, str]] = None
    comments: Optional[dict[str, str]] = None
    domain_ids: Optional[list[str]] = None
    range_ids: Optional[list[str]] = None
    characteristics: Optional[list[PropertyCharacteristic]] = None
    super_property_id: Optional[str] = None
    inverse_of_id: Optional[str] = None
    property_chain: Optional[list[str]] = None


class ObjectPropertyResponse(ObjectPropertyBase):
    id: str
    ontology_id: Optional[str] = None
    domain_ids: list[str] = Field(default_factory=list)
    range_ids: list[str] = Field(default_factory=list)
    characteristics: list[PropertyCharacteristic] = Field(default_factory=list)
    super_property_id: Optional[str] = None
    inverse_of_id: Optional[str] = None
    property_chain: list[str] = Field(default_factory=list)


# ============================================================
# AnnotationProperty (注解属性 - owl:AnnotationProperty)
# ============================================================


class AnnotationPropertyBase(CamelCaseModel):
    name: str
    display_name: Optional[str] = None
    description: Optional[str] = None


class AnnotationPropertyCreate(AnnotationPropertyBase):
    domain_ids: list[str] = Field(default_factory=list)
    range_ids: list[str] = Field(default_factory=list)
    sub_property_of_id: Optional[str] = None


class AnnotationPropertyResponse(AnnotationPropertyBase):
    id: str
    ontology_id: Optional[str] = None
    domain_ids: list[str] = Field(default_factory=list)
    range_ids: list[str] = Field(default_factory=list)
    sub_property_of_id: Optional[str] = None


# ============================================================
# Individual (个体 - owl:NamedIndividual)
# ============================================================


class DataPropertyAssertion(CamelCaseModel):
    property_id: str
    value: Any


class ObjectPropertyAssertion(CamelCaseModel):
    property_id: str
    target_individual_id: str


class IndividualBase(CamelCaseModel):
    name: str
    display_name: Optional[str] = None
    description: Optional[str] = None
    types: list[str] = Field(default_factory=list)
    labels: dict[str, str] = Field(default_factory=dict)
    comments: dict[str, str] = Field(default_factory=dict)


class IndividualCreate(IndividualBase):
    data_property_assertions: list[DataPropertyAssertion] = Field(default_factory=list)
    object_property_assertions: list[ObjectPropertyAssertion] = Field(
        default_factory=list
    )


class IndividualUpdate(CamelCaseModel):
    name: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    types: Optional[list[str]] = None
    labels: Optional[dict[str, str]] = None
    comments: Optional[dict[str, str]] = None


class IndividualResponse(IndividualBase):
    id: str
    ontology_id: Optional[str] = None
    data_property_assertions: list[DataPropertyAssertion] = Field(default_factory=list)
    object_property_assertions: list[ObjectPropertyAssertion] = Field(
        default_factory=list
    )


# ============================================================
# Axiom (公理)
# ============================================================

AxiomType = Literal[
    "SubClassOf",
    "EquivalentClasses",
    "DisjointClasses",
    "SubPropertyOf",
    "EquivalentProperties",
    "FunctionalProperty",
    "InverseFunctionalProperty",
    "SymmetricProperty",
    "TransitiveProperty",
    "ClassAssertion",
    "SameIndividual",
    "DifferentIndividuals",
]


class AxiomBase(CamelCaseModel):
    type: AxiomType
    annotations: list[Annotation] = Field(default_factory=list)


class AxiomCreate(AxiomBase):
    subject: Optional[str] = None
    assertions: dict[str, Any] = Field(default_factory=dict)


class AxiomResponse(AxiomBase):
    id: str
    ontology_id: Optional[str] = None
    subject: Optional[str] = None
    assertions: dict[str, Any] = Field(default_factory=dict)


# ============================================================
# PropertyRestriction (属性约束)
# ============================================================

RestrictionType = Literal[
    "cardinality",
    "minCardinality",
    "maxCardinality",
    "someValuesFrom",
    "allValuesFrom",
    "hasValue",
]


class PropertyRestriction(CamelCaseModel):
    type: RestrictionType
    on_property_id: str
    cardinality: int | None = None
    value: Any | None = None
    on_class_id: str | None = None


# ============================================================
# Ontology (本体)
# ============================================================


class OntologyBase(CamelCaseModel):
    name: str
    description: Optional[str] = None
    version: Optional[str] = None
    status: str = "draft"
    datasource: Optional[str] = None


class OntologyCreate(OntologyBase):
    base_iri: Optional[str] = Field(default=None, validation_alias="baseIri")
    imports: list[str] = Field(default_factory=list, validation_alias="imports")
    prefix_mappings: dict[str, str] = Field(
        default_factory=dict, validation_alias="prefixMappings"
    )


class OntologyUpdate(CamelCaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None
    status: Optional[str] = None
    datasource: Optional[str] = None
    base_iri: Optional[str] = None
    imports: Optional[list[str]] = None
    prefix_mappings: Optional[dict[str, str]] = None


class OntologyResponse(OntologyBase):
    id: str
    base_iri: str
    imports: list[str] = Field(default_factory=list)
    prefix_mappings: dict[str, str] = Field(default_factory=dict)
    object_count: int = 0
    data_property_count: int = 0
    object_property_count: int = 0
    individual_count: int = 0
    axiom_count: int = 0
    created_at: str
    updated_at: str


# ============================================================
# Ontology Detail (完整本体详情)
# ============================================================


class OntologyDetailResponse(OntologyResponse):
    classes: list[OntologyClassResponse] = Field(default_factory=list)
    data_properties: list[DataPropertyResponse] = Field(default_factory=list)
    object_properties: list[ObjectPropertyResponse] = Field(default_factory=list)
    annotation_properties: list[AnnotationPropertyResponse] = Field(
        default_factory=list
    )
    individuals: list[IndividualResponse] = Field(default_factory=list)
    axioms: list[AxiomResponse] = Field(default_factory=list)
    data_ranges: list[DataRangeResponse] = Field(default_factory=list)
