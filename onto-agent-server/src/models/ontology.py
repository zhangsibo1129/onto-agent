"""
PostgreSQL 轻量索引模型（修改后）

- 支持 Named Graph 架构（TBox/ABox 分离）
- 支持 Saga 事务追踪
- 支持版本管理

只存实体 ID、名称、Jena URI，不存业务数据（业务数据以 Jena 为唯一可信源）。
"""

from datetime import datetime
from enum import Enum
from sqlalchemy import String, Text, DateTime, ForeignKey, func, Index, UniqueConstraint, JSON
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class EntityStatus(str, Enum):
    """操作日志状态枚举"""
    PENDING = "pending"          # 待同步
    CONFIRMED = "confirmed"      # 已确认（成功）
    COMPENSATED = "compensated"  # 已补偿（失败回滚）
    FAILED = "failed"            # 最终失败


class OperationType(str, Enum):
    """操作类型枚举"""
    CREATE_CLASS = "create_class"
    UPDATE_CLASS = "update_class"
    DELETE_CLASS = "delete_class"
    CREATE_DP = "create_dp"
    UPDATE_DP = "update_dp"
    DELETE_DP = "delete_dp"
    CREATE_OP = "create_op"
    UPDATE_OP = "update_op"
    DELETE_OP = "delete_op"
    CREATE_AP = "create_ap"
    CREATE_INDIVIDUAL = "create_individual"


class Ontology(Base):
    """
    本体索引表（修改后）
    
    增加 Named Graph URI 字段，支持 TBox/ABox 分离
    """
    __tablename__ = "ontologies"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # 版本管理
    version: Mapped[str] = mapped_column(String(20), default="v1.0")
    status: Mapped[str] = mapped_column(String(20), default="draft")  # draft/published/archived

    # IRI 和共享 Dataset（统一 dataset）
    base_iri: Mapped[str] = mapped_column(String(500), nullable=False)
    dataset: Mapped[str] = mapped_column(String(100), default="/onto-agent")  # 统一的共享 dataset

    # Named Graph URI（TBox 和 ABox 分离）- 新增字段
    tbox_graph_uri: Mapped[str] = mapped_column(String(500), nullable=False)
    abox_graph_uri: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # 关联数据源
    datasource_id: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
    published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # entity_count 字段：在实体写入 Jena 后由 service 层维护
    class_count: Mapped[int] = mapped_column(default=0)
    dp_count: Mapped[int] = mapped_column(default=0)
    op_count: Mapped[int] = mapped_column(default=0)
    ap_count: Mapped[int] = mapped_column(default=0)
    individual_count: Mapped[int] = mapped_column(default=0)
    axiom_count: Mapped[int] = mapped_column(default=0)


class OntologyVersion(Base):
    """
    本体版本表 - Named Graph 快照
    
    每次发布版本时创建，记录版本对应的 TBox/ABox Graph URI
    """
    __tablename__ = "ontology_versions"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    ontology_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("ontologies.id", ondelete="CASCADE"), nullable=False
    )

    version: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="published")

    # 版本对应的 Named Graph URI
    tbox_graph_uri: Mapped[str] = mapped_column(String(500), nullable=False)
    abox_graph_uri: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # 变更日志
    change_log: Mapped[list] = mapped_column(JSON, default=list)  # [{"type": "added", "category": "class", "name": "Customer"}, ...]

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    __table_args__ = (
        UniqueConstraint('ontology_id', 'version', name='uix_onto_ver'),
    )


class EntityIndex(Base):
    """
    实体索引表 - 修改后增加 graph_uri
    
    用途：列表页快速渲染 + Jena URI 回写时不需再次查询 Jena
    """
    __tablename__ = "entity_index"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    ontology_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("ontologies.id", ondelete="CASCADE"), nullable=False
    )

    entity_type: Mapped[str] = mapped_column(String(20), nullable=False)  # CLASS / DP / OP / AP / INDIVIDUAL / AXIOM
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(200), nullable=True)

    # 实体所在的 Named Graph URI - 新增字段
    graph_uri: Mapped[str] = mapped_column(String(500), nullable=False)

    # Jena URI（完整 IRI）
    jena_uri: Mapped[str | None] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class OperationLog(Base):
    """
    操作日志表 - 用于 Saga 事务追踪
    
    记录跨系统事务的每个步骤，失败时用于补偿
    """
    __tablename__ = "operation_logs"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    ontology_id: Mapped[str] = mapped_column(String(50), nullable=False)

    # 操作信息
    operation_type: Mapped[str] = mapped_column(String(30), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(20), nullable=False)  # CLASS/DP/OP...
    entity_id: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_name: Mapped[str] = mapped_column(String(200), nullable=False)

    # Jena 数据快照（用于补偿删除）
    jena_uri: Mapped[str] = mapped_column(String(500), nullable=False)
    jena_data: Mapped[dict] = mapped_column(JSON, nullable=True)  # {"triples": "...", "graph_uri": "..."}

    # PostgreSQL 数据
    pg_data: Mapped[dict] = mapped_column(JSON, nullable=True)

    # 事务状态
    status: Mapped[str] = mapped_column(String(20), default=EntityStatus.PENDING.value)
    step: Mapped[str] = mapped_column(String(20), default="prepare")  # prepare/jena/pg_final/settlement

    # 错误信息
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(default=0)

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
    settled_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    __table_args__ = (
        Index('ix_operation_logs_status', 'status'),
        Index('ix_operation_logs_step', 'step'),
        Index('ix_operation_logs_ontology', 'ontology_id'),
    )
