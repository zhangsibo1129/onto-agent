/**
 * Query API Service
 * Phase 7: SPARQL execution, history, saved queries
 */

const API_BASE = "/api"

interface ApiResponse<T> {
  success: boolean
  data?: T
  error?: string
  [key: string]: unknown
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
    throw new Error((json.error as unknown as { message?: string })?.message || "Request failed")
  }
  return json as unknown as T
}

// ============================================================
// Types
// ============================================================

export interface SparqlResult {
  success: boolean
  queryType: "SELECT" | "ASK" | "CONSTRUCT" | "DESCRIBE"
  results: unknown | boolean | string
  resultCount: number
  executionTimeMs: number
  historyId: string
  error?: string
}

export interface QueryHistoryItem {
  id: string
  queryType: string
  queryText: string
  resultCount: number
  errorMessage?: string
  executionTimeMs?: number
  createdAt: string
}

export interface SavedQuery {
  id: string
  ontologyId: string
  name: string
  description?: string
  queryType: string
  queryText: string
  createdAt: string
  updatedAt: string
}

export interface NlQueryResult {
  success: boolean
  nlText: string
  sparql: string
  note?: string
}

// ============================================================
// SPARQL Execution
// ============================================================

/**
 * Execute SPARQL query (SELECT / ASK / CONSTRUCT / DESCRIBE)
 */
export async function executeSparql(
  ontologyId: string,
  query: string,
  saveAs?: string
): Promise<SparqlResult> {
  const body: Record<string, string> = { query }
  if (saveAs) body.saveAs = saveAs
  return request<SparqlResult>(
    `/ontologies/${ontologyId}/sparql`,
    { method: "POST", body: JSON.stringify(body) }
  )
}

// ============================================================
// Query History
// ============================================================

/**
 * Get SPARQL query history for an ontology
 */
export async function getQueryHistory(
  ontologyId: string,
  limit = 50
): Promise<QueryHistoryItem[]> {
  return request<QueryHistoryItem[]>(
    `/ontologies/${ontologyId}/sparql/history?limit=${limit}`
  )
}

// ============================================================
// Saved Queries
// ============================================================

/**
 * Save a SPARQL query
 */
export async function saveQuery(
  ontologyId: string,
  name: string,
  query: string,
  description?: string
): Promise<SavedQuery> {
  return request<SavedQuery>(
    `/ontologies/${ontologyId}/sparql/saved`,
    {
      method: "POST",
      body: JSON.stringify({ name, query, description }),
    }
  )
}

/**
 * Get all saved queries for an ontology
 */
export async function getSavedQueries(
  ontologyId: string
): Promise<SavedQuery[]> {
  return request<SavedQuery[]>(
    `/ontologies/${ontologyId}/sparql/saved`
  )
}

/**
 * Get a single saved query by ID
 */
export async function getSavedQuery(
  ontologyId: string,
  queryId: string
): Promise<SavedQuery> {
  return request<SavedQuery>(
    `/ontologies/${ontologyId}/sparql/saved/${queryId}`
  )
}

/**
 * Update a saved query
 */
export async function updateSavedQuery(
  ontologyId: string,
  queryId: string,
  updates: { name?: string; query?: string; description?: string }
): Promise<SavedQuery> {
  return request<SavedQuery>(
    `/ontologies/${ontologyId}/sparql/saved/${queryId}`,
    { method: "PUT", body: JSON.stringify(updates) }
  )
}

/**
 * Delete a saved query
 */
export async function deleteSavedQuery(
  ontologyId: string,
  queryId: string
): Promise<void> {
  return request<void>(
    `/ontologies/${ontologyId}/sparql/saved/${queryId}`,
    { method: "DELETE" }
  )
}

// ============================================================
// NL → SPARQL
// ============================================================

/**
 * Convert natural language to SPARQL (simplified / LLM in production)
 */
export async function nlToSparql(
  ontologyId: string,
  text: string
): Promise<NlQueryResult> {
  return request<NlQueryResult>(
    `/ontologies/${ontologyId}/nl-query`,
    { method: "POST", body: JSON.stringify({ text }) }
  )
}
