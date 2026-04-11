"""
EntityIndex Repository — 数据访问层

封装 EntityIndex 模型的所有数据库操作
"""

from typing import Optional
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.ontology import EntityIndex
from src.database import SystemSession
from src.logging_config import get_logger

logger = get_logger("repository.entity_index")


class EntityIndexRepository:
    """EntityIndex 数据访问类"""
    
    def __init__(self, session: AsyncSession = None):
        self._session = session
    
    @property
    def session(self) -> AsyncSession:
        if self._session is None:
            raise RuntimeError("Session not set")
        return self._session
    
    async def get_by_id(self, entity_id: str) -> Optional[EntityIndex]:
        """根据 ID 查询实体"""
        result = await self.session.execute(
            select(EntityIndex).where(EntityIndex.id == entity_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_ontology_and_name(
        self, 
        ontology_id: str, 
        entity_type: str, 
        name: str
    ) -> Optional[EntityIndex]:
        """根据本体、类型、名称查询实体"""
        result = await self.session.execute(
            select(EntityIndex).where(
                and_(
                    EntityIndex.ontology_id == ontology_id,
                    EntityIndex.entity_type == entity_type,
                    EntityIndex.name == name
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def list_by_ontology(
        self, 
        ontology_id: str, 
        entity_type: str = None,
        limit: int = 100,
        offset: int = 0
    ) -> list[EntityIndex]:
        """查询本体的所有实体"""
        query = select(EntityIndex).where(
            EntityIndex.ontology_id == ontology_id
        )
        if entity_type:
            query = query.where(EntityIndex.entity_type == entity_type)
        
        query = query.limit(limit).offset(offset)
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def create(self, entity: EntityIndex) -> EntityIndex:
        """创建实体索引"""
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity
    
    async def delete(self, entity: EntityIndex) -> bool:
        """删除实体索引"""
        await self.session.delete(entity)
        await self.session.commit()
        return True
    
    async def delete_by_ontology(
        self, 
        ontology_id: str, 
        entity_type: str = None,
        name: str = None
    ) -> int:
        """
        删除本体的实体索引
        
        Returns:
            删除的数量
        """
        query = select(EntityIndex).where(
            EntityIndex.ontology_id == ontology_id
        )
        if entity_type:
            query = query.where(EntityIndex.entity_type == entity_type)
        if name:
            query = query.where(EntityIndex.name == name)
        
        result = await self.session.execute(query)
        entities = result.scalars().all()
        count = len(entities)
        
        for entity in entities:
            await self.session.delete(entity)
        await self.session.commit()
        
        return count
    
    async def count_by_ontology(self, ontology_id: str, entity_type: str = None) -> int:
        """统计本体的实体数量"""
        query = select(func.count(EntityIndex.id)).where(
            EntityIndex.ontology_id == ontology_id
        )
        if entity_type:
            query = query.where(EntityIndex.entity_type == entity_type)
        
        result = await self.session.execute(query)
        return result.scalar() or 0


# ==================== 快捷函数 ====================

async def index_entity(
    ontology_id: str,
    entity_type: str,
    name: str,
    graph_uri: str = None,
    display_name: str = None
) -> EntityIndex:
    """快捷函数：创建实体索引"""
    async with SystemSession() as session:
        repo = EntityIndexRepository(session)
        entity = EntityIndex(
            ontology_id=ontology_id,
            entity_type=entity_type,
            name=name,
            graph_uri=graph_uri,
            display_name=display_name
        )
        return await repo.create(entity)


async def delete_entity_index(
    ontology_id: str,
    entity_type: str,
    name: str
) -> bool:
    """快捷函数：删除实体索引"""
    async with SystemSession() as session:
        repo = EntityIndexRepository(session)
        entity = await repo.get_by_ontology_and_name(ontology_id, entity_type, name)
        if entity:
            return await repo.delete(entity)
        return False
