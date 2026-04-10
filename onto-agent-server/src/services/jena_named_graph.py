"""
Jena Named Graph 扩展模块

提供 Named Graph 操作的便捷方法，支持版本管理
"""

from typing import Optional
from rdflib import RDF, RDFS, OWL

# 默认共享 Dataset
DEFAULT_DATASET = "/onto-agent"


def inject_named_graph_methods(cls):
    """将 Named Graph 方法注入到 JenaClient 类"""
    
    # ==================== Named Graph 基础方法 ====================
    
    def list_named_graphs(self) -> list[dict]:
        """
        列出当前 Dataset 中所有命名图
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
                    "uri": row.get("graph", {}).get("value", ""),
                    "triple_count": int(row.get("tripleCount", {}).get("value", 0))
                }
                for row in results
            ]
        except Exception:
            return []

    def insert_named_graph(self, graph_uri: str, triples: str) -> bool:
        """
        向指定命名图插入三元组
        
        Args:
            graph_uri: 命名图 URI
            triples: SPARQL 三元组字符串（不含 GRAPH 包装）
        
        Returns:
            bool: 插入是否成功
        """
        upd = f"""
        INSERT DATA {{ GRAPH <{graph_uri}> {{ {triples} }} }}
        """
        try:
            return self._update(upd)
        except Exception as e:
            print(f"[Jena] Insert to named graph failed: {e}")
            return False

    def delete_named_graph(self, graph_uri: str) -> bool:
        """
        删除命名图（清除所有三元组）
        """
        upd = f"""
        DROP SILENT GRAPH <{graph_uri}>
        """
        try:
            return self._update(upd)
        except Exception as e:
            print(f"[Jena] Delete named graph failed: {e}")
            return False

    def query_named_graph(self, graph_uri: str, where_clause: str) -> list[dict]:
        """
        查询指定命名图
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
            print(f"[Jena] Query named graph failed: {e}")
            return []

    def copy_graph(self, source_graph: str, target_graph: str) -> bool:
        """
        复制源命名图到目标命名图（用于版本快照）
        """
        # 先清空目标图（如果存在）
        self._update(f"DROP SILENT GRAPH <{target_graph}>")
        
        # 复制数据
        upd = f"""
        WITH <{source_graph}>
        INSERT GRAPH <{target_graph}> {{ ?s ?p ?o }}
        WHERE {{ ?s ?p ?o }}
        """
        try:
            return self._update(upd)
        except Exception as e:
            print(f"[Jena] Copy graph failed: {e}")
            return False

    # ==================== TBox 便捷方法 ====================

    def create_ontology_tbox(self, ontology_iri: str, name: str, description: str = None) -> bool:
        """
        创建本体 TBox 命名图
        """
        graph_uri = f"{ontology_iri}tbox"
        
        triples = [
            (ontology_iri, str(RDF.type), str(OWL.Ontology)),
            (ontology_iri, str(RDFS.label), f'"{name}"'),
        ]
        if description:
            triples.append((ontology_iri, str(RDFS.comment), f'"{description}"'))
        
        triples_str = "\n".join(f"<{s}> <{p}> {o} ." for s, p, o in triples)
        return self.insert_named_graph(graph_uri, triples_str)

    def add_class_to_tbox(self, tbox_graph_uri: str, class_uri: str, 
                          display_name: str = None, description: str = None,
                          super_classes: list = None) -> bool:
        """
        向 TBox 命名图添加类定义
        """
        triples = [
            (class_uri, str(RDF.type), str(OWL.Class)),
            (class_uri, str(RDFS.label), f'"{display_name or class_uri.split("#")[-1]}"'),
        ]
        if description:
            triples.append((class_uri, str(RDFS.comment), f'"{description}"'))
        if super_classes:
            for sc in super_classes:
                triples.append((class_uri, str(RDFS.subClassOf), f"<{sc}>"))
        
        triples_str = "\n".join(f"<{s}> <{p}> {o} ." for s, p, o in triples)
        return self.insert_named_graph(tbox_graph_uri, triples_str)

    def add_datatype_property_to_tbox(self, tbox_graph_uri: str, prop_uri: str,
                                       domain_uri: str, range_type: str,
                                       display_name: str = None,
                                       characteristics: list = None) -> bool:
        """
        向 TBox 命名图添加数据属性
        """
        xsd_range = f"http://www.w3.org/2001/XMLSchema#{range_type}"
        
        triples = [
            (prop_uri, str(RDF.type), str(OWL.DatatypeProperty)),
            (prop_uri, str(RDFS.label), f'"{display_name or prop_uri.split("#")[-1]}"'),
            (prop_uri, str(RDFS.domain), f"<{domain_uri}>"),
            (prop_uri, str(RDFS.range), f"<{xsd_range}>"),
        ]
        
        if characteristics:
            char_map = {"functional": str(OWL.FunctionalProperty)}
            for char in characteristics:
                if char in char_map:
                    triples.append((prop_uri, str(RDF.type), char_map[char]))
        
        triples_str = "\n".join(f"<{s}> <{p}> {o} ." for s, p, o in triples)
        return self.insert_named_graph(tbox_graph_uri, triples_str)

    def add_object_property_to_tbox(self, tbox_graph_uri: str, prop_uri: str,
                                    domain_uri: str, range_uri: str,
                                    display_name: str = None,
                                    characteristics: list = None,
                                    inverse_of: str = None) -> bool:
        """
        向 TBox 命名图添加对象属性
        """
        triples = [
            (prop_uri, str(RDF.type), str(OWL.ObjectProperty)),
            (prop_uri, str(RDFS.label), f'"{display_name or prop_uri.split("#")[-1]}"'),
            (prop_uri, str(RDFS.domain), f"<{domain_uri}>"),
            (prop_uri, str(RDFS.range), f"<{range_uri}>"),
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
                    triples.append((prop_uri, str(RDF.type), char_map[char]))
        
        if inverse_of:
            triples.append((prop_uri, str(OWL.inverseOf), f"<{inverse_of}>"))
        
        triples_str = "\n".join(f"<{s}> <{p}> {o} ." for s, p, o in triples)
        return self.insert_named_graph(tbox_graph_uri, triples_str)

    def delete_entity_from_tbox(self, entity_uri: str) -> bool:
        """
        从 TBox 删除实体（类/属性）
        """
        upd = f"""
        DELETE WHERE {{ <{entity_uri}> ?p ?o }}
        """
        try:
            return self._update(upd)
        except Exception as e:
            print(f"[Jena] Delete entity failed: {e}")
            return False

    # 注入方法到类
    cls.list_named_graphs = list_named_graphs
    cls.insert_named_graph = insert_named_graph
    cls.delete_named_graph = delete_named_graph
    cls.query_named_graph = query_named_graph
    cls.copy_graph = copy_graph
    cls.create_ontology_tbox = create_ontology_tbox
    cls.add_class_to_tbox = add_class_to_tbox
    cls.add_datatype_property_to_tbox = add_datatype_property_to_tbox
    cls.add_object_property_to_tbox = add_object_property_to_tbox
    cls.delete_entity_from_tbox = delete_entity_from_tbox
    
    return cls


# 在模块导入时自动注入
from src.services.jena_client import JenaClient
inject_named_graph_methods(JenaClient)


def get_jena_client_for_default_dataset():
    """
    获取默认共享 Dataset 的客户端
    
    使用统一的 /onto-agent dataset，支持 Named Graph 架构
    """
    from src.services.jena_client import get_jena_client_for_dataset
    return get_jena_client_for_dataset(DEFAULT_DATASET)
