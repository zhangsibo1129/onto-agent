"""
Pytest 配置和 fixtures
"""

import pytest
import asyncio


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环 fixture"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_jena_client():
    """Mock Jena 客户端"""
    from unittest.mock import Mock
    
    mock = Mock()
    mock.insert_named_graph.return_value = True
    mock.delete_named_graph.return_value = True
    mock.copy_graph.return_value = True
    mock.list_named_graphs.return_value = [
        {"uri": "http://test/graph1", "triple_count": 100},
        {"uri": "http://test/graph2", "triple_count": 50},
    ]
    
    return mock


@pytest.fixture
def test_ontology_data():
    """测试用本体数据"""
    return {
        "name": "TestCompany",
        "description": "Test company ontology",
        "base_iri": "http://test-ontology.com/company#",
        "tbox_graph": "http://test-ontology.com/company#tbox",
        "abox_graph": "http://test-ontology.com/company#abox",
    }
