"""
数据库迁移脚本 v002

修改内容：
1. 修改 ontologies 表 - 添加 Named Graph 相关字段
2. 新增 ontology_versions 表 - 版本管理
3. 修改 entity_index 表 - 添加 graph_uri 字段
4. 新增 operation_logs 表 - Saga 事务追踪

运行方式:
    cd onto-agent-server
    source .venv/bin/activate
    python -m alembic upgrade head
    alembic revision --autogenerate -m "update ontology named graphs"
    python -m alembic upgrade head
"""

import asyncio
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv()


def upgrade(connection):
    """执行数据库升级"""
    
    # 1. 修改 ontologies 表
    print("Modifying ontologies table...")
    connection.execute(text("""
        ALTER TABLE ontologies 
        ADD COLUMN IF NOT EXISTS dataset VARCHAR(100) DEFAULT '/onto-agent'
    """))
    connection.execute(text("""
        ALTER TABLE ontologies 
        ADD COLUMN IF NOT EXISTS tbox_graph_uri VARCHAR(500) NOT NULL
    """))
    connection.execute(text("""
        ALTER TABLE ontologies 
        ADD COLUMN IF NOT EXISTS abox_graph_uri VARCHAR(500)
    """))
    connection.execute(text("""
        ALTER TABLE ontologies 
        ADD COLUMN IF NOT EXISTS published_at TIMESTAMP
    """))
    
    # 2. 新增 ontology_versions 表
    print("Creating ontology_versions table...")
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS ontology_versions (
            id VARCHAR(50) PRIMARY KEY,
            ontology_id VARCHAR(50) NOT NULL REFERENCES ontologies(id) ON DELETE CASCADE,
            version VARCHAR(20) NOT NULL,
            status VARCHAR(20) DEFAULT 'published',
            tbox_graph_uri VARCHAR(500) NOT NULL,
            abox_graph_uri VARCHAR(500),
            change_log JSONB DEFAULT '[]',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            published_at TIMESTAMP,
            UNIQUE (ontology_id, version)
        )
    """))
    connection.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_ontology_versions_ontology_id 
        ON ontology_versions(ontology_id)
    """))
    
    # 3. 修改 entity_index 表
    print("Modifying entity_index table...")
    connection.execute(text("""
        ALTER TABLE entity_index 
        ADD COLUMN IF NOT EXISTS graph_uri VARCHAR(500) NOT NULL
    """))
    connection.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_entity_index_graph_uri 
        ON entity_index(graph_uri)
    """))
    
    # 4. 新增 operation_logs 表
    print("Creating operation_logs table...")
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS operation_logs (
            id VARCHAR(50) PRIMARY KEY,
            ontology_id VARCHAR(50) NOT NULL,
            operation_type VARCHAR(30) NOT NULL,
            entity_type VARCHAR(20) NOT NULL,
            entity_id VARCHAR(100) NOT NULL,
            entity_name VARCHAR(200) NOT NULL,
            jena_uri VARCHAR(500) NOT NULL,
            jena_data JSONB,
            pg_data JSONB,
            status VARCHAR(20) DEFAULT 'pending',
            step VARCHAR(20) DEFAULT 'prepare',
            error_message TEXT,
            retry_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            settled_at TIMESTAMP
        )
    """))
    connection.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_operation_logs_status 
        ON operation_logs(status)
    """))
    connection.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_operation_logs_step 
        ON operation_logs(step)
    """))
    connection.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_operation_logs_ontology 
        ON operation_logs(ontology_id)
    """))
    
    print("Migration completed successfully!")


def downgrade(connection):
    """执行数据库降级"""
    
    print("Rolling back migration...")
    
    # 删除 operation_logs 表
    connection.execute(text("DROP TABLE IF EXISTS operation_logs"))
    
    # 删除 ontology_versions 表
    connection.execute(text("DROP TABLE IF EXISTS ontology_versions"))
    
    # 回滚 entity_index
    connection.execute(text("""
        ALTER TABLE entity_index 
        DROP COLUMN IF EXISTS graph_uri
    """))
    
    # 回滚 ontologies
    connection.execute(text("""
        ALTER TABLE ontologies 
        DROP COLUMN IF EXISTS published_at
    """))
    connection.execute(text("""
        ALTER TABLE ontologies 
        DROP COLUMN IF EXISTS abox_graph_uri
    """))
    connection.execute(text("""
        ALTER TABLE ontologies 
        DROP COLUMN IF EXISTS tbox_graph_uri
    """))
    connection.execute(text("""
        ALTER TABLE ontologies 
        DROP COLUMN IF EXISTS dataset
    """))
    
    print("Rollback completed!")


# 直接运行迁移（用于调试）
if __name__ == "__main__":
    import os
    from sqlalchemy import create_engine
    
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/onto_agent")
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # 启用事务自动提交
        # 注意：实际运行请使用 alembic
        print("Running upgrade...")
        upgrade(conn)
        conn.commit()
        print("Done!")
