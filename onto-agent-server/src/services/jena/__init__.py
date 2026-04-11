"""
Jena 服务模块

提供组合后的 JenaClient，支持：
- Graph Store Protocol（GSP 四原子操作）
- TBox 操作（Class / DataProperty / ObjectProperty 的 CRUD）
- ABox 操作（Individual 的 CRUD）
- Version 操作（快照的创建 / 回滚 / 删除 / 列出）
- Named Graph 操作（图级别管理）

命名图设计：
    {baseIri}/meta         → 本体元数据
    {baseIri}/tbox         → Schema（Class + Property）
    {baseIri}/abox         → 当前实例
    {baseIri}/abox@vN      → 版本快照

使用方式:
    from src.services.jena import JenaClient, get_jena_client

    client = get_jena_client()
    classes = client.list_classes("http://example.org/onto#")
    individuals = client.list_individuals("http://example.org/onto#")

    # GSP 操作
    client.graph_post("http://example.org/onto/meta", rdf_data, "text/turtle")
    client.graph_put("http://example.org/onto/tbox", rdf_data, "text/turtle")

    # 版本快照
    client.create_version_snapshot("http://example.org/onto#", "v1")
    snapshots = client.list_version_snapshots("http://example.org/onto#")
    client.rollback_to_version("http://example.org/onto#", "v1")
"""

from src.services.jena.jena_base import JenaBaseClient, get_fuseki_settings
from src.services.jena.jena_tbox import JenaTBoxMixin
from src.services.jena.jena_abox import JenaABoxMixin
from src.services.jena.jena_named_graph import JenaNamedGraphMixin, DEFAULT_DATASET
from src.services.jena.jena_graph_protocol import JenaGraphProtocolMixin
from src.services.jena.jena_version import JenaVersionMixin


# ============================================================================
# JenaClient - 组合所有 Mixin
# ============================================================================

class JenaClient(
    JenaBaseClient,
    JenaGraphProtocolMixin,
    JenaTBoxMixin,
    JenaABoxMixin,
    JenaNamedGraphMixin,
    JenaVersionMixin,
):
    """
    组合后的 Jena 客户端

    同时支持:
    - GSP 操作: graph_get, graph_post, graph_put, graph_delete
    - TBox 操作: list_classes, create_class, list_datatype_properties 等
    - ABox 操作: list_individuals, create_individual 等
    - Version 操作: create_version_snapshot, rollback_to_version,
                    list_version_snapshots, delete_version_snapshot
    - Named Graph 操作: list_named_graphs, delete_named_graph 等
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
    "JenaGraphProtocolMixin",
    "JenaTBoxMixin",
    "JenaABoxMixin",
    "JenaNamedGraphMixin",
    "JenaVersionMixin",
    "get_jena_client",
    "get_fuseki_settings",
    "DEFAULT_DATASET",
]
