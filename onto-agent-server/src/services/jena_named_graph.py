"""
Jena Named Graph 扩展模块（向后兼容）

已迁移到 src.services.jena 模块，此文件保留向后兼容
"""

# 向后兼容：从新模块导入
from src.services.jena import (
    JenaNamedGraphMixin,
    JenaClient,
    get_jena_client,
    get_jena_client_for_dataset,
    get_jena_client_for_default_dataset,
    DEFAULT_DATASET,
)

__all__ = [
    "JenaNamedGraphMixin",
    "JenaClient",
    "get_jena_client",
    "get_jena_client_for_dataset",
    "get_jena_client_for_default_dataset",
    "DEFAULT_DATASET",
]


# 向后兼容：旧的注入函数（已不需要，保留空实现）
def inject_named_graph_methods(cls):
    """向后兼容：已不再需要，方法已通过 Mixin 继承"""
    return cls