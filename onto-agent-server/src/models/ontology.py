from datetime import datetime
from typing import Optional, List

from sqlalchemy import String, Text, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base  # 统一使用 database.py 的 Base，确保 init_db 能扫到所有表


class OntologyStatus:
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class Ontology(Base):
    __tablename__ = "ontologies"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    version: Mapped[str] = mapped_column(String(20), default="v1.0")
    status: Mapped[str] = mapped_column(String(20), default="draft")
    base_iri: Mapped[str] = mapped_column(String(500), nullable=False)
    dataset: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    datasource_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    classes: Mapped[List["OntologyClass"]] = relationship(
        back_populates="ontology", cascade="all, delete-orphan"
    )
    data_properties: Mapped[List["DataProperty"]] = relationship(
        back_populates="ontology", cascade="all, delete-orphan"
    )
    object_properties: Mapped[List["ObjectProperty"]] = relationship(
        back_populates="ontology", cascade="all, delete-orphan"
    )
    annotation_properties: Mapped[List["AnnotationProperty"]] = relationship(
        back_populates="ontology", cascade="all, delete-orphan"
    )
    individuals: Mapped[List["Individual"]] = relationship(
        back_populates="ontology", cascade="all, delete-orphan"
    )
    axioms: Mapped[List["Axiom"]] = relationship(
        back_populates="ontology", cascade="all, delete-orphan"
    )
    data_ranges: Mapped[List["DataRange"]] = relationship(
        back_populates="ontology", cascade="all, delete-orphan"
    )


class OntologyClass(Base):
    __tablename__ = "ontology_classes"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    ontology_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("ontologies.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    display_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    labels: Mapped[dict] = mapped_column(JSON, default=dict)
    comments: Mapped[dict] = mapped_column(JSON, default=dict)
    equivalent_to: Mapped[list] = mapped_column(JSON, default=list)
    disjoint_with: Mapped[list] = mapped_column(JSON, default=list)
    super_classes: Mapped[list] = mapped_column(JSON, default=list)

    ontology: Mapped["Ontology"] = relationship(back_populates="classes")


class DataProperty(Base):
    __tablename__ = "data_properties"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    ontology_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("ontologies.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    display_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    labels: Mapped[dict] = mapped_column(JSON, default=dict)
    comments: Mapped[dict] = mapped_column(JSON, default=dict)
    domain_ids: Mapped[list] = mapped_column(JSON, default=list)
    range_type: Mapped[str] = mapped_column(String(50), default="string")
    characteristics: Mapped[list] = mapped_column(JSON, default=list)
    super_property_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    ontology: Mapped["Ontology"] = relationship(back_populates="data_properties")


class ObjectProperty(Base):
    __tablename__ = "object_properties"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    ontology_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("ontologies.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    display_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    labels: Mapped[dict] = mapped_column(JSON, default=dict)
    comments: Mapped[dict] = mapped_column(JSON, default=dict)
    domain_ids: Mapped[list] = mapped_column(JSON, default=list)
    range_ids: Mapped[list] = mapped_column(JSON, default=list)
    characteristics: Mapped[list] = mapped_column(JSON, default=list)
    super_property_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    inverse_of_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    property_chain: Mapped[list] = mapped_column(JSON, default=list)

    ontology: Mapped["Ontology"] = relationship(back_populates="object_properties")


class AnnotationProperty(Base):
    __tablename__ = "annotation_properties"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    ontology_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("ontologies.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    display_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    labels: Mapped[dict] = mapped_column(JSON, default=dict)
    comments: Mapped[dict] = mapped_column(JSON, default=dict)
    domain_ids: Mapped[list] = mapped_column(JSON, default=list)
    range_ids: Mapped[list] = mapped_column(JSON, default=list)
    sub_property_of_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    ontology: Mapped["Ontology"] = relationship(back_populates="annotation_properties")


class Individual(Base):
    __tablename__ = "individuals"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    ontology_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("ontologies.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    display_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    types: Mapped[list] = mapped_column(JSON, default=list)
    labels: Mapped[dict] = mapped_column(JSON, default=dict)
    comments: Mapped[dict] = mapped_column(JSON, default=dict)
    data_property_assertions: Mapped[list] = mapped_column(JSON, default=list)
    object_property_assertions: Mapped[list] = mapped_column(JSON, default=list)

    ontology: Mapped["Ontology"] = relationship(back_populates="individuals")


class Axiom(Base):
    __tablename__ = "axioms"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    ontology_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("ontologies.id", ondelete="CASCADE"), nullable=False
    )
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    subject: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    assertions: Mapped[dict] = mapped_column(JSON, default=dict)
    annotations: Mapped[list] = mapped_column(JSON, default=list)

    ontology: Mapped["Ontology"] = relationship(back_populates="axioms")


class DataRange(Base):
    __tablename__ = "data_ranges"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    ontology_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("ontologies.id", ondelete="CASCADE"), nullable=False
    )
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    values: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    base_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    facets: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    ontology: Mapped["Ontology"] = relationship(back_populates="data_ranges")
