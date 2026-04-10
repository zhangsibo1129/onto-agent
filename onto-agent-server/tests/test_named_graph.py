"""
Named Graph 架构测试用例

测试范围：
1. Jena Named Graph 操作
2. Saga 事务管理器
3. 本体创建（含版本管理）
4. 类/属性创建（含事务一致性）

运行方式:
    cd onto-agent-server
    source .venv/bin/activate
    pytest tests/test_named_graph.py -v
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime


# ============================================================================
# 测试配置
# ============================================================================

# 测试用 Jena 配置（需要确保 Fuseki 运行）
TEST_FUSEKI_URL = "http://localhost:3030"
TEST_DATASET = "/onto-agent-test"

# 测试用本体参数
TEST_ONTOLOGY = {
    "name": "TestCompany",
    "description": "Test ontology for unit testing",
    "base_iri": "http://test-ontology.com/company#",
    "tbox_graph": "http://test-ontology.com/company#tbox",
    "abox_graph": "http://test-ontology.com/company#abox",
}


# ============================================================================
# 1. Named Graph 基础测试
# ============================================================================

class TestNamedGraph:
    """Named Graph 操作测试"""
    
    @pytest.mark.asyncio
    async def test_list_named_graphs(self):
        """测试列出命名图"""
        from src.services.jena_client import get_jena_client_for_default_dataset
        
        jena = get_jena_client_for_default_dataset()
        graphs = jena.list_named_graphs()
        
        # 验证返回格式
        assert isinstance(graphs, list)
        if graphs:
            assert "uri" in graphs[0]
            assert "triple_count" in graphs[0]
    
    @pytest.mark.asyncio
    async def test_insert_and_delete_named_graph(self):
        """测试插入和删除命名图"""
        from src.services.jena_client import get_jena_client_for_default_dataset
        
        jena = get_jena_client_for_default_dataset()
        test_graph = f"http://test-ontology.com/temp/graph_{datetime.now().timestamp()}"
        
        # 插入测试三元组
        triples = "<http://test/s> <http://test/p> <http://test/o> ."
        result = jena.insert_named_graph(test_graph, triples)
        assert result is True
        
        # 删除测试命名图
        result = jena.delete_named_graph(test_graph)
        assert result is True
    
    @pytest.mark.asyncio
    async def test_copy_graph(self):
        """测试复制命名图（版本快照）"""
        from src.services.jena_client import get_jena_client_for_default_dataset
        
        jena = get_jena_client_for_default_dataset()
        source_graph = f"http://test-source/graph_{datetime.now().timestamp()}"
        target_graph = f"http://test-target/graph_{datetime.now().timestamp()}"
        
        # 插入源图数据
        triples = "<http://test/s> <http://test/p> <http://test/o> ."
        jena.insert_named_graph(source_graph, triples)
        
        # 复制到目标图
        result = jena.copy_graph(source_graph, target_graph)
        assert result is True
        
        # 清理
        jena.delete_named_graph(source_graph)
        jena.delete_named_graph(target_graph)


# ============================================================================
# 2. Saga 事务测试
# ============================================================================

class TestSagaManager:
    """Saga 事务管理测试"""
    
    @pytest.mark.asyncio
    async def test_begin_saga(self):
        """测试 Saga 开始"""
        from src.services.saga_manager import SagaManager, SagaOperation
        
        operation = SagaOperation(
            ontology_id="onto_123",
            operation_type="create_class",
            entity_type="CLASS",
            entity_id="Customer",
            entity_name="Customer",
            jena_uri="http://onto#Customer",
            jena_graph_uri="http://onto#tbox",
            jena_data={"triples": "...", "graph_uri": "http://onto#tbox"},
            pg_data={"name": "Customer"},
        )
        
        saga_id = await SagaManager.begin_saga(operation)
        assert saga_id is not None
        assert len(saga_id) == 12  # UUID 前12位
    
    @pytest.mark.asyncio
    async def test_saga_status_query(self):
        """测试 Saga 状态查询"""
        from src.services.saga_manager import SagaManager, SagaOperation
        
        operation = SagaOperation(
            ontology_id="onto_123",
            operation_type="create_class",
            entity_type="CLASS",
            entity_id="Customer",
            entity_name="Customer",
            jena_uri="http://onto#Customer",
            jena_graph_uri="http://onto#tbox",
            jena_data={},
            pg_data={},
        )
        
        saga_id = await SagaManager.begin_saga(operation)
        
        # 查询状态
        status = await SagaManager.get_saga_status(saga_id)
        assert status is not None
        assert status["status"] == "pending"
        assert status["step"] == "prepare"


# ============================================================================
# 3. 集成测试：本体创建和版本管理
# ============================================================================

class TestOntologyIntegration:
    """本体集成测试（需要数据库和 Jena）"""
    
    @pytest.mark.skipif(
        not pytest.config.getoption("--run-integration", default=False),
        reason="Integration tests require running database and Jena"
    )
    @pytest.mark.asyncio
    async def test_create_ontology_with_named_graph(self):
        """测试创建本体（含 Named Graph）"""
        from src.services.ontology_service import OntologyService
        
        # 创建测试本体
        onto = await OntologyService.create_ontology(
            name="IntegrationTest",
            description="Test"
        )
        
        assert onto.name == "IntegrationTest"
        assert onto.tbox_graph_uri is not None
        assert onto.dataset == "/onto-agent"  # 统一共享 dataset
    
    @pytest.mark.skipif(
        not pytest.config.getoption("--run-integration", default=False),
        reason="Integration tests require running database and Jena"
    )
    @pytest.mark.asyncio
    async def test_version_publish(self):
        """测试版本发布"""
        from src.services.ontology_service import OntologyService
        
        # 创建本体
        onto = await OntologyService.create_ontology(
            name="VersionTest",
            description="Version test"
        )
        
        # 发布版本
        version = await OntologyService.publish_version(
            onto.id,
            [{"type": "added", "category": "class", "name": "Customer"}]
        )
        
        assert version.version == "v2.0"
        assert version.status == "published"


# ============================================================================
# 4. 事务一致性测试（模拟故障场景）
# ============================================================================

class TestTransactionConsistency:
    """事务一致性测试"""
    
    @pytest.mark.asyncio
    async def test_jena_failure_compensation(self):
        """测试 Jena 失败时的补偿机制"""
        from src.services.saga_manager import SagaManager, SagaOperation
        
        # 模拟 Jena 失败
        operation = SagaOperation(
            ontology_id="onto_123",
            operation_type="create_class",
            entity_type="CLASS",
            entity_id="Customer",
            entity_name="Customer",
            jena_uri="http://onto#Customer",
            jena_graph_uri="http://onto#tbox",
            jena_data={"triples": "...", "graph_uri": "http://onto#tbox"},
            pg_data={},
            
            # 模拟失败
            jena_execute=lambda: False,
            jena_compensate=lambda: True,
            pg_final_execute=lambda: True,
            pg_final_compensate=lambda: True,
        )
        
        saga_id = await SagaManager.begin_saga(operation)
        
        # 执行 Jena（应该失败并自动补偿）
        success = await SagaManager.execute_jena(operation, saga_id)
        assert success is False
        
        # 验证状态
        status = await SagaManager.get_saga_status(saga_id)
        assert status["status"] == "compensated"
    
    @pytest.mark.asyncio
    async def test_pg_failure_compensation(self):
        """测试 PG 失败时的补偿机制（删除 Jena 数据）"""
        from src.services.saga_manager import SagaManager, SagaOperation
        
        jena_deleted = False
        
        def mock_jena_compensate():
            nonlocal jena_deleted
            jena_deleted = True
        
        operation = SagaOperation(
            ontology_id="onto_123",
            operation_type="create_class",
            entity_type="CLASS",
            entity_id="Customer",
            entity_name="Customer",
            jena_uri="http://onto#Customer",
            jena_graph_uri="http://onto#tbox",
            jena_data={"triples": "...", "graph_uri": "http://onto#tbox"},
            pg_data={},
            
            jena_execute=lambda: True,
            jena_compensate=mock_jena_compensate,
            pg_final_execute=lambda: False,  # 模拟 PG 失败
            pg_final_compensate=lambda: True,
        )
        
        saga_id = await SagaManager.begin_saga(operation)
        
        # 先执行 Jena
        await SagaManager.execute_jena(operation, saga_id)
        
        # 执行 PG（应该失败并触发补偿）
        success = await SagaManager.execute_pg_final(operation, saga_id)
        assert success is False
        
        # 验证补偿被触发
        assert jena_deleted is True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--run-integration"])
