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

export interface OntologyClass {
  id: string
  name: string
  displayName?: string
  description?: string
}

export interface DataProperty {
  id: string
  name: string
  displayName?: string
  domainId: string
  rangeType: string
}

export interface ObjectProperty {
  id: string
  name: string
  displayName?: string
  domainId: string
  rangeId: string
}

export interface OntologyRelation {
  id: string
  sourceId: string
  targetId: string
  propertyId: string
}

export interface Ontology {
  id: string
  name: string
  description?: string
  status: "draft" | "published" | "archived"
  objectCount: number
  propertyCount: number
  relationCount: number
  updatedAt?: string
  version?: string
  datasource?: string
}

export interface OntologyDetail extends Ontology {
  classes: OntologyClass[]
  dataProperties: DataProperty[]
  objectProperties: ObjectProperty[]
  relations: OntologyRelation[]
}

export interface CreateClassDto {
  name: string
  displayName?: string
  description?: string
}

export interface CreateDataPropertyDto {
  name: string
  displayName?: string
  domainId: string
  rangeType?: string
}

export interface CreateObjectPropertyDto {
  name: string
  displayName?: string
  domainId: string
  rangeId: string
}

export interface CreateRelationDto {
  sourceId: string
  targetId: string
  propertyId: string
}

export const ontologyApi = {
  list: () => request<Ontology[]>("/ontologies"),

  get: (id: string) => request<Ontology>(`/ontologies/${id}`),

  getDetail: (id: string) => request<OntologyDetail>(`/ontologies/${id}/detail`),

  getClasses: (ontologyId: string) =>
    request<OntologyClass[]>(`/ontologies/${ontologyId}/classes`),

  createClass: (ontologyId: string, dto: CreateClassDto) =>
    request<OntologyClass>(`/ontologies/${ontologyId}/classes`, {
      method: "POST",
      body: JSON.stringify(dto),
    }),

  getDataProperties: (ontologyId: string) =>
    request<DataProperty[]>(`/ontologies/${ontologyId}/data-properties`),

  createDataProperty: (ontologyId: string, dto: CreateDataPropertyDto) =>
    request<DataProperty>(`/ontologies/${ontologyId}/data-properties`, {
      method: "POST",
      body: JSON.stringify(dto),
    }),

  getObjectProperties: (ontologyId: string) =>
    request<ObjectProperty[]>(`/ontologies/${ontologyId}/object-properties`),

  createObjectProperty: (ontologyId: string, dto: CreateObjectPropertyDto) =>
    request<ObjectProperty>(`/ontologies/${ontologyId}/object-properties`, {
      method: "POST",
      body: JSON.stringify(dto),
    }),

  getRelations: (ontologyId: string) =>
    request<OntologyRelation[]>(`/ontologies/${ontologyId}/relations`),

  createRelation: (ontologyId: string, dto: CreateRelationDto) =>
    request<OntologyRelation>(`/ontologies/${ontologyId}/relations`, {
      method: "POST",
      body: JSON.stringify(dto),
    }),
}
