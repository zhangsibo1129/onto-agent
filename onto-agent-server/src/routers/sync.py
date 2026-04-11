"""
Phase 5: 同步管理路由
GET  /api/ontologies/{id}/sync/tasks           → 列表
POST /api/ontologies/{id}/sync/tasks           → 触发同步
GET  /api/ontologies/{id}/sync/tasks/{tid}    → 任务详情
GET  /api/ontologies/{id}/sync/tasks/{tid}/logs → 日志
DELETE /api/ontologies/{id}/sync/tasks/{tid}  → 删除任务
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Optional

from src.core.naming import CamelCaseModel
from src.services import sync_service

router = APIRouter(prefix="/api/ontologies", tags=["sync"])


def success(data: Any = None, **extra):
    r = {"success": True}
    if data is not None:
        r["data"] = data
    r.update(extra)
    return r


class SyncTriggerRequest(CamelCaseModel):
    mode: str = "full"  # "full" | "incremental"


# ============================================================
# 同步任务
# ============================================================

@router.get("/{ontology_id}/sync/tasks")
async def list_sync_tasks(ontology_id: str):
    """列出同步任务"""
    tasks = await sync_service.get_sync_tasks(ontology_id)
    return success(data=tasks)


@router.post("/{ontology_id}/sync/tasks")
async def trigger_sync(ontology_id: str, body: SyncTriggerRequest = None):
    """触发同步任务（异步）"""
    mode = body.mode if body else "full"
    result = await sync_service.trigger_sync(ontology_id, mode)
    return success(**result)


@router.get("/{ontology_id}/sync/tasks/{task_id}")
async def get_sync_task(ontology_id: str, task_id: str):
    """获取任务详情"""
    task = await sync_service.get_sync_task(task_id)
    if not task:
        return {"success": False, "error": "Task not found"}
    if task["ontology_id"] != ontology_id:
        return {"success": False, "error": "Task does not belong to this ontology"}
    return success(data=task)


@router.get("/{ontology_id}/sync/tasks/{task_id}/logs")
async def get_sync_logs(ontology_id: str, task_id: str):
    """获取任务日志"""
    # 先验证任务归属
    task = await sync_service.get_sync_task(task_id)
    if not task:
        return {"success": False, "error": "Task not found"}
    if task["ontology_id"] != ontology_id:
        return {"success": False, "error": "Task does not belong to this ontology"}

    logs = await sync_service.get_sync_logs(task_id)
    return success(data=logs)


@router.delete("/{ontology_id}/sync/tasks/{task_id}")
async def delete_sync_task(ontology_id: str, task_id: str):
    """删除任务"""
    task = await sync_service.get_sync_task(task_id)
    if not task:
        return {"success": False, "error": "Task not found"}
    if task["ontology_id"] != ontology_id:
        return {"success": False, "error": "Task does not belong to this ontology"}

    result = await sync_service.delete_sync_task(task_id)
    return success(success=result)
