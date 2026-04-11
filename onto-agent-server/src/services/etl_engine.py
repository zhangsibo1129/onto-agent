"""
Phase 5+6: ETL Engine
属性数据源配置 → SQL → RDF → Jena ABox
"""
import asyncio
import asyncpg
from datetime import datetime
from collections import defaultdict
from typing import Optional

from src.database import SystemSession
from src.services.jena import get_jena_client
from src.logging_config import get_logger

logger = get_logger("etl_engine")


class ETLEngine:
    """
    ETL 引擎：根据属性来源配置，构造 SQL，读取数据，转换为 RDF，写入 Jena ABox
    """

    def __init__(self, ontology_id: str):
        self.ontology_id = ontology_id
        self.ontology = None
        self.property_sources = []
        self.datasource = None
        self.source_conn: Optional[asyncpg.Connection] = None
        self.logs = []  # (level, message)
        self._jena_client = None

    # ============================================================
    # 辅助方法
    # ============================================================

    def _log(self, level: str, message: str):
        ts = datetime.now().strftime("%H:%M:%S")
        self.logs.append((level, f"[{ts}] {message}"))
        logger.info(f"[{level.upper()}] {message}")

    @property
    def jena(self):
        if self._jena_client is None:
            self._jena_client = get_jena_client(self.ontology.dataset)
        return self._jena_client

    # ============================================================
    # Step 1: 加载配置
    # ============================================================

    async def load_config(self):
        """从 PostgreSQL 加载本体、数据源、属性配置"""
        async with SystemSession() as session:
            # 加载本体
            from sqlalchemy import text
            result = await session.execute(
                text("SELECT * FROM ontologies WHERE id = :id"),
                {"id": self.ontology_id}
            )
            row = result.fetchone()
            if not row:
                raise ValueError(f"Ontology {self.ontology_id} not found")
            
            self.ontology = dict(row._mapping)
            self.base_iri = self.ontology['base_iri']

            # 加载属性配置
            result = await session.execute(
                text("SELECT * FROM property_sources WHERE ontology_id = :id ORDER BY source_table, property_local_name"),
                {"id": self.ontology_id}
            )
            self.property_sources = [dict(r._mapping) for r in result.fetchall()]

            # 加载数据源
            datasource_id = self.ontology.get('datasource_id')
            if not datasource_id:
                raise ValueError(f"Ontology {self.ontology_id} has no datasource_id")

            # 数据源在 System DB
            from src.database import system_engine
            async with system_engine.connect() as sys_conn:
                result = await sys_conn.execute(
                    text("SELECT * FROM datasources WHERE id = :id"),
                    {"id": datasource_id}
                )
                row = result.fetchone()
                if not row:
                    raise ValueError(f"Datasource {datasource_id} not found")
                self.datasource = dict(row._mapping)

        if not self.property_sources:
            raise ValueError(f"No property sources configured for ontology {self.ontology_id}")

        self._log("info", f"加载配置：本体的数据源={self.datasource['name']}({self.datasource['type']})")
        self._log("info", f"加载了 {len(self.property_sources)} 个属性配置")

    # ============================================================
    # Step 2: 连接源数据库
    # ============================================================

    async def connect_source(self):
        """连接到源数据库"""
        ds = self.datasource
        try:
            if ds['type'] == 'postgres':
                conn = await asyncpg.connect(
                    host=ds.get('host') or 'localhost',
                    port=ds.get('port') or 5432,
                    user=ds.get('username') or 'postgres',
                    password=ds.get('password') or '',
                    database=ds.get('database') or ds.get('schema') or 'postgres',
                )
            elif ds['type'] == 'mysql':
                import aiomysql
                conn = await aiomysql.connect(
                    host=ds.get('host') or 'localhost',
                    port=ds.get('port') or 3306,
                    user=ds.get('username') or 'root',
                    password=ds.get('password') or '',
                    db=ds.get('database') or ds.get('schema') or '',
                )
            else:
                raise ValueError(f"Unsupported db type: {ds['type']}")
            
            self.source_conn = conn
            self._log("success", f"连接源数据库成功")
        except Exception as e:
            self._log("error", f"连接源数据库失败: {e}")
            raise

    # ============================================================
    # Step 3: 分组属性 by 表
    # ============================================================

    def group_by_table(self) -> dict[str, list]:
        """按 source_table 分组属性"""
        tables = defaultdict(list)
        for prop in self.property_sources:
            tables[prop['source_table']].append(prop)
        return dict(tables)

    # ============================================================
    # Step 4: 推断 join 关系
    # ============================================================

    async def infer_joins(self, table_groups: dict) -> list[dict]:
        """
        自动推断表间的 join 关系
        规则：两张表都有同一个列名 → 尝试作为 join key
        """
        tables = list(table_groups.keys())
        joins = []

        if len(tables) <= 1:
            return joins

        # 收集每张表的 instance_id_column
        id_columns = {}
        all_columns = defaultdict(set)
        for table, props in table_groups.items():
            id_col = props[0]['instance_id_column']
            id_columns[table] = id_col
            all_columns[table].add(id_col)

        # 两两检查是否有共同的列名（排除主键本身）
        for i, t1 in enumerate(tables):
            for t2 in tables[i+1:]:
                common = all_columns[t1] & all_columns[t2]
                # 排除自己跟自己的交集
                common = {c for c in common if c != id_columns[t1] or c != id_columns[t2]}
                if len(common) == 1:
                    join_col = common.pop()
                    joins.append({
                        'from_table': t1,
                        'to_table': t2,
                        'join_column': join_col,
                        'from_instance_id': id_columns[t1],
                        'to_instance_id': id_columns[t2],
                        'auto_inferred': True
                    })
                    self._log("info", f"自动推断 join: {t1}.{join_col} = {t2}.{join_col}")
                elif len(common) > 1:
                    self._log("warning", f"表 {t1} 和 {t2} 有多个共同列 {common}，请手动配置关联")
                else:
                    self._log("warning", f"无法自动推断 {t1} 和 {t2} 的关联，请配置显式关系")

        return joins

    # ============================================================
    # Step 5: 补充兜底配置
    # ============================================================

    async def load_explicit_relations(self, joins: list) -> list:
        """查询显式配置的关联关系"""
        if not self.datasource:
            return joins

        from src.database import system_engine
        async with system_engine.connect() as conn:
            from sqlalchemy import text
            result = await conn.execute(
                text("SELECT * FROM data_source_relations WHERE datasource_id = :ds_id"),
                {"ds_id": self.datasource['id']}
            )
            explicit = [dict(r._mapping) for r in result.fetchall()]

        existing_pairs = {(j['from_table'], j['to_table']) for j in joins}
        for rel in explicit:
            pair = (rel['from_table'], rel['to_table'])
            reverse = (rel['to_table'], rel['from_table'])
            if pair not in existing_pairs and reverse not in existing_pairs:
                joins.append({
                    'from_table': rel['from_table'],
                    'to_table': rel['to_table'],
                    'join_column': rel['from_column'],
                    'to_column': rel['to_column'],
                    'auto_inferred': False
                })
                self._log("info", f"使用显式配置 join: {rel['from_table']}.{rel['from_column']} = {rel['to_table']}.{rel['to_column']}")

        return joins

    # ============================================================
    # Step 6: 构造 SQL
    # ============================================================

    def build_sql(self, table_groups: dict, joins: list) -> tuple[str, dict]:
        """
        构造 JOIN SQL，返回 (sql, col_alias_map)
        col_alias_map: { property_name: column_alias }
        """
        tables = list(table_groups.keys())
        col_alias_map = {}  # property_local_name -> column alias in SQL

        if len(tables) == 1:
            # 单表
            table = tables[0]
            props = table_groups[table]
            id_col = props[0]['instance_id_column']
            
            cols = [f't0."{id_col}" AS _instance_id']
            for p in props:
                alias = f"{p['source_table']}__{p['source_column']}"
                cols.append(f't0."{p['source_column']}" AS "{alias}"')
                col_alias_map[p['property_local_name']] = alias
            
            sql = f'SELECT {", ".join(cols)} FROM "{table}" t0'
            
            # WHERE 过滤条件
            filters = [p['filter_condition'] for p in props if p.get('filter_condition')]
            if filters:
                sql += ' WHERE ' + ' AND '.join(filters)

        else:
            # 多表：构造 JOIN
            id_col = table_groups[tables[0]][0]['instance_id_column']
            
            # SELECT
            cols = [f't0."{id_col}" AS _instance_id']
            for i, (table, props) in enumerate(table_groups.items()):
                for p in props:
                    alias = f"{p['source_table']}__{p['source_column']}"
                    cols.append(f't{i}."{p['source_column']}" AS "{alias}"')
                    col_alias_map[p['property_local_name']] = alias
            
            sql = f'SELECT {", ".join(cols)} FROM "{tables[0]}" t0 '
            
            # JOIN 子句
            for i, table in enumerate(tables[1:], 1):
                join_info = next(
                    (j for j in joins if j['from_table'] == tables[0] and j['to_table'] == table),
                    None
                )
                if not join_info:
                    join_info = next(
                        (j for j in joins if j['from_table'] == table and j['to_table'] == tables[0]),
                        None
                    )
                
                if join_info and join_info.get('auto_inferred'):
                    join_col = join_info['join_column']
                    sql += f'LEFT JOIN "{table}" t{i} ON t0."{join_col}" = t{i}."{join_col}" '
                elif join_info:
                    # 显式配置
                    sql += f'LEFT JOIN "{table}" t{i} ON t0."{join_info["join_column"]}" = t{i}."{join_info["to_column"]}" '
                else:
                    # 无法 join，跳过
                    self._log("warning", f"无法 join 表 {table}，跳过")
            
            # WHERE 过滤
            filters = []
            for props in table_groups.values():
                for p in props:
                    if p.get('filter_condition'):
                        filters.append(p['filter_condition'])
            if filters:
                sql += ' WHERE ' + ' AND '.join(filters)

        return sql, col_alias_map

    # ============================================================
    # Step 7: 执行 ETL
    # ============================================================

    async def execute(self):
        """
        执行完整 ETL 流程，返回 (success, logs)
        """
        try:
            await self.load_config()
            await self.connect_source()

            # 分组
            table_groups = self.group_by_table()
            self._log("info", f"属性来自 {len(table_groups)} 张表: {list(table_groups.keys())}")

            # 推断 join
            joins = await self.infer_joins(table_groups)

            # 补充显式配置
            joins = await self.load_explicit_relations(joins)

            # 构造 SQL
            sql, col_alias_map = self.build_sql(table_groups, joins)
            self._log("info", f"构造 SQL: {sql[:300]}...")

            # 执行查询
            rows = await self.source_conn.fetch(sql)
            total = len(rows)
            self._log("info", f"从源数据库读取 {total} 行")

            if total == 0:
                self._log("warning", "源数据库返回 0 行，ETL 结束")
                return True, self.logs

            # 转换为 RDF triples
            triples = self._rows_to_triples(rows, col_alias_map)
            self._log("info", f"生成 {len(triples)} 个 RDF triples")

            # 写入 Jena ABox
            await self._write_to_jena(triples)
            self._log("success", f"ETL 完成：写入 {total} 个实例到 Jena ABox")

            return True, self.logs

        except Exception as e:
            import traceback
            self._log("error", f"ETL 失败: {e}")
            self._log("error", traceback.format_exc())
            return False, self.logs

        finally:
            if self.source_conn:
                await self.source_conn.close()

    # ============================================================
    # Step 8: RDF 转换
    # ============================================================

    def _rows_to_triples(self, rows: list, col_alias_map: dict) -> list:
        """将 SQL 结果行转换为 (subject, predicate, object) triples"""
        triples = []

        for row in rows:
            instance_id = row['_instance_id']
            if instance_id is None:
                continue

            # 支持 instance_id 是 int 或 string
            instance_uri = f"{self.base_iri}/{instance_id}"

            for prop_name, alias in col_alias_map.items():
                if alias in row and row[alias] is not None:
                    value = row[alias]
                    value_str = str(value)
                    # 简单判断：数字/布尔 → 直接值，其他 → 带引号字符串
                    if isinstance(value, (int, float)):
                        triples.append((instance_uri, prop_name, f'"{value_str}"^^<http://www.w3.org/2001/XMLSchema#integer>' if isinstance(value, int) else f'"{value_str}"^^<http://www.w3.org/2001/XMLSchema#decimal>'))
                    elif isinstance(value, bool):
                        triples.append((instance_uri, prop_name, f'"{value_str}"^^<http://www.w3.org/2001/XMLSchema#boolean>'))
                    else:
                        # 字符串，转义引号
                        value_str = value_str.replace('"', '\\"')
                        triples.append((instance_uri, prop_name, f'"{value_str}"'))

        return triples

    # ============================================================
    # Step 9: 写入 Jena
    # ============================================================

    async def _write_to_jena(self, triples: list):
        """将 triples 写入 Jena ABox"""
        abox_graph = f"{self.base_iri}/abox"

        # 构造 Turtle
        turtle = self._triples_to_turtle(triples)

        # GSP 写入（原子替换）
        self.jena.gsp.put(abox_graph, turtle, content_type="text/turtle")

    def _triples_to_turtle(self, triples: list) -> str:
        """triples list → Turtle 字符串"""
        lines = [
            '@prefix : <{}#> .'.format(self.base_iri.rstrip('/#')),
            '@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .',
            '@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .',
            '@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .',
            ''
        ]

        # 按 instance 分组
        instances = defaultdict(list)
        for s, p, o in triples:
            instances[s].append((p, o))

        base = self.base_iri.rstrip('/#')
        for s, props in instances.items():
            # 去掉 base 前缀，简化表示
            s_short = s.replace(base + '/', '').replace(base + '#', '').replace(base + '/', '')
            s_short = s_short or 'instance'
            lines.append(f':{s_short} rdf:type :Thing ;')
            for p, o in props:
                lines.append(f'    :{p} {o} ;')
            lines[-1] = lines[-1][:-2] + '.'  # 最后一句改分号为句号

        return '\n'.join(lines)
