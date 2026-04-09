const API_BASE = "/api"

interface ApiResponse<T> {
  success: boolean
  data: T
  error?: {
    code: string
    message: string
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    ...options,
  })

  const json: ApiResponse<T> = await response.json()

  if (!json.success) {
    throw new Error(json.error?.message || "Request failed")
  }

  return json.data
}

// ============================================================
// Property Characteristics (属性特性)
// ============================================================

export type DataPropertyCharacteristic = "functional"

export type ObjectPropertyCharacteristic =
  | "functional"
  | "inverseFunctional"
  | "transitive"
  | "symmetric"
  | "asymmetric"
  | "reflexive"
  | "irreflexive"

export type PropertyCharacteristic =
  | "functional"
  | "inverseFunctional"
  | "transitive"
  | "symmetric"
  | "asymmetric"
  | "reflexive"
  | "irreflexive"

// ============================================================
// Data Types (OWL 2 Built-in DataTypes)
// ============================================================

export type DataType =
  | "string"
  | "boolean"
  | "integer"
  | "decimal"
  | "float"
  | "double"
  | "dateTime"
  | "date"
  | "time"
  | "duration"
  | "hexBinary"
  | "base64Binary"
  | "anyURI"
  | "normalizedString"
  | "token"
  | "language"
  | "positiveInteger"
  | "negativeInteger"
  | "nonPositiveInteger"
  | "nonNegativeInteger"

// ============================================================
// Annotation (注解)
// ============================================================

export interface Annotation {
  propertyId: string
  value: string
}

// ============================================================
// DataRange (数据范围)
// ============================================================

export type DataRangeType = "datatype" | "enumeration" | "restriction" | "union" | "intersection"

export type DataTypeFacetType =
  | "length"
  | "minLength"
  | "maxLength"
  | "pattern"
  | "minInclusive"
  | "maxInclusive"
  | "minExclusive"
  | "maxExclusive"
  | "totalDigits"
  | "fractionDigits"

export interface DataTypeFacet {
  type: DataTypeFacetType
  value: string | number
}

export interface DataRange {
  id: string
  type: DataRangeType
  values?: unknown[]
  baseType?: DataType
  facets?: DataTypeFacet[]
}

// ============================================================
// OntologyClass (类 - owl:Class)
// ============================================================

export interface OntologyClass {
  id: string
  ontologyId: string
  name: string
  displayName?: string
  description?: string
  labels: Record<string, string>
  comments: Record<string, string>
  equivalentTo: string[]
  disjointWith: string[]
  superClasses: string[]
}

export interface CreateClassDto {
  name: string
  displayName?: string
  description?: string
  labels?: Record<string, string>
  comments?: Record<string, string>
  equivalentTo?: string[]
  disjointWith?: string[]
  superClasses?: string[]
}

// ============================================================
// DataProperty (数据属性 - owl:DatatypeProperty)
// ============================================================

export interface DataProperty {
  id: string
  ontologyId: string
  name: string
  displayName?: string
  description?: string
  labels: Record<string, string>
  comments: Record<string, string>
  domainIds: string[]
  rangeType: DataType
  characteristics: PropertyCharacteristic[]
  superPropertyId?: string
}

export interface CreateDataPropertyDto {
  name: string
  displayName?: string
  description?: string
  domainIds: string[]
  rangeType?: DataType
  characteristics?: PropertyCharacteristic[]
  superPropertyId?: string
}

// ============================================================
// ObjectProperty (对象属性 - owl:ObjectProperty)
// ============================================================

export interface ObjectProperty {
  id: string
  ontologyId: string
  name: string
  displayName?: string
  description?: string
  labels: Record<string, string>
  comments: Record<string, string>
  domainIds: string[]
  rangeIds: string[]
  characteristics: PropertyCharacteristic[]
  superPropertyId?: string
  inverseOfId?: string
  propertyChain: string[]
}

export interface CreateObjectPropertyDto {
  name: string
  displayName?: string
  description?: string
  domainIds: string[]
  rangeIds: string[]
  characteristics?: PropertyCharacteristic[]
  superPropertyId?: string
  inverseOfId?: string
  propertyChain?: string[]
}

// ============================================================
// AnnotationProperty (注解属性 - owl:AnnotationProperty)
// ============================================================

export interface AnnotationProperty {
  id: string
  ontologyId: string
  name: string
  displayName?: string
  description?: string
  domainIds: string[]
  rangeIds: string[]
  subPropertyOfId?: string
}

export interface CreateAnnotationPropertyDto {
  name: string
  displayName?: string
  description?: string
  domainIds?: string[]
  rangeIds?: string[]
  subPropertyOfId?: string
}

// ============================================================
// Individual (个体 - owl:NamedIndividual)
// ============================================================

export interface DataPropertyAssertion {
  propertyId: string
  value: unknown
}

export interface ObjectPropertyAssertion {
  propertyId: string
  targetIndividualId: string
}

export interface Individual {
  id: string
  ontologyId: string
  name: string
  displayName?: string
  description?: string
  types: string[]
  labels: Record<string, string>
  comments: Record<string, string>
  dataPropertyAssertions: DataPropertyAssertion[]
  objectPropertyAssertions: ObjectPropertyAssertion[]
}

