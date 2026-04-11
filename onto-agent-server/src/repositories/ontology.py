"""
Ontology Repository — 数据访问层

封装 Ontology 模型的所有数据库操作
"""

from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.ontology import Ontology
from src.database import SystemSession
from src.logging_config import get_logger

logger = get_logger("repository.ontology")


class OntologyRepository:
    """Ontology 数据访问类"""
    
    def __init__(self, session: AsyncSession = None):
        self._session = session
    
    @property
    def session(self) -> AsyncSession:
        """延迟获取 session"""
        if self._session is None:
            raise RuntimeError("Session not set. Use async context or provide session.")
        return self._session
    
    async def get_by_id(self, ontology_id: str) -> Optional[Ontology]:
        """根据 ID 查询本体"""
        result = await self.session.execute(
            select(Ontology).where(Ontology.id == ontology_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_name(self, name: str) -> Optional[Ontology]:
        """根据名称查询本体"""
        result = await self.session.execute(
            select(Ontology).where(Ontology.name == name)
        )
        return result.scalar_one_or_none()
    
    async def list_all(self, limit: int = 100, offset: int = 0) -> tuple[list[Ontology], int]:
        """
        查询所有本体
        
        Returns:
            (ontologies, total_count)
        """
        # 计数
        count_result = await self.session.execute(
            select(func.count(Ontology.id))
        )
        total = count_result.scalar() or 0
        
        # 分页查询
        result = await self.session.execute(
            select(Ontology)
            .order_by(Ontology.updated_at.desc())
            .limit(limit)
            .offset(offset)
        )
        ontologies = result.scalars().all()
        
        return list(ontologies), total
    
    async def create(self, ontology: Ontology) -> Ontology:
        """创建本体"""
        self.session.add(ontology)
        await self.session.commit()
        await self.session.refresh(ontology)
        return ontology
    
    async def update(self, ontology: Ontology) -> Ontology:
        """更新本体"""
        await self.session.commit()
        await self.session.refresh(ontology)
        return ontology
    
    async def delete(self, ontology: Ontology) -> bool:
        """删除本体"""
        await self.session.delete(ontology)
        await self.session.commit()
        return True
    
    async def exists(self, ontology_id: str) -> bool:
        """检查本体是否存在"""
        result = await self.session.execute(
            select(func.count(Ontology.id)).where(Ontology.id == ontology_id)
        )
        return (result.scalar() or 0) > 0


# ==================== 快捷函数 ====================

async def get_ontology_by_id(ontology_id: str) -> Optional[Ontology]:
    """快捷函数：通过 ID 获取本体"""
    async with SystemSession() as session:
        repo = OntologyRepository(session)
        return await repo.get_by_id(ontology_id)


async def list_ontologies(limit: int = 100, offset: int = 0) -> tuple[list[Ontology], int]:
    """快捷函数：分页查询本体"""
    async with SystemSession() as session:
        repo = OntologyRepository(session)
        return await repo.list_all(limit, offset)


async def delete_ontology_by_id(ontology_id: str) -> bool:
    """快捷函数：通过 ID 删除本体"""
    async with SystemSession() as session:
        repo = OntologyRepository(session)
        ontology = await repo.get_by_id(ontology_id)
        if ontology is None:
            return False
        return await repo.delete(ontology)
