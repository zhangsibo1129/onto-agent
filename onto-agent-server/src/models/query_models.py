"""
Phase 7: Query models
Query history and saved queries
"""
import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class QueryHistory(Base):
    """
    SPARQL 查询历史
    """
    __tablename__ = "query_history"

    id: Mapped[str] = mapped_column(
        String(50), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    ontology_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("ontologies.id", ondelete="CASCADE"), nullable=False
    )
    query_type: Mapped[str] = mapped_column(String(20), nullable=False)  # SELECT/ASK/CONSTRUCT/DESCRIBE
    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    result_count: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    execution_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    __table_args__ = (
        Index('ix_query_history_ontology', 'ontology_id'),
        Index('ix_query_history_created', 'created_at'),
    )


class SavedQuery(Base):
    """
    保存的 SPARQL 查询
    """
    __tablename__ = "saved_queries"

    id: Mapped[str] = mapped_column(
        String(50), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    ontology_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("ontologies.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    query_type: Mapped[str] = mapped_column(String(20), nullable=False)  # SELECT/ASK/CONSTRUCT
    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        Index('ix_saved_query_ontology', 'ontology_id'),
    )


# SQLAlchemy needs Index imported
from sqlalchemy import Index
