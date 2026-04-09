"""
Ontology TBox Service using Apache Jena Fuseki

This module provides RDF-based ontology storage using Apache Jena Fuseki
as the backend RDF store with SPARQL protocol support.
"""

from typing import Optional
from functools import lru_cache
from os import getenv
from dotenv import load_dotenv
import httpx
from rdflib import Graph, Namespace, URIRef, Literal, ConjunctiveGraph
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
# Fuseki Configuration
# ============================================================================


@lru_cache
def get_fuseki_settings() -> dict:
    """Load Fuseki settings from environment variables"""
    return {
        "fuseki_url": getenv("FUSEKI_URL", "http://localhost:3030"),
        "username": getenv("FUSEKI_USER", "admin"),
        "password": getenv("FUSEKI_PASSWORD", ""),
    }


# Default Fuseki endpoint
DEFAULT_FUSEKI_URL = "http://localhost:3030"
DEFAULT_DATASET = "/onto"

# Standard Namespaces
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
    """Base exception for Jena service errors"""

    pass


class JenaConnectionError(JenaServiceError):
    """Fuseki connection error"""

    pass


class JenaQueryError(JenaServiceError):
    """SPARQL query execution error"""

    pass


# ============================================================================
# Jena Client
# ============================================================================


class JenaClient:
    """
    Client for Apache Jena Fuseki SPARQL endpoint

    Provides CRUD operations for OWL 2 ontology entities:
    - Classes (owl:Class)
    - Datatype Properties (owl:DatatypeProperty)
    - Object Properties (owl:ObjectProperty)
    """

    def __init__(
        self,
        fuseki_url: str = DEFAULT_FUSEKI_URL,
        dataset: str = DEFAULT_DATASET,
        timeout: int = 30,
        username: str = None,
        password: str = None,
    ):
        import os

        self.fuseki_url = fuseki_url.rstrip("/")
        self.dataset = dataset
        self.timeout = timeout

        self.username = username or os.getenv("FUSEKI_USER", "admin")
        self.password = password or os.getenv("FUSEKI_PASSWORD", "")

        # SPARQL endpoints
        self.query_endpoint = f"{fuseki_url}{dataset}/query"
        self.update_endpoint = f"{fuseki_url}{dataset}/update"
        self.data_endpoint = f"{fuseki_url}{dataset}/data"

        # Verify connection
        self._health_check()

    def _get_auth(self):
        """Get basic auth tuple if credentials are set"""
        if self.username and self.password:
            return httpx.BasicAuth(self.username, self.password)
        return None

    def _health_check(self) -> bool:
        """Check if Fuseki is reachable"""
        try:
            response = httpx.get(
                f"{self.fuseki_url}/$/ping",
                timeout=5,
                auth=self._get_auth(),
            )
            return response.status_code == 200
        except Exception as e:
            raise JenaConnectionError(f"Cannot connect to Fuseki: {e}")

    def create_dataset(self, dataset: str) -> bool:
        """Create a new dataset in Fuseki"""
        try:
            response = httpx.post(
                f"{self.fuseki_url}/$/datasets",
                data=f"dbName={dataset.lstrip('/')}&dbType=tdb2",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                auth=self._get_auth(),
                timeout=self.timeout,
            )
            return response.status_code in (200, 201)
        except Exception as e:
            raise JenaServiceError(f"Failed to create dataset {dataset}: {e}")

    def delete_dataset(self, dataset: str) -> bool:
        """Delete a dataset from Fuseki"""
        try:
            response = httpx.delete(
                f"{self.fuseki_url}/$/datasets/{dataset.lstrip('/')}",
                auth=self._get_auth(),
                timeout=self.timeout,
            )
            return response.status_code in (200, 204)
        except Exception as e:
            raise JenaServiceError(f"Failed to delete dataset {dataset}: {e}")

    def list_datasets(self) -> list[dict]:
        """List all datasets in Fuseki"""
        try:
            response = httpx.get(
                f"{self.fuseki_url}/$/datasets",
                auth=self._get_auth(),
                timeout=self.timeout,
            )
            if response.status_code == 200:
                return response.json().get("datasets", [])
            return []
        except Exception:
            return []

    def switch_dataset(self, dataset: str) -> "JenaClient":
        """Return a new JenaClient instance with different dataset"""
        return JenaClient(
            fuseki_url=self.fuseki_url,
            dataset=dataset,
            username=self.username,
            password=self.password,
        )

    def _sparql_update(self, query: str) -> bool:
        """Execute SPARQL Update query"""
        try:
            response = httpx.post(
                self.update_endpoint,
                data=query,
                headers={"Content-Type": "application/sparql-update"},
                timeout=self.timeout,
                auth=self._get_auth(),
            )
            return response.status_code in (200, 204)
        except Exception as e:
            raise JenaQueryError(f"SPARQL Update failed: {e}")

    def _sparql_query(self, query: str) -> list[dict]:
        """Execute SPARQL SELECT query and return results as list of dicts"""
        try:
            response = httpx.get(
                self.query_endpoint,
                params={"query": query, "format": "json"},
                headers={"Accept": "application/sparql-results+json"},
                timeout=self.timeout,
                auth=self._get_auth(),
            )
            if response.status_code != 200:
                raise JenaQueryError(f"Query failed: {response.text}")

            import json

            results = json.loads(response.text)
            return results.get("results", {}).get("bindings", [])
        except Exception as e:
            raise JenaQueryError(f"SPARQL Query failed: {e}")

    # =========================================================================
    # Class Operations (owl:Class)
    # =========================================================================

    def list_classes(self, ontology_iri: str) -> list[OntologyClassResponse]:
        """
        List all classes in an ontology

        SPARQL:
        SELECT ?class WHERE {
            ?class a owl:Class .
            FILTER(STRSTARTS(STR(?class), "{ontology_iri}"))
        }
        """
        query = f"""
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT DISTINCT ?class (COUNT(?equivalent) as ?eqCount) (COUNT(?disjoint) as ?djCount)
        WHERE {{
            ?class a owl:Class .
            FILTER(STRSTARTS(STR(?class), "{ontology_iri}"))
            OPTIONAL {{ ?class owl:equivalentClass ?equivalent }}
            OPTIONAL {{ ?class owl:disjointWith ?disjoint }}
        }}
        GROUP BY ?class
        """

        results = self._sparql_query(query)
        classes = []

        for row in results:
            class_uri = row.get("class", {}).get("value", "")
            label = self._get_label(class_uri) or self._get_local_name(class_uri)
            description = self._get_comment(class_uri)
            super_classes = self._get_super_classes(class_uri)

            classes.append(
                OntologyClassResponse(
                    id=self._get_local_name(class_uri),
                    ontology_id=self._get_ontology_id(class_uri),
                    name=self._get_local_name(class_uri),
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

    def list_ontologies(self) -> list[dict]:
        """
        List all ontologies in the dataset

        SPARQL:
        SELECT ?ontology WHERE {
            ?ontology a owl:Ontology .
        }
        """
        query = """
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT DISTINCT ?ontology ?label ?comment
        WHERE {
            ?ontology a owl:Ontology .
            OPTIONAL { ?ontology rdfs:label ?label }
            OPTIONAL { ?ontology rdfs:comment ?comment }
        }
        """

        results = self._sparql_query(query)
        ontologies = []

        for row in results:
            ontology_uri = row.get("ontology", {}).get("value", "")
            label = row.get("label", {}).get("value", "")
            comment = row.get("comment", {}).get("value", "")

            ontologies.append(
                {
                    "base_iri": ontology_uri,
                    "name": label or self._get_local_name(ontology_uri),
                    "description": comment or "",
                }
            )

        return ontologies

    def create_ontology(
        self,
        name: str,
        base_iri: str,
        description: Optional[str] = None,
    ) -> bool:
        """Create a new owl:Ontology"""
        triples = [
            (base_iri, RDF.type, OWL.Ontology),
            (base_iri, RDFS.label, Literal(name)),
        ]

        if description:
            triples.append((base_iri, RDFS.comment, Literal(description)))

        return self._add_triples(triples)

    def create_class(
        self,
        ontology_iri: str,
        name: str,
        display_name: Optional[str] = None,
        description: Optional[str] = None,
        super_classes: Optional[list[str]] = None,
    ) -> OntologyClassResponse:
        """Create a new owl:Class"""
        class_uri = f"{ontology_iri}{name}"
        label = display_name or name

        triples = [
            (class_uri, RDF.type, OWL.Class),
            (class_uri, RDFS.label, Literal(label)),
        ]

        if description:
            triples.append((class_uri, RDFS.comment, Literal(description)))

        if super_classes:
            for sc in super_classes:
                triples.append((class_uri, RDFS.subClassOf, URIRef(sc)))

        self._add_triples(triples)

        return OntologyClassResponse(
            id=name,
            ontology_id=self._get_ontology_id(class_uri),
            name=name,
            display_name=label,
            description=description,
            labels={},
            comments={},
            equivalent_to=[],
            disjoint_with=[],
            super_classes=super_classes or [],
        )

    def get_class(self, class_uri: str) -> Optional[OntologyClassResponse]:
        """Get a single class by URI"""
        query = f"""
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?label ?comment WHERE {{
            <{class_uri}> rdfs:label ?label .
            OPTIONAL {{ <{class_uri}> rdfs:comment ?comment }}
        }}
        """

        results = self._sparql_query(query)
        if not results:
            return None

        label = results[0].get("label", {}).get("value", "")
        comment = results[0].get("comment", {}).get("value", "")

        return OntologyClassResponse(
            id=self._get_local_name(class_uri),
            ontology_id=self._get_ontology_id(class_uri),
            name=self._get_local_name(class_uri),
            display_name=label,
            description=comment,
            labels={},
            comments={},
            equivalent_to=self._get_equivalent_classes(class_uri),
            disjoint_with=self._get_disjoint_classes(class_uri),
            super_classes=self._get_super_classes(class_uri),
        )

    def delete_class(self, class_uri: str) -> bool:
        """Delete a class"""
        query = f"""
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        
        DELETE {{ <{class_uri}> ?p ?o }}
        WHERE {{
            <{class_uri}> ?p ?o .
        }}
        """
        return self._sparql_update(query)

    # =========================================================================
    # Datatype Property Operations (owl:DatatypeProperty)
    # =========================================================================

    def list_datatype_properties(self, ontology_iri: str) -> list[DataPropertyResponse]:
        """List all datatype properties"""
        query = f"""
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

        results = self._sparql_query(query)
        properties = []

        for row in results:
            prop_uri = row.get("prop", {}).get("value", "")

            # Get characteristics
            chars = self._get_property_characteristics(prop_uri)

            properties.append(
                DataPropertyResponse(
                    id=self._get_local_name(prop_uri),
                    ontology_id=self._get_ontology_id(prop_uri),
                    name=self._get_local_name(prop_uri),
                    display_name=row.get("label", {}).get("value", ""),
                    description="",
                    labels={},
                    comments={},
                    domain_ids=[
                        self._get_local_name(row.get("domain", {}).get("value", ""))
                    ]
                    if row.get("domain")
                    else [],
                    range_type=self._get_local_name(
                        row.get("range", {}).get("value", "string")
                    ),
                    characteristics=chars,
                )
            )

        return properties

    def create_datatype_property(
        self,
        ontology_iri: str,
        name: str,
        domain_iri: str,
        range_type: str = "string",
        display_name: Optional[str] = None,
        characteristics: Optional[list[str]] = None,
    ) -> DataPropertyResponse:
        """Create a new owl:DatatypeProperty"""
        prop_uri = f"{ontology_iri}{name}"
        label = display_name or name

        # Map range type to XSD
        xsd_range = f"http://www.w3.org/2001/XMLSchema#{range_type}"

        triples = [
            (prop_uri, RDF.type, OWL.DatatypeProperty),
            (prop_uri, RDFS.label, Literal(label)),
            (prop_uri, RDFS.domain, URIRef(domain_iri)),
            (
                prop_uri,
                RDFS.range,
                URIRef(f"http://www.w3.org/2001/XMLSchema#{range_type}"),
            ),
        ]

        # Add characteristics
        if characteristics:
            for char in characteristics:
                if char == "functional":
                    triples.append((prop_uri, RDF.type, OWL.FunctionalProperty))

        self._add_triples(triples)

        return DataPropertyResponse(
            id=name,
            ontology_id=self._get_ontology_id(prop_uri),
            name=name,
            display_name=label,
            description="",
            labels={},
            comments={},
            domain_ids=[self._get_local_name(domain_iri)],
            range_type=range_type,
            characteristics=characteristics or [],
        )

    # =========================================================================
    # Object Property Operations (owl:ObjectProperty)
    # =========================================================================

    def list_object_properties(self, ontology_iri: str) -> list[ObjectPropertyResponse]:
        """List all object properties"""
        query = f"""
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

        results = self._sparql_query(query)
        properties = []

        for row in results:
            prop_uri = row.get("prop", {}).get("value", "")
            chars = self._get_property_characteristics(prop_uri)

            properties.append(
                ObjectPropertyResponse(
                    id=self._get_local_name(prop_uri),
                    ontology_id=self._get_ontology_id(prop_uri),
                    name=self._get_local_name(prop_uri),
                    display_name=row.get("label", {}).get("value", ""),
                    description="",
                    labels={},
                    comments={},
                    domain_ids=[
                        self._get_local_name(row.get("domain", {}).get("value", ""))
                    ]
                    if row.get("domain")
                    else [],
                    range_ids=[
                        self._get_local_name(row.get("range", {}).get("value", ""))
                    ]
                    if row.get("range")
                    else [],
                    characteristics=chars,
                    super_property_id=None,
                    inverse_of_id=None,
                    property_chain=[],
                )
            )

        return properties

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
        """Create a new owl:ObjectProperty"""
        prop_uri = f"{ontology_iri}{name}"
        label = display_name or name

        triples = [
            (prop_uri, RDF.type, OWL.ObjectProperty),
            (prop_uri, RDFS.label, Literal(label)),
            (prop_uri, RDFS.domain, URIRef(domain_iri)),
            (prop_uri, RDFS.range, URIRef(range_iri)),
        ]

        if characteristics:
            char_map = {
                "functional": OWL.FunctionalProperty,
                "inverseFunctional": OWL.InverseFunctionalProperty,
                "transitive": OWL.TransitiveProperty,
                "symmetric": OWL.SymmetricProperty,
                "asymmetric": OWL.AsymmetricProperty,
                "reflexive": OWL.ReflexiveProperty,
                "irreflexive": OWL.IrreflexiveProperty,
            }
            for char in characteristics:
                if char in char_map:
                    triples.append((prop_uri, RDF.type, char_map[char]))

        if inverse_of:
            triples.append((prop_uri, OWL.inverseOf, URIRef(inverse_of)))

        self._add_triples(triples)

        return ObjectPropertyResponse(
            id=name,
            ontology_id=self._get_ontology_id(prop_uri),
            name=name,
            display_name=label,
            description="",
            labels={},
            comments={},
            domain_ids=[self._get_local_name(domain_iri)],
            range_ids=[self._get_local_name(range_iri)],
            characteristics=characteristics or [],
            super_property_id=None,
            inverse_of_id=inverse_of,
            property_chain=[],
        )

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _add_triples(self, triples: list) -> bool:
        """Add RDF triples using SPARQL Update"""
        triples_str = "\n".join(
            [f"<{s}> <{p}> {self._format_object(o)} ." for s, p, o in triples]
        )

        query = f"""
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        
        INSERT DATA {{
            {triples_str}
        }}
        """
        return self._sparql_update(query)

    def _format_object(self, obj) -> str:
        """Format object for SPARQL (handle URIRef vs Literal)"""
        if isinstance(obj, URIRef):
            return f"<{obj}>"
        elif isinstance(obj, Literal):
            if obj.language:
                return f'"{obj}"@{obj.language}'
            elif obj.datatype:
                return f'"{obj}"^^<{obj.datatype}>'
            else:
                return f'"{obj}"'
        return f"<{obj}>"

    def _get_label(self, uri: str) -> Optional[str]:
        """Get rdfs:label for a URI"""
        query = f"""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?label WHERE {{ <{uri}> rdfs:label ?label }}
        LIMIT 1
        """
        results = self._sparql_query(query)
        return results[0].get("label", {}).get("value") if results else None

    def _get_comment(self, uri: str) -> Optional[str]:
        """Get rdfs:comment for a URI"""
        query = f"""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?comment WHERE {{ <{uri}> rdfs:comment ?comment }}
        LIMIT 1
        """
        results = self._sparql_query(query)
        return results[0].get("comment", {}).get("value") if results else None

    def _get_super_classes(self, class_uri: str) -> list[str]:
        """Get direct super classes"""
        query = f"""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?super WHERE {{ <{class_uri}> rdfs:subClassOf ?super }}
        """
        results = self._sparql_query(query)
        return [
            self._get_local_name(row.get("super", {}).get("value", ""))
            for row in results
        ]

    def _get_equivalent_classes(self, class_uri: str) -> list[str]:
        """Get equivalent classes"""
        query = f"""
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        SELECT ?eq WHERE {{ <{class_uri}> owl:equivalentClass ?eq }}
        """
        results = self._sparql_query(query)
        return [
            self._get_local_name(row.get("eq", {}).get("value", "")) for row in results
        ]

    def _get_disjoint_classes(self, class_uri: str) -> list[str]:
        """Get disjoint classes"""
        query = f"""
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        SELECT ?dj WHERE {{ <{class_uri}> owl:disjointWith ?dj }}
        """
        results = self._sparql_query(query)
        return [
            self._get_local_name(row.get("dj", {}).get("value", "")) for row in results
        ]

    def _get_property_characteristics(self, prop_uri: str) -> list[str]:
        """Get property characteristics (Functional, Transitive, etc.)"""
        query = f"""
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        SELECT ?type WHERE {{
            <{prop_uri}> a ?type .
            FILTER(?type IN (owl:FunctionalProperty, owl:InverseFunctionalProperty, 
                            owl:TransitiveProperty, owl:SymmetricProperty,
                            owl:AsymmetricProperty, owl:ReflexiveProperty, owl:IrreflexiveProperty))
        }}
        """
        results = self._sparql_query(query)

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
            char_map.get(row.get("type", {}).get("value", ""), "") for row in results
        ]

    def _get_local_name(self, uri: str) -> str:
        """Extract local name from URI"""
        if not uri:
            return ""
        return (
            uri.split("#")[-1].split("/")[-1] if "#" not in uri else uri.split("#")[-1]
        )

    def _get_ontology_id(self, uri: str) -> str:
        """Extract ontology ID from entity URI"""
        if not uri:
            return ""
        # Extract from namespace, e.g., "http://onto-agent.com/ontology/customer360#Product" -> "customer360"
        parts = uri.replace("http://", "").replace("https://", "").split("/")
        if len(parts) >= 2:
            return parts[-2]  # Second to last part
        return parts[-1].split("#")[0]


# ============================================================================
# Service Singleton
# ============================================================================

_jena_client: Optional[JenaClient] = None


def get_jena_client(
    fuseki_url: str = None,
    dataset: str = None,
    username: str = None,
    password: str = None,
) -> JenaClient:
    """
    Get or create Jena client singleton

    Args:
        fuseki_url: Fuseki server URL (default from env)
        dataset: Dataset path (default from env)
        username: Fuseki username (default from env)
        password: Fuseki password (default from env)
    """
    global _jena_client

    if _jena_client is None:
        settings = get_fuseki_settings()

        _jena_client = JenaClient(
            fuseki_url=fuseki_url or settings["fuseki_url"],
            dataset=dataset or "/_admin",  # Used for admin ops only
            username=username or settings["username"],
            password=password or settings["password"],
        )

    return _jena_client


def get_jena_client_for_dataset(dataset: str) -> JenaClient:
    """Get a JenaClient for a specific dataset"""
    settings = get_fuseki_settings()
    return JenaClient(
        fuseki_url=settings["fuseki_url"],
        dataset=dataset,
        username=settings["username"],
        password=settings["password"],
    )
