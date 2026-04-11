#!/usr/bin/env python3
"""
SRM (Supplier Relationship Management) 数据模拟脚本
==============================================
业务场景：制造业采购管理
数据规模：供应商 50 / 物料 100 / 合同 30 / 采购订单 200 / 发票 300 / 付款 250 / 评估 100

运行方式：
    cd onto-agent-server
    source .venv/bin/activate
    python scripts/srm_data/seed.py

前置条件：
    1. PostgreSQL 运行中（默认 localhost:5432）
    2. 已创建数据库 srm_demo
    3. 已执行 schema.sql 建表
    4. 已安装 faker: pip install faker
"""

import random
import sys
import os
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Optional

# ============================================================
# Faker 实例（中英文混合，更真实）
# ============================================================
try:
    from faker import Faker
except ImportError:
    print("❌ 请先安装 faker: pip install faker")
    sys.exit(1)

fake = Faker(['zh_CN', 'en_US'])  # 中英双语
random.seed(42)
fake.seed_instance(42)

# ============================================================
# 数据库连接
# ============================================================
import psycopg2
from psycopg2.extras import execute_batch
from psycopg2 import sql

DB_CONFIG = {
    "host": os.getenv("PGHOST", "localhost"),
    "port": os.getenv("PGPORT", "5432"),
    "dbname": os.getenv("PGDATABASE", "srm_demo"),
    "user": os.getenv("PGUSER", "postgres"),
    "password": os.getenv("PGPASSWORD", "postgres"),
}

def get_conn():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = False
        return conn
    except psycopg2.OperationalError as e:
        print(f"❌ 数据库连接失败: {e}")
        print(f"   请确认 PostgreSQL 已启动，或检查连接配置: {DB_CONFIG}")
        sys.exit(1)

# ============================================================
# 业务常量
# ============================================================
SUPPLIER_LEVELS = ['A', 'B', 'C', 'D']
SUPPLIER_STATUSES = ['active', 'active', 'active', 'pending', 'suspended']  # active 权重更高
MATERIAL_CATEGORIES = ['电子元器件', '结构件', '原材料', '紧固件', '塑料件', '金属件', '包装材料', '化学品', '轴承', '线缆']
MATERIAL_SUB = {
    '电子元器件': ['电阻', '电容', 'IC芯片', '连接器', 'PCB板'],
    '结构件': ['钣金件', '压铸件', '挤出件'],
    '原材料': ['钢材', '铝材', '塑料粒子', '橡胶'],
    '紧固件': ['螺栓', '螺钉', '螺母', '垫圈'],
    '塑料件': ['注塑件', '吹塑件', '吸塑件'],
    '金属件': ['冲压件', '车削件', 'CNC件'],
    '包装材料': ['纸箱', '托盘', '泡沫', '缠绕膜'],
    '化学品': ['胶水', '清洗剂', '涂料', '溶剂'],
    '轴承': ['深沟球轴承', '滚子轴承', '直线轴承'],
    '线缆': ['电源线', '数据线', '同轴电缆'],
}
UNITS = ['PCS', 'KG', 'M', 'L', 'SET', 'BOX', 'ROLL', 'SHEET']
CURRENCIES = ['CNY', 'CNY', 'CNY', 'CNY', 'USD', 'EUR']  # CNY 为主
PO_STATUSES = ['draft', 'submitted', 'approved', 'fulfilled', 'approved', 'approved', 'closed']
INVOICE_STATUSES = ['issued', 'verified', 'approved', 'paid', 'paid', 'paid', 'paid']
PAYMENT_METHODS = ['bank_transfer', 'bank_transfer', 'bank_transfer', 'credit_line', 'letter_of_credit']
PAYMENT_STATUSES = ['pending', 'processing', 'completed', 'completed', 'completed', 'failed']
EVALUATION_PERIODS = ['quarterly', 'annual']
EVAL_YEARS = [2024, 2025]

