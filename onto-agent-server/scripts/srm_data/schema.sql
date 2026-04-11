-- ============================================================
-- SRM (Supplier Relationship Management) 数据架构
-- 供应商关系管理系统 - PostgreSQL DDL
-- ============================================================
-- 业务场景：制造业采购管理
-- 核心流程：供应商管理 → 合同签订 → 采购下单 → 收货发票 → 付款结算 → 绩效评估

-- ============================================================
-- 扩展
-- ============================================================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- 模糊查询支持

-- ============================================================
-- 枚举类型
-- ============================================================

CREATE TYPE supplier_level AS ENUM ('A', 'B', 'C', 'D');  -- 供应商等级
CREATE TYPE supplier_status AS ENUM ('active', 'pending', 'suspended', 'blacklisted');
CREATE TYPE po_status AS ENUM ('draft', 'submitted', 'approved', 'fulfilled', 'cancelled', 'closed');
CREATE TYPE invoice_status AS ENUM ('issued', 'verified', 'approved', 'paid', 'disputed', 'cancelled');
CREATE TYPE payment_method AS ENUM ('bank_transfer', 'credit_line', 'letter_of_credit', 'cash');
CREATE TYPE payment_status AS ENUM ('pending', 'processing', 'completed', 'failed', 'cancelled');
CREATE TYPE currency AS ENUM ('CNY', 'USD', 'EUR', 'JPY');
CREATE TYPE evaluation_period AS ENUM ('quarterly', 'annual');

-- ============================================================
-- 1. 供应商主数据 (suppliers)
-- ============================================================
CREATE TABLE suppliers (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code            VARCHAR(20) UNIQUE NOT NULL,          -- 供应商编码 S-XXXXX
    name            VARCHAR(200) NOT NULL,
    short_name      VARCHAR(100),
    legal_name      VARCHAR(300),                        -- 法人名称
    tax_id          VARCHAR(30),                          -- 税务登记号
    registration_no VARCHAR(50),                          -- 工商注册号

    -- 联系方式
    province        VARCHAR(50),
    city            VARCHAR(50),
    address         VARCHAR(500),
    postal_code     VARCHAR(10),
    website         VARCHAR(200),
    phone           VARCHAR(30),
    email           VARCHAR(100),

    -- 商业信息
    level           supplier_level DEFAULT 'B',
    status          supplier_status DEFAULT 'active',
    category        VARCHAR(100),                        -- 供应商类别：原材料/设备/服务
    subcategory     VARCHAR(100),                        -- 子类别

    -- 合作信息
    contract_start_date DATE,
    contract_end_date   DATE,
    payment_terms_days  INTEGER DEFAULT 30,              -- 付款账期（天）

    -- 财务信息
    bank_name       VARCHAR(200),
    bank_account    VARCHAR(50),
    tax_rate        DECIMAL(5,4) DEFAULT 0.13,          -- 税率
    credit_limit    DECIMAL(15,2),                       -- 信用额度

    -- 元数据
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    created_by      VARCHAR(100),
    is_deleted      BOOLEAN DEFAULT FALSE,

    CONSTRAINT chk_supplier_level CHECK (level IN ('A', 'B', 'C', 'D')),
    CONSTRAINT chk_payment_terms CHECK (payment_terms_days > 0 AND payment_terms_days <= 365)
);

CREATE INDEX idx_suppliers_code ON suppliers(code);
CREATE INDEX idx_suppliers_status ON suppliers(status);
CREATE INDEX idx_suppliers_level ON suppliers(level);
CREATE INDEX idx_suppliers_category ON suppliers(category);

