"""
Jena Graph Store Protocol 操作

提供 HTTP 层面的 GSP 四原子操作：
- GET    /data?graph={uri}  → 获取整个图
- POST   /data?graph={uri}  → 追加三元组到图
- PUT    /data?graph={uri}  → 替换整个图
- DELETE /data?graph={uri}  → 删除整个图

使用说明：
    from src.services.jena import JenaClient
    client = get_jena_client()
    client.graph_get("http://onto-agent.com/ontology/customer360/meta")
    client.graph_post("http://onto-agent.com/ontology/customer360/meta", rdf_data, "text/turtle")
    client.graph_put("http://onto-agent.com/ontology/customer360/tbox", rdf_data, "text/turtle")
    client.graph_delete("http://onto-agent.com/ontology/customer360/tbox")
"""

import httpx
from typing import TYPE_CHECKING, Optional

from src.constants import JENA_TIMEOUT_SECONDS
from src.logging_config import get_logger

logger = get_logger("jena.gsp")


# ============================================================================
# Content Types
# ============================================================================

CONTENT_TYPE_TURTLE = "text/turtle"
CONTENT_TYPE_XML = "application/rdf+xml"
CONTENT_TYPE_JSON = "application/json"
CONTENT_TYPE_N3 = "text/n3"
CONTENT_TYPE_NTRIPLES = "application/n-triples"
CONTENT_TYPE_NQUADS = "application/x-nquads"

DEFAULT_CONTENT_TYPE = CONTENT_TYPE_TURTLE


# ============================================================================
# JenaGraphProtocolMixin
# ============================================================================

