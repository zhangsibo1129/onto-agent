from typing import Union, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from src.database import get_system_db as get_db
from src.models.datasource import Datasource
from src.schemas.datasource import (
    DatasourceCreate,
    DatasourceUpdate,
    DatasourceResponse,
    TableInfo,
    ColumnInfo,
    TestResult,
    TestConnectionRequest,
)
from src.services import datasource as datasource_service

router = APIRouter(prefix="/datasources", tags=["datasources"])


def datasource_to_dict(ds: Datasource) -> dict:
    return {
        "id": ds.id,
        "name": ds.name,
        "type": ds.type,
        "status": ds.status,
        "tableCount": ds.table_count,
        "host": ds.host,
        "port": ds.port,
        "database": ds.database,
        "schema": ds.schema,
        "username": ds.username,
        "sslMode": ds.ssl_mode,
        "description": ds.description,
        "lastSyncAt": ds.last_sync_at.isoformat() if ds.last_sync_at else None,
        "createdAt": ds.created_at.isoformat(),
        "updatedAt": ds.updated_at.isoformat(),
    }


def success_response(data):
    return {"success": True, "data": data}


@router.get("")
async def list_datasources(db: AsyncSession = Depends(get_db)) -> dict:
    result = await db.execute(select(Datasource).order_by(Datasource.created_at.desc()))
    datasources = result.scalars().all()
    return success_response([datasource_to_dict(ds) for ds in datasources])


@router.get("/{datasource_id}")
async def get_datasource(
    datasource_id: str, db: AsyncSession = Depends(get_db)
) -> dict:
    result = await db.execute(select(Datasource).where(Datasource.id == datasource_id))
    datasource = result.scalar_one_or_none()
    if not datasource:
        raise HTTPException(status_code=404, detail="Datasource not found")
    return success_response(datasource_to_dict(datasource))


@router.post("")
async def create_datasource(
    data: DatasourceCreate, db: AsyncSession = Depends(get_db)
) -> dict:
    dump = data.model_dump()
    datasource = Datasource(
        name=dump["name"],
        type=dump["type"],
        host=dump.get("host"),
        port=dump.get("port"),
        database=dump.get("database"),
        schema=dump.get("db_schema"),
        username=dump.get("username"),
        password=dump.get("password"),
        ssl_mode=dump.get("ssl_mode"),
        description=dump.get("description"),
        status="disconnected",
        table_count=0,
    )
    db.add(datasource)
    await db.commit()
    await db.refresh(datasource)
    return success_response(datasource_to_dict(datasource))


@router.post("/test-connection")
async def test_connection_before_save(data: TestConnectionRequest) -> dict:
    dump = data.model_dump()
    if dump.get("type") == "postgresql":
        test_result = await datasource_service.test_postgres_connection(
            host=dump.get("host") or "localhost",
            port=dump.get("port") or 5432,
            database=dump.get("database") or "",
            user=dump.get("username") or "",
            password=dump.get("password") or "",
            schema=dump.get("db_schema") or "public",
        )
        return success_response(test_result)
    return success_response(
        {"connected": False, "error": f"Unsupported database type: {dump.get('type')}"}
    )


@router.put("/{datasource_id}")
async def update_datasource(
    datasource_id: str, data: DatasourceUpdate, db: AsyncSession = Depends(get_db)
) -> dict:
    result = await db.execute(select(Datasource).where(Datasource.id == datasource_id))
    datasource = result.scalar_one_or_none()
    if not datasource:
        raise HTTPException(status_code=404, detail="Datasource not found")

    dump = data.model_dump(exclude_unset=True)
    for key, value in dump.items():
        if key == "db_schema":
            setattr(datasource, "schema", value)
        else:
            setattr(datasource, key, value)

    await db.commit()
    await db.refresh(datasource)
    return success_response(datasource_to_dict(datasource))


