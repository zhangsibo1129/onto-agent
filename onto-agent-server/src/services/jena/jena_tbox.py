"""
Jena TBox 操作

提供 Class、DataProperty、ObjectProperty、AnnotationProperty 的 CRUD 操作。

命名图约定：
  {baseIri}/meta  → 本体元数据（owl:Ontology 自身）
  {baseIri}/tbox  → Schema（Class + Property）

所有方法需要 baseIri 参数以构造正确的命名图 URI。
"""

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.services.jena.jena_base import JenaBaseClient

from rdflib import RDF, RDFS, OWL

from src.schemas.ontology import (
    OntologyClassResponse,
    DataPropertyResponse,
    ObjectPropertyResponse,
)
from src.logging_config import get_logger

logger = get_logger("jena.tbox")


# ============================================================================
# Helpers
# ============================================================================

def _tbox_uri(base_iri: str) -> str:
    """从 baseIri 计算 tbox 命名图 URI"""
    return f"{base_iri}/tbox"


def _meta_uri(base_iri: str) -> str:
    """从 baseIri 计算 meta 命名图 URI"""
    return f"{base_iri}/meta"


# ============================================================================
# JenaTBoxMixin
# ============================================================================

class JenaTBoxMixin:
    """Jena TBox 操作 Mixin"""

    base: "JenaBaseClient"  # 来自 JenaBaseClient

    # ==================== 本体操作（meta 图） ====================

    def create_ontology(
        self,
        name: str,
        base_iri: str,
        description: str = None,
    ) -> bool:
        """
        创建本体：初始化 meta + tbox + abox 三个命名图

        Args:
            name: 本体名称
            base_iri: 本体 base IRI
            description: 描述

        Returns:
            bool: 是否成功
        """
        from src.services.jena.jena_graph_protocol import DEFAULT_CONTENT_TYPE

        meta_graph = _meta_uri(base_iri)
        tbox_graph = _tbox_uri(base_iri)
        abox_graph = f"{base_iri}/abox"

        # 构造本体元数据 Turtle
        triples = [
            f"<{base_iri}> <{RDF.type}> <{OWL.Ontology}> .",
            f'<{base_iri}> <{RDFS.label}> "{name}" .',
        ]
        if description:
            triples.append(f'<{base_iri}> <{RDFS.comment}> "{description}" .')

        rdf_data = "\n".join(triples)

        # 确保 meta 图存在并写入元数据
        # tbox 和 abox 在首次写入内容时自然创建（TDB 图懒创建）
        meta_ok = self.graph_post(meta_graph, rdf_data, DEFAULT_CONTENT_TYPE)
        try:
            self.graph_post_empty(tbox_graph)
            self.graph_post_empty(abox_graph)
        except Exception as e:
            logger.warning(f"pre-create tbox/abox skipped: {e}")

        return meta_ok

    def list_ontologies(self) -> list[dict]:
        """
        列出所有本体（从所有 meta 图中查询）

        注意：此方法查询所有 Dataset 中的本体。
        在共享 Dataset 架构下，会返回所有本体。
        """
        q = """
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT DISTINCT ?ont ?label ?comment
        WHERE {
            GRAPH ?g {
                ?ont a owl:Ontology .
                OPTIONAL { ?ont rdfs:label ?label }
                OPTIONAL { ?ont rdfs:comment ?comment }
            }
        }
        """
        try:
            return self._query(q)
        except Exception as e:
            logger.error(f"list_ontologies failed: {e}")
            return []

    def get_ontology_meta(self, base_iri: str) -> dict:
        """
        获取本体元数据（从 meta 图查询）

        Args:
            base_iri: 本体 base IRI

        Returns:
            dict: 包含 label, comment
        """
        meta_graph = _meta_uri(base_iri)

        q = f"""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>

        SELECT ?label ?comment
        FROM NAMED <{meta_graph}>
        WHERE {{
            GRAPH <{meta_graph}> {{
                OPTIONAL {{ <{base_iri}> rdfs:label ?label }}
                OPTIONAL {{ <{base_iri}> rdfs:comment ?comment }}
            }}
        }}
        LIMIT 1
        """
        try:
            results = self._query(q)
            if not results:
                return {}
            return {
                "label": results[0].get("label", ""),
                "comment": results[0].get("comment", ""),
            }
        except Exception as e:
            logger.error(f"get_ontology_meta failed: {e}")
            return {}

    def update_ontology_meta(
        self,
        base_iri: str,
        name: str = None,
        description: str = None,
    ) -> bool:
        """
        更新本体元数据（meta 图）

        Args:
            base_iri: 本体 base IRI
            name: 新名称
            description: 新描述

        Returns:
            bool: 是否成功
        """
        meta_graph = _meta_uri(base_iri)

        if name:
            upd = f"""
            DELETE {{ <{base_iri}> <{RDFS.label}> ?old }}
            INSERT {{ <{base_iri}> <{RDFS.label}> "{name}" }}
            WHERE {{ <{base_iri}> <{RDFS.label}> ?old }}
            """
            if not self._update(upd):
                return False

        if description:
            upd = f"""
            DELETE {{ <{base_iri}> <{RDFS.comment}> ?old }}
            INSERT {{ <{base_iri}> <{RDFS.comment}> "{description}" }}
            WHERE {{ <{base_iri}> <{RDFS.comment}> ?old }}
            """
            if not self._update(upd):
                return False

        return True

    # ==================== 类操作（tbox 图） ====================

    def list_classes(self, base_iri: str) -> list[OntologyClassResponse]:
        """
        列出本体所有类（从 tbox 图查询）

        Args:
            base_iri: 本体 base IRI

        Returns:
            list[OntologyClassResponse]
        """
        tbox_graph = _tbox_uri(base_iri)

        q = f"""
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT DISTINCT ?class ?label ?comment
        FROM NAMED <{tbox_graph}>
        WHERE {{
            GRAPH <{tbox_graph}> {{
                ?class a owl:Class .
                FILTER(STRSTARTS(STR(?class), "{base_iri}"))
                OPTIONAL {{ ?class rdfs:label ?label }}
                OPTIONAL {{ ?class rdfs:comment ?comment }}
            }}
        }}
        """
        try:
            results = self._query(q)
        except Exception as e:
            logger.error(f"list_classes failed: {e}")
            return []

        classes = []
        for row in results:
            class_uri = row.get("class", "")
            if not class_uri:
                continue

            super_classes = self._get_super_classes(class_uri, tbox_graph)
            equivalent = self._get_equivalent_classes(class_uri, tbox_graph)
            disjoint = self._get_disjoint_classes(class_uri, tbox_graph)

            classes.append(OntologyClassResponse(
                id=self._local_name(class_uri),
                name=self._local_name(class_uri),
                display_name=row.get("label", ""),
                description=row.get("comment", ""),
                super_classes=super_classes,
                equivalent_to=equivalent,
                disjoint_with=disjoint,
                annotations={},
            ))

        return classes

    def create_class(
        self,
        base_iri: str,
        class_local_name: str,
        display_name: str = None,
        description: str = None,
        super_class_iris: list[str] = None,
    ) -> bool:
        """
        创建 OWL 类（POST 到 tbox 图）

        Args:
            base_iri: 本体 base IRI
            class_local_name: 类局部名称（不含 baseIri 前缀）
            display_name: 显示名称
            description: 描述
            super_class_iris: 父类 URI 列表

        Returns:
            bool: 是否成功
        """
        tbox_graph = _tbox_uri(base_iri)
        class_uri = f"{base_iri}{class_local_name}"

        triples = [
            f"<{class_uri}> <{RDF.type}> <{OWL.Class}> .",
            f'<{class_uri}> <{RDFS.label}> "{display_name or class_local_name}" .',
        ]
        if description:
            triples.append(f'<{class_uri}> <{RDFS.comment}> "{description}" .')
        if super_class_iris:
            for sc_uri in super_class_iris:
                triples.append(f"<{class_uri}> <{RDFS.subClassOf}> <{sc_uri}> .")

        rdf_data = "\n".join(triples)
        return self.graph_post(tbox_graph, rdf_data)

    def update_class(
        self,
        class_uri: str,
        display_name: str = None,
        description: str = None,
    ) -> bool:
        """
        更新类定义（SPARQL DELETE+INSERT，跨图操作）

        注意：此方法不限定图范围，会删除所有匹配三元组。
        建议使用带 base_iri 和 graph 参数的版本。

        Args:
            class_uri: 类完整 URI
            display_name: 新显示名称
            description: 新描述

        Returns:
            bool: 是否成功
        """
        if display_name:
            upd = f"""
            DELETE {{ <{class_uri}> <{RDFS.label}> ?old }}
            INSERT {{ <{class_uri}> <{RDFS.label}> "{display_name}" }}
            WHERE {{ <{class_uri}> <{RDFS.label}> ?old }}
            """
            self._update(upd)

        if description:
            upd = f"""
            DELETE {{ <{class_uri}> <{RDFS.comment}> ?old }}
            INSERT {{ <{class_uri}> <{RDFS.comment}> "{description}" }}
            WHERE {{ <{class_uri}> <{RDFS.comment}> ?old }}
            """
            self._update(upd)

        return True

    def delete_class(self, class_uri: str) -> bool:
        """
        删除类（SPARQL DELETE，跨图操作）

        ⚠️ 注意：这会从所有图中删除该类的三元组。

        Args:
            class_uri: 类完整 URI

        Returns:
            bool: 是否成功
        """
        upd = f"DELETE WHERE {{ <{class_uri}> ?p ?o }}"
        return self._update(upd)

    # ==================== 数据属性（tbox 图） ====================

    def list_datatype_properties(self, base_iri: str) -> list[DataPropertyResponse]:
        """
        列出本体所有数据属性（从 tbox 图查询）

        Args:
            base_iri: 本体 base IRI

        Returns:
            list[DataPropertyResponse]
        """
        tbox_graph = _tbox_uri(base_iri)

        q = f"""
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?prop ?label ?domain ?range
        FROM NAMED <{tbox_graph}>
        WHERE {{
            GRAPH <{tbox_graph}> {{
                ?prop a owl:DatatypeProperty .
                FILTER(STRSTARTS(STR(?prop), "{base_iri}"))
                OPTIONAL {{ ?prop rdfs:label ?label }}
                OPTIONAL {{ ?prop rdfs:domain ?domain }}
                OPTIONAL {{ ?prop rdfs:range ?range }}
            }}
        }}
        """
        try:
            results = self._query(q)
        except Exception as e:
            logger.error(f"list_datatype_properties failed: {e}")
            return []

        props = []
        for row in results:
            prop_uri = row.get("prop", "")
            if not prop_uri:
                continue

            characteristics = self._get_property_characteristics(prop_uri, tbox_graph)
            domain_uri = row.get("domain", "")
            range_uri = row.get("range", "")

            props.append(DataPropertyResponse(
                id=self._local_name(prop_uri),
                name=self._local_name(prop_uri),
                display_name=row.get("label", ""),
                description="",
                domain_ids=[self._local_name(domain_uri)] if domain_uri else [],
                range_type=self._local_name(range_uri) if range_uri else "string",
                characteristics=characteristics,
                annotations={},
            ))

        return props

    def create_datatype_property(
        self,
        base_iri: str,
        prop_local_name: str,
        domain_local_name: str,
        range_type: str = "string",
        display_name: str = None,
        characteristics: list[str] = None,
    ) -> bool:
        """
        创建数据属性（POST 到 tbox 图）

        Args:
            base_iri: 本体 base IRI
            prop_local_name: 属性局部名称
            domain_local_name: 定义域类局部名称
            range_type: 数据类型
            display_name: 显示名称
            characteristics: 属性特性列表

        Returns:
            bool: 是否成功
        """
        tbox_graph = _tbox_uri(base_iri)
        prop_uri = f"{base_iri}{prop_local_name}"
        domain_uri = f"{base_iri}{domain_local_name}"
        xsd_range = f"http://www.w3.org/2001/XMLSchema#{range_type}"

        triples = [
            f"<{prop_uri}> <{RDF.type}> <{OWL.DatatypeProperty}> .",
            f'<{prop_uri}> <{RDFS.label}> "{display_name or prop_local_name}" .',
            f"<{prop_uri}> <{RDFS.domain}> <{domain_uri}> .",
            f"<{prop_uri}> <{RDFS.range}> <{xsd_range}> .",
        ]

        if characteristics:
            char_map = {"functional": str(OWL.FunctionalProperty)}
            for char in characteristics:
                if char in char_map:
                    triples.append(f"<{prop_uri}> <{RDF.type}> <{char_map[char]}> .")

        rdf_data = "\n".join(triples)
        return self.graph_post(tbox_graph, rdf_data)

    def delete_datatype_property(self, prop_uri: str) -> bool:
        """
        删除数据属性（跨图操作）

        Args:
            prop_uri: 属性完整 URI

        Returns:
            bool: 是否成功
        """
        upd = f"DELETE WHERE {{ <{prop_uri}> ?p ?o }}"
        return self._update(upd)

    # ==================== 对象属性（tbox 图） ====================

    def list_object_properties(self, base_iri: str) -> list[ObjectPropertyResponse]:
        """
        列出本体所有对象属性（从 tbox 图查询）

        Args:
            base_iri: 本体 base IRI

        Returns:
            list[ObjectPropertyResponse]
        """
        tbox_graph = _tbox_uri(base_iri)

        q = f"""
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?prop ?label ?domain ?range
        FROM NAMED <{tbox_graph}>
        WHERE {{
            GRAPH <{tbox_graph}> {{
                ?prop a owl:ObjectProperty .
                FILTER(STRSTARTS(STR(?prop), "{base_iri}"))
                OPTIONAL {{ ?prop rdfs:label ?label }}
                OPTIONAL {{ ?prop rdfs:domain ?domain }}
                OPTIONAL {{ ?prop rdfs:range ?range }}
            }}
        }}
        """
        try:
            results = self._query(q)
        except Exception as e:
            logger.error(f"list_object_properties failed: {e}")
            return []

        props = []
        for row in results:
            prop_uri = row.get("prop", "")
            if not prop_uri:
                continue

            characteristics = self._get_property_characteristics(prop_uri, tbox_graph)
            domain_uri = row.get("domain", "")
            range_uri = row.get("range", "")

            props.append(ObjectPropertyResponse(
                id=self._local_name(prop_uri),
                name=self._local_name(prop_uri),
                display_name=row.get("label", ""),
                description="",
                domain_ids=[self._local_name(domain_uri)] if domain_uri else [],
                range_ids=[self._local_name(range_uri)] if range_uri else [],
                characteristics=characteristics,
                annotations={},
            ))

        return props

    def create_object_property(
        self,
        base_iri: str,
        prop_local_name: str,
        domain_local_name: str,
        range_local_name: str,
        display_name: str = None,
        characteristics: list[str] = None,
        inverse_of_local_name: str = None,
    ) -> bool:
        """
        创建对象属性（POST 到 tbox 图）

        Args:
            base_iri: 本体 base IRI
            prop_local_name: 属性局部名称
            domain_local_name: 定义域类局部名称
            range_local_name: 值域类局部名称
            display_name: 显示名称
            characteristics: 属性特性列表
            inverse_of_local_name: 反向属性局部名称

        Returns:
            bool: 是否成功
        """
        tbox_graph = _tbox_uri(base_iri)
        prop_uri = f"{base_iri}{prop_local_name}"
        domain_uri = f"{base_iri}{domain_local_name}"
        range_uri = f"{base_iri}{range_local_name}"

        triples = [
            f"<{prop_uri}> <{RDF.type}> <{OWL.ObjectProperty}> .",
            f'<{prop_uri}> <{RDFS.label}> "{display_name or prop_local_name}" .',
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

        if inverse_of_local_name:
            inverse_uri = f"{base_iri}{inverse_of_local_name}"
            triples.append(f"<{prop_uri}> <{OWL.inverseOf}> <{inverse_uri}> .")

        rdf_data = "\n".join(triples)
        return self.graph_post(tbox_graph, rdf_data)

    def delete_object_property(self, prop_uri: str) -> bool:
        """
        删除对象属性（跨图操作）

        Args:
            prop_uri: 属性完整 URI

        Returns:
            bool: 是否成功
        """
        upd = f"DELETE WHERE {{ <{prop_uri}> ?p ?o }}"
        return self._update(upd)

    # ==================== 注解属性（tbox 图） ====================

    def list_annotation_properties(self, base_iri: str) -> list:
        """
        列出本体所有注解属性（从 tbox 图查询）

        Args:
            base_iri: 本体 base IRI

        Returns:
            list[dict]
        """
        tbox_graph = _tbox_uri(base_iri)

        q = f"""
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?prop ?label
        FROM NAMED <{tbox_graph}>
        WHERE {{
            GRAPH <{tbox_graph}> {{
                ?prop a owl:AnnotationProperty .
                FILTER(STRSTARTS(STR(?prop), "{base_iri}"))
                OPTIONAL {{ ?prop rdfs:label ?label }}
            }}
        }}
        """
        try:
            results = self._query(q)
        except Exception as e:
            logger.error(f"list_annotation_properties failed: {e}")
            return []

        props = []
        for row in results:
            prop_uri = row.get("prop", "")
            if not prop_uri:
                continue
            props.append({
                "id": self._local_name(prop_uri),
                "name": self._local_name(prop_uri),
                "displayName": row.get("label", ""),
            })

        return props

    def delete_annotation_property(self, prop_uri: str) -> bool:
        """删除注解属性（跨图操作）"""
        upd = f"DELETE WHERE {{ <{prop_uri}> ?p ?o }}"
        return self._update(upd)

    # ==================== 辅助方法（带命名图限定） ====================

    def _get_super_classes(self, class_uri: str, tbox_graph: str = None) -> list[str]:
        q = f"""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?super
        """
        if tbox_graph:
            q += f" FROM NAMED <{tbox_graph}>"
            q += f" WHERE {{ GRAPH <{tbox_graph}> {{ <{class_uri}> rdfs:subClassOf ?super }} }}"
        else:
            q += f" WHERE {{ <{class_uri}> rdfs:subClassOf ?super }}"
        try:
            results = self._query(q)
            return [self._local_name(row.get("super", "")) for row in results]
        except Exception:
            return []

    def _get_equivalent_classes(self, class_uri: str, tbox_graph: str = None) -> list[str]:
        q = f"""
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        SELECT ?eq
        """
        if tbox_graph:
            q += f" FROM NAMED <{tbox_graph}>"
            q += f" WHERE {{ GRAPH <{tbox_graph}> {{ <{class_uri}> owl:equivalentClass ?eq }} }}"
        else:
            q += f" WHERE {{ <{class_uri}> owl:equivalentClass ?eq }}"
        try:
            results = self._query(q)
            return [self._local_name(row.get("eq", "")) for row in results]
        except Exception:
            return []

    def _get_disjoint_classes(self, class_uri: str, tbox_graph: str = None) -> list[str]:
        q = f"""
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        SELECT ?disjoint
        """
        if tbox_graph:
            q += f" FROM NAMED <{tbox_graph}>"
            q += f" WHERE {{ GRAPH <{tbox_graph}> {{ <{class_uri}> owl:disjointWith ?disjoint }} }}"
        else:
            q += f" WHERE {{ <{class_uri}> owl:disjointWith ?disjoint }}"
        try:
            results = self._query(q)
            return [self._local_name(row.get("disjoint", "")) for row in results]
        except Exception:
            return []

    def _get_property_characteristics(self, prop_uri: str, tbox_graph: str = None) -> list[str]:
        q = f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT ?type
        """
        if tbox_graph:
            q += f" FROM NAMED <{tbox_graph}>"
            q += f" WHERE {{ GRAPH <{tbox_graph}> {{ <{prop_uri}> rdf:type ?type }} }}"
        else:
            q += f" WHERE {{ <{prop_uri}> rdf:type ?type }}"
        try:
            results = self._query(q)
        except Exception:
            return []

        char_map = {
            "FunctionalProperty": "functional",
            "InverseFunctionalProperty": "inverseFunctional",
            "TransitiveProperty": "transitive",
            "SymmetricProperty": "symmetric",
        }

        chars = []
        for row in results:
            type_uri = row.get("type", "")
            local = self._local_name(type_uri)
            if local in char_map:
                chars.append(char_map[local])

        return chars

    def _local_name(self, uri: str) -> str:
        if not uri:
            return ""
        if "#" in uri:
            return uri.split("#")[-1]
        return uri.split("/")[-1]
