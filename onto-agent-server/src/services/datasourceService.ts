import { AppDataSource } from "../index"
import { Datasource, DatasourceType, DatasourceStatus } from "../entities/Datasource"
import { v4 as uuidv4 } from "uuid"
import { Pool } from "pg"

export interface CreateDatasourceDto {
  name: string
  type: DatasourceType
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
  type?: DatasourceType
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

const datasourceRepository = () => AppDataSource.getRepository(Datasource)

async function createExternalPool(datasource: Datasource): Promise<Pool> {
  const pool = new Pool({
    host: datasource.host || undefined,
    port: datasource.port || 5432,
    user: datasource.username || undefined,
    password: datasource.password || undefined,
    database: datasource.database || undefined,
    max: 5,
    idleTimeoutMillis: 30000,
  })
  return pool
}

async function fetchPostgresTableMetadata(pool: Pool, schema: string): Promise<TableInfo[]> {
  const query = `
    SELECT
      t.table_name,
      (SELECT COUNT(*) FROM information_schema.columns c WHERE c.table_name = t.table_name AND c.table_schema = t.table_schema) as columns,
      (SELECT reltuples::bigint FROM pg_class WHERE relname = t.table_name) as row_count
    FROM information_schema.tables t
    WHERE t.table_schema = $1 AND t.table_type = 'BASE TABLE'
    ORDER BY t.table_name
  `
  const result = await pool.query(query, [schema || "public"])

  return result.rows.map((row) => ({
    name: row.table_name,
    columns: parseInt(row.columns) || 0,
    rowCount: parseInt(row.row_count) || 0,
  }))
}

async function fetchPostgresColumns(pool: Pool, schema: string, tableName: string): Promise<ColumnInfo[]> {
  const query = `
    SELECT 
      c.column_name, 
      c.data_type, 
      c.is_nullable, 
      c.column_default,
      CASE WHEN pk.column_name IS NOT NULL THEN true ELSE false END as is_primary_key
    FROM information_schema.columns c
    LEFT JOIN (
      SELECT ku.column_name
      FROM information_schema.table_constraints tc
      JOIN information_schema.key_column_usage ku ON tc.constraint_name = ku.constraint_name
      WHERE tc.constraint_type = 'PRIMARY KEY'
        AND tc.table_schema = $1
        AND tc.table_name = $2
    ) pk ON c.column_name = pk.column_name
    WHERE c.table_schema = $1 AND c.table_name = $2
    ORDER BY c.ordinal_position
  `
  
  const result = await pool.query(query, [schema || "public", tableName])

  return result.rows.map((row) => ({
    name: row.column_name,
    type: row.data_type,
    nullable: row.is_nullable === "YES",
    primaryKey: row.is_primary_key === true,
    defaultValue: row.column_default,
  }))
}

export const datasourceService = {
  async findAll(): Promise<Datasource[]> {
    return datasourceRepository().find({
      order: { createdAt: "DESC" },
    })
  },

  async findById(id: string): Promise<Datasource | null> {
    return datasourceRepository().findOne({ where: { id } })
  },

  async create(dto: CreateDatasourceDto): Promise<Datasource> {
    const datasource = new Datasource()
    datasource.id = uuidv4()
    datasource.name = dto.name
    datasource.type = dto.type
    datasource.host = dto.host || null
    datasource.port = dto.port || null
    datasource.database = dto.database || null
    datasource.schema = dto.schema || null
    datasource.username = dto.username || null
    datasource.password = dto.password || null
    datasource.sslMode = dto.sslMode || null
    datasource.status = DatasourceStatus.DISCONNECTED
    datasource.tableCount = 0
    return datasourceRepository().save(datasource)
  },

  async update(id: string, dto: UpdateDatasourceDto): Promise<Datasource | null> {
    const datasource = await this.findById(id)
    if (!datasource) return null

    if (dto.name !== undefined) datasource.name = dto.name
    if (dto.type !== undefined) datasource.type = dto.type
    if (dto.host !== undefined) datasource.host = dto.host
    if (dto.port !== undefined) datasource.port = dto.port
    if (dto.database !== undefined) datasource.database = dto.database
    if (dto.schema !== undefined) datasource.schema = dto.schema
    if (dto.username !== undefined) datasource.username = dto.username
    if (dto.password !== undefined) datasource.password = dto.password
    if (dto.sslMode !== undefined) datasource.sslMode = dto.sslMode

    return datasourceRepository().save(datasource)
  },

  async delete(id: string): Promise<boolean> {
    const result = await datasourceRepository().delete(id)
    return (result.affected ?? 0) > 0
  },

  async testConnection(id: string): Promise<{ connected: boolean; latency?: string; version?: string; tableCount?: number; error?: string }> {
    const datasource = await this.findById(id)
    if (!datasource) {
      return { connected: false, error: "Datasource not found" }
    }

    let pool: Pool | null = null
    const start = Date.now()

    try {
      pool = await createExternalPool(datasource)
      const client = await pool.connect()

      try {
        let version = ""
        let tableCount = 0

        if (datasource.type === DatasourceType.POSTGRESQL) {
          const versionResult = await client.query("SELECT version()")
          version = versionResult.rows[0]?.version?.split(" ")[0] || ""
          
          const tables = await fetchPostgresTableMetadata(pool, datasource.schema || "public")
          tableCount = tables.length
        } else {
          throw new Error(`Unsupported datasource type: ${datasource.type}`)
        }

        const latency = `${Date.now() - start}ms`

        datasource.status = DatasourceStatus.CONNECTED
        datasource.tableCount = tableCount
        datasource.lastSyncAt = new Date()
        await datasourceRepository().save(datasource)

        return { connected: true, latency, version, tableCount }
      } finally {
        client.release()
      }
    } catch (error: any) {
      datasource.status = DatasourceStatus.ERROR
      await datasourceRepository().save(datasource)

      return { connected: false, error: error.message }
    } finally {
      if (pool) {
        await pool.end()
      }
    }
  },

  async getTables(datasource: Datasource): Promise<TableInfo[]> {
    let pool: Pool | null = null

    try {
      pool = await createExternalPool(datasource)
      const client = await pool.connect()

      try {
        let tables: TableInfo[] = []
        
        if (datasource.type === DatasourceType.POSTGRESQL) {
          tables = await fetchPostgresTableMetadata(pool, datasource.schema || "public")
        } else {
          throw new Error(`Unsupported datasource type: ${datasource.type}`)
        }

        datasource.status = DatasourceStatus.CONNECTED
        datasource.tableCount = tables.length
        datasource.lastSyncAt = new Date()
        await datasourceRepository().save(datasource)

        return tables
      } finally {
        client.release()
      }
    } catch (error) {
      throw error
    } finally {
      if (pool) {
        await pool.end()
      }
    }
  },

  async getColumns(datasource: Datasource, tableName: string): Promise<ColumnInfo[]> {
    let pool: Pool | null = null

    try {
      pool = await createExternalPool(datasource)
      const client = await pool.connect()

      try {
        let columns: ColumnInfo[] = []
        
        if (datasource.type === DatasourceType.POSTGRESQL) {
          columns = await fetchPostgresColumns(pool, datasource.schema || "public", tableName)
        } else {
          throw new Error(`Unsupported datasource type: ${datasource.type}`)
        }

        return columns
      } finally {
        client.release()
      }
    } catch (error) {
      throw error
    } finally {
      if (pool) {
        await pool.end()
      }
    }
  },
}
