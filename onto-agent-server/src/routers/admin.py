"""
Admin 路由

系统管理接口：健康检查、备份、压缩、统计
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any

import httpx
from src.database import SystemSession, create_session_maker, BUSINESS_DB_URL, BusinessSession
from src.services.jena import get_jena_client
from src.services.jena.jena_base import get_fuseki_settings, JENA_DEFAULT_HOST, JENA_DEFAULT_PORT
from src.models.ontology import Ontology
from src.models.sync_models import SyncTask
from sqlalchemy import select, func
from src.logging_config import get_logger

router = APIRouter(prefix="/api/admin", tags=["admin"])
logger = get_logger("admin")


class HealthResponse(BaseModel):
    status: str
    fuseki: dict[str, Any]
    system_db: dict[str, Any]
    business_db: dict[str, Any]
    tables: dict[str, str]


class StatsResponse(BaseModel):
    ontologies: int
    total_classes: int
    total_properties: int
    total_individuals: int
    sync_tasks_by_status: dict[str, int]
    disk_usage_estimate: str


class BackupResponse(BaseModel):
    success: bool
    message: str
    backup_path: str | None = None


# ==================== Health Check ====================

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    系统健康检查

    - Jena Fuseki 存活检查
    - System DB 连接检查
    - Business DB 连接检查
    - 关键表存在性检查
    """
    result: dict[str, Any] = {
        "status": "healthy",
        "fuseki": {"status": "unknown"},
        "system_db": {"status": "unknown"},
        "business_db": {"status": "unknown"},
        "tables": {},
    }

    # Fuseki check
    try:
        settings = get_fuseki_settings()
        fuseki_url = settings["fuseki_url"]
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.get(f"{fuseki_url}/$/ping")
            if r.status_code == 200:
                result["fuseki"] = {"status": "ok", "url": fuseki_url}
            else:
                result["fuseki"] = {"status": "error", "code": r.status_code}
                result["status"] = "degraded"
    except Exception as e:
        result["fuseki"] = {"status": "error", "message": str(e)}
        result["status"] = "degraded"

    # System DB check
    try:
        async with SystemSession() as session:
            await session.execute(select(func.count()).select_from(Ontology))
            result["system_db"] = {"status": "ok"}

            # Check critical tables via raw SQL
            tables_to_check = [
                "ontologies",
                "entity_index",
                "ontology_versions",
                "datasources",
                "property_sources",
                "sync_tasks",
                "query_history",
                "saved_queries",
            ]
            for tbl in tables_to_check:
                try:
                    from sqlalchemy import text
                    await session.execute(text(f'SELECT 1 FROM {tbl} LIMIT 1'))
                    result["tables"][tbl] = "ok"
                except Exception:
                    result["tables"][tbl] = "missing"
    except Exception as e:
        result["system_db"] = {"status": "error", "message": str(e)}
        result["status"] = "unhealthy"

    # Business DB check
    try:
        async with BusinessSession() as session:
            from sqlalchemy import text
            await session.execute(text("SELECT 1"))
            result["business_db"] = {"status": "ok"}
    except Exception as e:
        result["business_db"] = {"status": "error", "message": str(e)}

    return result


# ==================== Backup ====================

@router.post("/backup", response_model=BackupResponse)
async def create_backup():
    """
    备份系统数据

    - 导出 Jena Fuseki 数据集（Turtle）
    - 导出 System DB（pg_dump 格式说明）
    """
    import os
    import uuid
    from datetime import datetime

    backup_id = uuid.uuid4().hex[:8]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = "/tmp/onto-agent-backups"
    os.makedirs(backup_dir, exist_ok=True)

    # 1. Export Jena dataset to Turtle
    try:
        settings = get_fuseki_settings()
        fuseki_url = settings["fuseki_url"]
        username = settings["username"]
        password = settings["password"]
        turtle_file = f"{backup_dir}/fuseki_{timestamp}_{backup_id}.ttl"

        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.get(
                f"{fuseki_url}/onto-agent/data",
                headers={"Accept": "application/turtle"},
                auth=httpx.BasicAuth(username, password),
            )
            if r.status_code == 200:
                with open(turtle_file, "wb") as f:
                    f.write(r.content)
                fuseki_backup_size = len(r.content)
            else:
                return BackupResponse(
                    success=False,
                    message=f"Fuseki export failed: {r.status_code} {r.text[:200]}",
                    backup_path=None,
                )

        return BackupResponse(
            success=True,
            message=f"Backup created successfully. Fuseki export: {fuseki_backup_size} bytes",
            backup_path=backup_dir,
        )
    except Exception as e:
        logger.error(f"Backup failed: {e}")
        raise HTTPException(status_code=500, detail=f"Backup failed: {str(e)}")


# ==================== Compact ====================

@router.post("/compact")
async def compact_fuseki():
    """
    压缩 Fuseki 数据集

    执行 Fuseki REPEATABLE-READ + compact 操作，减少磁盘占用
    """
    try:
        settings = get_fuseki_settings()
        fuseki_url = settings["fuseki_url"]
        username = settings["username"]
        password = settings["password"]
        auth = httpx.BasicAuth(username, password)

        async with httpx.AsyncClient(timeout=120) as client:
            # Compact (直接压缩，不需要先设置事务模式)
            r = await client.post(
                f"{fuseki_url}/$/compact/onto-agent",
                auth=auth,
            )
            if r.status_code in (200, 201, 204):
                return {"success": True, "message": "Fuseki compaction started/completed"}
            else:
                return {"success": False, "message": f"Compact failed: {r.status_code} {r.text}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Compact failed: {str(e)}")


# ==================== Stats ====================

@router.get("/stats", response_model=StatsResponse)
async def get_stats():
    """
    系统统计信息

    - 本体数量
    - TBox 实体数量（Classes / Properties）
    - ABox 实例数量
    - 同步任务状态分布
    """
    try:
        async with SystemSession() as session:
            # Ontology count
            ont_count = await session.scalar(select(func.count()).select_from(Ontology))

            # Entity counts
            from src.models.ontology import EntityIndex
            class_count = await session.scalar(
                select(func.count()).select_from(EntityIndex).where(EntityIndex.entity_type == "class")
            )
            prop_count = await session.scalar(
                select(func.count()).select_from(EntityIndex).where(
                    EntityIndex.entity_type.in_(["datatype_property", "object_property"])
                )
            )
            ind_count = await session.scalar(
                select(func.count()).select_from(EntityIndex).where(EntityIndex.entity_type == "individual")
            )

            # Sync tasks by status
            status_counts = {}
            for status in ["pending", "running", "completed", "failed"]:
                cnt = await session.scalar(
                    select(func.count()).select_from(SyncTask).where(SyncTask.status == status)
                )
                status_counts[status] = cnt or 0

            return StatsResponse(
                ontologies=ont_count or 0,
                total_classes=class_count or 0,
                total_properties=prop_count or 0,
                total_individuals=ind_count or 0,
                sync_tasks_by_status=status_counts,
                disk_usage_estimate="N/A",
            )
    except Exception as e:
        logger.error(f"Stats failed: {e}")
        raise HTTPException(status_code=500, detail=f"Stats failed: {str(e)}")
