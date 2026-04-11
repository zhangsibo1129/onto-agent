"""
Jena TBox 操作

提供类、属性、本体等 TBox 层的 SPARQL 操作
"""

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.services.jena.jena_base import JenaBaseClient

from rdflib import RDF, RDFS, OWL

from src.schemas.ontology import (
    OntologyClassResponse,
    DataPropertyResponse,
    ObjectPropertyResponse,
    OntologyResponse,
    OntologyDetailResponse,
)
from src.logging_config import get_logger

logger = get_logger("jena.tbox")


# ============================================================================
# JenaTBoxMixin
# ============================================================================

class JenaTBoxMixin:
    """Jena TBox 操作 Mixin"""
    
    base: "JenaBaseClient"  # 来自 JenaBaseClient
    
    # ==================== 本体操作 ====================
    
    def list_ontologies(self) -> list[dict]:
        """列出所有本体（从 Jena 中查询）"""
        q = """
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT DISTINCT ?ont ?label ?comment
        WHERE {
            ?ont a owl:Ontology .
            OPTIONAL { ?ont rdfs:label ?label }
            OPTIONAL { ?ont rdfs:comment ?comment }
        }
        """
        return self._query(q)
    
    def get_ontology_detail(self, ontology_iri: str) -> dict:
        """获取本体完整详情"""
        meta_q = f"""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?label ?comment WHERE {{
            OPTIONAL {{ <{ontology_iri}> rdfs:label ?label }}
            OPTIONAL {{ <{ontology_iri}> rdfs:comment ?comment }}
        }}
        LIMIT 1
        """
        meta_results = self._query(meta_q)
        
        classes = self.list_classes(ontology_iri)
        data_properties = self.list_datatype_properties(ontology_iri)
        object_properties = self.list_object_properties(ontology_iri)
        annotation_properties = self.list_annotation_properties(ontology_iri)
        individuals = self.list_individuals(ontology_iri)
        
        meta = meta_results[0] if meta_results else {}
        
        return {
            "label": meta.get("label", {}).get("value", ""),
            "comment": meta.get("comment", {}).get("value", ""),
            "classes": classes,
            "dataProperties": data_properties,
            "objectProperties": object_properties,
            "annotationProperties": annotation_properties,
            "individuals": individuals,
        }
    
    # ==================== 类操作 ====================
    
    def list_classes(self, ontology_iri: str) -> list[OntologyClassResponse]:
        """列出本体所有类"""
        q = f"""
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT DISTINCT ?class ?label ?comment
        WHERE {{
            ?class a owl:Class .
            FILTER(STRSTARTS(STR(?class), "{ontology_iri}"))
            OPTIONAL {{ ?class rdfs:label ?label }}
            OPTIONAL {{ ?class rdfs:comment ?comment }}
        }}
        """
        results = self._query(q)
        
        classes = []
        for row in results:
            class_uri = row.get("class", {}).get("value", "")
            super_classes = self._get_super_classes(class_uri)
            equivalent = self._get_equivalent_classes(class_uri)
            disjoint = self._get_disjoint_classes(class_uri)
            
            classes.append(OntologyClassResponse(
                id=self._local_name(class_uri),
                name=self._local_name(class_uri),
                display_name=row.get("label", {}).get("value", ""),
                description=row.get("comment", {}).get("value", ""),
                super_classes=super_classes,
                equivalent_to=equivalent,
                disjoint_with=disjoint,
                annotations={},
            ))
        
        return classes
    
    def create_class(
        self,
        class_uri: str,
        display_name: str = None,
        description: str = None,
        super_class_uris: list[str] = None,
    ) -> bool:
        """创建 OWL 类"""
        triples = [
            f"<{class_uri}> <{RDF.type}> <{OWL.Class}> .",
            f"<{class_uri}> <{RDFS.label}> \"{display_name or self._local_name(class_uri)}\" .",
        ]
        if description:
            triples.append(f"<{class_uri}> <{RDFS.comment}> \"{description}\" .")
        if super_class_uris:
            for sc_uri in super_class_uris:
                triples.append(f"<{class_uri}> <{RDFS.subClassOf}> <{sc_uri}> .")
        
        upd = "INSERT DATA { " + " ".join(triples) + " }"
        return self._update(upd)
    
    def update_class(
        self,
        class_uri: str,
        display_name: str = None,
        description: str = None,
    ) -> bool:
        """更新类定义"""
        if display_name:
            upd = f"""
            DELETE {{ <{class_uri}> <{RDFS.label}> ?old }}
            INSERT {{ <{class_uri}> <{RDFS.label}> \"{display_name}\" }}
            WHERE {{ <{class_uri}> <{RDFS.label}> ?old }}
            """
            self._update(upd)
        
        if description:
            upd = f"""
            DELETE {{ <{class_uri}> <{RDFS.comment}> ?old }}
            INSERT {{ <{class_uri}> <{RDFS.comment}> \"{description}\" }}
            WHERE {{ <{class_uri}> <{RDFS.comment}> ?old }}
            """
            self._update(upd)
        
        return True
    
    def delete_class(self, class_uri: str) -> bool:
        """删除类"""
        upd = f"DELETE WHERE {{ <{class_uri}> ?p ?o }}"
        return self._update(upd)
    
    # ==================== 数据属性 ====================
    
    def list_datatype_properties(self, ontology_iri: str) -> list[DataPropertyResponse]:
        """列出本体所有数据属性"""
        q = f"""
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?prop ?label ?domain ?range
        WHERE {{
            ?prop a owl:DatatypeProperty .
            FILTER(STRSTARTS(STR(?prop), "{ontology_iri}"))
            OPTIONAL {{ ?prop rdfs:label ?label }}
            OPTIONAL {{ ?prop rdfs:domain ?domain }}
            OPTIONAL {{ ?prop rdfs:range ?range }}
        }}
        """
        results = self._query(q)
        
        props = []
        for row in results:
            prop_uri = row.get("prop", {}).get("value", "")
            characteristics = self._get_property_characteristics(prop_uri)
            
            domain_uri = row.get("domain", {}).get("value", "")
            range_uri = row.get("range", {}).get("value", "")
            
            props.append(DataPropertyResponse(
                id=self._local_name(prop_uri),
                name=self._local_name(prop_uri),
                display_name=row.get("label", {}).get("value", ""),
                description="",
                domain_ids=[self._local_name(domain_uri)] if domain_uri else [],
                range_type=self._local_name(range_uri) if range_uri else "string",
                characteristics=characteristics,
                annotations={},
            ))
        
        return props
    
    def create_datatype_property(
        self,
        prop_uri: str,
        domain_uri: str,
        range_type: str = "string",
        display_name: str = None,
        characteristics: list[str] = None,
    ) -> bool:
        """创建数据属性"""
        xsd_range = f"http://www.w3.org/2001/XMLSchema#{range_type}"
        
        triples = [
            f"<{prop_uri}> <{RDF.type}> <{OWL.DatatypeProperty}> .",
            f"<{prop_uri}> <{RDFS.label}> \"{display_name or self._local_name(prop_uri)}\" .",
            f"<{prop_uri}> <{RDFS.domain}> <{domain_uri}> .",
            f"<{prop_uri}> <{RDFS.range}> <{xsd_range}> .",
        ]
        
        if characteristics:
            char_map = {"functional": str(OWL.FunctionalProperty)}
            for char in characteristics:
                if char in char_map:
                    triples.append(f"<{prop_uri}> <{RDF.type}> <{char_map[char]}> .")
        
        upd = "INSERT DATA { " + " ".join(triples) + " }"
        return self._update(upd)
    
    def delete_datatype_property(self, prop_uri: str) -> bool:
        """删除数据属性"""
        upd = f"DELETE WHERE {{ <{prop_uri}> ?p ?o }}"
        return self._update(upd)
    
    # ==================== 对象属性 ====================
    
    def list_object_properties(self, ontology_iri: str) -> list[ObjectPropertyResponse]:
        """列出本体所有对象属性"""
        q = f"""
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?prop ?label ?domain ?range
        WHERE {{
            ?prop a owl:ObjectProperty .
            FILTER(STRSTARTS(STR(?prop), "{ontology_iri}"))
            OPTIONAL {{ ?prop rdfs:label ?label }}
            OPTIONAL {{ ?prop rdfs:domain ?domain }}
            OPTIONAL {{ ?prop rdfs:range ?range }}
        }}
        """
        results = self._query(q)
        
        props = []
        for row in results:
            prop_uri = row.get("prop", {}).get("value", "")
            characteristics = self._get_property_characteristics(prop_uri)
            
            domain_uri = row.get("domain", {}).get("value", "")
            range_uri = row.get("range", {}).get("value", "")
            
            props.append(ObjectPropertyResponse(
                id=self._local_name(prop_uri),
                name=self._local_name(prop_uri),
                display_name=row.get("label", {}).get("value", ""),
                description="",
                domain_ids=[self._local_name(domain_uri)] if domain_uri else [],
                range_ids=[self._local_name(range_uri)] if range_uri else [],
                characteristics=characteristics,
                annotations={},
            ))
        
        return props
    
    def create_object_property(
        self,
        prop_uri: str,
        domain_uri: str,
        range_uri: str,
        display_name: str = None,
        characteristics: list[str] = None,
        inverse_of: str = None,
    ) -> bool:
        """创建对象属性"""
        triples = [
            f"<{prop_uri}> <{RDF.type}> <{OWL.ObjectProperty}> .",
            f"<{prop_uri}> <{RDFS.label}> \"{display_name or self._local_name(prop_uri)}\" .",
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
        
        upd = "INSERT DATA { " + " ".join(triples) + " }"
        return self._update(upd)
    
    def delete_object_property(self, prop_uri: str) -> bool:
        """删除对象属性"""
        upd = f"DELETE WHERE {{ <{prop_uri}> ?p ?o }}"
        return self._update(upd)
    
    # ==================== 注解属性 ====================
    
    def list_annotation_properties(self, ontology_iri: str) -> list:
        """列出本体所有注解属性"""
        q = f"""
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?prop ?label
        WHERE {{
            ?prop a owl:AnnotationProperty .
            FILTER(STRSTARTS(STR(?prop), "{ontology_iri}"))
            OPTIONAL {{ ?prop rdfs:label ?label }}
        }}
        """
        results = self._query(q)
        
        props = []
        for row in results:
            prop_uri = row.get("prop", {}).get("value", "")
            props.append({
                "id": self._local_name(prop_uri),
                "name": self._local_name(prop_uri),
                "displayName": row.get("label", {}).get("value", ""),
            })
        
        return props
    
    def delete_annotation_property(self, prop_uri: str) -> bool:
        """删除注解属性"""
        upd = f"DELETE WHERE {{ <{prop_uri}> ?p ?o }}"
        return self._update(upd)
    
    # ==================== 辅助方法 ====================
    
    def _get_label(self, uri: str) -> Optional[str]:
        q = f"PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> SELECT ?label WHERE {{ <{uri}> rdfs:label ?label }} LIMIT 1"
        results = self._query(q)
        return results[0].get("label", {}).get("value") if results else None
    
    def _get_comment(self, uri: str) -> Optional[str]:
        q = f"PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> SELECT ?comment WHERE {{ <{uri}> rdfs:comment ?comment }} LIMIT 1"
        results = self._query(q)
        return results[0].get("comment", {}).get("value") if results else None
    
    def _get_super_classes(self, class_uri: str) -> list[str]:
        q = f"PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> SELECT ?super WHERE {{ <{class_uri}> rdfs:subClassOf ?super }}"
        results = self._query(q)
        return [self._local_name(row.get("super", {}).get("value", "")) for row in results]
    
    def _get_equivalent_classes(self, class_uri: str) -> list[str]:
        q = f"PREFIX owl: <http://www.w3.org/2002/07/owl#> SELECT ?eq WHERE {{ <{class_uri}> owl:equivalentClass ?eq }}"
        results = self._query(q)
        return [self._local_name(row.get("eq", {}).get("value", "")) for row in results]
    
    def _get_disjoint_classes(self, class_uri: str) -> list[str]:
        q = f"PREFIX owl: <http://www.w3.org/2002/07/owl#> SELECT ?disjoint WHERE {{ <{class_uri}> owl:disjointWith ?disjoint }}"
        results = self._query(q)
        return [self._local_name(row.get("disjoint", {}).get("value", "")) for row in results]
    
    def _get_property_characteristics(self, prop_uri: str) -> list[str]:
        q = f"PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> SELECT ?type WHERE {{ <{prop_uri}> rdf:type ?type }}"
        results = self._query(q)
        
        char_map = {
            "FunctionalProperty": "functional",
            "InverseFunctionalProperty": "inverseFunctional",
            "TransitiveProperty": "transitive",
            "SymmetricProperty": "symmetric",
        }
        
        chars = []
        for row in results:
            type_uri = row.get("type", {}).get("value", "")
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