@router.delete("/{datasource_id}")
async def delete_datasource(
    datasource_id: str, db: AsyncSession = Depends(get_db)
) -> dict:
    result = await db.execute(select(Datasource).where(Datasource.id == datasource_id))
    datasource = result.scalar_one_or_none()
    if not datasource:
        raise HTTPException(status_code=404, detail="Datasource not found")
    await db.execute(delete(Datasource).where(Datasource.id == datasource_id))
    await db.commit()
    return success_response(None)


@router.post("/{datasource_id}/test")
async def test_connection(
    datasource_id: str, db: AsyncSession = Depends(get_db)
) -> dict:
    result = await db.execute(select(Datasource).where(Datasource.id == datasource_id))
    datasource = result.scalar_one_or_none()
    if not datasource:
        raise HTTPException(status_code=404, detail="Datasource not found")

    test_result = await datasource_service.test_postgres_connection(
        host=datasource.host or "localhost",
        port=datasource.port or 5432,
        database=datasource.database or "",
        user=datasource.username or "",
        password=datasource.password or "",
        schema=datasource.schema or "public",
    )

    if test_result["connected"]:
        datasource.status = "connected"
        datasource.table_count = test_result.get("table_count") or 0
        datasource.last_sync_at = datetime.utcnow()
    else:
        datasource.status = "error"
    await db.commit()
    return success_response(test_result)


@router.post("/{datasource_id}/scan")
async def scan_datasource(
    datasource_id: str, db: AsyncSession = Depends(get_db)
) -> dict:
    result = await db.execute(select(Datasource).where(Datasource.id == datasource_id))
    datasource = result.scalar_one_or_none()
    if not datasource:
        raise HTTPException(status_code=404, detail="Datasource not found")

    try:
        tables = await datasource_service.get_postgres_tables(
            host=datasource.host or "localhost",
            port=datasource.port or 5432,
            database=datasource.database or "",
            user=datasource.username or "",
            password=datasource.password or "",
            schema=datasource.schema or "public",
        )

        datasource.last_sync_at = datetime.utcnow()
        datasource.table_count = len(tables)
        await db.commit()

        now = datetime.now(timezone.utc)
        return success_response(
            {
                "status": "completed",
                "tables": [t.model_dump() for t in tables],
                "scannedAt": now.isoformat(),
            }
        )
    except Exception as e:
        datasource.status = "error"
        await db.commit()
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")


@router.get("/{datasource_id}/tables")
async def get_tables(datasource_id: str, db: AsyncSession = Depends(get_db)) -> dict:
    result = await db.execute(select(Datasource).where(Datasource.id == datasource_id))
    datasource = result.scalar_one_or_none()
    if not datasource:
        raise HTTPException(status_code=404, detail="Datasource not found")

    try:
        tables = await datasource_service.get_postgres_tables(
            host=datasource.host or "localhost",
            port=datasource.port or 5432,
            database=datasource.database or "",
            user=datasource.username or "",
            password=datasource.password or "",
            schema=datasource.schema or "public",
        )

        datasource.last_sync_at = datetime.utcnow()
        datasource.table_count = len(tables)
        await db.commit()

        return success_response(
            {
                "tables": [t.model_dump() for t in tables],
                "scannedAt": datetime.utcnow().isoformat(),
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get tables: {str(e)}")


@router.get("/{datasource_id}/tables/{table_name}/columns")
async def get_columns(
    datasource_id: str, table_name: str, db: AsyncSession = Depends(get_db)
) -> dict:
    result = await db.execute(select(Datasource).where(Datasource.id == datasource_id))
    datasource = result.scalar_one_or_none()
    if not datasource:
        raise HTTPException(status_code=404, detail="Datasource not found")

    try:
        columns = await datasource_service.get_postgres_columns(
            host=datasource.host or "localhost",
            port=datasource.port or 5432,
            database=datasource.database or "",
            user=datasource.username or "",
            password=datasource.password or "",
            table_name=table_name,
            schema=datasource.schema or "public",
        )

        return success_response(
            {
                "tableName": table_name,
                "columns": [c.model_dump() for c in columns],
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get columns: {str(e)}")