PROVINCES = ['广东省', '江苏省', '浙江省', '上海市', '北京市', '山东省', '四川省', '湖北省', '河南省', '安徽省']
CITIES = {
    '广东省': ['深圳', '广州', '东莞', '佛山', '中山'],
    '江苏省': ['苏州', '南京', '无锡', '常州', '南通'],
    '浙江省': ['杭州', '宁波', '温州', '嘉兴', '绍兴'],
    '上海市': ['上海'],
    '山东省': ['青岛', '济南', '烟台', '潍坊', '威海'],
    '四川省': ['成都', '绵阳', '德阳', '宜宾'],
    '湖北省': ['武汉', '襄阳', '宜昌', '荆州'],
    '河南省': ['郑州', '洛阳', '新乡', '许昌'],
    '安徽省': ['合肥', '芜湖', '蚌埠', '马鞍山'],
    '北京市': ['北京'],
}

BANKS = ['中国工商银行', '中国建设银行', '中国农业银行', '中国银行', '招商银行', '交通银行', '浦发银行', '兴业银行']

# ============================================================
# 辅助函数
# ============================================================

def random_date(start: date, end: date) -> date:
    """随机日期"""
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))

def random_future_date(start: date, max_days: int) -> date:
    """随机未来日期"""
    return start + timedelta(days=random.randint(1, max_days))

def d(s: str) -> Decimal:
    """快捷 Decimal"""
    return Decimal(str(s))

def batch_insert(conn, table: str, columns: list, rows: list[tuple], page_size: int = 500):
    """批量插入，内存友好"""
    if not rows:
        return
    col_names = ', '.join(columns)
    placeholders = ', '.join(['%s'] * len(columns))
    query = f"INSERT INTO {table} ({col_names}) VALUES ({placeholders})"
    for i in range(0, len(rows), page_size):
        batch = rows[i:i + page_size]
        with conn.cursor() as cur:
            execute_batch(cur, query, batch, page_size=page_size)
        conn.commit()
        print(f"   {table}: {min(i+page_size, len(rows))}/{len(rows)} rows")

def progress(step: str, current: int, total: int):
    pct = current / total * 100
    bar = '█' * int(pct / 5) + '░' * (20 - int(pct / 5))
    print(f"\r   [{bar}] {pct:5.1f}%  {step}", end='', flush=True)
    if current == total:
        print()

# ============================================================
# 数据生成
# ============================================================

