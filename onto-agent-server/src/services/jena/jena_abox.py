"""
Jena ABox 操作

提供 Individual、属性断言等 ABox 层的 SPARQL 操作。

命名图约定：
  {baseIri}/abox      → 当前实例数据
  {baseIri}/abox@vN   → 版本快照（只读）

所有方法需要 baseIri 参数以构造正确的命名图 URI。
"""

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.services.jena.jena_base import JenaBaseClient

from rdflib import RDF, RDFS, OWL

from src.logging_config import get_logger

logger = get_logger("jena.abox")


# ============================================================================
# Helpers
# ============================================================================

def _abox_uri(base_iri: str) -> str:
    """从 baseIri 计算 abox 命名图 URI"""
    return f"{base_iri}/abox"


# ============================================================================
# JenaABoxMixin
# ============================================================================

class JenaABoxMixin:
    """Jena ABox 操作 Mixin"""

    base: "JenaBaseClient"  # 来自 JenaBaseClient

    # ==================== Individual 操作 ====================

    def list_individuals(
        self,
        base_iri: str,
        class_local_name: str = None,
        search: str = None,
    ) -> list[dict]:
        """
        列出本体所有 Individual（从 abox 图查询）

        Args:
            base_iri: 本体 base IRI
            class_local_name: 可选，按类局部名称筛选
            search: 可选，按名称/标签搜索

        Returns:
            list[dict]
        """
        abox_graph = _abox_uri(base_iri)
        filters = []

        # 按类型筛选
        if class_local_name:
            class_uri = f"{base_iri}{class_local_name}"
            filters.append(f'FILTER(EXISTS {{ ?ind rdf:type <{class_uri}> }})')

        # 按名称/标签搜索
        if search:
            filters.append(f'FILTER(CONTAINS(LCASE(STR(?label)), LCASE("{search}")))')

        filter_str = " . " + " . ".join(filters) if filters else ""

        q = f"""
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

        SELECT ?ind ?label ?comment
        FROM NAMED <{abox_graph}>
        WHERE {{
            GRAPH <{abox_graph}> {{
                ?ind a owl:NamedIndividual .
                FILTER(STRSTARTS(STR(?ind), "{base_iri}"))
                OPTIONAL {{ ?ind rdfs:label ?label }}
                OPTIONAL {{ ?ind rdfs:comment ?comment }}
                {filter_str}
            }}
        }}
        """
        try:
            results = self._query(q)
        except Exception as e:
            logger.error(f"list_individuals failed: {e}")
            return []

        individuals = []
        for row in results:
            ind_uri = row.get("ind", "")
            if not ind_uri:
                continue

            types = self._get_individual_types(ind_uri, abox_graph)
            data_props = self._get_individual_data_properties(ind_uri, abox_graph)
            obj_props = self._get_individual_object_properties(ind_uri, abox_graph)

            individuals.append({
                "id": self._local_name(ind_uri),
                "name": self._local_name(ind_uri),
                "display_name": row.get("label", ""),
                "description": row.get("comment", ""),
                "types": types,
                "labels": {},
                "comments": {},
                "data_property_assertions": data_props,
                "object_property_assertions": obj_props,
            })

        return individuals

    def create_individual(
        self,
        base_iri: str,
        individual_local_name: str,
        class_local_names: list[str],
        display_name: str = None,
        data_property_assertions: list[dict] = None,
        object_property_assertions: list[dict] = None,
    ) -> bool:
        """
        创建 Individual（POST 到 abox 图）

        Args:
            base_iri: 本体 base IRI
            individual_local_name: Individual 局部名称（不含 baseIri 前缀）
            class_local_names: 类型类局部名称列表
            display_name: 显示名称
            data_property_assertions: [{"propertyLocalName": "...", "value": "..."}]
            object_property_assertions: [{"propertyLocalName": "...", "targetLocalName": "..."}]

        Returns:
            bool: 是否成功
        """
        from src.services.jena.jena_graph_protocol import DEFAULT_CONTENT_TYPE

        abox_graph = _abox_uri(base_iri)
        ind_uri = f"{base_iri}{individual_local_name}"

        triples = [
            f"<{ind_uri}> <{RDF.type}> <{OWL.NamedIndividual}> .",
        ]

        # 添加类型
        for cls_name in class_local_names:
            cls_uri = f"{base_iri}{cls_name}"
            triples.append(f"<{ind_uri}> <{RDF.type}> <{cls_uri}> .")

        # 添加显示名称
        if display_name:
            triples.append(f'<{ind_uri}> <{RDFS.label}> "{display_name}" .')

        # 添加数据属性断言
        if data_property_assertions:
            for assertion in data_property_assertions:
                prop_name = assertion.get("propertyLocalName", "")
                value = assertion.get("value", "")
                prop_uri = f"{base_iri}{prop_name}"
                triples.append(f'<{ind_uri}> <{prop_uri}> "{value}" .')

        # 添加对象属性断言
        if object_property_assertions:
            for assertion in object_property_assertions:
                prop_name = assertion.get("propertyLocalName", "")
                target_name = assertion.get("targetLocalName", "")
                prop_uri = f"{base_iri}{prop_name}"
                target_uri = f"{base_iri}{target_name}"
                triples.append(f"<{ind_uri}> <{prop_uri}> <{target_uri}> .")

        rdf_data = "\n".join(triples)
        return self.graph_post(abox_graph, rdf_data)

    def delete_individual(self, individual_uri: str) -> bool:
        """
        删除 Individual（跨图操作）

        ⚠️ 注意：这会从所有图中删除该个体的三元组。

        Args:
            individual_uri: Individual 完整 URI

        Returns:
            bool: 是否成功
        """
        upd = f"DELETE WHERE {{ <{individual_uri}> ?p ?o }}"
        return self._update(upd)

    # ==================== 属性断言（带 abox 图限定） ====================

    def _get_individual_data_properties(
        self,
        ind_uri: str,
        abox_graph: str = None,
    ) -> list[dict]:
        """
        获取 Individual 的数据属性断言

        Args:
            ind_uri: Individual URI
            abox_graph: abox 图 URI（可选，不传则查所有图）
        """
        q = f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT ?prop ?value
        """
        if abox_graph:
            q += f" FROM NAMED <{abox_graph}>"
            q += f" WHERE {{ GRAPH <{abox_graph}> {{ <{ind_uri}> ?prop ?value . FILTER(IsLiteral(?value)) }} }}"
        else:
            q += f" WHERE {{ <{ind_uri}> ?prop ?value . FILTER(IsLiteral(?value)) }}"

        try:
            results = self._query(q)
        except Exception:
            return []

        props = []
        for row in results:
            prop_uri = row.get("prop", "")
            # 跳过 rdfs:label 等注解属性
            if self._local_name(prop_uri) in ["label", "comment"]:
                continue
            props.append({
                "propertyId": self._local_name(prop_uri),
                "value": str(row.get("value", "")),
            })
        return props

    def _get_individual_object_properties(
        self,
        ind_uri: str,
        abox_graph: str = None,
    ) -> list[dict]:
        """
        获取 Individual 的对象属性断言

        Args:
            ind_uri: Individual URI
            abox_graph: abox 图 URI（可选，不传则查所有图）
        """
        q = f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT ?prop ?target
        """
        if abox_graph:
            q += f" FROM NAMED <{abox_graph}>"
            q += f" WHERE {{ GRAPH <{abox_graph}> {{ <{ind_uri}> ?prop ?target . FILTER(IsIRI(?target)) }} }}"
        else:
            q += f" WHERE {{ <{ind_uri}> ?prop ?target . FILTER(IsIRI(?target)) }}"

        try:
            results = self._query(q)
        except Exception:
            return []

        props = []
        for row in results:
            prop_uri = row.get("prop", "")
            target_uri = row.get("target", "")
            # 跳过 rdf:type
            if self._local_name(prop_uri) in ["type"]:
                continue
            props.append({
                "propertyId": self._local_name(prop_uri),
                "targetIndividualId": self._local_name(target_uri),
            })
        return props

    def _get_individual_types(
        self,
        ind_uri: str,
        abox_graph: str = None,
    ) -> list[str]:
        """
        获取 Individual 的类型

        Args:
            ind_uri: Individual URI
            abox_graph: abox 图 URI（可选）
        """
        q = f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT ?type
        """
        if abox_graph:
            q += f" FROM NAMED <{abox_graph}>"
            q += f" WHERE {{ GRAPH <{abox_graph}> {{ <{ind_uri}> rdf:type ?type }} }}"
        else:
            q += f" WHERE {{ <{ind_uri}> rdf:type ?type }}"

        try:
            results = self._query(q)
        except Exception:
            return []

        return [
            self._local_name(row.get("type", ""))
            for row in results
            if self._local_name(row.get("type", "")) != "NamedIndividual"
        ]

    # ==================== 辅助方法 ====================

    def _local_name(self, uri: str) -> str:
        if not uri:
            return ""
        if "#" in uri:
            return uri.split("#")[-1]
        return uri.split("/")[-1]
