"""
Debug 路由

用于调试和监控
"""

from typing import Any
from fastapi import APIRouter

from src.services.saga_manager import SagaManager

router = APIRouter(prefix="/api", tags=["debug"])


def success_response(data: Any):
    return {"success": True, "data": data}


@router.get("/debug/saga/{saga_id}")
async def get_saga_status(saga_id: str):
    """获取 Saga 状态"""
    manager = SagaManager()
    saga = await manager.get_saga_status(saga_id)
    if not saga:
        return {"success": False, "error": "Saga not found"}
    return success_response(saga)


@router.get("/debug/saga/pending")
async def list_pending_sagas():
    """列出待处理的 Sagas"""
    manager = SagaManager()
    sagas = await manager.get_pending_sagas()
    return success_response(sagas)
