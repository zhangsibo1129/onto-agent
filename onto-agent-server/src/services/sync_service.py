"""
Phase 5: 同步服务
管理同步任务的生命周期
"""
import asyncio
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import text

from src.database import SystemSession
from src.services.etl_engine import ETLEngine
from src.logging_config import get_logger

logger = get_logger("sync_service")


# ============================================================
# 任务管理
# ============================================================

async def create_sync_task(ontology_id: str, mode: str = "full") -> dict:
    """创建同步任务记录"""
    task_id = str(uuid.uuid4())
    async with SystemSession() as session:
        await session.execute(
            text("""
                INSERT INTO sync_tasks (id, ontology_id, mode, status, created_at)
                VALUES (:id, :ontology_id, :mode, 'pending', :now)
            """),
            {"id": task_id, "ontology_id": ontology_id, "mode": mode, "now": datetime.now()}
        )
        await session.commit()
    
    return {"id": task_id, "status": "pending"}


async def get_sync_tasks(ontology_id: str) -> list[dict]:
    """获取本体的所有同步任务"""
    async with SystemSession() as session:
        result = await session.execute(
            text("""
                SELECT id, ontology_id, mode, status, progress, processed, total,
                       error_message, started_at, finished_at, created_at
                FROM sync_tasks
                WHERE ontology_id = :ontology_id
                ORDER BY created_at DESC
            """),
            {"ontology_id": ontology_id}
        )
        return [dict(r._mapping) for r in result.fetchall()]


async def get_sync_task(task_id: str) -> Optional[dict]:
    """获取单个任务"""
    async with SystemSession() as session:
        result = await session.execute(
            text("SELECT * FROM sync_tasks WHERE id = :id"),
            {"id": task_id}
        )
        row = result.fetchone()
        return dict(row._mapping) if row else None


async def get_sync_logs(task_id: str) -> list[dict]:
    """获取任务日志"""
    async with SystemSession() as session:
        result = await session.execute(
            text("""
                SELECT id, task_id, level, message, created_at
                FROM sync_logs
                WHERE task_id = :task_id
                ORDER BY created_at ASC
            """),
            {"task_id": task_id}
        )
        return [dict(r._mapping) for r in result.fetchall()]


async def update_task_status(
    task_id: str,
    status: str,
    progress: int = None,
    processed: int = None,
    total: int = None,
    error_message: str = None
):
    """更新任务状态"""
    async with SystemSession() as session:
        updates = ["status = :status"]
        params = {"id": task_id, "status": status}
        
        if status == "running" and progress is not None:
            updates.append("started_at = :started_at")
            params["started_at"] = datetime.now()
        
        if status in ("success", "error", "cancelled"):
            updates.append("finished_at = :finished_at")
            params["finished_at"] = datetime.now()
        
        if progress is not None:
            updates.append("progress = :progress")
            params["progress"] = progress
        
        if processed is not None:
            updates.append("processed = :processed")
            params["processed"] = processed
        
        if total is not None:
            updates.append("total = :total")
            params["total"] = total
        
        if error_message is not None:
            updates.append("error_message = :error_message")
            params["error_message"] = error_message

        await session.execute(
            text(f"UPDATE sync_tasks SET {', '.join(updates)} WHERE id = :id"),
            params
        )
        await session.commit()


async def add_sync_log(task_id: str, level: str, message: str):
    """添加任务日志"""
    log_id = str(uuid.uuid4())
    async with SystemSession() as session:
        await session.execute(
            text("""
                INSERT INTO sync_logs (id, task_id, level, message, created_at)
                VALUES (:id, :task_id, :level, :message, :now)
            """),
            {"id": log_id, "task_id": task_id, "level": level, "message": message, "now": datetime.now()}
        )
        await session.commit()


async def delete_sync_task(task_id: str) -> bool:
    """删除任务"""
    async with SystemSession() as session:
        await session.execute(
            text("DELETE FROM sync_tasks WHERE id = :id"),
            {"id": task_id}
        )
        await session.commit()
    return True


# ============================================================
# ETL 执行（异步后台）
# ============================================================

async def execute_sync_task(task_id: str, ontology_id: str):
    """
    执行同步任务（后台运行）
    """
    logger.info(f"Starting sync task {task_id} for ontology {ontology_id}")
    
    # 更新状态为 running
    await update_task_status(task_id, "running", progress=0, processed=0, total=0)

    try:
        engine = ETLEngine(ontology_id)
        success, logs = await engine.execute()

        if success:
            await update_task_status(task_id, "success", progress=100)
            for level, msg in logs:
                await add_sync_log(task_id, level, msg)
        else:
            error_msg = next((msg for l, msg in logs if l == "error"), "Unknown error")
            await update_task_status(task_id, "error", error_message=error_msg)
            for level, msg in logs:
                await add_sync_log(task_id, level, msg)

    except Exception as e:
        import traceback
        logger.error(f"Sync task {task_id} failed: {e}\n{traceback.format_exc()}")
        await update_task_status(task_id, "error", error_message=str(e))
        await add_sync_log(task_id, "error", f"任务执行异常: {e}")


async def trigger_sync(ontology_id: str, mode: str = "full") -> dict:
    """
    触发同步任务
    创建任务记录，立即返回，后台异步执行
    """
    # 1. 创建任务记录
    task = await create_sync_task(ontology_id, mode)
    task_id = task["id"]

    # 2. 立即返回，不等待完成
    asyncio.create_task(execute_sync_task(task_id, ontology_id))

    return {"task_id": task_id, "status": "pending"}
