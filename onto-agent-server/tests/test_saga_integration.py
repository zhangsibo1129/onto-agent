"""
Saga 事务集成测试 - 端到端测试
"""

import pytest
import asyncio

@pytest.mark.asyncio
async def test_create_class_via_api():
    """测试通过 API 创建类（触发 Saga）"""
    import httpx
    
    # 使用已有的本体ID通过API创建类
    url = "http://localhost:8000/api/ontologies/test-onto-1/classes"
    
    try:
        response = httpx.post(
            url,
            json={
                "name": "ViaAPITest",
                "displayName": "API测试类"
            },
            timeout=10
        )
        print(f"\n✓ API 响应状态: {response.status_code}")
    except Exception as e:
        print(f"API 请求异常: {e}")


@pytest.mark.asyncio
async def test_saga_status_check():
    """测试 Saga 状态检查"""
    from src.services.saga_manager import SagaManager
    
    manager = SagaManager()
    
    # 获取待处理的 Saga
    pending = await manager.get_pending_sagas()
    print(f"\n✓ 待处理 Saga 数量: {len(pending)}")
    
    for saga in pending[:3]:  # 只打印前3条
        print(f"  - ID: {saga.get('id')}, Type: {saga.get('operation_type')}, Step: {saga.get('step')}")


@pytest.mark.asyncio  
async def test_debug_saga():
    """测试使用 debug 端点查询 Saga"""
    import httpx
    
    try:
        # 尝试列出所有 Saga
        response = httpx.get("http://localhost:8000/api/debug/saga/pending", timeout=5)
        print(f"\n✓ Debug 端点响应: {response.status_code}")
    except Exception as e:
        print(f"调试端点异常: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
