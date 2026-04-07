from typing import Union, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from src.database import get_db
from src.models.datasource import Datasource
from src.schemas.datasource import (
    DatasourceCreate,
    DatasourceUpdate,
    DatasourceResponse,
    TableInfo,
    ColumnInfo,
    TestResult,
    ApiResponse,
    TestConnectionRequest,
)
from src.services import datasource as datasource_service

router = APIRouter(prefix="/datasources", tags=["datasources"])


def success_response(data: Union[dict, list]) -> dict:
    return {"success": True, "data": data}


def error_response(code: str, message: str) -> dict:
    return {"success": False, "error": {"code": code, "message": message}}


@router.get("")
async def list_datasources(db: AsyncSession = Depends(get_db)) -> dict:
    result = await db.execute(select(Datasource).order_by(Datasource.created_at.desc()))
    datasources = result.scalars().all()

    return success_response(
        [
            {
                "id": ds.id,
                "name": ds.name,
                "type": ds.type,
                "host": ds.host,
                "port": ds.port,
                "database": ds.database,
                "schema": ds.schema,
                "username": ds.username,
                "password": ds.password,
                "ssl_mode": ds.ssl_mode,
                "status": ds.status,
                "table_count": ds.table_count,
                "last_sync_at": ds.last_sync_at.isoformat()
                if ds.last_sync_at
                else None,
                "created_at": ds.created_at.isoformat(),
                "updated_at": ds.updated_at.isoformat(),
            }
            for ds in datasources
        ]
    )


@router.get("/{datasource_id}")
async def get_datasource(
    datasource_id: str, db: AsyncSession = Depends(get_db)
) -> dict:
    result = await db.execute(select(Datasource).where(Datasource.id == datasource_id))
    datasource = result.scalar_one_or_none()

    if not datasource:
        raise HTTPException(status_code=404, detail="Datasource not found")

    return success_response(
        {
            "id": datasource.id,
            "name": datasource.name,
            "type": datasource.type,
            "host": datasource.host,
            "port": datasource.port,
            "database": datasource.database,
            "schema": datasource.schema,
            "username": datasource.username,
            "password": datasource.password,
            "ssl_mode": datasource.ssl_mode,
            "status": datasource.status,
            "table_count": datasource.table_count,
            "last_sync_at": datasource.last_sync_at.isoformat()
            if datasource.last_sync_at
            else None,
            "created_at": datasource.created_at.isoformat(),
            "updated_at": datasource.updated_at.isoformat(),
        }
    )


@router.post("")
async def create_datasource(
    data: DatasourceCreate, db: AsyncSession = Depends(get_db)
) -> dict:
    create_data = data.model_dump(by_alias=True)
    datasource = Datasource(
        name=create_data.get("name"),
        type=create_data.get("type"),
        host=create_data.get("host"),
        port=create_data.get("port"),
        database=create_data.get("database"),
        schema=create_data.get("db_schema"),
        username=create_data.get("username"),
        password=create_data.get("password"),
        ssl_mode=create_data.get("ssl_mode"),
        status="disconnected",
        table_count=0,
    )

    db.add(datasource)
    await db.commit()
    await db.refresh(datasource)

    return success_response(
        {
            "id": datasource.id,
            "name": datasource.name,
            "type": datasource.type,
            "host": datasource.host,
            "port": datasource.port,
            "database": datasource.database,
            "schema": datasource.schema,
            "username": datasource.username,
            "password": datasource.password,
            "ssl_mode": datasource.ssl_mode,
            "status": datasource.status,
            "table_count": datasource.table_count,
            "last_sync_at": None,
            "created_at": datasource.created_at.isoformat(),
            "updated_at": datasource.updated_at.isoformat(),
        }
    )


@router.post("/test-connection")
async def test_connection_before_save(data: TestConnectionRequest) -> dict:
    test_data = data.model_dump(by_alias=True)

    if test_data.get("type") == "postgresql":
        test_result = await datasource_service.test_postgres_connection(
            host=test_data.get("host") or "localhost",
            port=test_data.get("port") or 5432,
            database=test_data.get("database") or "",
            user=test_data.get("username") or "",
            password=test_data.get("password") or "",
            schema=test_data.get("db_schema") or "public",
        )
    else:
        test_result = {
            "connected": False,
            "error": f"Unsupported database type: {test_data.get('type')}",
        }

    return success_response(test_result)


@router.put("/{datasource_id}")
async def update_datasource(
    datasource_id: str, data: DatasourceUpdate, db: AsyncSession = Depends(get_db)
) -> dict:
    result = await db.execute(select(Datasource).where(Datasource.id == datasource_id))
    datasource = result.scalar_one_or_none()

    if not datasource:
        raise HTTPException(status_code=404, detail="Datasource not found")

    update_data = data.model_dump(exclude_unset=True, by_alias=True)
    for key, value in update_data.items():
        if key == "db_schema":
            setattr(datasource, "schema", value)
        else:
            setattr(datasource, key, value)

    await db.commit()
    await db.refresh(datasource)

    return success_response(
        {
            "id": datasource.id,
            "name": datasource.name,
            "type": datasource.type,
            "host": datasource.host,
            "port": datasource.port,
            "database": datasource.database,
            "schema": datasource.schema,
            "username": datasource.username,
            "password": datasource.password,
            "ssl_mode": datasource.ssl_mode,
            "status": datasource.status,
            "table_count": datasource.table_count,
            "last_sync_at": datasource.last_sync_at.isoformat()
            if datasource.last_sync_at
            else None,
            "created_at": datasource.created_at.isoformat(),
            "updated_at": datasource.updated_at.isoformat(),
        }
    )


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
        datasource.table_count = test_result["table_count"]
        datasource.last_sync_at = datetime.utcnow()
        await db.commit()
    else:
        datasource.status = "error"
        await db.commit()

    return success_response(test_result)


@router.get("/{datasource_id}/tables")
async def get_tables(datasource_id: str, db: AsyncSession = Depends(get_db)) -> dict:
    result = await db.execute(select(Datasource).where(Datasource.id == datasource_id))
    datasource = result.scalar_one_or_none()

    if not datasource:
        raise HTTPException(status_code=404, detail="Datasource not found")

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
            "scanned_at": datetime.utcnow().isoformat(),
        }
    )


@router.get("/{datasource_id}/tables/{table_name}/columns")
async def get_columns(
    datasource_id: str, table_name: str, db: AsyncSession = Depends(get_db)
) -> dict:
    result = await db.execute(select(Datasource).where(Datasource.id == datasource_id))
    datasource = result.scalar_one_or_none()

    if not datasource:
        raise HTTPException(status_code=404, detail="Datasource not found")

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
            "table_name": table_name,
            "columns": [c.model_dump() for c in columns],
        }
    )
