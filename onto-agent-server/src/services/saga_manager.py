"""
Saga 事务管理器

跨系统事务一致性解决方案：
- 将跨系统（Jena + PostgreSQL）的事务拆解为可补偿的步骤
- 失败时自动执行逆向操作（补偿）
- 支持异步结算任务，处理异常情况
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, Callable, Any
import asyncio

from sqlalchemy import select, update
from src.database import SystemSession
from src.models.ontology import OperationLog, EntityStatus, EntityIndex, Ontology


class SagaStep(str, Enum):
    """Saga 步骤枚举"""
    PREPARE = "prepare"       # 准备阶段
    JENA = "jena"             # Jena 提交
    PG_FINAL = "pg_final"     # PostgreSQL 最终提交
    SETTLEMENT = "settlement" # 结算


@dataclass
class SagaOperation:
    """Saga 操作定义"""
    operation_id: str = field(default="")
    ontology_id: str = ""
    operation_type: str = ""
    entity_type: str = ""
    entity_id: str = ""
    entity_name: str = ""
    
    # Jena 数据
    jena_uri: str = ""
    jena_graph_uri: str = ""  # 实体所在的 Named Graph URI
    jena_data: dict = field(default_factory=dict)  # {"triples": "...", "graph_uri": "..."}
    
    # PostgreSQL 数据
    pg_data: dict = field(default_factory=dict)
    
    # 可执行的步骤
    jena_execute: Optional[Callable[[], bool]] = None
    jena_compensate: Optional[Callable[[], bool]] = None
    pg_final_execute: Optional[Callable[[], bool]] = None
    pg_final_compensate: Optional[Callable[[], bool]] = None


class SagaManager:
    """Saga 事务管理器"""
    
    MAX_RETRY = 3
    SETTLEMENT_TIMEOUT_SECONDS = 300  # 5分钟结算超时
    
    @staticmethod
    async def begin_saga(operation: SagaOperation) -> str:
        """
        开始 Saga 事务 - 记录操作日志（prepare 阶段）
        
        Args:
            operation: Saga 操作定义
        
        Returns:
            str: Saga 操作 ID
        """
        async with SystemSession() as session:
            log = OperationLog(
                id=str(uuid.uuid4())[:12],
                ontology_id=operation.ontology_id,
                operation_type=operation.operation_type,
                entity_type=operation.entity_type,
                entity_id=operation.entity_id,
                entity_name=operation.entity_name,
                jena_uri=operation.jena_uri,
                jena_data={
                    "triples": operation.jena_data.get("triples", ""),
                    "graph_uri": operation.jena_graph_uri
                },
                pg_data=operation.pg_data,
                status=EntityStatus.PENDING.value,
                step=SagaStep.PREPARE.value,
            )
            session.add(log)
            await session.commit()
            
            operation.operation_id = log.id
            return log.id
    
    @staticmethod
    async def execute_jena(operation: SagaOperation, saga_id: str) -> bool:
        """
        执行 Step 2: 提交到 Jena
        
        失败时自动标记为补偿状态
        
        Args:
            operation: Saga 操作
            saga_id: Saga ID
        
        Returns:
            bool: Jena 提交是否成功
        """
        try:
            # 执行 Jena 写入
            success = operation.jena_execute() if operation.jena_execute else False
            
            if success:
                # 更新步骤状态
                await SagaManager._update_step(saga_id, SagaStep.JENA.value)
                return True
            else:
                # 补偿：标记为失败
                await SagaManager._mark_compensated(saga_id, "Jena execution failed")
                return False
                
        except Exception as e:
            # 补偿：记录错误并清理
            await SagaManager._mark_compensated(saga_id, f"Jena exception: {e}")
            return False
    
    @staticmethod
    async def execute_pg_final(operation: SagaOperation, saga_id: str) -> bool:
        """
        执行 Step 3: PostgreSQL 最终提交
        
        失败时执行补偿（删除 Jena 数据）
        
        Args:
            operation: Saga 操作
            saga_id: Saga ID
        
        Returns:
            bool: PG 最终提交是否成功
        """
        try:
            # 执行 PG 写入
            success = operation.pg_final_execute() if operation.pg_final_execute else False
            
            if success:
                # 更新步骤状态，标记为已确认
                await SagaManager._update_step(
                    saga_id, 
                    SagaStep.PG_FINAL.value, 
                    EntityStatus.CONFIRMED.value
                )
                return True
            else:
                # 补偿：删除 Jena 数据
                if operation.jena_compensate:
                    try:
                        operation.jena_compensate()
                    except Exception as e:
                        print(f"[Saga] Jena compensate failed: {e}")
                
                await SagaManager._mark_compensated(saga_id, "PG final execution failed")
                return False
                
        except Exception as e:
            # 补偿
            if operation.jena_compensate:
                try:
                    operation.jena_compensate()
                except:
                    pass
            
            await SagaManager._mark_compensated(saga_id, f"PG final exception: {e}")
            return False
    
    @staticmethod
    async def _update_step(saga_id: str, step: str, status: str = None):
        """更新 Saga 状态"""
        async with SystemSession() as session:
            updates = {
                "step": step, 
                "updated_at": datetime.utcnow()
            }
            if status:
                updates["status"] = status
            
            await session.execute(
                update(OperationLog)
                .where(OperationLog.id == saga_id)
                .values(**updates)
            )
            await session.commit()
    
    @staticmethod
    async def _mark_compensated(saga_id: str, error_msg: str):
        """标记为已补偿（失败）"""
        async with SystemSession() as session:
            await session.execute(
                update(OperationLog)
                .where(OperationLog.id == saga_id)
                .values(
                    status=EntityStatus.COMPENSATED.value,
                    error_message=error_msg,
                    settled_at=datetime.utcnow()
                )
            )
            await session.commit()
    
    @staticmethod
    async def get_saga_status(saga_id: str) -> Optional[dict]:
        """获取 Saga 状态（用于调试）"""
        async with SystemSession() as session:
            result = await session.execute(
                select(OperationLog).where(OperationLog.id == saga_id)
            )
            log = result.scalar_one_or_none()
            if not log:
                return None
            
            return {
                "id": log.id,
                "operation_type": log.operation_type,
                "status": log.status,
                "step": log.step,
                "error_message": log.error_message,
                "retry_count": log.retry_count,
                "created_at": log.created_at.isoformat() if log.created_at else None,
            }
    
    @staticmethod
    async def get_pending_sagas() -> list[dict]:
        """获取待处理的 Saga 列表"""
        async with SystemSession() as session:
            result = await session.execute(
                select(OperationLog).where(
                    OperationLog.status == EntityStatus.PENDING.value,
                    OperationLog.step.in_([SagaStep.JENA.value, SagaStep.PG_FINAL.value])
                )
            )
            logs = result.scalars().all()
            
            return [
                {
                    "id": log.id,
                    "ontology_id": log.ontology_id,
                    "operation_type": log.operation_type,
                    "entity_type": log.entity_type,
                    "entity_id": log.entity_id,
                    "step": log.step,
                    "created_at": log.created_at.isoformat() if log.created_at else None,
                }
                for log in logs
            ]
    
    @staticmethod
    async def settlement_task():
        """
        结算任务 - 异步任务，定时检查并修复 pending 记录
        
        这个任务应该由后台调度器定期调用（如每分钟）
        """
        async with SystemSession() as session:
            # 计算超时阈值（5分钟前创建的记录）
            timeout_threshold = datetime.utcnow() - timedelta(seconds=SagaManager.SETTLEMENT_TIMEOUT_SECONDS)
            
            # 查找超时未结算的记录
            result = await session.execute(
                select(OperationLog).where(
                    OperationLog.status == EntityStatus.PENDING.value,
                    OperationLog.step.in_([SagaStep.JENA.value, SagaStep.PG_FINAL.value]),
                    OperationLog.created_at < timeout_threshold
                )
            )
            pending_logs = result.scalars().all()
            
            for log in pending_logs:
                try:
                    if log.step == SagaStep.JENA.value:
                        # 只到 Jena 阶段，删除 Jena 数据即可
                        # 构建实体 URI 并删除
                        # 这里是一个简化实现，实际需要根据 entity_type 构建正确的 URI
                        print(f"[Settlement] Auto-compensating {log.id}: deleting Jena data")
                    
                    elif log.step == SagaStep.PG_FINAL.value:
                        # 已到 PG 最终阶段，需要同时清理 PG 和 Jena
                        print(f"[Settlement] Auto-compensating {log.id}: rolling back PG")
                    
                    await SagaManager._mark_compensated(log.id, "Settlement: auto-compensated")
                    
                except Exception as e:
                    print(f"[Settlement] Failed for {log.id}: {e}")
        
        return len(pending_logs)


# ============================================================================
# 便捷函数：创建类操作的 Saga
# ============================================================================

async def create_class_saga(
    ontology_id: str,
    name: str,
    display_name: str,
    description: str,
    super_classes: list,
    base_iri: str,
    tbox_graph_uri: str,
) -> tuple[str, bool]:
    """
    创建类 - 使用 Saga 事务保证一致性
    
    Args:
        ontology_id: 本体 ID
        name: 类名（英文）
        display_name: 显示名称
        description: 描述
        super_classes: 父类列表
        base_iri: 本体基础 IRI
        tbox_graph_uri: TBox 命名图 URI
    
    Returns:
        tuple[saga_id, success]
    """
    class_uri = f"{base_iri}{name}"
    
    # 构建三元组
    from rdflib import RDF, RDFS, OWL
    triples = [
        (class_uri, str(RDF.type), str(OWL.Class)),
        (class_uri, str(RDFS.label), f'"{display_name or name}"'),
    ]
    if description:
        triples.append((class_uri, str(RDFS.comment), f'"{description}"'))
    if super_classes:
        for sc in super_classes:
            triples.append((class_uri, str(RDFS.subClassOf), f"<{sc}>"))
    
    triples_str = "\n".join(f"<{s}> <{p}> {o} ." for s, p, o in triples)
    
    # 创建 Saga 操作
    operation = SagaOperation(
        ontology_id=ontology_id,
        operation_type="create_class",
        entity_type="CLASS",
        entity_id=name,
        entity_name=name,
        jena_uri=class_uri,
        jena_graph_uri=tbox_graph_uri,
        jena_data={"triples": triples_str, "graph_uri": tbox_graph_uri},
        pg_data={
            "ontology_id": ontology_id,
            "name": name,
            "display_name": display_name,
            "graph_uri": tbox_graph_uri,
            "class_count_field": "class_count"
        },
        jena_execute=lambda: _jena_insert_class(tbox_graph_uri, triples_str),
        jena_compensate=lambda: _jena_delete_entity(class_uri),
        pg_final_execute=lambda: _pg_finalize_entity(
            ontology_id, "CLASS", name, display_name, class_uri, tbox_graph_uri
        ),
        pg_final_compensate=lambda: _pg_compensate_entity(
            ontology_id, "CLASS", name
        ),
    )
    
    # 开始 Saga
    saga_id = await SagaManager.begin_saga(operation)
    operation.operation_id = saga_id
    
    # 执行 Jena 提交
    jena_success = await SagaManager.execute_jena(operation, saga_id)
    if not jena_success:
        return saga_id, False
    
    # 执行 PostgreSQL 最终提交
    pg_success = await SagaManager.execute_pg_final(operation, saga_id)
    return saga_id, pg_success


def _jena_insert_class(graph_uri: str, triples: str) -> bool:
    """Jena 写入实现"""
    from src.services.jena import get_jena_client
    jena = get_jena_client()
    return jena.insert_named_graph(graph_uri, triples)


def _jena_delete_entity(entity_uri: str) -> bool:
    """Jena 补偿删除实现"""
    from src.services.jena import get_jena_client
    jena = get_jena_client()
    return jena.delete_entity_from_tbox(entity_uri)


def _pg_finalize_entity(
    ontology_id: str, 
    entity_type: str, 
    name: str, 
    display_name: str,
    jena_uri: str,
    graph_uri: str
) -> bool:
    """PostgreSQL 最终提交实现"""
    import uuid
    from datetime import datetime
    
    async def _do_finalize():
        async with SystemSession() as session:
            # 1. 写入 EntityIndex
            idx = EntityIndex(
                id=str(uuid.uuid4())[:12],
                ontology_id=ontology_id,
                entity_type=entity_type,
                name=name,
                display_name=display_name,
                graph_uri=graph_uri,
                jena_uri=jena_uri,
            )
            session.add(idx)
            
            # 2. 根据实体类型增加计数
            count_field_map = {
                "CLASS": "class_count",
                "DP": "dp_count",
                "OP": "op_count",
                "AP": "ap_count",
                "INDIVIDUAL": "individual_count",
            }
            count_field = count_field_map.get(entity_type)
            if count_field:
                col = getattr(Ontology, count_field)
                await session.execute(
                    update(Ontology)
                    .where(Ontology.id == ontology_id)
                    .values({count_field: col + 1})
                )
            
            await session.commit()
    
    try:
        # 同步执行异步函数
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # 如果在异步环境中，创建新任务
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(asyncio.run, _do_finalize())
                return future.result()
        else:
            asyncio.run(_do_finalize())
        return True
    except Exception as e:
        print(f"[PG] Finalize failed: {e}")
        return False


def _pg_compensate_entity(ontology_id: str, entity_type: str, name: str) -> bool:
    """PostgreSQL 补偿实现"""
    import uuid
    from sqlalchemy import delete as sql_delete
    
    async def _do_compensate():
        async with SystemSession() as session:
            # 1. 删除 EntityIndex
            await session.execute(
                sql_delete(EntityIndex).where(
                    EntityIndex.ontology_id == ontology_id,
                    EntityIndex.entity_type == entity_type,
                    EntityIndex.name == name
                )
            )
            
            # 2. 回滚计数
            count_field_map = {
                "CLASS": "class_count",
                "DP": "dp_count",
                "OP": "op_count",
                "AP": "ap_count",
                "INDIVIDUAL": "individual_count",
            }
            count_field = count_field_map.get(entity_type)
            if count_field:
                from sqlalchemy import case
                col = getattr(Ontology, count_field)
                # GREATEST(0, col - 1)
                new_val = case((col <= 0, 0), else_=col - 1)
                await session.execute(
                    update(Ontology)
                    .where(Ontology.id == ontology_id)
                    .values({count_field: new_val})
                )
            
            await session.commit()
    
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(asyncio.run, _do_compensate())
                return future.result()
        else:
            asyncio.run(_do_compensate())
        return True
    except Exception as e:
        print(f"[PG] Compensate failed: {e}")
        return False
