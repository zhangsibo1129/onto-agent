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
// Version Types
// ============================================================

export interface VersionChange {
  type: "added" | "modified" | "deleted"
  text: string
}

export interface Version {
  version: string
  status: "draft" | "published" | "archived"
  createdAt: string
  description: string
  changeLog: VersionChange[]
  tripleCount?: number
  isSnapshot?: boolean
}

export interface VersionDetail {
  version: string
  tboxContent: string
  aboxContent: string
}

export interface VersionCompareResult {
  fromVersion: string
  toVersion: string
  fromContent: string
  toContent: string
}

export interface SyncTask {
  id: string
  ontologyId: string
  status: "pending" | "running" | "success" | "failed"
  mode: string
  createdAt: string
  startedAt?: string
  completedAt?: string
  processedCount?: number
  totalCount?: number
  error?: string
}

export interface SyncLog {
  id: string
  taskId: string
  level: "info" | "warning" | "error" | "success"
  message: string
  createdAt: string
}

export interface Mapping {
  propertyName: string
  columnName: string
  transform?: string
  createdAt: string
}

export interface MappingCreateDto {
  propertyName: string
  columnName: string
  transform?: string
}

export interface CreateVersionDto {
  version: string
  description?: string
  changeLog?: VersionChange[]
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
  deleteOntology: (id: string) =>
    request<void>(`/ontologies/${id}`, {
      method: "DELETE",
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
  getIndividuals: (ontologyId: string, params?: { classId?: string; search?: string }) => {
    let url = `/ontologies/${ontologyId}/individuals`;
    if (params) {
      const searchParams = new URLSearchParams();
      if (params.classId) searchParams.set('classId', params.classId);
      if (params.search) searchParams.set('search', params.search);
      const qs = searchParams.toString();
      if (qs) url += '?' + qs;
    }
    return request<Individual[]>(url);
  },
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

  // ============================================================
  // Version Management
  // ============================================================
  listVersions: (ontologyId: string) =>
    request<Version[]>(`/ontologies/${ontologyId}/versions`),

  createVersion: (ontologyId: string, dto: CreateVersionDto) =>
    request<Version>(`/ontologies/${ontologyId}/versions`, {
      method: "POST",
      body: JSON.stringify(dto),
    }),

  getVersion: (ontologyId: string, version: string) =>
    request<VersionDetail>(
      `/ontologies/${ontologyId}/versions/${encodeURIComponent(version)}`
    ),

  rollbackVersion: (ontologyId: string, targetVersion: string) =>
    request<{ success: boolean }>(`/ontologies/${ontologyId}/rollback`, {
      method: "POST",
      body: JSON.stringify({ target_version: targetVersion }),
    }),

  compareVersions: (
    ontologyId: string,
    fromVer: string,
    toVer: string
  ) =>
    request<VersionCompareResult>(
      `/ontologies/${ontologyId}/versions/compare?from_ver=${encodeURIComponent(fromVer)}&to_ver=${encodeURIComponent(toVer)}`
    ),

  publishOntology: (ontologyId: string) =>
    request<{ success: boolean }>(`/ontologies/${ontologyId}/publish`, {
      method: "POST",
    }),

  unpublishOntology: (ontologyId: string) =>
    request<{ success: boolean }>(`/ontologies/${ontologyId}/unpublish`, {
      method: "POST",
    }),

  deleteVersion: (ontologyId: string, version: string) =>
    request<{ success: boolean }>(
      `/ontologies/${ontologyId}/versions/${encodeURIComponent(version)}`,
      { method: "DELETE" }
    ),

  // ============================================================
  // Ontology Update
  // ============================================================
  updateOntology: (ontologyId: string, dto: Partial<CreateOntologyDto>) =>
    request<Ontology>(`/ontologies/${ontologyId}`, {
      method: "PUT",
      body: JSON.stringify(dto),
    }),

  // ============================================================
  // Class CRUD
  // ============================================================
  updateClass: (ontologyId: string, classId: string, dto: Partial<CreateClassDto>) =>
    request<OntologyClass>(
      `/ontologies/${ontologyId}/classes/${classId}`,
      { method: "PUT", body: JSON.stringify(dto) }
    ),

  deleteClass: (ontologyId: string, classId: string) =>
    request<void>(
      `/ontologies/${ontologyId}/classes/${classId}`,
      { method: "DELETE" }
    ),

  // ============================================================
  // Data Property CRUD
  // ============================================================
  updateDataProperty: (ontologyId: string, propId: string, dto: Partial<CreateDataPropertyDto>) =>
    request<DataProperty>(
      `/ontologies/${ontologyId}/data-properties/${propId}`,
      { method: "PUT", body: JSON.stringify(dto) }
    ),

  deleteDataProperty: (ontologyId: string, propId: string) =>
    request<void>(
      `/ontologies/${ontologyId}/data-properties/${propId}`,
      { method: "DELETE" }
    ),

  // ============================================================
  // Object Property CRUD
  // ============================================================
  updateObjectProperty: (ontologyId: string, propId: string, dto: Partial<CreateObjectPropertyDto>) =>
    request<ObjectProperty>(
      `/ontologies/${ontologyId}/object-properties/${propId}`,
      { method: "PUT", body: JSON.stringify(dto) }
    ),

  deleteObjectProperty: (ontologyId: string, propId: string) =>
    request<void>(
      `/ontologies/${ontologyId}/object-properties/${propId}`,
      { method: "DELETE" }
    ),

  // ============================================================
  // Individual CRUD
  // ============================================================
  getIndividual: (ontologyId: string, individualId: string) =>
    request<Individual>(
      `/ontologies/${ontologyId}/individuals/${individualId}`
    ),

  updateIndividual: (ontologyId: string, individualId: string, dto: Partial<CreateIndividualDto>) =>
    request<Individual>(
      `/ontologies/${ontologyId}/individuals/${individualId}`,
      { method: "PUT", body: JSON.stringify(dto) }
    ),

  deleteIndividual: (ontologyId: string, individualId: string) =>
    request<void>(
      `/ontologies/${ontologyId}/individuals/${individualId}`,
      { method: "DELETE" }
    ),

  // ============================================================
  // Sync Tasks
  // ============================================================
  listSyncTasks: (ontologyId: string) =>
    request<SyncTask[]>(`/ontologies/${ontologyId}/sync/tasks`),

  triggerSync: (ontologyId: string, mode: string = "full") =>
    request<{ success: boolean; taskId: string }>(
      `/ontologies/${ontologyId}/sync/tasks`,
      { method: "POST", body: JSON.stringify({ mode }) }
    ),

  getSyncTask: (ontologyId: string, taskId: string) =>
    request<SyncTask>(`/ontologies/${ontologyId}/sync/tasks/${taskId}`),

  getSyncTaskLogs: (ontologyId: string, taskId: string) =>
    request<SyncLog[]>(`/ontologies/${ontologyId}/sync/tasks/${taskId}/logs`),

  deleteSyncTask: (ontologyId: string, taskId: string) =>
    request<void>(`/ontologies/${ontologyId}/sync/tasks/${taskId}`, { method: "DELETE" }),

  // ============================================================
  // Mappings
  // ============================================================
  listMappings: (ontologyId: string) =>
    request<Mapping[]>(`/ontologies/${ontologyId}/mappings`),

  createMapping: (ontologyId: string, dto: Partial<MappingCreateDto>) =>
    request<Mapping>(`/ontologies/${ontologyId}/mappings`, { method: "POST", body: JSON.stringify(dto) }),

  deleteMapping: (ontologyId: string, propertyName: string) =>
    request<void>(`/ontologies/${ontologyId}/mappings/${propertyName}`, { method: "DELETE" }),
}
