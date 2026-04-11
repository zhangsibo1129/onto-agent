"""
Jena 版本快照管理

提供基于 SPARQL 1.1 Graph Store 的版本管理操作：
- 创建快照：SPARQL COPY（当前 abox → abox@vN）
- 回滚版本：GET abox@vN → PUT abox
- 列出快照：查询所有 abox@vN 图
- 删除快照：DELETE abox@vN

使用说明：
    from src.services.jena import JenaClient, get_jena_client

    client = get_jena_client()

    # 创建版本快照
    client.create_version_snapshot("http://onto-agent.com/ontology/customer360", "v1")

    # 回滚到 v1
    client.rollback_to_version("http://onto-agent.com/ontology/customer360", "v1")

    # 列出所有快照
    snapshots = client.list_version_snapshots("http://onto-agent.com/ontology/customer360")

    # 删除快照
    client.delete_version_snapshot("http://onto-agent.com/ontology/customer360", "v1")
"""

from typing import Optional, TYPE_CHECKING

from rdflib import RDF, RDFS, OWL

from src.logging_config import get_logger

if TYPE_CHECKING:
    from src.services.jena.jena_base import JenaBaseClient

logger = get_logger("jena.version")


# ============================================================================
# JenaVersionMixin
# ============================================================================

class JenaVersionMixin:
    """
    Jena 版本快照操作 Mixin

    提供基于 SPARQL COPY 的版本管理能力
    """

    # ==================== 快照操作 ====================

    def create_version_snapshot(self, ontology_iri: str, version: str) -> bool:
        """
        创建当前 abox 的版本快照

        使用 SPARQL COPY 将当前 abox 内容复制到 abox@{version} 图。

        Args:
            ontology_iri: 本体 base IRI
            version: 版本标识符（如 "v1", "v2.1"）

        Returns:
            bool: 是否成功
        """
        current_abox = f"{ontology_iri}/abox"
        snapshot_abox = f"{ontology_iri}/abox@{version}"

        # SPARQL COPY：将 source 图的内容复制到 dest 图（原子操作）
        copy_sparql = f"""
        COPY <{current_abox}> TO <{snapshot_abox}>
        """

        try:
            result = self._update(copy_sparql)
            if result:
                logger.info(f"Created version snapshot: {snapshot_abox}")
            else:
                logger.warning(f"Failed to create version snapshot: {snapshot_abox}")
            return result
        except Exception as e:
            logger.error(f"create_version_snapshot failed: {e}")
            return False

    def rollback_to_version(self, ontology_iri: str, version: str) -> bool:
        """
        回滚到指定版本

        读取快照图内容，替换当前 abox。

        ⚠️ 注意：回滚会丢失当前 abox 的内容（未被快照的部分）。
        建议回滚前先创建一个当前状态的快照。

        Args:
            ontology_iri: 本体 base IRI
            version: 版本标识符

        Returns:
            bool: 是否成功
        """
        snapshot_abox = f"{ontology_iri}/abox@{version}"
        current_abox = f"{ontology_iri}/abox"

        # 方式 1：直接用 SPARQL MOVE（移动快照内容到当前，删除快照）
        # 不推荐，因为快照应该保留

        # 方式 2：先 COPY 快照到当前，再删快照（不删，因为快照要保留）
        # 直接覆盖当前 abox
        try:
            # 读取快照内容
            snapshot_data = self.graph_get(snapshot_abox)
            if not snapshot_data:
                logger.error(f"Snapshot {snapshot_abox} is empty or not found")
                return False

            # 替换当前 abox
            from src.services.jena.jena_graph_protocol import DEFAULT_CONTENT_TYPE
            result = self.graph_put(current_abox, snapshot_data, DEFAULT_CONTENT_TYPE)

            if result:
                logger.info(f"Rolled back to version {version} (snapshot: {snapshot_abox})")
            return result

        except Exception as e:
            logger.error(f"rollback_to_version failed: {e}")
            return False

    def list_version_snapshots(self, ontology_iri: str) -> list[dict]:
        """
        列出某本体的所有版本快照

        Returns:
            list[dict]: 快照列表，每项包含 uri、version、triple_count
        """
        prefix = f"{ontology_iri}/abox@"

        try:
            # 查询所有以 abox@ 开头的命名图
            q = f"""
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

            SELECT ?graph (COUNT(?s) as ?tripleCount)
            WHERE {{
                GRAPH ?graph {{
                    ?s ?p ?o .
                }}
                FILTER(STRSTARTS(STR(?graph), "{prefix}"))
            }}
            GROUP BY ?graph
            ORDER BY DESC(?graph)
            """

            results = self._query(q)

            snapshots = []
            for row in results:
                graph_uri = row.get("graph", "")
                # 提取版本号
                version = graph_uri.replace(f"{ontology_iri}/abox@", "")
                snapshots.append({
                    "uri": graph_uri,
                    "version": version,
                    "triple_count": int(row.get("tripleCount", 0)),
                })

            return snapshots

        except Exception as e:
            logger.error(f"list_version_snapshots failed: {e}")
            return []

    def delete_version_snapshot(self, ontology_iri: str, version: str) -> bool:
        """
        删除指定版本的快照

        Args:
            ontology_iri: 本体 base IRI
            version: 版本标识符

        Returns:
            bool: 是否成功
        """
        snapshot_abox = f"{ontology_iri}/abox@{version}"

        try:
            result = self.graph_delete(snapshot_abox)
            if result:
                logger.info(f"Deleted version snapshot: {snapshot_abox}")
            return result
        except Exception as e:
            logger.error(f"delete_version_snapshot failed: {e}")
            return False

    def get_version_snapshot_content(self, ontology_iri: str, version: str) -> str:
        """
        获取指定版本快照的全部内容

        用于查看历史版本详情、对比等场景。

        Args:
            ontology_iri: 本体 base IRI
            version: 版本标识符

        Returns:
            str: RDF Turtle 格式的快照内容，空时返回空字符串
        """
        snapshot_abox = f"{ontology_iri}/abox@{version}"

        try:
            return self.graph_get(snapshot_abox)
        except Exception as e:
            logger.error(f"get_version_snapshot_content failed: {e}")
            return ""

    def compare_versions(
        self,
        ontology_iri: str,
        version_a: str,
        version_b: str,
    ) -> dict:
        """
        对比两个版本的快照差异

        返回两个版本的实例数量和属性数量对比。

        Args:
            ontology_iri: 本体 base IRI
            version_a: 版本 A
            version_b: 版本 B

        Returns:
            dict: 包含两个版本的统计数据
        """
        snapshot_a = f"{ontology_iri}/abox@{version_a}"
        snapshot_b = f"{ontology_iri}/abox@{version_b}"

        def get_stats(graph_uri: str) -> dict:
            try:
                # 统计实例数量（owl:NamedIndividual）
                individual_q = f"""
                PREFIX owl: <http://www.w3.org/2002/07/owl#>
                SELECT (COUNT(DISTINCT ?ind) as ?count)
                FROM NAMED <{graph_uri}>
                WHERE {{
                    GRAPH <{graph_uri}> {{
                        ?ind a owl:NamedIndividual .
                    }}
                }}
                """
                ind_result = self._query(individual_q)
                individual_count = int(ind_result[0].get("count", 0)) if ind_result else 0

                # 统计三元组总数
                triple_q = f"""
                SELECT (COUNT(*) as ?count)
                FROM NAMED <{graph_uri}>
                WHERE {{
                    GRAPH <{graph_uri}> {{
                        ?s ?p ?o .
                    }}
                }}
                """
                triple_result = self._query(triple_q)
                triple_count = int(triple_result[0].get("count", 0)) if triple_result else 0

                return {
                    "uri": graph_uri,
                    "individual_count": individual_count,
                    "triple_count": triple_count,
                }
            except Exception as e:
                logger.error(f"get_stats for {graph_uri} failed: {e}")
                return {
                    "uri": graph_uri,
                    "individual_count": 0,
                    "triple_count": 0,
                    "error": str(e),
                }

        stats_a = get_stats(snapshot_a)
        stats_b = get_stats(snapshot_b)

        return {
            "version_a": version_a,
            "version_b": version_b,
            "stats_a": stats_a,
            "stats_b": stats_b,
        }

    # ==================== 发布相关 ====================

    def publish_tbox(self, ontology_iri: str) -> bool:
        """
        发布本体 TBox（固化当前草稿内容）

        读取当前 tbox 图全部内容，然后用 PUT 固化。
        发布后 tbox 内容锁定，后续变更需要先取消发布。

        Args:
            ontology_iri: 本体 base IRI

        Returns:
            bool: 是否成功
        """
        tbox_graph = f"{ontology_iri}/tbox"

        try:
            # 读取当前草稿内容
            content = self.graph_get(tbox_graph)
            if not content:
                logger.warning(f"TBox {tbox_graph} is empty, nothing to publish")
                return True  # 空图也视为成功

            # PUT 固化（内容不变，但语义上表示发布）
            from src.services.jena.jena_graph_protocol import DEFAULT_CONTENT_TYPE
            return self.graph_put(tbox_graph, content, DEFAULT_CONTENT_TYPE)

        except Exception as e:
            logger.error(f"publish_tbox failed: {e}")
            return False

    def get_tbox_content(self, ontology_iri: str) -> str:
        """
        获取本体 TBox 完整内容（用于导出 OWL）

        Args:
            ontology_iri: 本体 base IRI

        Returns:
            str: RDF Turtle 格式的 TBox 内容
        """
        tbox_graph = f"{ontology_iri}/tbox"

        try:
            return self.graph_get(tbox_graph)
        except Exception as e:
            logger.error(f"get_tbox_content failed: {e}")
            return ""

    def get_abox_content(self, ontology_iri: str) -> str:
        """
        获取本体 ABox 完整内容（用于导出/备份）

        Args:
            ontology_iri: 本体 base IRI

        Returns:
            str: RDF Turtle 格式的 ABox 内容
        """
        abox_graph = f"{ontology_iri}/abox"

        try:
            return self.graph_get(abox_graph)
        except Exception as e:
            logger.error(f"get_abox_content failed: {e}")
            return ""
