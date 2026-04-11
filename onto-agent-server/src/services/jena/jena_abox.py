"""
Jena ABox 操作

提供 Individual、属性断言等 ABox 层的 SPARQL 操作
"""

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.services.jena.jena_base import JenaBaseClient

from rdflib import RDF

from src.logging_config import get_logger

logger = get_logger("jena.abox")


# ============================================================================
# JenaABoxMixin
# ============================================================================

class JenaABoxMixin:
    """Jena ABox 操作 Mixin"""
    
    base: "JenaBaseClient"  # 来自 JenaBaseClient
    
    # ==================== Individual 操作 ====================
    
    def list_individuals(
        self,
        ontology_iri: str,
        class_id: str = None,
        search: str = None,
    ) -> list[dict]:
        """
        列出本体所有 Individual
        
        Args:
            ontology_iri: 本体 IRI 前缀
            class_id: 可选，按类筛选
            search: 可选，按名称/标签搜索
        """
        filters = []
        
        # 按类型筛选
        if class_id:
            class_uri = f"{ontology_iri}{class_id}"
            filters.append(f'FILTER(EXISTS {{ ?ind rdf:type <{class_uri}> }})')
        
        # 按名称/标签搜索
        if search:
            filters.append(f'FILTER(CONTAINS(LCASE(STR(?label)), LCASE("{search}")))')
        
        filter_str = " . " + " . ".join(filters) if filters else ""
        
        q = f"""
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT ?ind ?label ?comment WHERE {{
            ?ind a owl:NamedIndividual .
            FILTER(STRSTARTS(STR(?ind), "{ontology_iri}"))
            OPTIONAL {{ ?ind rdfs:label ?label }}
            OPTIONAL {{ ?ind rdfs:comment ?comment }}
            {filter_str}
        }}
        """
        results = self._query(q)
        
        individuals = []
        for row in results:
            ind_uri = row.get("ind", {}).get("value", "")
            types = self._get_individual_types(ind_uri)
            data_props = self._get_individual_data_properties(ind_uri)
            obj_props = self._get_individual_object_properties(ind_uri)
            
            individuals.append({
                "id": self._local_name(ind_uri),
                "ontology_id": self._ontology_id(ind_uri),
                "name": self._local_name(ind_uri),
                "display_name": row.get("label", {}).get("value", ""),
                "description": row.get("comment", {}).get("value", ""),
                "types": types,
                "labels": {},
                "comments": {},
                "data_property_assertions": data_props,
                "object_property_assertions": obj_props,
            })
        
        return individuals
    
    def create_individual(
        self,
        individual_uri: str,
        class_uris: list[str],
        display_name: str = None,
        data_property_assertions: list[dict] = None,
        object_property_assertions: list[dict] = None,
        abox_graph_uri: str = None,
    ) -> bool:
        """
        创建 Individual
        
        Args:
            individual_uri: Individual URI
            class_uris: 类型列表（owl:Class 的 URI）
            display_name: 显示名称
            data_property_assertions: [{"propertyUri": "...", "value": "..."}]
            object_property_assertions: [{"propertyUri": "...", "targetUri": "..."}]
            abox_graph_uri: ABox 命名图 URI
        """
        triples = [
            f"<{individual_uri}> <{RDF.type}> <http://www.w3.org/2002/07/owl#NamedIndividual> .",
        ]
        
        # 添加类型
        for class_uri in class_uris:
            triples.append(f"<{individual_uri}> <{RDF.type}> <{class_uri}> .")
        
        # 添加显示名称
        if display_name:
            triples.append(f'<{individual_uri}> <http://www.w3.org/2000/01/rdf-schema#label> "{display_name}" .')
        
        # 添加数据属性断言
        if data_property_assertions:
            for assertion in data_property_assertions:
                prop_uri = assertion.get("propertyUri", "")
                value = assertion.get("value", "")
                triples.append(f'<{individual_uri}> <{prop_uri}> "{value}" .')
        
        # 添加对象属性断言
        if object_property_assertions:
            for assertion in object_property_assertions:
                prop_uri = assertion.get("propertyUri", "")
                target_uri = assertion.get("targetUri", "")
                triples.append(f"<{individual_uri}> <{prop_uri}> <{target_uri}> .")
        
        triples_str = " ".join(triples)
        if abox_graph_uri:
            upd = f"INSERT DATA {{ GRAPH <{abox_graph_uri}> {{ {triples_str} }} }}"
        else:
            upd = f"INSERT DATA {{ {triples_str} }}"
        return self._update(upd)
    
    def delete_individual(self, individual_uri: str) -> bool:
        """删除 Individual"""
        upd = f"DELETE WHERE {{ <{individual_uri}> ?p ?o }}"
        return self._update(upd)
    
    # ==================== 属性断言 ====================
    
    def _get_individual_data_properties(self, ind_uri: str) -> list[dict]:
        """获取 Individual 的数据属性断言"""
        q = f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT ?prop ?value WHERE {{
            <{ind_uri}> ?prop ?value .
            FILTER(IsLiteral(?value))
        }}
        """
        results = self._query(q)
        props = []
        for row in results:
            prop_uri = row.get("prop", {}).get("value", "")
            props.append({
                "propertyId": self._local_name(prop_uri),
                "value": str(row.get("value", {}).get("value", "")),
            })
        return props
    
    def _get_individual_object_properties(self, ind_uri: str) -> list[dict]:
        """获取 Individual 的对象属性断言"""
        q = f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT ?prop ?target WHERE {{
            <{ind_uri}> ?prop ?target .
            FILTER(IsIRI(?target))
        }}
        """
        results = self._query(q)
        props = []
        for row in results:
            prop_uri = row.get("prop", {}).get("value", "")
            target_uri = row.get("target", {}).get("value", "")
            # 跳过 rdf:type
            if self._local_name(prop_uri) not in ["type"]:
                props.append({
                    "propertyId": self._local_name(prop_uri),
                    "targetIndividualId": self._local_name(target_uri),
                })
        return props
    
    def _get_individual_types(self, ind_uri: str) -> list[str]:
        """获取 Individual 的类型"""
        q = f"PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> SELECT ?type WHERE {{ <{ind_uri}> rdf:type ?type }}"
        results = self._query(q)
        return [
            self._local_name(row.get("type", {}).get("value", ""))
            for row in results
            if self._local_name(row.get("type", {}).get("value", "")) != "NamedIndividual"
        ]
    
    # ==================== 辅助方法 ====================
    
    def _local_name(self, uri: str) -> str:
        if not uri:
            return ""
        if "#" in uri:
            return uri.split("#")[-1]
        return uri.split("/")[-1]
    
    def _ontology_id(self, uri: str) -> str:
        if not uri:
            return ""
        parts = uri.replace("http://", "").replace("https://", "").split("/")
        if len(parts) >= 2:
            return parts[-2]
        return parts[-1].split("#")[0]
