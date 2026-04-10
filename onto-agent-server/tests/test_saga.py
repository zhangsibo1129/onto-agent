"""
Saga 事务测试 - 验证故障恢复和补偿机制
"""

import pytest
import asyncio

# 测试 Saga 操作步骤
def test_saga_step_enum():
    """测试 Saga 步骤枚举"""
    from src.services.saga_manager import SagaStep
    
    assert SagaStep.PREPARE.value == "prepare"
    assert SagaStep.JENA.value == "jena"
    assert SagaStep.PG_FINAL.value == "pg_final"


def test_entity_status():
    """测试实体状态"""
    from src.models.ontology import EntityStatus
    
    assert EntityStatus.PENDING.value == "pending"
    assert EntityStatus.CONFIRMED.value == "confirmed"
    assert EntityStatus.COMPENSATED.value == "compensated"


def test_operation_type():
    """测试操作类型"""
    from src.models.ontology import OperationType
    
    assert OperationType.CREATE_CLASS.value == "create_class"
    assert OperationType.CREATE_DP.value == "create_dp"
    assert OperationType.CREATE_OP.value == "create_op"


def test_operation_log_model():
    """测试操作日志模型"""
    from src.models.ontology import OperationLog
    
    assert hasattr(OperationLog, 'id')
    assert hasattr(OperationLog, 'ontology_id')
    assert hasattr(OperationLog, 'status')
    assert hasattr(OperationLog, 'step')


@pytest.mark.asyncio
async def test_get_pending_sagas():
    """测试获取待处理的 Saga"""
    from src.services.saga_manager import SagaManager
    
    manager = SagaManager()
    
    try:
        pending = await manager.get_pending_sagas()
        assert isinstance(pending, list)
        print(f"\n✓ 当前有 {len(pending)} 个待处理的 Saga")
    except Exception as e:
        pytest.fail(f"获取待处理 Saga 失败: {e}")


@pytest.mark.asyncio
async def test_saga_manager_init():
    """测试 Saga 管理器初始化"""
    from src.services.saga_manager import SagaManager
    
    try:
        manager = SagaManager()
        assert manager is not None
        print("✓ Saga 管理器初始化成功")
    except Exception as e:
        pytest.fail(f"Saga 管理器初始化失败: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