export interface CreateIndividualDto {
  name: string
  displayName?: string
  description?: string
  types?: string[]
  labels?: Record<string, string>
  comments?: Record<string, string>
  dataPropertyAssertions?: DataPropertyAssertion[]
  objectPropertyAssertions?: ObjectPropertyAssertion[]
}

// ============================================================
// Axiom (公理)
// ============================================================

export type AxiomType =
  | "SubClassOf"
  | "EquivalentClasses"
  | "DisjointClasses"
  | "SubPropertyOf"
  | "EquivalentProperties"
  | "FunctionalProperty"
  | "InverseFunctionalProperty"
  | "SymmetricProperty"
  | "TransitiveProperty"
  | "ClassAssertion"
  | "SameIndividual"
  | "DifferentIndividuals"

export interface Axiom {
  id: string
  ontologyId: string
  type: AxiomType
  subject?: string
  assertions: Record<string, unknown>
  annotations: Annotation[]
}

export interface CreateAxiomDto {
  type: AxiomType
  subject?: string
  assertions?: Record<string, unknown>
  annotations?: Annotation[]
}

// ============================================================
// Ontology (本体)
// ============================================================

export interface Ontology {
  id: string
  name: string
  description?: string
  version?: string
  status: "draft" | "published" | "archived"
  datasource?: string
  baseIri: string
  imports: string[]
  prefixMappings: Record<string, string>
  objectCount: number
  dataPropertyCount: number
  objectPropertyCount: number
  individualCount: number
  axiomCount: number
  createdAt: string
  updatedAt: string
}

export interface OntologyDetail extends Ontology {
  classes: OntologyClass[]
  dataProperties: DataProperty[]
  objectProperties: ObjectProperty[]
  annotationProperties: AnnotationProperty[]
  individuals: Individual[]
  axioms: Axiom[]
  dataRanges: DataRange[]
}

export interface CreateOntologyDto {
  name: string
  description?: string
  baseIri: string
}

// ============================================================
// API Methods
// ============================================================

export const ontologyApi = {
  // Ontology
  list: () => request<Ontology[]>("/ontologies"),
  get: (id: string) => request<Ontology>(`/ontologies/${id}`),
  getDetail: (id: string) => request<OntologyDetail>(`/ontologies/${id}/detail`),
  createOntology: (dto: CreateOntologyDto) =>
    request<Ontology>("/ontologies", {
      method: "POST",
      body: JSON.stringify(dto),
    }),

  // Classes
  getClasses: (ontologyId: string) =>
    request<OntologyClass[]>(`/ontologies/${ontologyId}/classes`),
  createClass: (ontologyId: string, dto: CreateClassDto) =>
    request<OntologyClass>(`/ontologies/${ontologyId}/classes`, {
      method: "POST",
      body: JSON.stringify(dto),
    }),

  // Data Properties
  getDataProperties: (ontologyId: string) =>
    request<DataProperty[]>(`/ontologies/${ontologyId}/data-properties`),
  createDataProperty: (ontologyId: string, dto: CreateDataPropertyDto) =>
    request<DataProperty>(`/ontologies/${ontologyId}/data-properties`, {
      method: "POST",
      body: JSON.stringify(dto),
    }),

  // Object Properties
  getObjectProperties: (ontologyId: string) =>
    request<ObjectProperty[]>(`/ontologies/${ontologyId}/object-properties`),
  createObjectProperty: (ontologyId: string, dto: CreateObjectPropertyDto) =>
    request<ObjectProperty>(`/ontologies/${ontologyId}/object-properties`, {
      method: "POST",
      body: JSON.stringify(dto),
    }),

  // Annotation Properties
  getAnnotationProperties: (ontologyId: string) =>
    request<AnnotationProperty[]>(`/ontologies/${ontologyId}/annotation-properties`),
  createAnnotationProperty: (ontologyId: string, dto: CreateAnnotationPropertyDto) =>
    request<AnnotationProperty>(`/ontologies/${ontologyId}/annotation-properties`, {
      method: "POST",
      body: JSON.stringify(dto),
    }),

  // Individuals
  getIndividuals: (ontologyId: string) =>
    request<Individual[]>(`/ontologies/${ontologyId}/individuals`),
  createIndividual: (ontologyId: string, dto: CreateIndividualDto) =>
    request<Individual>(`/ontologies/${ontologyId}/individuals`, {
      method: "POST",
      body: JSON.stringify(dto),
    }),

  // Axioms
  getAxioms: (ontologyId: string) =>
    request<Axiom[]>(`/ontologies/${ontologyId}/axioms`),
  createAxiom: (ontologyId: string, dto: CreateAxiomDto) =>
    request<Axiom>(`/ontologies/${ontologyId}/axioms`, {
      method: "POST",
      body: JSON.stringify(dto),
    }),

  // Data Ranges
  getDataRanges: (ontologyId: string) =>
    request<DataRange[]>(`/ontologies/${ontologyId}/data-ranges`),
}
