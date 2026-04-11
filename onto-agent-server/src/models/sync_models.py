"""
Phase 5+6: Sync and Mapping models
"""
import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, Integer, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from src.database import Base


class PropertySource(Base):
    """
    属性数据源配置
    每个属性声明自己的数据来源（表 + 列 + 实例 ID 列）
    """
    __tablename__ = "property_sources"

    id: Mapped[str] = mapped_column(
        String(50), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    ontology_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("ontologies.id", ondelete="CASCADE"), nullable=False
    )
    property_local_name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_table: Mapped[str] = mapped_column(String(255), nullable=False)
    source_column: Mapped[str] = mapped_column(String(255), nullable=False)
    instance_id_column: Mapped[str] = mapped_column(String(255), nullable=False)
    filter_condition: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        UniqueConstraint('ontology_id', 'property_local_name', name='uix_onto_prop'),
    )


class DataSourceRelation(Base):
    """
    显式关联关系（join 兜底配置）
    当自动推断 join key 失败时，使用此配置
    """
    __tablename__ = "data_source_relations"

    id: Mapped[str] = mapped_column(
        String(50), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    datasource_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("datasources.id", ondelete="CASCADE"), nullable=False
    )
    from_table: Mapped[str] = mapped_column(String(255), nullable=False)
    to_table: Mapped[str] = mapped_column(String(255), nullable=False)
    from_column: Mapped[str] = mapped_column(String(255), nullable=False)
    to_column: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    __table_args__ = (
        UniqueConstraint('datasource_id', 'from_table', 'to_table', name='uix_ds_rel'),
    )


class SyncTask(Base):
    """
    同步任务
    """
    __tablename__ = "sync_tasks"

    id: Mapped[str] = mapped_column(
        String(50), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    ontology_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("ontologies.id", ondelete="CASCADE"), nullable=False
    )
    mode: Mapped[str] = mapped_column(String(20), default="full")  # full / incremental
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending/running/success/error/cancelled
    progress: Mapped[int] = mapped_column(Integer, default=0)  # 0-100
    processed: Mapped[int] = mapped_column(Integer, default=0)
    total: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_sync_instance_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    __table_args__ = (
        Index('ix_sync_tasks_ontology', 'ontology_id'),
        Index('ix_sync_tasks_status', 'status'),
    )


class SyncLog(Base):
    """
    同步任务日志
    """
    __tablename__ = "sync_logs"

    id: Mapped[str] = mapped_column(
        String(50), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    task_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("sync_tasks.id", ondelete="CASCADE"), nullable=False
    )
    level: Mapped[str] = mapped_column(String(10), nullable=False)  # info/warning/error/success
    message: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    __table_args__ = (
        Index('ix_sync_logs_task', 'task_id'),
    )