-- ============================================================
-- 2. 供应商联系人 (supplier_contacts)
-- ============================================================
CREATE TABLE supplier_contacts (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    supplier_id     UUID NOT NULL REFERENCES suppliers(id) ON DELETE CASCADE,

    name            VARCHAR(100) NOT NULL,
    title           VARCHAR(100),                        -- 职位
    department      VARCHAR(100),
    phone           VARCHAR(30),
    mobile          VARCHAR(30),
    email           VARCHAR(100),
    is_primary      BOOLEAN DEFAULT FALSE,
    is_active       BOOLEAN DEFAULT TRUE,

    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_contacts_supplier ON supplier_contacts(supplier_id);
CREATE INDEX idx_contacts_primary ON supplier_contacts(supplier_id, is_primary) WHERE is_primary = TRUE;

-- ============================================================
-- 3. 物料主数据 (materials)
-- ============================================================
CREATE TABLE materials (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code            VARCHAR(30) UNIQUE NOT NULL,          -- 物料编码 M-XXXXX
    name            VARCHAR(300) NOT NULL,
    description     TEXT,

    -- 分类
    category        VARCHAR(100),                        -- 物料类别
    subcategory     VARCHAR(100),
    specification   VARCHAR(500),                        -- 规格型号

    -- 单位与转换
    unit            VARCHAR(20) DEFAULT 'PCS',           -- 基本单位
    unit_of_measure VARCHAR(20),                         -- 采购单位
    conversion_rate DECIMAL(10,4) DEFAULT 1,             -- 转换率

    -- 采购信息
    standard_cost   DECIMAL(15,4),                       -- 标准成本
    currency        currency DEFAULT 'CNY',

    -- 库存
    min_stock_level DECIMAL(15,4) DEFAULT 0,
    max_stock_level DECIMAL(15,4),
    reorder_point   DECIMAL(15,4),

    -- 状态
    is_active       BOOLEAN DEFAULT TRUE,
    is_suspended    BOOLEAN DEFAULT FALSE,

    -- 元数据
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    created_by      VARCHAR(100),
    is_deleted      BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_materials_code ON materials(code);
CREATE INDEX idx_materials_category ON materials(category);
CREATE INDEX idx_materials_active ON materials(is_active) WHERE is_active = TRUE;

-- ============================================================
-- 4. 采购合同 (contracts)
-- ============================================================
CREATE TABLE contracts (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    contract_no     VARCHAR(50) UNIQUE NOT NULL,         -- 合同编号 C-YYYY-XXXXX
    supplier_id     UUID NOT NULL REFERENCES suppliers(id),

    title           VARCHAR(300),
    category        VARCHAR(100),                        -- 合同类别
    value           DECIMAL(18,2),                       -- 合同总金额（含税）
    currency        currency DEFAULT 'CNY',

    -- 有效期
    start_date      DATE NOT NULL,
    end_date        DATE NOT NULL,

    -- 条款
    payment_terms   VARCHAR(50),                         -- 付款条款
    delivery_terms  VARCHAR(100),                        -- 交货条款（EXW/FOB/CIF等）
    warranty_months INTEGER DEFAULT 12,

    -- 状态
    status          VARCHAR(30) DEFAULT 'active',         -- draft/active/amended/expired/terminated
    is_framework    BOOLEAN DEFAULT FALSE,               -- 是否框架协议

    -- 元数据
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    created_by      VARCHAR(100),
    is_deleted      BOOLEAN DEFAULT FALSE,

    CONSTRAINT chk_contract_dates CHECK (end_date > start_date),
    CONSTRAINT chk_contract_value CHECK (value >= 0)
);

CREATE INDEX idx_contracts_supplier ON contracts(supplier_id);
CREATE INDEX idx_contracts_no ON contracts(contract_no);
CREATE INDEX idx_contracts_dates ON contracts(start_date, end_date);
CREATE INDEX idx_contracts_status ON contracts(status);

-- ============================================================
-- 5. 合同物料明细 (contract_items)
-- ============================================================
CREATE TABLE contract_items (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    contract_id     UUID NOT NULL REFERENCES contracts(id) ON DELETE CASCADE,

    material_id     UUID REFERENCES materials(id),
    material_code   VARCHAR(30),                         -- 反范式：冗余便于查询
    material_name   VARCHAR(300),

    unit_price      DECIMAL(15,4) NOT NULL,
    quantity        DECIMAL(15,4) NOT NULL,
    discount_rate   DECIMAL(5,4) DEFAULT 0,             -- 折扣率
    tax_rate        DECIMAL(5,4) DEFAULT 0.13,
    currency        currency DEFAULT 'CNY',

    line_no         INTEGER,                             -- 行号

    created_at      TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT chk_line_price CHECK (unit_price >= 0),
    CONSTRAINT chk_line_qty CHECK (quantity > 0),
    CONSTRAINT chk_discount CHECK (discount_rate >= 0 AND discount_rate <= 1)
);

CREATE INDEX idx_contract_items_contract ON contract_items(contract_id);
CREATE INDEX idx_contract_items_material ON contract_items(material_id);

-- ============================================================
-- 6. 采购订单 (purchase_orders)
-- ============================================================
CREATE TABLE purchase_orders (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    po_no           VARCHAR(50) UNIQUE NOT NULL,         -- 订单号 PO-YYYY-XXXXX
    contract_id     UUID REFERENCES contracts(id),       -- 可从合同创建
    supplier_id     UUID NOT NULL REFERENCES suppliers(id),

    -- 订单信息
    title           VARCHAR(300),
    category        VARCHAR(100),
    currency        currency DEFAULT 'CNY',
    exchange_rate   DECIMAL(12,6) DEFAULT 1,             -- 汇率（外币订单）

    -- 金额
    subtotal        DECIMAL(18,2) DEFAULT 0,             -- 小计（不含税）
    tax_amount      DECIMAL(18,2) DEFAULT 0,             -- 税额
    total_amount    DECIMAL(18,2) DEFAULT 0,             -- 含税总额

    -- 日期
    order_date      DATE NOT NULL,
    expected_date   DATE,                                 -- 期望交货日期
    delivery_date   DATE,                                -- 实际交货日期

    -- 地点
    delivery_address VARCHAR(500),
    province        VARCHAR(50),
    city            VARCHAR(50),

    -- 状态
    status          po_status DEFAULT 'draft',
    approval_status VARCHAR(30) DEFAULT 'pending',      -- pending/approved/rejected
    approved_by     VARCHAR(100),
    approved_at     TIMESTAMPTZ,

    -- 元数据
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    created_by      VARCHAR(100),
    notes           TEXT,
    is_deleted      BOOLEAN DEFAULT FALSE,

    CONSTRAINT chk_po_dates CHECK (expected_date >= order_date OR expected_date IS NULL)
);

CREATE INDEX idx_po_supplier ON purchase_orders(supplier_id);
CREATE INDEX idx_po_no ON purchase_orders(po_no);
CREATE INDEX idx_po_status ON purchase_orders(status);
CREATE INDEX idx_po_order_date ON purchase_orders(order_date);
CREATE INDEX idx_po_contract ON purchase_orders(contract_id);

-- ============================================================
-- 7. 采购订单行项 (purchase_order_items)
-- ============================================================
CREATE TABLE purchase_order_items (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    po_id           UUID NOT NULL REFERENCES purchase_orders(id) ON DELETE CASCADE,

    line_no         INTEGER NOT NULL,
    material_id     UUID REFERENCES materials(id),
    material_code   VARCHAR(30),
    material_name   VARCHAR(300),
    specification   VARCHAR(500),

    -- 数量
    quantity        DECIMAL(15,4) NOT NULL,
    received_qty    DECIMAL(15,4) DEFAULT 0,             -- 已收货数量
    invoiced_qty    DECIMAL(15,4) DEFAULT 0,             -- 已开票数量

    -- 价格
    unit_price      DECIMAL(15,4) NOT NULL,
    discount_rate   DECIMAL(5,4) DEFAULT 0,
    tax_rate        DECIMAL(5,4) DEFAULT 0.13,
    currency        currency DEFAULT 'CNY',

    -- 计算字段
    net_amount      DECIMAL(18,4) GENERATED ALWAYS AS (
                        quantity * unit_price * (1 - discount_rate)
                    ) STORED,
    tax_amount      DECIMAL(18,4) GENERATED ALWAYS AS (
                        quantity * unit_price * (1 - discount_rate) * tax_rate
                    ) STORED,
    line_total      DECIMAL(18,4) GENERATED ALWAYS AS (
                        quantity * unit_price * (1 - discount_rate) * (1 + tax_rate)
                    ) STORED,

    -- 状态
    status          VARCHAR(30) DEFAULT 'pending',        -- pending/partial/fulfilled

    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT chk_item_qty CHECK (quantity > 0),
    CONSTRAINT chk_received_qty CHECK (received_qty >= 0 AND received_qty <= quantity)
);

CREATE INDEX idx_poi_po ON purchase_order_items(po_id);
CREATE INDEX idx_poi_material ON purchase_order_items(material_id);

-- ============================================================
-- 8. 发票 (invoices)
-- ============================================================
CREATE TABLE invoices (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    invoice_no      VARCHAR(50) UNIQUE NOT NULL,         -- 发票号 INV-YYYY-XXXXX
    supplier_id     UUID NOT NULL REFERENCES suppliers(id),
    po_id           UUID REFERENCES purchase_orders(id),

    -- 发票信息
    invoice_type    VARCHAR(30),                          -- 增值税专用发票/普通发票
    invoice_date    DATE NOT NULL,
    billing_period  VARCHAR(20),                          -- 账单周期

    -- 金额
    currency        currency DEFAULT 'CNY',
    subtotal        DECIMAL(18,2) DEFAULT 0,
    tax_amount      DECIMAL(18,2) DEFAULT 0,
    total_amount    DECIMAL(18,2) DEFAULT 0,
    paid_amount     DECIMAL(18,2) DEFAULT 0,              -- 已付款金额

    -- 税票信息
    tax_authority   VARCHAR(200),                         -- 税务机关
    tax_rate        DECIMAL(5,4) DEFAULT 0.13,
    tax_number      VARCHAR(50),                          -- 发票号码

    -- 状态
    status          invoice_status DEFAULT 'issued',

    -- 核对信息
    verified_by     VARCHAR(100),
    verified_at     TIMESTAMPTZ,
    verified_notes  TEXT,

    -- 元数据
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    created_by      VARCHAR(100),
    is_deleted      BOOLEAN DEFAULT FALSE,

    CONSTRAINT chk_invoice_amounts CHECK (
        subtotal >= 0 AND tax_amount >= 0 AND total_amount >= 0 AND paid_amount >= 0
    )
);

CREATE INDEX idx_invoices_supplier ON invoices(supplier_id);
CREATE INDEX idx_invoices_po ON invoices(po_id);
CREATE INDEX idx_invoices_no ON invoices(invoice_no);
CREATE INDEX idx_invoices_status ON invoices(status);
CREATE INDEX idx_invoices_date ON invoices(invoice_date);

-- ============================================================
-- 9. 发票行项 (invoice_items)
-- ============================================================
CREATE TABLE invoice_items (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    invoice_id      UUID NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
    po_item_id      UUID REFERENCES purchase_order_items(id), -- 关联PO行项

    line_no         INTEGER NOT NULL,
    description     VARCHAR(500),
    material_code   VARCHAR(30),
    material_name   VARCHAR(300),

    quantity        DECIMAL(15,4) NOT NULL,
    unit_price      DECIMAL(15,4) NOT NULL,
    discount_rate   DECIMAL(5,4) DEFAULT 0,
    tax_rate        DECIMAL(5,4) DEFAULT 0.13,

    net_amount      DECIMAL(18,4) GENERATED ALWAYS AS (
                        quantity * unit_price * (1 - discount_rate)
                    ) STORED,
    tax_amount      DECIMAL(18,4) GENERATED ALWAYS AS (
                        quantity * unit_price * (1 - discount_rate) * tax_rate
                    ) STORED,
    line_total      DECIMAL(18,4) GENERATED ALWAYS AS (
                        quantity * unit_price * (1 - discount_rate) * (1 + tax_rate)
                    ) STORED,

    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_invoice_items_invoice ON invoice_items(invoice_id);

-- ============================================================
-- 10. 付款记录 (payments)
-- ============================================================
CREATE TABLE payments (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    payment_no      VARCHAR(50) UNIQUE NOT NULL,         -- 付款单号 PAY-YYYY-XXXXX
    supplier_id     UUID NOT NULL REFERENCES suppliers(id),
    invoice_id      UUID REFERENCES invoices(id),

    -- 金额
    currency        currency DEFAULT 'CNY',
    amount          DECIMAL(18,2) NOT NULL,
    exchange_rate   DECIMAL(12,6) DEFAULT 1,

    -- 付款信息
    payment_date    DATE NOT NULL,
    due_date        DATE,
    method          payment_method DEFAULT 'bank_transfer',

    -- 状态
    status          payment_status DEFAULT 'pending',

    -- 银行信息
    bank_name       VARCHAR(200),
    bank_account    VARCHAR(50),
    transaction_ref VARCHAR(100),                         -- 银行交易流水号

    -- 审批
    approved_by     VARCHAR(100),
    approved_at     TIMESTAMPTZ,

    -- 元数据
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    created_by      VARCHAR(100),
    notes           TEXT,

    CONSTRAINT chk_payment_amount CHECK (amount > 0)
);

CREATE INDEX idx_payments_supplier ON payments(supplier_id);
CREATE INDEX idx_payments_invoice ON payments(invoice_id);
CREATE INDEX idx_payments_status ON payments(status);
CREATE INDEX idx_payments_date ON payments(payment_date);

-- ============================================================
-- 11. 供应商评估 (supplier_evaluations)
-- ============================================================
CREATE TABLE supplier_evaluations (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    supplier_id     UUID NOT NULL REFERENCES suppliers(id),

    -- 评估周期
    evaluation_year INTEGER NOT NULL,
    evaluation_quarter INTEGER,                          -- 季度评估（1-4）
    period_type     evaluation_period DEFAULT 'quarterly',

    -- 评分维度（满分100）
    quality_score   DECIMAL(5,2),                         -- 质量（30%权重）
    delivery_score  DECIMAL(5,2),                         -- 交货（25%权重）
    price_score     DECIMAL(5,2),                         -- 价格（20%权重）
    service_score   DECIMAL(5,2),                         -- 服务（15%权重）
    tech_score      DECIMAL(5,2),                         -- 技术（10%权重）

    -- 综合评分
    overall_score   DECIMAL(5,2),                         -- 加权总分
    grade           supplier_level,                        -- 评定等级 A/B/C/D

    -- 评估结果
    strengths       TEXT,
    weaknesses      TEXT,
    improvement_plan TEXT,
    is_final        BOOLEAN DEFAULT FALSE,                -- 是否正式评定

    -- 评估人
    evaluated_by    VARCHAR(100),
    evaluated_at    TIMESTAMPTZ,

    created_at      TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT chk_year CHECK (evaluation_year >= 2020 AND evaluation_year <= 2100),
    CONSTRAINT chk_quarter CHECK (evaluation_quarter BETWEEN 1 AND 4 OR evaluation_quarter IS NULL),
    CONSTRAINT chk_quality CHECK (quality_score BETWEEN 0 AND 100),
    CONSTRAINT chk_overall CHECK (overall_score BETWEEN 0 AND 100)
);

CREATE UNIQUE INDEX idx_eval_unique ON supplier_evaluations(supplier_id, evaluation_year, evaluation_quarter, is_final)
    WHERE is_final = TRUE;
CREATE INDEX idx_evaluations_supplier ON supplier_evaluations(supplier_id);
CREATE INDEX idx_evaluations_year ON supplier_evaluations(evaluation_year, evaluation_quarter);

-- ============================================================
-- 12. 审计日志表（自动追踪）
-- ============================================================
CREATE TABLE srm_audit_log (
    id              BIGSERIAL PRIMARY KEY,
    table_name      VARCHAR(50) NOT NULL,
    record_id       UUID NOT NULL,
    operation       VARCHAR(10) NOT NULL,                 -- INSERT/UPDATE/DELETE
    old_data        JSONB,
    new_data        JSONB,
    changed_by      VARCHAR(100),
    changed_at      TIMESTAMPTZ DEFAULT NOW(),
    client_ip       VARCHAR(45)
);

CREATE INDEX idx_audit_table ON srm_audit_log(table_name, record_id);
CREATE INDEX idx_audit_time ON srm_audit_log(changed_at);

-- ============================================================
-- 触发器：自动更新 updated_at
-- ============================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_suppliers_updated_at
    BEFORE UPDATE ON suppliers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER tr_materials_updated_at
    BEFORE UPDATE ON materials
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER tr_contracts_updated_at
    BEFORE UPDATE ON contracts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER tr_purchase_orders_updated_at
    BEFORE UPDATE ON purchase_orders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER tr_purchase_order_items_updated_at
    BEFORE UPDATE ON purchase_order_items
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER tr_invoices_updated_at
    BEFORE UPDATE ON invoices
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER tr_payments_updated_at
    BEFORE UPDATE ON payments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- 业务规则约束
-- ============================================================

-- 规则1：已取消的PO不能再添加行项（应用层控制）
-- 规则2：同一供应商在合同期内不能重复签订相同类别合同（数据库层面）
-- 规则3：付款金额不能超过发票未付金额（CHECK约束在应用层实现）

-- ============================================================
-- 物化视图：供应商应付账款汇总
-- ============================================================
CREATE MATERIALIZED VIEW supplier_payables AS
SELECT
    s.id AS supplier_id,
    s.code AS supplier_code,
    s.name AS supplier_name,
    s.payment_terms_days,
    COUNT(i.id) AS invoice_count,
    SUM(i.total_amount) AS total_invoiced,
    SUM(i.paid_amount) AS total_paid,
    SUM(i.total_amount - i.paid_amount) AS outstanding_amount,
    MAX(i.invoice_date + (s.payment_terms_days || ' days')::interval)::DATE AS latest_due_date
FROM suppliers s
LEFT JOIN invoices i ON i.supplier_id = s.id AND i.status != 'cancelled'
WHERE s.is_deleted = FALSE
GROUP BY s.id, s.code, s.name, s.payment_terms_days;

CREATE UNIQUE INDEX idx_payables_supplier ON supplier_payables(supplier_id);

-- ============================================================
-- 完成
-- ============================================================
