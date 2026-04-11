"""
Jena Named Graph 扩展模块

提供基于 GSP 的命名图便捷方法。

⚠️ 注意：此模块已重构，底层操作全部基于 Graph Store Protocol。
命名图 URI 格式为 {baseIri}/meta、{baseIri}/tbox、{baseIri}/abox，
与旧版的 {dataset}/{ontologyId}/tbox 格式不同。

使用 Mixin 模式，直接继承到 JenaClient。
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.services.jena.jena_base import JenaBaseClient

import httpx
from rdflib import RDF, RDFS, OWL

from src.logging_config import get_logger

logger = get_logger("jena.named_graph")

# 默认共享 Dataset
DEFAULT_DATASET = "/onto-agent"


class JenaNamedGraphMixin:
    """
    Named Graph 操作 Mixin

    ⚠️ 注意：此模块已重构。
    底层 GSP 操作已迁移到 JenaGraphProtocolMixin。
    此模块保留便捷方法，统一调用 GSP 层。
    """

    base: "JenaBaseClient"

    # ==================== Dataset 操作 ====================

    def create_dataset(self, dataset: str) -> bool:
        """
        创建或确认 Dataset 存在 (使用 Fuseki 管理 API)

        Args:
            dataset: Dataset 名称，如 "/onto-agent"

        Returns:
            bool: 是否成功
        """
        import json

        dataset_name = dataset.lstrip("/")  # 如 "onto-agent"
        url = f"{self.fuseki_url}/$/datasets"
        data = {
            "dbName": dataset_name,
            "dbType": "tdb",
        }
        try:
            response = httpx.put(
                url,
                json=data,
                auth=self.auth,
                timeout=10.0,
            )
            if response.status_code in (200, 201, 204, 405):
                # 405 = Method Not Allowed → dataset 已存在（PUT 不允许覆盖已有 dataset）
                logger.info(f"Dataset {dataset} created/verified (status={response.status_code})")
                return True
            elif response.status_code == 409:
                # 已存在（Conflict）
                logger.info(f"Dataset {dataset} already exists")
                return True
            else:
                logger.warning(f"create_dataset failed: {response.status_code}")
                return False
        except Exception as e:
            logger.warning(f"create_dataset error: {e}")
            return False

    # ==================== 命名图基础操作（委托给 GSP） ====================

    def insert_named_graph(self, graph_uri: str, triples: str) -> bool:
        """
        向指定命名图插入三元组（便捷封装）

        内部调用 graph_post，将字符串 triples 直接发送。

        Args:
            graph_uri: 命名图 URI
            triples: Turtle 格式三元组字符串

        Returns:
            bool: 是否成功
        """
        # 直接透传给 graph_post
        return self.graph_post(graph_uri, triples)

    def delete_named_graph(self, graph_uri: str) -> bool:
        """
        删除命名图（委托给 GSP）

        内部调用 graph_delete。

        Args:
            graph_uri: 命名图 URI

        Returns:
            bool: 是否成功
        """
        return self.graph_delete(graph_uri)

    def list_named_graphs(self) -> list[dict]:
        """
        列出当前 Dataset 中所有命名图

        Returns:
            list[dict]: 每项包含 uri 和 triple_count
        """
        q = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

        SELECT ?graph (COUNT(?s) as ?tripleCount)
        WHERE {
            GRAPH ?graph { ?s ?p ?o }
        }
        GROUP BY ?graph
        """
        try:
            results = self._query(q)
            return [
                {
                    "uri": row.get("graph", ""),
                    "triple_count": int(row.get("tripleCount", 0)),
                }
                for row in results
            ]
        except Exception as e:
            logger.error(f"list_named_graphs failed: {e}")
            return []

    def query_named_graph(self, graph_uri: str, where_clause: str) -> list[dict]:
        """
        查询指定命名图（FROM NAMED 方式）

        Args:
            graph_uri: 命名图 URI
            where_clause: WHERE 子句内容

        Returns:
            list[dict]: 查询结果
        """
        q = f"""
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT *
        FROM NAMED <{graph_uri}>
        WHERE {{ GRAPH <{graph_uri}> {{ {where_clause} }} }}
        """
        try:
            return self._query(q)
        except Exception as e:
            logger.error(f"query_named_graph failed: {e}")
            return []

    # ==================== TBox 便捷方法 ====================

    def create_ontology_tbox(
        self,
        ontology_iri: str,
        name: str,
        description: str = None,
    ) -> bool:
        """
        创建本体元数据（TBox 命名图初始化 + 本体头写入 meta 图）

        Args:
            ontology_iri: 本体 base IRI
            name: 本体名称
            description: 本体描述

        Returns:
            bool: 是否成功
        """
        from src.services.jena.jena_graph_protocol import DEFAULT_CONTENT_TYPE

        meta_graph_uri = f"{ontology_iri}/meta"
        tbox_graph_uri = f"{ontology_iri}/tbox"

        # 构造本体元数据 Turtle
        triples = [
            f"<{ontology_iri}> <{RDF.type}> <{OWL.Ontology}> .",
            f'<{ontology_iri}> <{RDFS.label}> "{name}" .',
        ]
        if description:
            triples.append(f'<{ontology_iri}> <{RDFS.comment}> "{description}" .')

        rdf_data = "\n".join(triples)

        # 确保 meta 图存在并写入元数据
        success_meta = self.graph_post(meta_graph_uri, rdf_data, DEFAULT_CONTENT_TYPE)

        # 确保 tbox 图存在（空图）
        success_tbox = self.graph_post_empty(tbox_graph_uri)

        return success_meta and success_tbox

    def add_class_to_tbox(
        self,
        tbox_graph_uri: str,
        class_uri: str,
        display_name: str = None,
        description: str = None,
        super_classes: list = None,
    ) -> bool:
        """
        向 TBox 命名图添加类定义（POST 追加）

        Args:
            tbox_graph_uri: TBox 图 URI（{baseIri}/tbox）
            class_uri: 类 URI
            display_name: 显示名称
            description: 描述
            super_classes: 父类 URI 列表

        Returns:
            bool: 是否成功
        """
        triples = [
            f"<{class_uri}> <{RDF.type}> <{OWL.Class}> .",
            f'<{class_uri}> <{RDFS.label}> "{display_name or class_uri.split("#")[-1]}" .',
        ]
        if description:
            triples.append(f'<{class_uri}> <{RDFS.comment}> "{description}" .')
        if super_classes:
            for sc in super_classes:
                triples.append(f"<{class_uri}> <{RDFS.subClassOf}> <{sc}> .")

        rdf_data = "\n".join(triples)
        return self.graph_post(tbox_graph_uri, rdf_data)

    def add_datatype_property_to_tbox(
        self,
        tbox_graph_uri: str,
        prop_uri: str,
        domain_uri: str,
        range_type: str,
        display_name: str = None,
        characteristics: list = None,
    ) -> bool:
        """
        向 TBox 命名图添加数据属性

        Args:
            tbox_graph_uri: TBox 图 URI
            prop_uri: 属性 URI
            domain_uri: 定义域 URI
            range_type: 数据类型（如 string, integer）
            display_name: 显示名称
            characteristics: 属性特性列表

        Returns:
            bool: 是否成功
        """
        xsd_range = f"http://www.w3.org/2001/XMLSchema#{range_type}"

        triples = [
            f"<{prop_uri}> <{RDF.type}> <{OWL.DatatypeProperty}> .",
            f'<{prop_uri}> <{RDFS.label}> "{display_name or prop_uri.split("#")[-1]}" .',
            f"<{prop_uri}> <{RDFS.domain}> <{domain_uri}> .",
            f"<{prop_uri}> <{RDFS.range}> <{xsd_range}> .",
        ]

        if characteristics:
            char_map = {"functional": str(OWL.FunctionalProperty)}
            for char in characteristics:
                if char in char_map:
                    triples.append(f"<{prop_uri}> <{RDF.type}> <{char_map[char]}> .")

        rdf_data = "\n".join(triples)
        return self.graph_post(tbox_graph_uri, rdf_data)

    def add_object_property_to_tbox(
        self,
        tbox_graph_uri: str,
        prop_uri: str,
        domain_uri: str,
        range_uri: str,
        display_name: str = None,
        characteristics: list = None,
        inverse_of: str = None,
    ) -> bool:
        """
        向 TBox 命名图添加对象属性

        Args:
            tbox_graph_uri: TBox 图 URI
            prop_uri: 属性 URI
            domain_uri: 定义域 URI
            range_uri: 值域 URI
            display_name: 显示名称
            characteristics: 属性特性列表
            inverse_of: 反向属性 URI

        Returns:
            bool: 是否成功
        """
        triples = [
            f"<{prop_uri}> <{RDF.type}> <{OWL.ObjectProperty}> .",
            f'<{prop_uri}> <{RDFS.label}> "{display_name or prop_uri.split("#")[-1]}" .',
            f"<{prop_uri}> <{RDFS.domain}> <{domain_uri}> .",
            f"<{prop_uri}> <{RDFS.range}> <{range_uri}> .",
        ]

        if characteristics:
            char_map = {
                "functional": str(OWL.FunctionalProperty),
                "inverseFunctional": str(OWL.InverseFunctionalProperty),
                "transitive": str(OWL.TransitiveProperty),
                "symmetric": str(OWL.SymmetricProperty),
            }
            for char in characteristics:
                if char in char_map:
                    triples.append(f"<{prop_uri}> <{RDF.type}> <{char_map[char]}> .")

        if inverse_of:
            triples.append(f"<{prop_uri}> <{OWL.inverseOf}> <{inverse_of}> .")

        rdf_data = "\n".join(triples)
        return self.graph_post(tbox_graph_uri, rdf_data)

    def delete_entity_from_tbox(self, entity_uri: str) -> bool:
        """
        从 TBox 删除实体（类/属性）的所有三元组

        ⚠️ 注意：这会删除该实体在所有图中的所有三元组。
        如需精确控制删除范围，请在调用前确保 entity_uri 正确。

        Args:
            entity_uri: 实体 URI

        Returns:
            bool: 是否成功
        """
        upd = f"DELETE WHERE {{ <{entity_uri}> ?p ?o }}"
        try:
            return self._update(upd)
        except Exception as e:
            logger.error(f"delete_entity_from_tbox failed: {e}")
            return False
