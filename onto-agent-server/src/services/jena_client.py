"""
Jena 客户端（已废弃）

⚠️ 此模块已废弃，请使用 src.services.jena 模块。

新的导入方式:
    from src.services.jena import JenaClient, get_jena_client
    
此模块保留向后兼容，将在未来版本移除。
"""

# 向后兼容：从新模块导入所有内容
from src.services.jena import (
    JenaClient,
    JenaBaseClient,
    JenaTBoxMixin,
    JenaABoxMixin,
    JenaNamedGraphMixin,
    get_jena_client,
    get_jena_client_for_dataset,
    get_jena_client_for_default_dataset,
    get_fuseki_settings,
)

# 向后兼容：错误类
from src.exceptions import JenaServiceError, JenaQueryError

__all__ = [
    # 主要导出
    "JenaClient",
    "get_jena_client",
    "get_jena_client_for_dataset",
    "get_jena_client_for_default_dataset",
    "get_fuseki_settings",
    # 兼容旧代码
    "JenaBaseClient",
    "JenaTBoxMixin",
    "JenaABoxMixin",
    "JenaNamedGraphMixin",
    "JenaServiceError",
    "JenaQueryError",
]

# 废弃警告（可选，生产环境不打印）
import warnings as _w
_w.warn(
    "src.services.jena_client 已废弃，请使用 src.services.jena",
    DeprecationWarning,
    stacklevel=2
)