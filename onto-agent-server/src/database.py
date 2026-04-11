"""
数据库连接配置（双数据库架构）

- system_db: 系统内部数据（本体、实体、版本、Saga）
- onto_agent: 本体业务数据（datasources, mappings, sync_tasks 等）

导出:
- Base: SQLAlchemy 声明式基类
- SystemSession: 系统数据库会话
- BusinessSession: 本体业务数据库会话
- init_db: 数据库初始化函数
- get_db: FastAPI 依赖项（本体业务数据库）
- get_system_db: FastAPI 依赖项（系统数据库）
"""

import os
from typing import AsyncGenerator
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import text

# 加载环境变量
load_dotenv()


# ==================== SQLAlchemy Base ====================
Base = declarative_base()


def create_session_maker(db_url: str):
    """创建异步会话制造器"""
    engine = create_async_engine(db_url, echo=False)
    return sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# ==================== 系统数据库 ====================
# 系统内部数据：ontologies, entity_index, ontology_versions, operation_logs
SYSTEM_DB_URL = os.getenv("SYSTEM_DB_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/system_db")
system_engine = create_async_engine(SYSTEM_DB_URL, echo=False)
SystemSession = create_session_maker(SYSTEM_DB_URL)


# ==================== 本体业务数据库 ====================
# 本体业务数据：datasources, mappings, sync_tasks 等
BUSINESS_DB_URL = os.getenv("BUSINESS_DB_URL", "postgresql+asyncpg://postgres:postgres@localhost:5433/onto_agent")
business_engine = create_async_engine(BUSINESS_DB_URL, echo=False)
BusinessSession = create_session_maker(BUSINESS_DB_URL)


# ==================== FastAPI 依赖项 ====================

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI 依赖项：获取本体业务数据库会话
    
    用于: datasource, mapping, sync_task 等业务路由
    """
    async with BusinessSession() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_system_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI 依赖项：获取系统数据库会话
    
    用于: ontology, entity, version 等系统路由
    """
    async with SystemSession() as session:
        try:
            yield session
        finally:
            await session.close()


# ==================== 数据库初始化 ====================
async def init_db():
    """
    初始化数据库连接
    """
    try:
        async with SystemSession() as session:
            await session.execute(text("SELECT 1"))
        print("✓ System database connected")
        
        async with BusinessSession() as session:
            await session.execute(text("SELECT 1"))
        print("✓ Business database connected")
            
    except Exception as e:
        print(f"⚠ Database init warning: {e}")
