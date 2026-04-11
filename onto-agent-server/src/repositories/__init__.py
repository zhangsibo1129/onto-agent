"""
Repositories — 数据访问层

导出:
- OntologyRepository
- EntityIndexRepository
"""

from src.repositories.ontology import (
    OntologyRepository,
    get_ontology_by_id,
    list_ontologies,
    delete_ontology_by_id,
)
from src.repositories.entity_index import (
    EntityIndexRepository,
    index_entity,
    delete_entity_index,
)

__all__ = [
    # Ontology Repository
    "OntologyRepository",
    "get_ontology_by_id",
    "list_ontologies",
    "delete_ontology_by_id",
    # EntityIndex Repository
    "EntityIndexRepository",
    "index_entity",
    "delete_entity_index",
]
