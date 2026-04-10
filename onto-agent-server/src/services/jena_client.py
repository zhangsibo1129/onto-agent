"""
Ontology TBox Service using Apache Jena Fuseki + SPARQLWrapper

SPARQLWrapper 处理所有 SPARQL Protocol 通信（查询/更新）；
httpx 仅用于 Fuseki 管理接口（dataset 增删）。
"""

import sys as _sys
from os import getenv, environ
# 强制让 urllib/httpx 忽略系统代理，避免 localhost 请求被劫持到代理服务器
environ.setdefault("NO_PROXY", "localhost,127.0.0.1")
environ.setdefault("no_proxy", "localhost,127.0.0.1")

from dotenv import load_dotenv
from functools import lru_cache
from typing import Optional

import httpx

# SPARQLWrapper — 以 site-packages 方式安装时需要 path hack
_sparqlwrapper_path = ".venv/lib/python3.12/site-packages"
import os as _os
_vendor_root = _os.path.join(
    _os.path.dirname(_os.path.abspath(__file__)), "..", ".."
)
_full_sparql_path = _os.path.join(_vendor_root, _sparqlwrapper_path)
if _full_sparql_path not in _sys.path:
    _sys.path.insert(0, _full_sparql_path)

from SPARQLWrapper import SPARQLWrapper2, JSON, GET

from rdflib import URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL

from src.schemas.ontology import (
    OntologyClassResponse,
    DataPropertyResponse,
    ObjectPropertyResponse,
    OntologyResponse,
    OntologyDetailResponse,
)

load_dotenv()

# ============================================================================
# Fuseki Configuration
# ============================================================================


@lru_cache
def get_fuseki_settings() -> dict:
    return {
        "fuseki_url": getenv("FUSEKI_URL", "http://localhost:3030"),
        "username": getenv("FUSEKI_USER", "admin"),
        "password": getenv("FUSEKI_PASSWORD", ""),
    }


DEFAULT_FUSEKI_URL = "http://localhost:3030"

NAMESPACES = {
    "owl": "http://www.w3.org/2002/07/owl#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
}


# ============================================================================
# Exceptions
# ============================================================================


class JenaServiceError(Exception):
    pass


class JenaConnectionError(JenaServiceError):
    pass


class JenaQueryError(JenaServiceError):
    pass


# ============================================================================
# Helpers
# ============================================================================


def _get_auth():
    settings = get_fuseki_settings()
    if settings["username"] and settings["password"]:
        return httpx.BasicAuth(settings["username"], settings["password"])
    return None


def _fuseki_get(path: str, timeout: int = 10) -> httpx.Response:
    settings = get_fuseki_settings()
    return httpx.get(
        f"{settings['fuseki_url']}{path}",
        auth=_get_auth(),
        timeout=timeout,
        trust_env=False,
    )


def _fuseki_post(path: str, data: str = None, timeout: int = 30) -> httpx.Response:
    settings = get_fuseki_settings()
    kwargs = {"auth": _get_auth(), "timeout": timeout, "trust_env": False}
    if data:
        kwargs["data"] = data
        kwargs["headers"] = {"Content-Type": "application/x-www-form-urlencoded"}
    return httpx.post(f"{settings['fuseki_url']}{path}", **kwargs)


def _fuseki_delete(path: str, timeout: int = 10) -> httpx.Response:
    settings = get_fuseki_settings()
    return httpx.delete(
        f"{settings['fuseki_url']}{path}",
        auth=_get_auth(),
        timeout=timeout,
        trust_env=False,
    )


def _sparql_query(query: str, endpoint: str) -> list[dict]:
    """
    通过 SPARQLWrapper 执行 SELECT 查询，返回 bindings 列表。
    """
    sw = SPARQLWrapper2(endpoint)
    sw.setQuery(query)
    sw.setMethod(GET)
    sw.setReturnFormat(JSON)

    try:
        sw.query()
        # SPARQLWrapper2 返回的是 ResultSet dict-like object
        result = sw.queryAndConvert()
        # SPARQLWrapper2 returns a SmartWrapper.Bindings object:
        # access raw JSON via fullResult['results']['bindings']
        if hasattr(result, "fullResult"):
            return result.fullResult.get("results", {}).get("bindings", [])
        elif isinstance(result, dict):
            return result.get("results", {}).get("bindings", [])
        return []
    except Exception as e:
        raise JenaQueryError(f"SPARQL query failed: {e}")


