"""
Ontology Metadata Store

Stores ontology registration information including dataset mappings.
Currently uses in-memory storage with JSON file persistence.
"""

import json
from pathlib import Path
from typing import Optional
from datetime import datetime


class OntologyMetadata:
    """本体元数据"""

    def __init__(
        self,
        id: str,
        name: str,
        base_iri: str,
        dataset: str,
        description: str = "",
        version: str = "v1.0",
        status: str = "draft",
        created_at: str = None,
        updated_at: str = None,
    ):
        self.id = id
        self.name = name
        self.base_iri = base_iri
        self.dataset = dataset
        self.description = description
        self.version = version
        self.status = status
        self.created_at = created_at or datetime.utcnow().isoformat() + "Z"
        self.updated_at = updated_at or self.created_at

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "base_iri": self.base_iri,
            "dataset": self.dataset,
            "description": self.description,
            "version": self.version,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "OntologyMetadata":
        return cls(**data)


class OntologyMetadataStore:
    """本体元数据存储（内存 + 文件持久化）"""

    def __init__(self, storage_path: str = None):
        if storage_path is None:
            storage_path = (
                Path(__file__).parent.parent.parent / "data" / "ontologies.json"
            )
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._ontologies: dict[str, OntologyMetadata] = {}
        self._load()

    def _load(self):
        """从文件加载"""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._ontologies = {
                        k: OntologyMetadata.from_dict(v) for k, v in data.items()
                    }
            except Exception as e:
                print(f"Failed to load ontology metadata: {e}")
                self._ontologies = {}

    def _save(self):
        """保存到文件"""
        try:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                data = {k: v.to_dict() for k, v in self._ontologies.items()}
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Failed to save ontology metadata: {e}")

    def list_all(self) -> list[OntologyMetadata]:
        """列出所有本体"""
        return list(self._ontologies.values())

    def get(self, ontology_id: str) -> Optional[OntologyMetadata]:
        """获取本体"""
        return self._ontologies.get(ontology_id)

    def add(self, metadata: OntologyMetadata) -> OntologyMetadata:
        """添加本体"""
        self._ontologies[metadata.id] = metadata
        self._save()
        return metadata

    def update(self, ontology_id: str, **kwargs) -> Optional[OntologyMetadata]:
        """更新本体"""
        if ontology_id not in self._ontologies:
            return None
        meta = self._ontologies[ontology_id]
        for key, value in kwargs.items():
            if hasattr(meta, key) and key not in ["id", "dataset"]:
                setattr(meta, key, value)
        meta.updated_at = datetime.utcnow().isoformat() + "Z"
        self._save()
        return meta

    def delete(self, ontology_id: str) -> bool:
        """删除本体"""
        if ontology_id in self._ontologies:
            del self._ontologies[ontology_id]
            self._save()
            return True
        return False

    def get_by_dataset(self, dataset: str) -> Optional[OntologyMetadata]:
        """根据 dataset 查找本体"""
        for meta in self._ontologies.values():
            if meta.dataset == dataset:
                return meta
        return None

    def generate_id(self) -> str:
        """生成新 ID"""
        if not self._ontologies:
            return "1"
        max_id = max(int(k) for k in self._ontologies.keys())
        return str(max_id + 1)

    def generate_dataset(self, ontology_id: str) -> str:
        """生成 dataset 路径"""
        return f"/ontology_{ontology_id}"


# Global store instance
_metadata_store: Optional[OntologyMetadataStore] = None


def get_metadata_store() -> OntologyMetadataStore:
    """获取元数据存储单例"""
    global _metadata_store
    if _metadata_store is None:
        _metadata_store = OntologyMetadataStore()
    return _metadata_store
