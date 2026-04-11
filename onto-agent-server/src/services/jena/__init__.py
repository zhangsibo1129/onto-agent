"""
Jena 服务模块

提供组合后的 JenaClient，支持 TBox、ABox、Named Graph 操作

使用方式:
    from src.services.jena import JenaClient, get_jena_client
    
    client = get_jena_client("/onto-agent")
    classes = client.list_classes("http://example.org/onto#")
    individuals = client.list_individuals("http://example.org/onto#")
    graphs = client.list_named_graphs()
"""

from src.services.jena.jena_base import JenaBaseClient, get_fuseki_settings
from src.services.jena.jena_tbox import JenaTBoxMixin
from src.services.jena.jena_abox import JenaABoxMixin
from src.services.jena.jena_named_graph import JenaNamedGraphMixin, DEFAULT_DATASET


# ============================================================================
# JenaClient - 组合所有 Mixin
# ============================================================================

class JenaClient(JenaBaseClient, JenaTBoxMixin, JenaABoxMixin, JenaNamedGraphMixin):
    """
    组合后的 Jena 客户端
    
    同时支持:
    - TBox 操作: list_classes, create_class, list_datatype_properties 等
    - ABox 操作: list_individuals, create_individual 等
    - Named Graph 操作: list_named_graphs, delete_named_graph, copy_graph 等
    - 基础操作: _query, _update, health_check 等
    """
    
    def __init__(self, dataset: str = "/onto-agent", fuseki_url: str = None):
        super().__init__(dataset=dataset, fuseki_url=fuseki_url)


# ============================================================================
# Client Factory
# ============================================================================

_jena_clients: dict = {}


def get_jena_client(dataset: str = "/onto-agent") -> JenaClient:
    """获取 Jena 客户端单例"""
    if dataset not in _jena_clients:
        _jena_clients[dataset] = JenaClient(dataset=dataset)
    return _jena_clients[dataset]


__all__ = [
    "JenaClient",
    "JenaBaseClient",
    "JenaTBoxMixin",
    "JenaABoxMixin",
    "JenaNamedGraphMixin",
    "get_jena_client",
    "get_fuseki_settings",
    "DEFAULT_DATASET",
]