def _sparql_update(update: str, endpoint: str) -> bool:
    """
    通过 httpx + SPARQL Update protocol 直连 /update 端点。
    SPARQLWrapper 对 SPARQL Update 支持不完整（/sparql 端点不支持
    application/sparql-update content type）。
    """
    import httpx  # Import regardless of auth settings
    settings = get_fuseki_settings()
    auth = None
    if settings["username"] and settings["password"]:
        auth = httpx.BasicAuth(settings["username"], settings["password"])

    try:
        r = httpx.post(
            endpoint,
            data=update.encode("utf-8"),
            headers={"Content-Type": "application/sparql-update"},
            auth=auth,
            timeout=30,
            trust_env=False,
        )
        if r.status_code not in (200, 204):
            raise JenaQueryError(f"SPARQL Update failed: {r.status_code} {r.text[:200]}")
        return True
    except Exception as e:
        raise JenaQueryError(f"SPARQL update failed: {e}")


# ============================================================================
# Jena Client
# ============================================================================


class JenaClient:
    """
    Jena Fuseki 客户端。

    管理操作（dataset 增删）用 httpx 直接调 Fuseki Admin API；
    实体操作（类/属性 CRUD）统一走 SPARQLWrapper + SPARQL Protocol。
    """

    def __init__(
        self,
        fuseki_url: str = DEFAULT_FUSEKI_URL,
        dataset: str = "/onto",
        timeout: int = 30,
        username: str = None,
        password: str = None,
    ):
        self.fuseki_url = fuseki_url.rstrip("/")
        self.dataset = dataset
        self.timeout = timeout

        settings = get_fuseki_settings()
        self.username = username or settings["username"]
        self.password = password or settings["password"]

        # SPARQL endpoints
        self.query_endpoint = f"{fuseki_url}{dataset}/sparql"
        self.update_endpoint = f"{fuseki_url}{dataset}/update"
        self.data_endpoint = f"{fuseki_url}{dataset}/data"

        self._health_check()

    def _health_check(self) -> bool:
        try:
            r = _fuseki_get("/$/ping", timeout=1)
            if r.status_code != 200:
                raise JenaConnectionError(f"Fuseki ping failed: {r.status_code}")
            return True
        except Exception as e:
            raise JenaConnectionError(f"Cannot connect to Fuseki: {e}")

    # -------------------------------------------------------------------------
    # Dataset Management (admin via httpx)
    # -------------------------------------------------------------------------

    def create_dataset(self, dataset: str) -> bool:
        name = dataset.lstrip("/")
        try:
            r = _fuseki_post(
                "/$/datasets",
                data=f"dbName={name}&dbType=tdb2",
                timeout=self.timeout,
            )
            return r.status_code in (200, 201)
        except Exception as e:
            raise JenaServiceError(f"Failed to create dataset {dataset}: {e}")

    def delete_dataset(self, dataset: str) -> bool:
        name = dataset.lstrip("/")
        try:
            r = _fuseki_delete(f"/$/datasets/{name}", timeout=self.timeout)
            return r.status_code in (200, 204)
        except Exception as e:
            raise JenaServiceError(f"Failed to delete dataset {dataset}: {e}")

    def list_datasets(self) -> list[dict]:
        try:
            r = _fuseki_get("/$/datasets", timeout=5)
            if r.status_code == 200:
                return r.json().get("datasets", [])
            return []
        except Exception:
            return []

    def switch_dataset(self, dataset: str) -> "JenaClient":
        return JenaClient(
            fuseki_url=self.fuseki_url,
            dataset=dataset,
            username=self.username,
            password=self.password,
        )

    # -------------------------------------------------------------------------
    # SPARQL Query helpers (via SPARQLWrapper)
    # -------------------------------------------------------------------------

    def _query(self, sparql: str) -> list[dict]:
        return _sparql_query(sparql, self.query_endpoint)

    def _update(self, sparql: str) -> bool:
        return _sparql_update(sparql, self.update_endpoint)

    # -------------------------------------------------------------------------
    # Ontology Operations
    # -------------------------------------------------------------------------

    def list_ontologies(self) -> list[dict]:
        q = """
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT DISTINCT ?ontology ?label ?comment
        WHERE {
            ?ontology a owl:Ontology .
            OPTIONAL { ?ontology rdfs:label ?label }
            OPTIONAL { ?ontology rdfs:comment ?comment }
        }
        """
        results = self._query(q)
        ontologies = []
        for row in results:
            uri = row.get("ontology", {}).get("value", "")
            ontologies.append({
                "base_iri": uri,
                "name": row.get("label", {}).get("value", "") or self._local_name(uri),
                "description": row.get("comment", {}).get("value", ""),
            })
        return ontologies

    def create_ontology(
        self,
        name: str,
        base_iri: str,
        description: Optional[str] = None,
    ) -> bool:
        # 使用 PREFIX 而非完整 URI
        triples = [
            (base_iri, "rdf:type", "owl:Ontology"),
            (base_iri, "rdfs:label", f'"{name}"'),
        ]
        if description:
            triples.append((base_iri, "rdfs:comment", f'"{description}"'))

        # URI 用 < >，字面量直接写
        triples_str = "\n".join(
            f"<{s}> <{p}> {o} ." for s, p, o in triples
        )
        upd = f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        INSERT DATA {{ {triples_str} }}
        """
        return self._update(upd)

    # -------------------------------------------------------------------------
    # Class Operations
    # -------------------------------------------------------------------------

    def list_classes(self, ontology_iri: str) -> list[OntologyClassResponse]:
        q = f"""
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT DISTINCT ?class
        WHERE {{
            ?class a owl:Class .
            FILTER(STRSTARTS(STR(?class), "{ontology_iri}"))
        }}
        """
        results = self._query(q)
        classes = []
        for row in results:
            class_uri = row.get("class", {}).get("value", "")
            label = self._get_label(class_uri) or self._local_name(class_uri)
            description = self._get_comment(class_uri) or ""
            super_classes = self._get_super_classes(class_uri)

            classes.append(
                OntologyClassResponse(
                    id=self._local_name(class_uri),
                    ontology_id=self._ontology_id(class_uri),
                    name=self._local_name(class_uri),
                    display_name=label,
                    description=description,
                    labels={},
                    comments={},
                    equivalent_to=[],
                    disjoint_with=[],
                    super_classes=super_classes,
                )
            )
        return classes

    def create_class(
        self,
        ontology_iri: str,
        name: str,
        display_name: Optional[str] = None,
        description: Optional[str] = None,
        super_classes: Optional[list[str]] = None,
    ) -> OntologyClassResponse:
        class_uri = f"{ontology_iri}{name}"
        label = display_name or name

        triples = [
            (class_uri, str(RDF.type), str(OWL.Class)),
            (class_uri, str(RDFS.label), f'"{label}"'),
        ]
        if description:
            triples.append((class_uri, str(RDFS.comment), f'"{description}"'))
        if super_classes:
            for sc in super_classes:
                triples.append((class_uri, str(RDFS.subClassOf), f"<{sc}>"))

        triples_str = "\n".join(f"<{s}> <{p}> <{o}> ." for s, p, o in triples)
        upd = f"""
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        INSERT DATA {{ {triples_str} }}
        """
        self._update(upd)

        return OntologyClassResponse(
            id=name,
            ontology_id=self._ontology_id(class_uri),
            name=name,
            display_name=label,
            description=description,
            labels={},
            comments={},
            equivalent_to=[],
            disjoint_with=[],
            super_classes=[self._local_name(sc) for sc in (super_classes or [])],
        )

    def get_class(self, class_uri: str) -> Optional[OntologyClassResponse]:
        q = f"""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?label ?comment WHERE {{
            OPTIONAL {{ <{{}}> rdfs:label ?label }}
            OPTIONAL {{ <{{}}> rdfs:comment ?comment }}
        }}
        """.format(class_uri, class_uri)

        results = self._query(q)
        if not results:
            return None

        label = results[0].get("label", {}).get("value", "")
        comment = results[0].get("comment", {}).get("value", "")

        return OntologyClassResponse(
            id=self._local_name(class_uri),
            ontology_id=self._ontology_id(class_uri),
            name=self._local_name(class_uri),
            display_name=label,
            description=comment,
            labels={},
            comments={},
            equivalent_to=self._get_equivalent_classes(class_uri),
            disjoint_with=self._get_disjoint_classes(class_uri),
            super_classes=self._get_super_classes(class_uri),
        )

    def update_class(
        self,
        class_uri: str,
        display_name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> bool:
        if not display_name and not description:
            return True

        # DELETE old label/comment
        del_parts = []
        ins_parts = []
        if display_name:
            del_parts.append(f"<{class_uri}> <{RDFS.label}> ?l .")
            ins_parts.append(f"<{class_uri}> <{RDFS.label}> \"{display_name}\" .")
        if description:
            del_parts.append(f"<{class_uri}> <{RDFS.comment}> ?c .")
            ins_parts.append(f"<{class_uri}> <{RDFS.comment}> \"{description}\" .")

        upd = f"""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        DELETE {{ {" ".join(del_parts)} }}
        INSERT {{ {" ".join(ins_parts)} }}
        WHERE {{ {" ".join(del_parts)} }}
        """
        return self._update(upd)

    def delete_class(self, class_uri: str) -> bool:
        upd = f"""
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        DELETE {{ <{class_uri}> ?p ?o }}
        WHERE {{ <{class_uri}> ?p ?o }}
        """
        return self._update(upd)

    # -------------------------------------------------------------------------
    # Datatype Property Operations
    # -------------------------------------------------------------------------

    def list_datatype_properties(self, ontology_iri: str) -> list[DataPropertyResponse]:
        q = f"""
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?prop ?label ?domain ?range WHERE {{
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
            chars = self._get_property_characteristics(prop_uri)
            domain_uri = row.get("domain", {}).get("value", "")
            range_uri = row.get("range", {}).get("value", "")

            props.append(
                DataPropertyResponse(
                    id=self._local_name(prop_uri),
                    ontology_id=self._ontology_id(prop_uri),
                    name=self._local_name(prop_uri),
                    display_name=row.get("label", {}).get("value", ""),
                    description="",
                    labels={},
                    comments={},
                    domain_ids=[self._local_name(domain_uri)] if domain_uri else [],
                    range_type=self._local_name(range_uri) or "string",
                    characteristics=chars,
                    super_property_id=None,
                )
            )
        return props

    def create_datatype_property(
        self,
        ontology_iri: str,
        name: str,
        domain_iri: str,
        range_type: str = "string",
        display_name: Optional[str] = None,
        characteristics: Optional[list[str]] = None,
    ) -> DataPropertyResponse:
        prop_uri = f"{ontology_iri}{name}"
        label = display_name or name
        xsd_range = f"http://www.w3.org/2001/XMLSchema#{range_type}"

        triples = [
            (prop_uri, str(RDF.type), str(OWL.DatatypeProperty)),
            (prop_uri, str(RDFS.label), f'"{label}"'),
            (prop_uri, str(RDFS.domain), f"<{domain_iri}>"),
            (prop_uri, str(RDFS.range), f"<{xsd_range}>"),
        ]

        if characteristics:
            char_map = {
                "functional": str(OWL.FunctionalProperty),
            }
            for char in characteristics:
                if char in char_map:
                    triples.append((prop_uri, str(RDF.type), char_map[char]))

        triples_str = "\n".join(f"<{s}> <{p}> <{o}> ." for s, p, o in triples)
        upd = f"""
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        INSERT DATA {{ {triples_str} }}
        """
        self._update(upd)

        return DataPropertyResponse(
            id=name,
            ontology_id=self._ontology_id(prop_uri),
            name=name,
            display_name=label,
            description="",
            labels={},
            comments={},
            domain_ids=[self._local_name(domain_iri)],
            range_type=range_type,
            characteristics=characteristics or [],
            super_property_id=None,
        )

    def delete_datatype_property(self, prop_uri: str) -> bool:
        upd = f"""
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        DELETE {{ <{prop_uri}> ?p ?o }}
        WHERE {{ <{prop_uri}> ?p ?o }}
        """
        return self._update(upd)

    # -------------------------------------------------------------------------
    # Object Property Operations
    # -------------------------------------------------------------------------

    def list_object_properties(self, ontology_iri: str) -> list[ObjectPropertyResponse]:
        q = f"""
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?prop ?label ?domain ?range WHERE {{
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
            chars = self._get_property_characteristics(prop_uri)
            domain_uri = row.get("domain", {}).get("value", "")
            range_uri = row.get("range", {}).get("value", "")

            props.append(
                ObjectPropertyResponse(
                    id=self._local_name(prop_uri),
                    ontology_id=self._ontology_id(prop_uri),
                    name=self._local_name(prop_uri),
                    display_name=row.get("label", {}).get("value", ""),
                    description="",
                    labels={},
                    comments={},
                    domain_ids=[self._local_name(domain_uri)] if domain_uri else [],
                    range_ids=[self._local_name(range_uri)] if range_uri else [],
                    characteristics=chars,
                    super_property_id=None,
                    inverse_of_id=None,
                    property_chain=[],
                )
            )
        return props

    def create_object_property(
        self,
        ontology_iri: str,
        name: str,
        domain_iri: str,
        range_iri: str,
        display_name: Optional[str] = None,
        characteristics: Optional[list[str]] = None,
        inverse_of: Optional[str] = None,
    ) -> ObjectPropertyResponse:
        prop_uri = f"{ontology_iri}{name}"
        label = display_name or name

        triples = [
            (prop_uri, str(RDF.type), str(OWL.ObjectProperty)),
            (prop_uri, str(RDFS.label), f'"{label}"'),
            (prop_uri, str(RDFS.domain), f"<{domain_iri}>"),
            (prop_uri, str(RDFS.range), f"<{range_iri}>"),
        ]

        if characteristics:
            char_map = {
                "functional": str(OWL.FunctionalProperty),
                "inverseFunctional": str(OWL.InverseFunctionalProperty),
                "transitive": str(OWL.TransitiveProperty),
                "symmetric": str(OWL.SymmetricProperty),
                "asymmetric": str(OWL.AsymmetricProperty),
                "reflexive": str(OWL.ReflexiveProperty),
                "irreflexive": str(OWL.IrreflexiveProperty),
            }
            for char in characteristics:
                if char in char_map:
                    triples.append((prop_uri, str(RDF.type), char_map[char]))

        if inverse_of:
            triples.append((prop_uri, str(OWL.inverseOf), f"<{inverse_of}>"))

        triples_str = "\n".join(f"<{s}> <{p}> <{o}> ." for s, p, o in triples)
        upd = f"""
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        INSERT DATA {{ {triples_str} }}
        """
        self._update(upd)

        return ObjectPropertyResponse(
            id=name,
            ontology_id=self._ontology_id(prop_uri),
            name=name,
            display_name=label,
            description="",
            labels={},
            comments={},
            domain_ids=[self._local_name(domain_iri)],
            range_ids=[self._local_name(range_iri)],
            characteristics=characteristics or [],
            super_property_id=None,
            inverse_of_id=self._local_name(inverse_of) if inverse_of else None,
            property_chain=[],
        )

    def delete_object_property(self, prop_uri: str) -> bool:
        upd = f"""
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        DELETE {{ <{prop_uri}> ?p ?o }}
        WHERE {{ <{prop_uri}> ?p ?o }}
        """
        return self._update(upd)

    def delete_annotation_property(self, prop_uri: str) -> bool:
        upd = f"""
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        DELETE {{ <{prop_uri}> ?p ?o }}
        WHERE {{ <{prop_uri}> ?p ?o }}
        """
        return self._update(upd)

    # -------------------------------------------------------------------------
    # AnnotationProperty & Individual (read-only)
    # -------------------------------------------------------------------------

    def list_annotation_properties(self, ontology_iri: str) -> list:
        q = f"""
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?prop ?label WHERE {{
            ?prop a owl:AnnotationProperty .
            FILTER(STRSTARTS(STR(?prop), "{ontology_iri}"))
            OPTIONAL {{ ?prop rdfs:label ?label }}
        }}
        """
        results = self._query(q)
        return [
            {
                "id": self._local_name(row.get("prop", {}).get("value", "")),
                "ontology_id": self._ontology_id(row.get("prop", {}).get("value", "")),
                "name": self._local_name(row.get("prop", {}).get("value", "")),
                "display_name": row.get("label", {}).get("value", ""),
                "description": "",
                "domain_ids": [],
                "range_ids": [],
                "sub_property_of_id": None,
            }
            for row in results
        ]

    def list_individuals(self, ontology_iri: str) -> list:
        q = f"""
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?ind ?label ?comment WHERE {{
            ?ind a owl:NamedIndividual .
            FILTER(STRSTARTS(STR(?ind), "{ontology_iri}"))
            OPTIONAL {{ ?ind rdfs:label ?label }}
            OPTIONAL {{ ?ind rdfs:comment ?comment }}
        }}
        """
        results = self._query(q)
        individuals = []
        for row in results:
            ind_uri = row.get("ind", {}).get("value", "")
            types = self._get_individual_types(ind_uri)
            individuals.append({
                "id": self._local_name(ind_uri),
                "ontology_id": self._ontology_id(ind_uri),
                "name": self._local_name(ind_uri),
                "display_name": row.get("label", {}).get("value", ""),
                "description": row.get("comment", {}).get("value", ""),
                "types": types,
                "labels": {},
                "comments": {},
                "data_property_assertions": [],
                "object_property_assertions": [],
            })
        return individuals

    # -------------------------------------------------------------------------
    # Full Ontology Detail (batched)
    # -------------------------------------------------------------------------

    def get_ontology_detail(self, ontology_iri: str) -> dict:
        # Name/description
        name, description = "", ""
        meta_q = f"""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?label ?comment WHERE {{
            OPTIONAL {{ <{ontology_iri}> rdfs:label ?label }}
            OPTIONAL {{ <{ontology_iri}> rdfs:comment ?comment }}
        }}
        LIMIT 1
        """
        meta_results = self._query(meta_q)
        if meta_results:
            name = meta_results[0].get("label", {}).get("value", "")
            description = meta_results[0].get("comment", {}).get("value", "")

        classes = self.list_classes(ontology_iri)
        datatype_props = self.list_datatype_properties(ontology_iri)
        object_props = self.list_object_properties(ontology_iri)
        annotation_props = self.list_annotation_properties(ontology_iri)
        individuals = self.list_individuals(ontology_iri)

        return {
            "name": name,
            "description": description,
            "classes": classes,
            "data_properties": datatype_props,
            "object_properties": object_props,
            "annotation_properties": annotation_props,
            "individuals": individuals,
        }

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------

    def _get_label(self, uri: str) -> Optional[str]:
        q = f"PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> SELECT ?l WHERE {{ <{uri}> rdfs:label ?l }} LIMIT 1"
        results = self._query(q)
        return results[0].get("l", {}).get("value") if results else None

    def _get_comment(self, uri: str) -> Optional[str]:
        q = f"PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> SELECT ?c WHERE {{ <{uri}> rdfs:comment ?c }} LIMIT 1"
        results = self._query(q)
        return results[0].get("c", {}).get("value") if results else None

    def _get_super_classes(self, class_uri: str) -> list[str]:
        q = f"PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> SELECT ?super WHERE {{ <{class_uri}> rdfs:subClassOf ?super }}"
        results = self._query(q)
        return [self._local_name(row.get("super", {}).get("value", "")) for row in results]

    def _get_equivalent_classes(self, class_uri: str) -> list[str]:
        q = f"PREFIX owl: <http://www.w3.org/2002/07/owl#> SELECT ?eq WHERE {{ <{class_uri}> owl:equivalentClass ?eq }}"
        results = self._query(q)
        return [self._local_name(row.get("eq", {}).get("value", "")) for row in results]

    def _get_disjoint_classes(self, class_uri: str) -> list[str]:
        q = f"PREFIX owl: <http://www.w3.org/2002/07/owl#> SELECT ?dj WHERE {{ <{class_uri}> owl:disjointWith ?dj }}"
        results = self._query(q)
        return [self._local_name(row.get("dj", {}).get("value", "")) for row in results]

    def _get_property_characteristics(self, prop_uri: str) -> list[str]:
        q = f"""
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        SELECT ?type WHERE {{
            <{prop_uri}> a ?type .
            FILTER(?type IN (owl:FunctionalProperty, owl:InverseFunctionalProperty,
                            owl:TransitiveProperty, owl:SymmetricProperty,
                            owl:AsymmetricProperty, owl:ReflexiveProperty, owl:IrreflexiveProperty))
        }}
        """
        results = self._query(q)
        char_map = {
            "http://www.w3.org/2002/07/owl#FunctionalProperty": "functional",
            "http://www.w3.org/2002/07/owl#InverseFunctionalProperty": "inverseFunctional",
            "http://www.w3.org/2002/07/owl#TransitiveProperty": "transitive",
            "http://www.w3.org/2002/07/owl#SymmetricProperty": "symmetric",
            "http://www.w3.org/2002/07/owl#AsymmetricProperty": "asymmetric",
            "http://www.w3.org/2002/07/owl#ReflexiveProperty": "reflexive",
            "http://www.w3.org/2002/07/owl#IrreflexiveProperty": "irreflexive",
        }
        return [
            char_map.get(row.get("type", {}).get("value", ""), "")
            for row in results
        ]

    def _get_individual_types(self, ind_uri: str) -> list[str]:
        q = f"PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> SELECT ?type WHERE {{ <{ind_uri}> rdf:type ?type }}"
        results = self._query(q)
        return [
            self._local_name(row.get("type", {}).get("value", ""))
            for row in results
            if self._local_name(row.get("type", {}).get("value", "")) != "NamedIndividual"
        ]

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


# ============================================================================
# Service: per-dataset JenaClient 缓存
# ============================================================================

_jena_admin_client: Optional[JenaClient] = None
_jena_dataset_clients: dict[str, JenaClient] = {}


def get_jena_client(
    fuseki_url: str = None,
    dataset: str = None,
    username: str = None,
    password: str = None,
) -> JenaClient:
    """
    获取 admin 客户端（用于创建/删除 dataset 等管理操作）。
    使用 /_admin dataset，缓存在 _jena_admin_client。
    """
    global _jena_admin_client

    if _jena_admin_client is None:
        settings = get_fuseki_settings()
        _jena_admin_client = JenaClient(
            fuseki_url=fuseki_url or settings["fuseki_url"],
            dataset="/_admin",
            username=username or settings["username"],
            password=password or settings["password"],
        )

    return _jena_admin_client


def get_jena_client_for_dataset(dataset: str) -> JenaClient:
    """
    获取指定 dataset 的客户端（用于 SPARQL 查询/更新）。
    每个 dataset 缓存一个实例，避免重复初始化。
    """
    if dataset not in _jena_dataset_clients:
        settings = get_fuseki_settings()
        _jena_dataset_clients[dataset] = JenaClient(
            fuseki_url=settings["fuseki_url"],
            dataset=dataset,
            username=settings["username"],
            password=settings["password"],
        )
    return _jena_dataset_clients[dataset]


# ============================================================================
# 常量：默认共享 Dataset（Named Graph 架构）
# ============================================================================

DEFAULT_DATASET = "/onto-agent"


# ============================================================================
# Named Graph 扩展方法已移至 jena_named_graph.py 模块
# 使用方式: from src.services.jena_named_graph import get_jena_client_for_default_dataset
# ============================================================================

