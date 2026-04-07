const API_BASE = "/api"

export interface Datasource {
  id: string
  name: string
  type: string
  status: "connected" | "disconnected" | "error"
  host: string | null
  port: number | null
  database: string | null
  schema: string | null
  username: string | null
  password?: string | null
  sslMode: string | null
  tableCount: number
  lastSyncAt: string | null
  createdAt: string
  updatedAt: string
}

export interface CreateDatasourceDto {
  name: string
  type: "postgresql" | "mysql" | "sqlserver" | "oracle"
  host?: string
  port?: number
  database?: string
  schema?: string
  username?: string
  password?: string
  sslMode?: string
}

export interface TestConnectionDto {
  type: string
  host?: string
  port?: number
  database?: string
  schema?: string
  username?: string
  password?: string
  sslMode?: string
}

export interface UpdateDatasourceDto {
  name?: string
  type?: string
  host?: string
  port?: number
  database?: string
  schema?: string
  username?: string
  password?: string
  sslMode?: string
}

export interface TableInfo {
  name: string
  columns: number
  rowCount: number
}

export interface ColumnInfo {
  name: string
  type: string
  nullable: boolean
  primaryKey: boolean
  defaultValue: string | null
}

export interface TestResult {
  connected: boolean
  latency?: string
  version?: string
  tableCount?: number
  error?: string
}

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

export const datasourceApi = {
  list: () => request<Datasource[]>("/datasources"),

  get: (id: string) => request<Datasource>(`/datasources/${id}`),

  create: (dto: CreateDatasourceDto) =>
    request<Datasource>("/datasources", {
      method: "POST",
      body: JSON.stringify(dto),
    }),

  update: (id: string, dto: UpdateDatasourceDto) =>
    request<Datasource>(`/datasources/${id}`, {
      method: "PUT",
      body: JSON.stringify(dto),
    }),

  delete: (id: string) =>
    request<void>(`/datasources/${id}`, { method: "DELETE" }),

  testConnection: (dto: TestConnectionDto) =>
    request<TestResult>("/datasources/test-connection", {
      method: "POST",
      body: JSON.stringify(dto),
    }),

  test: (id: string) => request<TestResult>(`/datasources/${id}/test`),

  getTables: (id: string) =>
    request<{ tables: TableInfo[]; scannedAt: string }>(
      `/datasources/${id}/tables`
    ),

  getColumns: (id: string, tableName: string) =>
    request<{ tableName: string; columns: ColumnInfo[] }>(
      `/datasources/${id}/tables/${tableName}/columns`
    ),
}