class JenaGraphProtocolMixin:
    """
    Graph Store Protocol 操作 Mixin

   混入到 JenaClient，提供 GSP 四原子操作
    """

    # ==================== Graph GET ====================

    def graph_get(self, graph_uri: str) -> str:
        """
        GET /data?graph={uri} → 获取整个图的所有三元组

        Args:
            graph_uri: 命名图 URI

        Returns:
            str: RDF 数据（原始格式，由 response Content-Type 决定）
            空图时返回空字符串

        Raises:
            JenaServiceError: 请求失败时抛出
        """
        url = f"{self.fuseki_url}/{self.dataset}/data"
        params = {"graph": graph_uri}

        try:
            response = httpx.get(
                url,
                params=params,
                auth=self.auth,
                timeout=self.timeout,
                headers={"Accept": "*/*"},
            )
            response.raise_for_status()

            if response.status_code == 204:
                # 204 No Content 表示图不存在或为空
                return ""

            return response.text

        except httpx.HTTPStatusError as e:
            logger.error(f"GSP GET failed for {graph_uri}: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"GSP GET failed for {graph_uri}: {e}")
            raise

    def graph_get_turtle(self, graph_uri: str) -> str:
        """GET 并指定接受 Turtle 格式"""
        url = f"{self.fuseki_url}/{self.dataset}/data"
        params = {"graph": graph_uri}

        try:
            response = httpx.get(
                url,
                params=params,
                auth=self.auth,
                timeout=self.timeout,
                headers={"Accept": CONTENT_TYPE_TURTLE},
            )
            response.raise_for_status()
            return response.text if response.text else ""

        except httpx.HTTPStatusError as e:
            logger.error(f"GSP GET Turtle failed for {graph_uri}: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"GSP GET Turtle failed for {graph_uri}: {e}")
            raise

    def graph_exists(self, graph_uri: str) -> bool:
        """
        检查命名图是否存在

        Args:
            graph_uri: 命名图 URI

        Returns:
            bool: 图是否存在
        """
        try:
            # HEAD 请求只检查图是否存在，不返回内容
            url = f"{self.fuseki_url}/{self.dataset}/data"
            params = {"graph": graph_uri}
            response = httpx.head(
                url,
                params=params,
                auth=self.auth,
                timeout=10,
            )
            return response.status_code == 200
        except Exception:
            return False

    # ==================== Graph POST ====================

    def graph_post(
        self,
        graph_uri: str,
        rdf_data: str,
        content_type: str = DEFAULT_CONTENT_TYPE,
    ) -> bool:
        """
        POST /data?graph={uri} → 追加三元组到指定命名图

        如果图不存在，自动创建。

        Args:
            graph_uri: 命名图 URI
            rdf_data: RDF 数据内容（Turtle/N-Triples/N-Quads 等）
            content_type: RDF 数据格式，默认 text/turtle

        Returns:
            bool: 是否成功（200/201 表示成功）
        """
        url = f"{self.fuseki_url}/{self.dataset}/data"
        params = {"graph": graph_uri}

        try:
            response = httpx.post(
                url,
                params=params,
                auth=self.auth,
                timeout=self.timeout,
                headers={"Content-Type": content_type},
                content=rdf_data.encode("utf-8") if isinstance(rdf_data, str) else rdf_data,
            )

            if response.status_code not in (200, 201):
                logger.warning(
                    f"GSP POST to {graph_uri} returned {response.status_code}: {response.text[:200]}"
                )

            return response.status_code in (200, 201)

        except httpx.HTTPStatusError as e:
            logger.error(f"GSP POST failed for {graph_uri}: {e.response.status_code}")
            return False
        except Exception as e:
            logger.error(f"GSP POST failed for {graph_uri}: {e}")
            return False

    def graph_post_empty(self, graph_uri: str) -> bool:
        """
        通过 SPARQL 初始化空命名图（Fuseki TDB 不会持久化空图）

        使用 INSERT DATA 写入一个最小 fake triple 来激活图。
        图被使用时会自动创建（首次 POST 内容时），
        所以这个方法主要用于需要预创建的场景。

        Args:
            graph_uri: 命名图 URI

        Returns:
            bool: 是否成功
        """
        upd = f"INSERT DATA {{ GRAPH <{graph_uri}> {{ <urn:ex:placeholder> <urn:ex:placeholder> <urn:ex:placeholder> }} }}"
        try:
            url = f"{self.fuseki_url}/{self.dataset}/update"
            r = httpx.post(url, data={"update": upd}, auth=self.auth, timeout=self.timeout)
            return r.status_code == 200
        except Exception as e:
            logger.warning(f"graph_post_empty failed for {graph_uri}: {e}")
            return False

    # ==================== Graph PUT ====================

    def graph_put(
        self,
        graph_uri: str,
        rdf_data: str,
        content_type: str = DEFAULT_CONTENT_TYPE,
    ) -> bool:
        """
        PUT /data?graph={uri} → 替换整个命名图的内容

        ⚠️ 警告：这是原子替换操作，原有内容会被完全覆盖。

        Args:
            graph_uri: 命名图 URI
            rdf_data: RDF 数据内容
            content_type: RDF 数据格式，默认 text/turtle

        Returns:
            bool: 是否成功（200/201/204 表示成功）
        """
        url = f"{self.fuseki_url}/{self.dataset}/data"
        params = {"graph": graph_uri}

        try:
            response = httpx.put(
                url,
                params=params,
                auth=self.auth,
                timeout=self.timeout,
                headers={"Content-Type": content_type},
                content=rdf_data.encode("utf-8") if isinstance(rdf_data, str) else rdf_data,
            )

            if response.status_code not in (200, 201, 204):
                logger.warning(
                    f"GSP PUT to {graph_uri} returned {response.status_code}: {response.text[:200]}"
                )

            return response.status_code in (200, 201, 204)

        except httpx.HTTPStatusError as e:
            logger.error(f"GSP PUT failed for {graph_uri}: {e.response.status_code}")
            return False
        except Exception as e:
            logger.error(f"GSP PUT failed for {graph_uri}: {e}")
            return False

    def graph_put_empty(self, graph_uri: str) -> bool:
        """
        清空命名图（PUT 空内容）

        Args:
            graph_uri: 命名图 URI

        Returns:
            bool: 是否成功
        """
        return self.graph_put(graph_uri, "", CONTENT_TYPE_TURTLE)

    # ==================== Graph DELETE ====================

    def graph_delete(self, graph_uri: str) -> bool:
        """
        DELETE /data?graph={uri} → 删除整个命名图

        Args:
            graph_uri: 命名图 URI

        Returns:
            bool: 是否成功（200/204 表示成功，404 也算成功因为结果是无图）
        """
        url = f"{self.fuseki_url}/{self.dataset}/data"
        params = {"graph": graph_uri}

        try:
            response = httpx.delete(
                url,
                params=params,
                auth=self.auth,
                timeout=self.timeout,
            )

            # 200/204 成功，404 也视为"图不存在"但操作已完成
            if response.status_code not in (200, 204, 404):
                logger.warning(
                    f"GSP DELETE on {graph_uri} returned {response.status_code}: {response.text[:200]}"
                )

            return response.status_code in (200, 204, 404)

        except httpx.HTTPStatusError as e:
            logger.error(f"GSP DELETE failed for {graph_uri}: {e.response.status_code}")
            return False
        except Exception as e:
            logger.error(f"GSP DELETE failed for {graph_uri}: {e}")
            return False

    # ==================== 批量操作 ====================

    def graph_ensure(
        self,
        graph_uri: str,
        rdf_data: str = "",
        content_type: str = DEFAULT_CONTENT_TYPE,
    ) -> bool:
        """
        确保图存在（如果不存在则创建空图）

        Args:
            graph_uri: 命名图 URI
            rdf_data: 初始数据，可选
            content_type: RDF 数据格式

        Returns:
            bool: 是否成功
        """
        if not self.graph_exists(graph_uri):
            if rdf_data:
                return self.graph_post(graph_uri, rdf_data, content_type)
            else:
                return self.graph_post_empty(graph_uri)
        elif rdf_data:
            # 图已存在且有数据 → PUT 替换
            return self.graph_put(graph_uri, rdf_data, content_type)
        return True

    def graph_copy(self, source_graph: str, target_graph: str) -> bool:
        """
        复制源命名图到目标命名图（用于快照）

        先清空目标图，再追加源图内容。

        Args:
            source_graph: 源图 URI
            target_graph: 目标图 URI

        Returns:
            bool: 是否成功
        """
        try:
            # 读取源图全部内容
            data = self.graph_get(source_graph)
            if not data:
                logger.warning(f"Source graph {source_graph} is empty, nothing to copy")
                return True

            # 替换目标图
            return self.graph_put(target_graph, data, DEFAULT_CONTENT_TYPE)

        except Exception as e:
            logger.error(f"graph_copy failed: {source_graph} -> {target_graph}: {e}")
            return False

    def graph_delete_all_version_snapshots(self, base_iri: str) -> int:
        """
        删除某本体的所有版本快照图

        Args:
            base_iri: 本体 base IRI

        Returns:
            int: 删除的快照图数量
        """
        deleted = 0
        prefix = f"{base_iri}/abox@"

        try:
            # 列出所有命名图
            graphs = self.list_named_graphs()
            for g in graphs:
                uri = g.get("uri", "")
                if uri.startswith(prefix):
                    if self.graph_delete(uri):
                        deleted += 1
                        logger.info(f"Deleted snapshot graph: {uri}")
        except Exception as e:
            logger.error(f"Failed to delete version snapshots for {base_iri}: {e}")

        return deleted

    def graph_delete_all_ontology_graphs(self, base_iri: str) -> int:
        """
        删除某本体所有相关命名图（meta + tbox + abox + 所有快照）

        用于删除本体时的级联清理。

        Args:
            base_iri: 本体 base IRI

        Returns:
            int: 删除的图数量
        """
        deleted = 0
        graphs_to_delete = [
            f"{base_iri}/meta",
            f"{base_iri}/tbox",
            f"{base_iri}/abox",
        ]

        # 先收集所有快照
        try:
            all_graphs = self.list_named_graphs()
            for g in all_graphs:
                uri = g.get("uri", "")
                if uri.startswith(f"{base_iri}/abox@"):
                    graphs_to_delete.append(uri)
        except Exception:
            pass

        # 删除所有图
        for graph_uri in graphs_to_delete:
            if self.graph_delete(graph_uri):
                deleted += 1
                logger.info(f"Deleted graph: {graph_uri}")

        return deleted