class SRMDataGenerator:
    def __init__(self, conn):
        self.conn = conn
        self.suppliers: list[dict] = []
        self.supplier_ids: list[str] = []
        self.materials: list[dict] = []
        self.material_ids: list[str] = []
        self.contracts: list[dict] = []
        self.contract_ids: list[str] = []
        self.pos: list[dict] = []
        self.po_ids: list[str] = []
        self.invoices: list[dict] = []
        self.invoice_ids: list[str] = []
        self.payments: list[dict] = []
        self.evaluations: list[dict] = []

    # ---- 1. 供应商 ------------------------------------------------

    def generate_suppliers(self, n: int = 50) -> None:
        print(f"\n📦 生成供应商 ({n})...")
        rows = []
        statuses = SUPPLIER_STATUSES
        for i in range(n):
            province = random.choice(PROVINCES)
            city = random.choice(CITIES[province])
            level = random.choices(SUPPLIER_LEVELS, weights=[20, 40, 25, 15])[0]
            status = random.choices(statuses, weights=[70, 10, 15, 4, 1])[0]
            category = random.choice(MATERIAL_CATEGORIES)
            contract_start = random_date(date(2022, 1, 1), date(2024, 12, 31))
            contract_end = contract_start + timedelta(days=random.choice([365, 730, 1095]))
            bank = random.choice(BANKS)
            bank_acc = ''.join([str(random.randint(0, 9)) for _ in range(19)])

            sup_id = str(uuid())
            self.supplier_ids.append(sup_id)
            rows.append((
                sup_id,                               # id (UUID)
                f'S-{i+1:05d}',                      # code
                fake.company(),                       # name
                fake.company_suffix(),                # short_name
                fake.company() + '有限公司',          # legal_name
                fake.bothify('##-#########'),  # tax_id
                fake.bothify('911##########'),       # registration_no
                province, city,
                fake.address(), fake.postcode(),
                fake.url(), fake.phone_number(), fake.email(),
                level, status, category,
                random.choice(MATERIAL_CATEGORIES[:5]) if random.random() > 0.5 else None,
                contract_start, contract_end,
                random.choice([30, 45, 60, 90, 30, 30]),  # payment_terms_days
                bank, bank_acc,
                round(random.uniform(0.06, 0.17), 4),  # tax_rate
                round(random.uniform(100000, 5000000), 2),  # credit_limit
                'system',
            ))
            if (i + 1) % 10 == 0:
                progress('suppliers', i + 1, n)

        batch_insert(self.conn, 'suppliers', [
            'id', 'code', 'name', 'short_name', 'legal_name', 'tax_id', 'registration_no',
            'province', 'city', 'address', 'postal_code', 'website', 'phone', 'email',
            'level', 'status', 'category', 'subcategory',
            'contract_start_date', 'contract_end_date', 'payment_terms_days',
            'bank_name', 'bank_account', 'tax_rate', 'credit_limit', 'created_by',
        ], rows)
        self.suppliers = rows

        # 重新获取真实 UUID
        with self.conn.cursor() as cur:
            cur.execute("SELECT id, code FROM suppliers ORDER BY code")
            self.supplier_ids = [r[0] for r in cur.fetchall()]
        print(f"   ✅ {len(self.supplier_ids)} suppliers inserted")

    # ---- 2. 供应商联系人 --------------------------------------------

    def generate_contacts(self) -> None:
        print(f"\n👤 生成供应商联系人...")
        rows = []
        titles = ['采购经理', '销售总监', '技术主管', '项目经理', '质量经理', '总经理']
        for idx, sid in enumerate(self.supplier_ids):
            num_contacts = random.randint(1, 3)
            for j in range(num_contacts):
                rows.append((
                    str(uuid()),
                    sid,
                    fake.name(), random.choice(titles),
                    random.choice(['采购部', '销售部', '技术部', '质量部', '市场部']),
                    fake.phone_number(), fake.phone_number(),
                    fake.email(), j == 0, True,
                ))
        batch_insert(self.conn, 'supplier_contacts', [
            'id', 'supplier_id', 'name', 'title', 'department',
            'phone', 'mobile', 'email', 'is_primary', 'is_active',
        ], rows)
        print(f"   ✅ {len(rows)} contacts inserted")

    # ---- 3. 物料 ---------------------------------------------------

    def generate_materials(self, n: int = 100) -> None:
        print(f"\n🔩 生成物料 ({n})...")
        rows = []
        for i in range(n):
            cat = random.choice(MATERIAL_CATEGORIES)
            sub = random.choice(MATERIAL_SUB.get(cat, ['通用件']))
            spec = f"{sub}-{fake.bothify('???-####')}"
            standard_cost = round(random.uniform(0.5, 5000), 4)
            currency = random.choices(CURRENCIES, weights=[80, 10, 5, 5, 0, 0])[0]  # 6 elements: CNY×4, USD, EUR

            rows.append((
                str(uuid()),
                f'M-{i+1:05d}',                       # code
                f"{fake.word().capitalize()}{sub}",    # name
                fake.text(max_nb_chars=100),           # description
                cat, sub, spec,
                random.choice(UNITS),
                random.choice(UNITS),
                round(random.uniform(0.8, 1.2), 4),   # conversion_rate
                standard_cost, currency,
                round(random.uniform(10, 1000), 4),   # min_stock
                round(random.uniform(1000, 50000), 4), # max_stock
                round(random.uniform(100, 5000), 4),   # reorder_point
                True, False, 'system',
            ))
            if (i + 1) % 20 == 0:
                progress('materials', i + 1, n)

        batch_insert(self.conn, 'materials', [
            'id', 'code', 'name', 'description', 'category', 'subcategory', 'specification',
            'unit', 'unit_of_measure', 'conversion_rate', 'standard_cost', 'currency',
            'min_stock_level', 'max_stock_level', 'reorder_point',
            'is_active', 'is_suspended', 'created_by',
        ], rows)
        self.materials = rows

        with self.conn.cursor() as cur:
            cur.execute("SELECT id, code FROM materials ORDER BY code")
            self.material_ids = [r[0] for r in cur.fetchall()]
        print(f"   ✅ {len(self.material_ids)} materials inserted")

    # ---- 4. 合同 ---------------------------------------------------

    def generate_contracts(self, n: int = 30) -> None:
        print(f"\n📄 生成采购合同 ({n})...")
        rows = []
        categories = ['年度框架协议', '项目合同', '单价合同', '批量采购合同']
        payment_terms = ['T/T 30天', 'T/T 45天', 'T/T 60天', '月结30天', '见票即付']
        delivery_terms = ['EXW', 'FOB Shanghai', 'FOB Shenzhen', 'CIF', 'DDP']

        for i in range(n):
            sid = random.choice(self.supplier_ids)
            start = random_date(date(2023, 1, 1), date(2024, 9, 30))
            end = start + timedelta(days=random.choice([365, 730]))
            value = round(random.uniform(50000, 5000000), 2)
            status = random.choices(
                ['active', 'active', 'active', 'amended', 'expired', 'terminated'],
                weights=[40, 40, 40, 10, 5, 5]
            )[0]

            rows.append((
                str(uuid()),
                f'C-{random.randint(2023,2025)}-{i+1:05d}',
                sid,
                fake.sentence(nb_words=6),
                random.choice(categories),
                value, 'CNY',
                start, end,
                random.choice(payment_terms),
                random.choice(delivery_terms),
                random.choice([6, 12, 18, 24]),
                status,
                random.random() > 0.7,
                'system',
            ))
            if (i + 1) % 10 == 0:
                progress('contracts', i + 1, n)

        batch_insert(self.conn, 'contracts', [
            'id', 'contract_no', 'supplier_id', 'title', 'category',
            'value', 'currency', 'start_date', 'end_date',
            'payment_terms', 'delivery_terms', 'warranty_months',
            'status', 'is_framework', 'created_by',
        ], rows)

        with self.conn.cursor() as cur:
            cur.execute("SELECT id, contract_no FROM contracts ORDER BY contract_no")
            self.contract_ids = [r[0] for r in cur.fetchall()]
        print(f"   ✅ {len(self.contract_ids)} contracts inserted")

    # ---- 5. 合同物料明细 -------------------------------------------

    def generate_contract_items(self) -> None:
        print(f"\n📎 生成合同物料明细...")
        rows = []
        for cid in self.contract_ids:
            num_items = random.randint(3, 15)
            sel_materials = random.sample(self.material_ids, min(num_items, len(self.material_ids)))
            for j, mid in enumerate(sel_materials):
                mat = self.materials[[m[0] for m in self.materials].index(mid)] if mid in [m[0] for m in self.materials] else None
                unit_price = mat[10] if mat else round(random.uniform(1, 5000), 4)
                qty = round(random.uniform(100, 10000), 4)
                rows.append((
                    str(uuid()), cid, mid,
                    f'M-{mid[-4:]}',  # material_code (简化)
                    f'物料-{mid[-4:]}',  # material_name
                    unit_price, qty,
                    round(random.uniform(0, 0.15), 4),  # discount_rate
                    round(random.uniform(0.06, 0.17), 4),  # tax_rate
                    'CNY', j + 1, datetime.now(),
                ))
        batch_insert(self.conn, 'contract_items', [
            'id', 'contract_id', 'material_id', 'material_code', 'material_name',
            'unit_price', 'quantity', 'discount_rate', 'tax_rate', 'currency', 'line_no', 'created_at',
        ], rows)
        print(f"   ✅ {len(rows)} contract items inserted")

    # ---- 6. 采购订单 -----------------------------------------------

    def generate_purchase_orders(self, n: int = 200) -> None:
        print(f"\n📋 生成采购订单 ({n})...")
        rows = []
        for i in range(n):
            sid = random.choice(self.supplier_ids)
            # 有合同/无合同混合
            contract_id = random.choice([None] + self.contract_ids) if random.random() > 0.3 else None
            order_date = random_date(date(2024, 1, 1), date(2025, 3, 31))
            expected = order_date + timedelta(days=random.randint(7, 90))
            status = random.choices(PO_STATUSES, weights=[5, 10, 60, 20, 3, 2, 0])[0]
            province = random.choice(PROVINCES)
            city = random.choice(CITIES[province])

            rows.append((
                str(uuid()),
                f'PO-{order_date.year}-{i+1:05d}',
                contract_id, sid,
                fake.sentence(nb_words=4),
                random.choice(['生产物资', '办公用品', '原材料', '设备配件']),
                'CNY', Decimal('1'),
                Decimal('0'), Decimal('0'), Decimal('0'),
                order_date, expected, None,
                fake.address(), province, city,
                status, 'approved',
                None, None,
                'system', fake.text(max_nb_chars=100),
            ))
            if (i + 1) % 40 == 0:
                progress('POs', i + 1, n)

        batch_insert(self.conn, 'purchase_orders', [
            'id', 'po_no', 'contract_id', 'supplier_id', 'title', 'category',
            'currency', 'exchange_rate',
            'subtotal', 'tax_amount', 'total_amount',
            'order_date', 'expected_date', 'delivery_date',
            'delivery_address', 'province', 'city',
            'status', 'approval_status', 'approved_by', 'approved_at',
            'created_by', 'notes',
        ], rows)

        with self.conn.cursor() as cur:
            cur.execute("SELECT id, po_no FROM purchase_orders ORDER BY po_no")
            self.po_ids = [r[0] for r in cur.fetchall()]
        print(f"   ✅ {len(self.po_ids)} POs inserted")

    # ---- 7. 采购订单行项 + 汇总PO金额 --------------------------------

    def generate_po_items(self) -> None:
        print(f"\n📎 生成采购订单行项...")
        rows = []
        po_totals: dict[str, dict] = {}  # po_id -> {subtotal, tax, total}

        for po_id in self.po_ids:
            num_items = random.randint(1, 8)
            sel_materials = random.sample(self.material_ids, min(num_items, len(self.material_ids)))
            po_subtotal = Decimal('0')
            po_tax = Decimal('0')
            po_total = Decimal('0')

            for j, mid in enumerate(sel_materials):
                mat = self.materials[j % len(self.materials)]
                qty = Decimal(str(round(random.uniform(10, 5000), 4)))
                unit_price = Decimal(str(round(random.uniform(1, 5000), 4)))
                tax_rate = Decimal(str(round(random.uniform(0.06, 0.17), 4)))
                discount = Decimal(str(round(random.uniform(0, 0.1), 4)))
                net = qty * unit_price * (Decimal('1') - discount)
                tax = net * tax_rate
                total = net * (Decimal('1') + tax_rate)
                po_subtotal += net
                po_tax += tax
                po_total += total

                received = qty * Decimal('0.9') if random.random() > 0.6 else qty
                rows.append((
                    str(uuid()), po_id, j + 1, mid,
                    f'M-{mid[-4:]}', f'物料-{mid[-4:]}', fake.word(),
                    qty, received, qty,
                    unit_price, discount, tax_rate, 'CNY',
                    'partial' if random.random() > 0.6 else 'fulfilled',
                ))
                po_totals[po_id] = {
                    'subtotal': float(po_subtotal.quantize(Decimal('0.01'))),
                    'tax': float(po_tax.quantize(Decimal('0.01'))),
                    'total': float(po_total.quantize(Decimal('0.01'))),
                }

        batch_insert(self.conn, 'purchase_order_items', [
            'id', 'po_id', 'line_no', 'material_id', 'material_code', 'material_name', 'specification',
            'quantity', 'received_qty', 'invoiced_qty',
            'unit_price', 'discount_rate', 'tax_rate', 'currency', 'status',
        ], rows)

        # 更新 PO 汇总金额
        print(f"   📐 更新 PO 汇总金额...")
        with self.conn.cursor() as cur:
            for po_id, amounts in po_totals.items():
                cur.execute(
                    "UPDATE purchase_orders SET subtotal=%s, tax_amount=%s, total_amount=%s WHERE id=%s",
                    (amounts['subtotal'], amounts['tax'], amounts['total'], po_id)
                )
        self.conn.commit()
        print(f"   ✅ {len(rows)} PO items inserted, {len(po_totals)} POs updated")

    # ---- 8. 发票 ---------------------------------------------------

    def generate_invoices(self, n: int = 300) -> None:
        print(f"\n🧾 生成发票 ({n})...")
        rows = []
        invoice_types = ['增值税专用发票', '增值税普通发票', '电子发票']
        tax_rates = [Decimal('0.13'), Decimal('0.13'), Decimal('0.13'), Decimal('0.06'), Decimal('0.03')]

        for i in range(n):
            sid = random.choice(self.supplier_ids)
            # 约70%的发票关联PO
            po_id = random.choice(self.po_ids) if random.random() > 0.3 else None
            invoice_date = random_date(date(2024, 1, 1), date(2025, 3, 31))
            subtotal = round(random.uniform(500, 200000), 2)
            tax_rate = random.choice(tax_rates)
            tax = round(subtotal * float(tax_rate), 2)
            total = round(subtotal + tax, 2)
            paid = Decimal('0')
            status = random.choices(INVOICE_STATUSES, weights=[5, 10, 15, 65, 3, 2, 0])[0]
            if status == 'paid':
                paid = Decimal(str(total))

            rows.append((
                str(uuid()),
                f'INV-{invoice_date.year}-{i+1:06d}',
                sid, po_id,
                random.choice(invoice_types),
                invoice_date,
                f'{invoice_date.year}年{invoice_date.month}月',
                'CNY',
                Decimal(str(subtotal)),
                Decimal(str(tax)),
                Decimal(str(total)),
                paid,
                fake.company() + '税务局',
                tax_rate,
                fake.bothify('##########'),
                status,
                None, None, None,
                'system',
            ))
            if (i + 1) % 60 == 0:
                progress('invoices', i + 1, n)

        batch_insert(self.conn, 'invoices', [
            'id', 'invoice_no', 'supplier_id', 'po_id', 'invoice_type', 'invoice_date',
            'billing_period', 'currency', 'subtotal', 'tax_amount', 'total_amount',
            'paid_amount', 'tax_authority', 'tax_rate', 'tax_number',
            'status', 'verified_by', 'verified_at', 'verified_notes', 'created_by',
        ], rows)

        with self.conn.cursor() as cur:
            cur.execute("SELECT id, total_amount FROM invoices ORDER BY invoice_no")
            self.invoice_ids = [r[0] for r in cur.fetchall()]
        print(f"   ✅ {len(self.invoice_ids)} invoices inserted")

    # ---- 9. 发票行项 -----------------------------------------------

    def generate_invoice_items(self) -> None:
        print(f"\n📎 生成发票行项...")
        rows = []
        for inv_id in self.invoice_ids:
            num_items = random.randint(1, 5)
            for j in range(num_items):
                qty = round(random.uniform(1, 1000), 4)
                unit_price = round(random.uniform(10, 10000), 4)
                tax_rate = random.choice([0.13, 0.13, 0.06, 0.03])
                rows.append((
                    str(uuid()), inv_id, None,
                    j + 1,
                    fake.sentence(nb_words=4),
                    f'M-{random.randint(1,100):04d}',
                    fake.word() + '物料',
                    Decimal(str(qty)),
                    Decimal(str(unit_price)),
                    Decimal('0'),
                    Decimal(str(tax_rate)),
                ))
        batch_insert(self.conn, 'invoice_items', [
            'id', 'invoice_id', 'po_item_id', 'line_no', 'description',
            'material_code', 'material_name', 'quantity', 'unit_price',
            'discount_rate', 'tax_rate',
        ], rows)
        print(f"   ✅ {len(rows)} invoice items inserted")

    # ---- 10. 付款记录 -----------------------------------------------

    def generate_payments(self, n: int = 250) -> None:
        print(f"\n💰 生成付款记录 ({n})...")
        rows = []
        for i in range(n):
            sid = random.choice(self.supplier_ids)
            invoice_id = random.choice(self.invoice_ids) if random.random() > 0.2 else None
            payment_date = random_date(date(2024, 2, 1), date(2025, 4, 15))
            amount = round(random.uniform(1000, 500000), 2)
            due_date = payment_date + timedelta(days=random.choice([0, 7, 15, 30]))
            status = random.choices(PAYMENT_STATUSES, weights=[10, 5, 75, 10, 0, 0])[0]
            method = random.choices(PAYMENT_METHODS, weights=[70, 15, 10, 5, 0])[0]
            bank = random.choice(BANKS)
            bank_acc = ''.join([str(random.randint(0, 9)) for _ in range(19)])
            tx_ref = fake.bothify('TXN-????????????') if status in ('completed', 'processing') else None

            rows.append((
                str(uuid()),
                f'PAY-{payment_date.year}-{i+1:06d}',
                sid, invoice_id,
                'CNY', Decimal(str(amount)), Decimal('1'),
                payment_date, due_date, method,
                status,
                bank, bank_acc, tx_ref,
                'approved' if status in ('completed', 'processing') else None,
                datetime.now() if status in ('completed', 'processing') else None,
                'system', fake.text(max_nb_chars=80),
            ))
            if (i + 1) % 50 == 0:
                progress('payments', i + 1, n)

        batch_insert(self.conn, 'payments', [
            'id', 'payment_no', 'supplier_id', 'invoice_id', 'currency', 'amount',
            'exchange_rate', 'payment_date', 'due_date', 'method',
            'status', 'bank_name', 'bank_account', 'transaction_ref',
            'approved_by', 'approved_at', 'created_by', 'notes',
        ], rows)
        self.payments = rows
        print(f"   ✅ {len(rows)} payments inserted")

    # ---- 11. 供应商评估 ---------------------------------------------

    def generate_evaluations(self) -> None:
        print(f"\n📊 生成供应商评估...")
        rows = []
        seen_eval_keys: set = set()
        for sid in self.supplier_ids:
            for year in EVAL_YEARS:
                for quarter in [1, 2, 3, 4]:
                    # 随机跳过一些评估
                    if random.random() > 0.85:
                        continue
                    # 去重
                    key = (sid, year, quarter)
                    if key in seen_eval_keys:
                        continue
                    seen_eval_keys.add(key)

                    quality = round(random.uniform(50, 100), 2)
                    delivery = round(random.uniform(50, 100), 2)
                    price = round(random.uniform(50, 100), 2)
                    service = round(random.uniform(50, 100), 2)
                    tech = round(random.uniform(50, 100), 2)
                    overall = round(quality * 0.30 + delivery * 0.25 + price * 0.20 + service * 0.15 + tech * 0.10, 2)
                    grade = 'A' if overall >= 90 else 'B' if overall >= 75 else 'C' if overall >= 60 else 'D'

                    rows.append((
                        str(uuid()), sid, year, quarter, 'quarterly',
                        quality, delivery, price, service, tech,
                        overall, grade,
                        fake.text(max_nb_chars=80),
                        fake.text(max_nb_chars=80),
                        fake.text(max_nb_chars=80) if random.random() > 0.5 else None,
                        True,  # is_final: always TRUE → only one row per supplier/year/quarter
                        fake.name(), datetime.now(),
                    ))

        batch_insert(self.conn, 'supplier_evaluations', [
            'id', 'supplier_id', 'evaluation_year', 'evaluation_quarter', 'period_type',
            'quality_score', 'delivery_score', 'price_score', 'service_score', 'tech_score',
            'overall_score', 'grade',
            'strengths', 'weaknesses', 'improvement_plan',
            'is_final', 'evaluated_by', 'evaluated_at',
        ], rows)
        self.evaluations = rows
        print(f"   ✅ {len(rows)} evaluations inserted")

    # ---- 12. 物化视图刷新 -------------------------------------------

    def refresh_views(self) -> None:
        print(f"\n🔄 刷新物化视图...")
        try:
            with self.conn.cursor() as cur:
                cur.execute("REFRESH MATERIALIZED VIEW supplier_payables")
            self.conn.commit()
            print("   ✅ supplier_payables 刷新完成")
        except Exception as e:
            print(f"   ⚠️ 物化视图刷新失败（无影响）: {e}")

    # ============================================================
    # 主流程
    # ============================================================
    def run(self):
        print("=" * 60)
        print("SRM 数据模拟脚本 - 供应商关系管理")
        print("=" * 60)

        t0 = datetime.now()

        self.generate_suppliers(50)
        self.generate_contacts()
        self.generate_materials(100)
        self.generate_contracts(30)
        self.generate_contract_items()
        self.generate_purchase_orders(200)
        self.generate_po_items()
        self.generate_invoices(300)
        self.generate_invoice_items()
        self.generate_payments(250)
        self.generate_evaluations()
        self.refresh_views()

        t1 = datetime.now()
        total = (t1 - t0).total_seconds()

        # 统计
        with self.conn.cursor() as cur:
            stats = {}
            for table in ['suppliers', 'supplier_contacts', 'materials', 'contracts',
                           'contract_items', 'purchase_orders', 'purchase_order_items',
                           'invoices', 'invoice_items', 'payments', 'supplier_evaluations']:
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                stats[table] = cur.fetchone()[0]

        print("\n" + "=" * 60)
        print("✅ 数据生成完成!")
        print(f"⏱️  耗时: {total:.1f}s")
        print("-" * 40)
        print(f"   供应商              {stats['suppliers']:>6} 条")
        print(f"   联系人              {stats['supplier_contacts']:>6} 条")
        print(f"   物料                {stats['materials']:>6} 条")
        print(f"   合同                {stats['contracts']:>6} 条")
        print(f"   合同物料明细        {stats['contract_items']:>6} 条")
        print(f"   采购订单            {stats['purchase_orders']:>6} 条")
        print(f"   订单行项            {stats['purchase_order_items']:>6} 条")
        print(f"   发票                {stats['invoices']:>6} 条")
        print(f"   发票行项            {stats['invoice_items']:>6} 条")
        print(f"   付款记录            {stats['payments']:>6} 条")
        print(f"   供应商评估          {stats['supplier_evaluations']:>6} 条")
        print("-" * 40)
        total_rows = sum(stats.values())
        print(f"   {'合计':<16} {total_rows:>6} 条")
        print("=" * 60)


