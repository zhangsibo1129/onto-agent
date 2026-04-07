import asyncpg
from typing import Optional
from src.schemas.datasource import TableInfo, ColumnInfo


async def create_connection(
    host: str, port: int, database: str, user: str, password: str
):
    return await asyncpg.connect(
        host=host,
        port=port,
        database=database,
        user=user,
        password=password,
    )


async def test_postgres_connection(
    host: str,
    port: int,
    database: str,
    user: str,
    password: str,
    schema: str = "public",
) -> dict:
    conn = None
    try:
        conn = await create_connection(host, port, database, user, password)

        version_result = await conn.fetchval("SELECT version()")
        version = version_result.split(" ")[0] if version_result else ""

        tables_query = """
            SELECT
                t.table_name,
                (SELECT COUNT(*) FROM information_schema.columns c 
                 WHERE c.table_name = t.table_name AND c.table_schema = t.table_schema) as columns,
                COALESCE((SELECT reltuples::bigint FROM pg_class WHERE relname = t.table_name), 0) as row_count
            FROM information_schema.tables t
            WHERE t.table_schema = $1 AND t.table_type = 'BASE TABLE'
            ORDER BY t.table_name
        """
        tables = await conn.fetch(tables_query, schema)

        table_count = len(tables)

        return {
            "connected": True,
            "version": version,
            "table_count": table_count,
            "latency": "N/A",
        }
    except Exception as e:
        return {"connected": False, "error": str(e)}
    finally:
        if conn:
            await conn.close()


async def get_postgres_tables(
    host: str,
    port: int,
    database: str,
    user: str,
    password: str,
    schema: str = "public",
) -> list[TableInfo]:
    conn = None
    try:
        conn = await create_connection(host, port, database, user, password)

        tables_query = """
            SELECT
                t.table_name,
                (SELECT COUNT(*) FROM information_schema.columns c 
                 WHERE c.table_name = t.table_name AND c.table_schema = t.table_schema) as columns,
                COALESCE((SELECT reltuples::bigint FROM pg_class WHERE relname = t.table_name), 0) as row_count
            FROM information_schema.tables t
            WHERE t.table_schema = $1 AND t.table_type = 'BASE TABLE'
            ORDER BY t.table_name
        """
        rows = await conn.fetch(tables_query, schema)

        return [
            TableInfo(
                name=row["table_name"],
                columns=row["columns"],
                row_count=row["row_count"],
            )
            for row in rows
        ]
    finally:
        if conn:
            await conn.close()


async def get_postgres_columns(
    host: str,
    port: int,
    database: str,
    user: str,
    password: str,
    table_name: str,
    schema: str = "public",
) -> list[ColumnInfo]:
    conn = None
    try:
        conn = await create_connection(host, port, database, user, password)

        columns_query = """
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
        """

        rows = await conn.fetch(columns_query, schema, table_name)

        return [
            ColumnInfo(
                name=row["column_name"],
                type=row["data_type"],
                nullable=row["is_nullable"] == "YES",
                primary_key=row["is_primary_key"],
                default_value=str(row["column_default"])
                if row["column_default"]
                else None,
            )
            for row in rows
        ]
    finally:
        if conn:
            await conn.close()
