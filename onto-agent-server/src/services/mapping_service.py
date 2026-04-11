"""
Phase 6: 映射服务
管理属性数据源配置（property_sources）
"""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import text

from src.database import SystemSession
from src.logging_config import get_logger

logger = get_logger("mapping_service")


async def list_mappings(ontology_id: str) -> list[dict]:
    """列出所有属性映射"""
    async with SystemSession() as session:
        result = await session.execute(
            text("""
                SELECT id, ontology_id, property_local_name, source_table,
                       source_column, instance_id_column, filter_condition,
                       created_at, updated_at
                FROM property_sources
                WHERE ontology_id = :ontology_id
                ORDER BY property_local_name
            """),
            {"ontology_id": ontology_id}
        )
        return [dict(r._mapping) for r in result.fetchall()]


async def get_mapping(ontology_id: str, property_name: str) -> Optional[dict]:
    """获取单个属性映射"""
    async with SystemSession() as session:
        result = await session.execute(
            text("""
                SELECT * FROM property_sources
                WHERE ontology_id = :ontology_id AND property_local_name = :prop
            """),
            {"ontology_id": ontology_id, "prop": property_name}
        )
        row = result.fetchone()
        return dict(row._mapping) if row else None


async def create_or_update_mapping(
    ontology_id: str,
    property_local_name: str,
    source_table: str,
    source_column: str,
    instance_id_column: str,
    filter_condition: str = None
) -> dict:
    """
    创建或更新属性映射
    upsert 语义
    """
    mapping_id = str(uuid.uuid4())
    now = datetime.now()

    async with SystemSession() as session:
        # upsert
        await session.execute(
            text("""
                INSERT INTO property_sources
                  (id, ontology_id, property_local_name, source_table, source_column,
                   instance_id_column, filter_condition, created_at, updated_at)
                VALUES
                  (:id, :onto_id, :prop, :table, :col, :id_col, :filter, :now, :now)
                ON CONFLICT (ontology_id, property_local_name)
                DO UPDATE SET
                  source_table = EXCLUDED.source_table,
                  source_column = EXCLUDED.source_column,
                  instance_id_column = EXCLUDED.instance_id_column,
                  filter_condition = EXCLUDED.filter_condition,
                  updated_at = EXCLUDED.updated_at
            """),
            {
                "id": mapping_id,
                "onto_id": ontology_id,
                "prop": property_local_name,
                "table": source_table,
                "col": source_column,
                "id_col": instance_id_column,
                "filter": filter_condition,
                "now": now
            }
        )
        await session.commit()

    return await get_mapping(ontology_id, property_local_name)


async def delete_mapping(ontology_id: str, property_name: str) -> bool:
    """删除属性映射"""
    async with SystemSession() as session:
        await session.execute(
            text("""
                DELETE FROM property_sources
                WHERE ontology_id = :ontology_id AND property_local_name = :prop
            """),
            {"ontology_id": ontology_id, "prop": property_name}
        )
        await session.commit()
    return True


async def bulk_create_mappings(ontology_id: str, mappings: list[dict]) -> int:
    """
    批量创建/更新属性映射
    mappings: [{property_local_name, source_table, source_column, instance_id_column, filter_condition}, ...]
    """
    now = datetime.now()
    count = 0

    async with SystemSession() as session:
        for m in mappings:
            mapping_id = str(uuid.uuid4())
            await session.execute(
                text("""
                    INSERT INTO property_sources
                      (id, ontology_id, property_local_name, source_table, source_column,
                       instance_id_column, filter_condition, created_at, updated_at)
                    VALUES
                      (:id, :onto_id, :prop, :table, :col, :id_col, :filter, :now, :now)
                    ON CONFLICT (ontology_id, property_local_name)
                    DO UPDATE SET
                      source_table = EXCLUDED.source_table,
                      source_column = EXCLUDED.source_column,
                      instance_id_column = EXCLUDED.instance_id_column,
                      filter_condition = EXCLUDED.filter_condition,
                      updated_at = EXCLUDED.updated_at
                """),
                {
                    "id": mapping_id,
                    "onto_id": ontology_id,
                    "prop": m["property_local_name"],
                    "table": m["source_table"],
                    "col": m["source_column"],
                    "id_col": m["instance_id_column"],
                    "filter": m.get("filter_condition"),
                    "now": now
                }
            )
            count += 1
        await session.commit()

    return count