# ============================================================
# UUID 兼容
# ============================================================
def uuid():
    import uuid as _uuid
    return str(_uuid.uuid4())

# ============================================================
# 主入口
# ============================================================
if __name__ == '__main__':
    print("\n🔌 连接数据库...")
    conn = get_conn()
    print(f"   已连接: {DB_CONFIG['dbname']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}")

    # 确认表存在
    with conn.cursor() as cur:
        cur.execute("""
            SELECT tablename FROM pg_tables
            WHERE schemaname = 'public'
            AND tablename IN ('suppliers', 'materials', 'purchase_orders')
        """)
        existing = {r[0] for r in cur.fetchall()}
        required = {'suppliers', 'materials', 'purchase_orders'}
        missing = required - existing
        if missing:
            print(f"\n❌ 以下表不存在，请先运行 schema.sql:")
            for t in sorted(missing):
                print(f"   - {t}")
            print(f"\n   运行命令:")
            print(f"   psql -h {DB_CONFIG['host']} -U {DB_CONFIG['user']} -d {DB_CONFIG['dbname']} -f scripts/srm_data/schema.sql")
            sys.exit(1)

    # 确认是否有数据
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM suppliers")
        count = cur.fetchone()[0]
        if count > 0:
            import sys
            if sys.stdin.isatty():
                response = input(f"\n⚠️  数据库已有 {count} 条供应商数据，是否清空后重新生成？(y/N): ")
            else:
                response = 'y'  # 非交互模式自动清空
            if response.strip().lower() == 'y':
                print("   清空现有数据...")
                with conn.cursor() as cur2:
                    # 禁用外键检查
                    cur2.execute("SET session_replication_role = 'replica'")
                    for table in ['payments', 'invoice_items', 'invoices',
                                   'purchase_order_items', 'purchase_orders',
                                   'contract_items', 'contracts',
                                   'supplier_evaluations', 'supplier_contacts',
                                   'materials', 'suppliers']:
                        cur2.execute(f"TRUNCATE TABLE {table} CASCADE")
                    cur2.execute("SET session_replication_role = DEFAULT")
                conn.commit()
                print("   ✅ 数据已清空")
            else:
                print("   取消操作，退出。")
                sys.exit(0)

    try:
        gen = SRMDataGenerator(conn)
        gen.run()
    finally:
        conn.close()
        print("\n🔌 数据库连接已关闭")
