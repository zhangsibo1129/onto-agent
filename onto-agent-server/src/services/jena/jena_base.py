"""
Jena 基础客户端

提供 HTTP 连接、认证、基础 SPARQL 操作
"""

import sys as _sys
from os import getenv, environ
# 强制让 urllib/httpx 忽略系统代理
environ.setdefault("NO_PROXY", "localhost,127.0.0.1")
environ.setdefault("no_proxy", "localhost,127.0.0.1")

from functools import lru_cache
from typing import TYPE_CHECKING, Any

import httpx

# SPARQLWrapper path hack
_sparqlwrapper_path = ".venv/lib/python3.12/site-packages"
import os as _os
_vendor_root = _os.path.join(
    _os.path.dirname(_os.path.abspath(__file__)), "..", "..", ".."
)
_full_sparql_path = _os.path.join(_vendor_root, _sparqlwrapper_path)
if _full_sparql_path not in _sys.path:
    _sys.path.insert(0, _full_sparql_path)

from SPARQLWrapper import SPARQLWrapper2, JSON, GET

from src.constants import (
    JENA_DEFAULT_HOST,
    JENA_DEFAULT_PORT,
    JENA_TIMEOUT_SECONDS,
)
from src.exceptions import JenaServiceError, JenaQueryError
from src.logging_config import get_logger

logger = get_logger("jena.base")


# ============================================================================
# Configuration
# ============================================================================

@lru_cache
def get_fuseki_settings() -> dict:
    return {
        "fuseki_url": getenv("FUSEKI_URL", f"http://{JENA_DEFAULT_HOST}:{JENA_DEFAULT_PORT}"),
        "username": getenv("FUSEKI_USER", "admin"),
        "password": getenv("FUSEKI_PASSWORD", "admin"),
    }


# ============================================================================
# JenaBaseClient
# ============================================================================

class JenaBaseClient:
    """Jena 基础客户端，处理连接、认证、基础 SPARQL 操作"""
    
    def __init__(
        self,
        dataset: str = "/onto-agent",
        fuseki_url: str = None,
        timeout: int = JENA_TIMEOUT_SECONDS,
    ):
        settings = get_fuseki_settings()
        self.fuseki_url = fuseki_url or settings["fuseki_url"]
        self.dataset = dataset.lstrip("/")
        self.timeout = timeout
        self.auth = self._get_auth()
        
        # SPARQL 端点
        self.query_endpoint = f"{self.fuseki_url}/{self.dataset}/sparql"
        self.update_endpoint = f"{self.fuseki_url}/{self.dataset}/update"
    
    def _get_auth(self):
        settings = get_fuseki_settings()
        if settings["username"] and settings["password"]:
            return httpx.BasicAuth(settings["username"], settings["password"])
        return None
    
    # ==================== 基础 SPARQL 操作 ====================
    
    def _query(self, sparql: str) -> list[dict]:
        """
        执行 SELECT/ASK 查询

        返回的 dict 中，每个单元格的值已展开为 Python 原生类型：
          URI/BlankNode → str
          Literal       → str / int / float / bool
          None          → 键不存在时返回 None
        """
        try:
            sw = SPARQLWrapper2(self.query_endpoint)
            sw.setQuery(sparql)
            sw.setReturnFormat(JSON)
            sw.setMethod(GET)

            results = sw.query()

            if not results or not results.bindings:
                return []

            def _expand(cell) -> Any:
                """将 SPARQLWrapper.Value 或 dict 展开为 Python 原生值"""
                if cell is None:
                    return None
                if hasattr(cell, "value"):  # SPARQLWrapper.Value
                    return cell.value
                if isinstance(cell, dict):  # 已经是 dict（如 SPARQLWrapper.SmartWrapper 可能返回的结构）
                    return cell.get("value")
                return cell

            return [
                {key: _expand(row[key]) for key in row.keys()}
                for row in results.bindings
            ]
        except Exception as e:
            logger.error(f"SPARQL query failed: {e}")
            raise JenaQueryError(f"SPARQL query failed: {e}")
    
    def _update(self, sparql: str) -> bool:
        """执行 SPARQL Update（INSERT/DELETE）"""
        try:
            # 使用 httpx 直接发送更新请求，因为 SPARQLWrapper 对更新操作支持不好
            url = f"{self.fuseki_url}/{self.dataset}/update"
            data = {"update": sparql}
            r = httpx.post(url, data=data, auth=self.auth, timeout=self.timeout)
            return r.status_code == 200
        except Exception as e:
            logger.error(f"SPARQL update failed: {e}")
            return False
    
    # ==================== 数据集管理 ====================
    
    def _fuseki_get(self, path: str, timeout: int = 10) -> httpx.Response:
        """Fuseki 管理 API GET"""
        url = f"{self.fuseki_url}{path}"
        return httpx.get(url, auth=self.auth, timeout=timeout)
    
    def _fuseki_post(self, path: str, **kwargs) -> httpx.Response:
        """Fuseki 管理 API POST"""
        url = f"{self.fuseki_url}{path}"
        return httpx.post(url, auth=self.auth, **kwargs)
    
    def _fuseki_delete(self, path: str, timeout: int = 10) -> httpx.Response:
        """Fuseki 管理 API DELETE"""
        url = f"{self.fuseki_url}{path}"
        return httpx.delete(url, auth=self.auth, timeout=timeout)
    
    def health_check(self) -> bool:
        """检查 Jena 服务健康状态"""
        try:
            r = self._fuseki_get("/$/ping", timeout=5)
            return r.status_code == 200
        except Exception:
            return False
    
    def switch_dataset(self, dataset: str) -> "JenaBaseClient":
        """切换到另一个数据集（返回新实例）"""
        return JenaBaseClient(dataset=dataset, fuseki_url=self.fuseki_url)
