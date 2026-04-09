from datetime import datetime
from typing import Optional
from src.schemas.ontology import (
    OntologyClassResponse,
    DataPropertyResponse,
    ObjectPropertyResponse,
    AnnotationPropertyResponse,
    IndividualResponse,
    AxiomResponse,
    OntologyResponse,
    OntologyDetailResponse,
    DataRangeResponse,
)

# Try to import Jena client, fall back gracefully
try:
    from src.services.jena_client import (
        JenaClient,
        get_jena_client,
        JenaConnectionError,
    )

    JENA_AVAILABLE = True
except ImportError:
    JENA_AVAILABLE = False
    JenaClient = None
    get_jena_client = None
    JenaConnectionError = Exception

# Global Jena client instance
_jena_client = None


def _get_jena() -> Optional["JenaClient"]:
    """Get Jena client if available"""
    global _jena_client
    if not JENA_AVAILABLE:
        return None
    try:
        if _jena_client is None:
            _jena_client = get_jena_client()
        return _jena_client
    except JenaConnectionError:
        return None


# Ontology IRI mapping (for Jena)
ONTOLOGY_IRI_MAP = {
    "1": "http://onto-agent.com/ontology/customer360#",
    "2": "http://onto-agent.com/ontology/supplier-network#",
    "3": "http://onto-agent.com/ontology/order全景#",
}

MOCK_ONTOLOGIES = [
    {
        "id": "1",
        "name": "客户360",
        "description": "企业客户全景视图",
        "status": "published",
        "base_iri": "http://onto-agent.com/ontology/customer360#",
        "imports": [],
        "prefix_mappings": {
            "owl": "http://www.w3.org/2002/07/owl#",
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
            "xsd": "http://www.w3.org/2001/XMLSchema#",
        },
        "object_count": 8,
        "data_property_count": 24,
        "object_property_count": 12,
        "individual_count": 150,
        "axiom_count": 45,
        "updated_at": "2 小时前",
        "version": "v2.1",
        "datasource": "ERP-Production",
        "created_at": "2024-01-15T10:00:00Z",
        "updated_at": "2024-03-20T14:30:00Z",
    },
    {
        "id": "2",
        "name": "供应商网络",
        "description": "供应商关系与供应链视图",
        "status": "published",
        "base_iri": "http://onto-agent.com/ontology/supplier-network#",
        "imports": [],
        "prefix_mappings": {},
        "object_count": 6,
        "data_property_count": 18,
        "object_property_count": 8,
        "individual_count": 80,
        "axiom_count": 28,
        "updated_at": "昨天",
        "version": "v1.3",
        "datasource": "SCM-SupplyChain",
        "created_at": "2024-02-01T09:00:00Z",
        "updated_at": "2024-03-19T11:00:00Z",
    },
    {
        "id": "3",
        "name": "订单全景",
        "description": "订单、发票与物流追踪",
        "status": "draft",
        "base_iri": "http://onto-agent.com/ontology/order全景#",
        "imports": ["http://onto-agent.com/ontology/customer360#"],
        "prefix_mappings": {},
        "object_count": 5,
        "data_property_count": 15,
        "object_property_count": 7,
        "individual_count": 0,
        "axiom_count": 12,
        "updated_at": "3 天前",
        "version": "v1.2-draft",
        "datasource": "ERP-Production",
        "created_at": "2024-02-20T08:00:00Z",
        "updated_at": "2024-03-17T16:00:00Z",
    },
]

ONTOLOGY_DATA: dict[str, dict] = {
    "1": {
        "classes": [
            {
                "id": "Product",
                "ontology_id": "1",
                "name": "Product",
                "display_name": "产品",
                "description": "商品或服务实体",
                "labels": {"zh": "产品", "en": "Product"},
                "comments": {
                    "zh": "企业销售的商品或提供的服务",
                    "en": "Goods or services sold by the company",
                },
                "equivalent_to": [],
                "disjoint_with": [],
                "super_classes": [],
            },
            {
                "id": "Order",
                "ontology_id": "1",
                "name": "Order",
                "display_name": "订单",
                "description": "客户下达的购买订单",
                "labels": {"zh": "订单", "en": "Order"},
                "comments": {
                    "zh": "客户提交的购买请求",
                    "en": "Purchase request submitted by customer",
                },
                "equivalent_to": [],
                "disjoint_with": [],
                "super_classes": [],
            },
            {
                "id": "Customer",
                "ontology_id": "1",
                "name": "Customer",
                "display_name": "客户",
                "description": "购买商品或服务的个人或企业",
                "labels": {"zh": "客户", "en": "Customer"},
                "comments": {
                    "zh": "企业产品和服务的购买者",
                    "en": "Purchasers of company products and services",
                },
                "equivalent_to": [],
                "disjoint_with": ["Supplier"],
                "super_classes": [],
            },
            {
                "id": "Supplier",
                "ontology_id": "1",
                "name": "Supplier",
                "display_name": "供应商",
                "description": "提供原材料或商品的供应商",
                "labels": {"zh": "供应商", "en": "Supplier"},
                "comments": {
                    "zh": "向企业提供商品或服务的组织",
                    "en": "Organization providing goods or services to the enterprise",
                },
                "equivalent_to": [],
                "disjoint_with": ["Customer"],
                "super_classes": [],
            },
            {
                "id": "Shipment",
                "ontology_id": "1",
                "name": "Shipment",
                "display_name": "货运",
                "description": "订单的发货记录",
                "labels": {"zh": "货运", "en": "Shipment"},
                "comments": {
                    "zh": "订单的配送信息",
                    "en": "Delivery information for orders",
                },
                "equivalent_to": [],
                "disjoint_with": [],
                "super_classes": [],
            },
            {
                "id": "Invoice",
                "ontology_id": "1",
                "name": "Invoice",
                "display_name": "发票",
                "description": "商业发票记录",
                "labels": {"zh": "发票", "en": "Invoice"},
                "comments": {},
                "equivalent_to": [],
                "disjoint_with": [],
                "super_classes": [],
            },
            {
                "id": "Address",
                "ontology_id": "1",
                "name": "Address",
                "display_name": "地址",
                "description": "物理地址信息",
                "labels": {"zh": "地址", "en": "Address"},
                "comments": {},
                "equivalent_to": [],
                "disjoint_with": [],
                "super_classes": [],
            },
            {
                "id": "Payment",
                "ontology_id": "1",
                "name": "Payment",
                "display_name": "支付",
                "description": "订单支付记录",
                "labels": {"zh": "支付", "en": "Payment"},
                "comments": {},
                "equivalent_to": [],
                "disjoint_with": [],
                "super_classes": [],
            },
        ],
        "data_properties": [
            {
                "id": "p1",
                "ontology_id": "1",
                "name": "productName",
                "display_name": "产品名称",
                "domain_ids": ["Product"],
                "range_type": "string",
                "characteristics": [],
                "super_property_id": None,
                "labels": {},
                "comments": {},
            },
            {
                "id": "p2",
                "ontology_id": "1",
                "name": "price",
                "display_name": "价格",
                "domain_ids": ["Product"],
                "range_type": "decimal",
                "characteristics": ["functional"],
                "super_property_id": None,
                "labels": {},
                "comments": {},
            },
            {
                "id": "p3",
                "ontology_id": "1",
                "name": "stockLevel",
                "display_name": "库存数量",
                "domain_ids": ["Product"],
                "range_type": "integer",
                "characteristics": [],
                "super_property_id": None,
                "labels": {},
                "comments": {},
            },
            {
                "id": "p4",
                "ontology_id": "1",
                "name": "orderDate",
                "display_name": "订单日期",
                "domain_ids": ["Order"],
                "range_type": "dateTime",
                "characteristics": ["functional"],
                "super_property_id": None,
                "labels": {},
                "comments": {},
            },
            {
                "id": "p5",
                "ontology_id": "1",
                "name": "totalAmount",
                "display_name": "总金额",
                "domain_ids": ["Order"],
                "range_type": "decimal",
                "characteristics": ["functional"],
                "super_property_id": None,
                "labels": {},
                "comments": {},
            },
            {
                "id": "p6",
                "ontology_id": "1",
                "name": "orderStatus",
                "display_name": "订单状态",
                "domain_ids": ["Order"],
                "range_type": "string",
                "characteristics": [],
                "super_property_id": None,
                "labels": {},
                "comments": {},
            },
            {
                "id": "p7",
                "ontology_id": "1",
                "name": "customerName",
                "display_name": "客户名称",
                "domain_ids": ["Customer"],
                "range_type": "string",
                "characteristics": [],
                "super_property_id": None,
                "labels": {},
                "comments": {},
            },
            {
                "id": "p8",
                "ontology_id": "1",
                "name": "customerTier",
                "display_name": "客户等级",
                "domain_ids": ["Customer"],
                "range_type": "string",
                "characteristics": [],
                "super_property_id": None,
                "labels": {},
                "comments": {},
            },
            {
                "id": "p9",
                "ontology_id": "1",
                "name": "email",
                "display_name": "邮箱",
                "domain_ids": ["Customer"],
                "range_type": "string",
                "characteristics": ["functional"],
                "super_property_id": None,
                "labels": {},
                "comments": {},
            },
            {
                "id": "p10",
                "ontology_id": "1",
                "name": "phone",
                "display_name": "电话",
                "domain_ids": ["Customer"],
                "range_type": "string",
                "characteristics": [],
                "super_property_id": None,
                "labels": {},
                "comments": {},
            },
            {
                "id": "p11",
                "ontology_id": "1",
                "name": "supplierName",
                "display_name": "供应商名称",
                "domain_ids": ["Supplier"],
                "range_type": "string",
                "characteristics": [],
                "super_property_id": None,
                "labels": {},
                "comments": {},
            },
            {
                "id": "p12",
                "ontology_id": "1",
                "name": "shipmentDate",
                "display_name": "发货日期",
                "domain_ids": ["Shipment"],
                "range_type": "dateTime",
                "characteristics": ["functional"],
                "super_property_id": None,
                "labels": {},
                "comments": {},
            },
            {
                "id": "p13",
                "ontology_id": "1",
                "name": "trackingNumber",
                "display_name": "追踪号",
                "domain_ids": ["Shipment"],
                "range_type": "string",
                "characteristics": ["functional"],
                "super_property_id": None,
                "labels": {},
                "comments": {},
            },
            {
                "id": "p14",
                "ontology_id": "1",
                "name": "invoiceNumber",
                "display_name": "发票号",
                "domain_ids": ["Invoice"],
                "range_type": "string",
                "characteristics": ["functional"],
                "super_property_id": None,
                "labels": {},
                "comments": {},
            },
            {
                "id": "p15",
                "ontology_id": "1",
                "name": "invoiceAmount",
                "display_name": "发票金额",
                "domain_ids": ["Invoice"],
                "range_type": "decimal",
                "characteristics": ["functional"],
                "super_property_id": None,
                "labels": {},
                "comments": {},
            },
            {
                "id": "p16",
                "ontology_id": "1",
                "name": "street",
                "display_name": "街道",
                "domain_ids": ["Address"],
                "range_type": "string",
                "characteristics": [],
                "super_property_id": None,
                "labels": {},
                "comments": {},
            },
            {
                "id": "p17",
                "ontology_id": "1",
                "name": "city",
                "display_name": "城市",
                "domain_ids": ["Address"],
                "range_type": "string",
                "characteristics": [],
                "super_property_id": None,
                "labels": {},
                "comments": {},
            },
            {
                "id": "p18",
                "ontology_id": "1",
                "name": "country",
                "display_name": "国家",
                "domain_ids": ["Address"],
                "range_type": "string",
                "characteristics": [],
                "super_property_id": None,
                "labels": {},
                "comments": {},
            },
            {
                "id": "p19",
                "ontology_id": "1",
                "name": "postalCode",
                "display_name": "邮编",
                "domain_ids": ["Address"],
                "range_type": "string",
                "characteristics": ["functional"],
                "super_property_id": None,
                "labels": {},
                "comments": {},
            },
            {
                "id": "p20",
                "ontology_id": "1",
                "name": "paymentAmount",
                "display_name": "支付金额",
                "domain_ids": ["Payment"],
                "range_type": "decimal",
                "characteristics": ["functional"],
                "super_property_id": None,
                "labels": {},
                "comments": {},
            },
            {
                "id": "p21",
                "ontology_id": "1",
                "name": "paymentDate",
                "display_name": "支付日期",
                "domain_ids": ["Payment"],
                "range_type": "dateTime",
                "characteristics": ["functional"],
                "super_property_id": None,
                "labels": {},
                "comments": {},
            },
            {
                "id": "p22",
                "ontology_id": "1",
                "name": "paymentMethod",
                "display_name": "支付方式",
                "domain_ids": ["Payment"],
                "range_type": "string",
                "characteristics": [],
                "super_property_id": None,
                "labels": {},
                "comments": {},
            },
            {
                "id": "p23",
                "ontology_id": "1",
                "name": "weight",
                "display_name": "重量",
                "domain_ids": ["Product", "Shipment"],
                "range_type": "double",
                "characteristics": [],
                "super_property_id": None,
                "labels": {},
                "comments": {},
            },
            {
                "id": "p24",
                "ontology_id": "1",
                "name": "createdAt",
                "display_name": "创建时间",
                "domain_ids": ["Product", "Order", "Customer", "Supplier"],
                "range_type": "dateTime",
                "characteristics": [],
                "super_property_id": None,
                "labels": {},
                "comments": {},
            },
        ],
        "object_properties": [
            {
                "id": "op1",
                "ontology_id": "1",
                "name": "hasProduct",
                "display_name": "包含产品",
                "domain_ids": ["Order"],
                "range_ids": ["Product"],
                "characteristics": [],
                "super_property_id": None,
                "inverse_of_id": "op6",
                "property_chain": [],
                "labels": {},
                "comments": {},
            },
            {
                "id": "op2",
                "ontology_id": "1",
                "name": "placedBy",
                "display_name": "下单",
                "domain_ids": ["Order"],
                "range_ids": ["Customer"],
                "characteristics": [],
                "super_property_id": None,
                "inverse_of_id": "op5",
                "property_chain": [],
                "labels": {},
                "comments": {},
            },
            {
                "id": "op3",
                "ontology_id": "1",
                "name": "suppliedBy",
                "display_name": "供应方",
                "domain_ids": ["Product"],
                "range_ids": ["Supplier"],
                "characteristics": [],
                "super_property_id": None,
                "inverse_of_id": None,
                "property_chain": [],
                "labels": {},
                "comments": {},
            },
            {
                "id": "op4",
                "ontology_id": "1",
                "name": "ships",
                "display_name": "发货运",
                "domain_ids": ["Order"],
                "range_ids": ["Shipment"],
                "characteristics": [],
                "super_property_id": None,
                "inverse_of_id": None,
                "property_chain": [],
                "labels": {},
                "comments": {},
            },
            {
                "id": "op5",
                "ontology_id": "1",
                "name": "owns",
                "display_name": "拥有",
                "domain_ids": ["Customer"],
                "range_ids": ["Order"],
                "characteristics": [],
                "super_property_id": None,
                "inverse_of_id": "op2",
                "property_chain": [],
                "labels": {},
                "comments": {},
            },
            {
                "id": "op6",
                "ontology_id": "1",
                "name": "orderedAs",
                "display_name": "被订购为",
                "domain_ids": ["Product"],
                "range_ids": ["Order"],
                "characteristics": [],
                "super_property_id": None,
                "inverse_of_id": "op1",
                "property_chain": [],
                "labels": {},
                "comments": {},
            },
            {
                "id": "op7",
                "ontology_id": "1",
                "name": "hasInvoice",
                "display_name": "包含发票",
                "domain_ids": ["Order"],
                "range_ids": ["Invoice"],
                "characteristics": [],
                "super_property_id": None,
                "inverse_of_id": None,
                "property_chain": [],
                "labels": {},
                "comments": {},
            },
            {
                "id": "op8",
                "ontology_id": "1",
                "name": "billedTo",
                "display_name": "开票给",
                "domain_ids": ["Invoice"],
                "range_ids": ["Customer"],
                "characteristics": [],
                "super_property_id": None,
                "inverse_of_id": None,
                "property_chain": [],
                "labels": {},
                "comments": {},
            },
            {
                "id": "op9",
                "ontology_id": "1",
                "name": "livesAt",
                "display_name": "住在",
                "domain_ids": ["Customer"],
                "range_ids": ["Address"],
                "characteristics": ["functional"],
                "super_property_id": None,
                "inverse_of_id": None,
                "property_chain": [],
                "labels": {},
                "comments": {},
            },
            {
                "id": "op10",
                "ontology_id": "1",
                "name": "locatedAt",
                "display_name": "位于",
                "domain_ids": ["Supplier"],
                "range_ids": ["Address"],
                "characteristics": ["functional"],
                "super_property_id": None,
                "inverse_of_id": None,
                "property_chain": [],
                "labels": {},
                "comments": {},
            },
            {
                "id": "op11",
                "ontology_id": "1",
                "name": "hasPayment",
                "display_name": "包含支付",
                "domain_ids": ["Order"],
                "range_ids": ["Payment"],
                "characteristics": [],
                "super_property_id": None,
                "inverse_of_id": None,
                "property_chain": [],
                "labels": {},
                "comments": {},
            },
            {
                "id": "op12",
                "ontology_id": "1",
                "name": "partOf",
                "display_name": "组成部分",
                "domain_ids": ["Product"],
                "range_ids": ["Product"],
                "characteristics": ["transitive", "reflexive"],
                "super_property_id": None,
                "inverse_of_id": None,
                "property_chain": [],
                "labels": {},
                "comments": {},
            },
        ],
        "annotation_properties": [
            {
                "id": "ap1",
                "ontology_id": "1",
                "name": "creator",
                "display_name": "创建者",
                "description": "资源创建者",
                "domain_ids": [],
                "range_ids": [],
                "sub_property_of_id": None,
            },
            {
                "id": "ap2",
                "ontology_id": "1",
                "name": "createdDate",
                "display_name": "创建日期",
                "description": "资源创建日期",
                "domain_ids": [],
                "range_ids": [],
                "sub_property_of_id": None,
            },
            {
                "id": "ap3",
                "ontology_id": "1",
                "name": "modifiedDate",
                "display_name": "修改日期",
                "description": "资源最后修改日期",
                "domain_ids": [],
                "range_ids": [],
                "sub_property_of_id": None,
            },
            {
                "id": "ap4",
                "ontology_id": "1",
                "name": "seeAlso",
                "display_name": "参见",
                "description": "相关资源链接",
                "domain_ids": [],
                "range_ids": [],
                "sub_property_of_id": None,
            },
        ],
        "individuals": [
            {
                "id": "ind1",
                "ontology_id": "1",
                "name": "customer-001",
                "display_name": "张三",
                "description": "VIP客户",
                "types": ["Customer"],
                "labels": {},
                "comments": {},
                "data_property_assertions": [
                    {"property_id": "p7", "value": "张三"},
                    {"property_id": "p8", "value": "VIP"},
                    {"property_id": "p9", "value": "zhangsan@example.com"},
                ],
                "object_property_assertions": [],
            },
            {
                "id": "ind2",
                "ontology_id": "1",
                "name": "customer-002",
                "display_name": "李四",
                "description": "普通客户",
                "types": ["Customer"],
                "labels": {},
                "comments": {},
                "data_property_assertions": [
                    {"property_id": "p7", "value": "李四"},
                    {"property_id": "p8", "value": "普通"},
                    {"property_id": "p9", "value": "lisi@example.com"},
                ],
                "object_property_assertions": [],
            },
            {
                "id": "ind3",
                "ontology_id": "1",
                "name": "product-001",
                "display_name": "笔记本电脑",
                "description": "高性能笔记本电脑",
                "types": ["Product"],
                "labels": {},
                "comments": {},
                "data_property_assertions": [
                    {"property_id": "p1", "value": "笔记本电脑"},
                    {"property_id": "p2", "value": 5999.00},
                ],
                "object_property_assertions": [],
            },
            {
                "id": "ind4",
                "ontology_id": "1",
                "name": "supplier-001",
                "display_name": "联想集团",
                "description": "主要供应商",
                "types": ["Supplier"],
                "labels": {},
                "comments": {},
                "data_property_assertions": [
                    {"property_id": "p11", "value": "联想集团"}
                ],
                "object_property_assertions": [],
            },
            {
                "id": "ind5",
                "ontology_id": "1",
                "name": "order-001",
                "display_name": "订单2024001",
                "description": "张三的订单",
                "types": ["Order"],
                "labels": {},
                "comments": {},
                "data_property_assertions": [{"property_id": "p5", "value": 5999.00}],
                "object_property_assertions": [],
            },
        ],
        "axioms": [
            {
                "id": "ax1",
                "ontology_id": "1",
                "type": "EquivalentClasses",
                "subject": None,
                "assertions": {"classIds": ["Customer"]},
                "annotations": [],
            },
            {
                "id": "ax2",
                "ontology_id": "1",
                "type": "DisjointClasses",
                "subject": None,
                "assertions": {"classIds": ["Customer", "Supplier"]},
                "annotations": [],
            },
            {
                "id": "ax3",
                "ontology_id": "1",
                "type": "FunctionalProperty",
                "subject": "price",
                "assertions": {},
                "annotations": [],
            },
            {
                "id": "ax4",
                "ontology_id": "1",
                "type": "FunctionalProperty",
                "subject": "email",
                "assertions": {},
                "annotations": [],
            },
            {
                "id": "ax5",
                "ontology_id": "1",
                "type": "TransitiveProperty",
                "subject": "partOf",
                "assertions": {},
                "annotations": [],
            },
        ],
        "data_ranges": [
            {
                "id": "dr1",
                "ontology_id": "1",
                "type": "enumeration",
                "values": [
                    "pending",
                    "processing",
                    "shipped",
                    "delivered",
                    "cancelled",
                ],
                "base_type": None,
                "facets": None,
            },
            {
                "id": "dr2",
                "ontology_id": "1",
                "type": "restriction",
                "values": None,
                "base_type": "integer",
                "facets": [{"type": "minInclusive", "value": 0}],
            },
        ],
    },
    "2": {
        "classes": [
            {
                "id": "Supplier",
                "ontology_id": "2",
                "name": "Supplier",
                "display_name": "供应商",
                "description": "供应商实体",
                "labels": {},
                "comments": {},
                "equivalent_to": [],
                "disjoint_with": [],
                "super_classes": [],
            },
            {
                "id": "Warehouse",
                "ontology_id": "2",
                "name": "Warehouse",
                "display_name": "仓库",
                "description": "仓库实体",
                "labels": {},
                "comments": {},
                "equivalent_to": [],
                "disjoint_with": [],
                "super_classes": [],
            },
            {
                "id": "Product",
                "ontology_id": "2",
                "name": "Product",
                "display_name": "产品",
                "description": "产品实体",
                "labels": {},
                "comments": {},
                "equivalent_to": [],
                "disjoint_with": [],
                "super_classes": [],
            },
            {
                "id": "RawMaterial",
                "ontology_id": "2",
                "name": "RawMaterial",
                "display_name": "原材料",
                "description": "原材料",
                "labels": {},
                "comments": {},
                "equivalent_to": [],
                "disjoint_with": [],
                "super_classes": ["Product"],
            },
            {
                "id": "Address",
                "ontology_id": "2",
                "name": "Address",
                "display_name": "地址",
                "description": "物理地址",
                "labels": {},
                "comments": {},
                "equivalent_to": [],
                "disjoint_with": [],
                "super_classes": [],
            },
        ],
        "data_properties": [
            {
                "id": "dp1",
                "ontology_id": "2",
                "name": "supplierName",
                "display_name": "供应商名称",
                "domain_ids": ["Supplier"],
                "range_type": "string",
                "characteristics": ["functional"],
                "super_property_id": None,
                "labels": {},
                "comments": {},
            },
            {
                "id": "dp2",
                "ontology_id": "2",
                "name": "warehouseLocation",
                "display_name": "仓库位置",
                "domain_ids": ["Warehouse"],
                "range_type": "string",
                "characteristics": ["functional"],
                "super_property_id": None,
                "labels": {},
                "comments": {},
            },
            {
                "id": "dp3",
                "ontology_id": "2",
                "name": "stockLevel",
                "display_name": "库存数量",
                "domain_ids": ["Product"],
                "range_type": "integer",
                "characteristics": [],
                "super_property_id": None,
                "labels": {},
                "comments": {},
            },
            {
                "id": "dp4",
                "ontology_id": "2",
                "name": "street",
                "display_name": "街道",
                "domain_ids": ["Address"],
                "range_type": "string",
                "characteristics": [],
                "super_property_id": None,
                "labels": {},
                "comments": {},
            },
            {
                "id": "dp5",
                "ontology_id": "2",
                "name": "city",
                "display_name": "城市",
                "domain_ids": ["Address"],
                "range_type": "string",
                "characteristics": ["functional"],
                "super_property_id": None,
                "labels": {},
                "comments": {},
            },
        ],
        "object_properties": [
            {
                "id": "op1",
                "ontology_id": "2",
                "name": "supplies",
                "display_name": "供应",
                "domain_ids": ["Supplier"],
                "range_ids": ["Product"],
                "characteristics": [],
                "super_property_id": None,
                "inverse_of_id": None,
                "property_chain": [],
                "labels": {},
                "comments": {},
            },
            {
                "id": "op2",
                "ontology_id": "2",
                "name": "stores",
                "display_name": "存储",
                "domain_ids": ["Warehouse"],
                "range_ids": ["Product"],
                "characteristics": [],
                "super_property_id": None,
                "inverse_of_id": None,
                "property_chain": [],
                "labels": {},
                "comments": {},
            },
            {
                "id": "op3",
                "ontology_id": "2",
                "name": "locatedIn",
                "display_name": "位于",
                "domain_ids": ["Supplier", "Warehouse"],
                "range_ids": ["Address"],
                "characteristics": ["transitive"],
                "super_property_id": None,
                "inverse_of_id": None,
                "property_chain": [],
                "labels": {},
                "comments": {},
            },
        ],
        "annotation_properties": [],
        "individuals": [],
        "axioms": [],
        "data_ranges": [],
    },
    "3": {
        "classes": [
            {
                "id": "Order",
                "ontology_id": "3",
                "name": "Order",
                "display_name": "订单",
                "description": "订单实体",
                "labels": {},
                "comments": {},
                "equivalent_to": [],
                "disjoint_with": [],
                "super_classes": [],
            },
            {
                "id": "Invoice",
                "ontology_id": "3",
                "name": "Invoice",
                "display_name": "发票",
                "description": "发票实体",
                "labels": {},
                "comments": {},
                "equivalent_to": [],
                "disjoint_with": [],
                "super_classes": [],
            },
            {
                "id": "Shipment",
                "ontology_id": "3",
                "name": "Shipment",
                "display_name": "货运",
                "description": "货运实体",
                "labels": {},
                "comments": {},
                "equivalent_to": [],
                "disjoint_with": [],
                "super_classes": [],
            },
        ],
        "data_properties": [
            {
                "id": "p1",
                "ontology_id": "3",
                "name": "orderDate",
                "display_name": "订单日期",
                "domain_ids": ["Order"],
                "range_type": "dateTime",
                "characteristics": ["functional"],
                "super_property_id": None,
                "labels": {},
                "comments": {},
            },
            {
                "id": "p2",
                "ontology_id": "3",
                "name": "invoiceAmount",
                "display_name": "发票金额",
                "domain_ids": ["Invoice"],
                "range_type": "decimal",
                "characteristics": ["functional"],
                "super_property_id": None,
                "labels": {},
                "comments": {},
            },
            {
                "id": "p3",
                "ontology_id": "3",
                "name": "trackingNumber",
                "display_name": "追踪号",
                "domain_ids": ["Shipment"],
                "range_type": "string",
                "characteristics": ["functional"],
                "super_property_id": None,
                "labels": {},
                "comments": {},
            },
        ],
        "object_properties": [
            {
                "id": "op1",
                "ontology_id": "3",
                "name": "hasInvoice",
                "display_name": "包含发票",
                "domain_ids": ["Order"],
                "range_ids": ["Invoice"],
                "characteristics": [],
                "super_property_id": None,
                "inverse_of_id": None,
                "property_chain": [],
                "labels": {},
                "comments": {},
            },
            {
                "id": "op2",
                "ontology_id": "3",
                "name": "hasShipment",
                "display_name": "包含货运",
                "domain_ids": ["Order"],
                "range_ids": ["Shipment"],
                "characteristics": [],
                "super_property_id": None,
                "inverse_of_id": None,
                "property_chain": [],
                "labels": {},
                "comments": {},
            },
        ],
        "annotation_properties": [],
        "individuals": [],
        "axioms": [],
        "data_ranges": [],
    },
}


async def list_ontologies() -> list[OntologyResponse]:
    jena = _get_jena()
    result = []

    for o in MOCK_ONTOLOGIES:
        ontology_id = o["id"]

        if jena and ontology_id in ONTOLOGY_IRI_MAP:
            # Use Jena to get real counts
            ontology_iri = ONTOLOGY_IRI_MAP[ontology_id]
            try:
                classes = jena.list_classes(ontology_iri)
                data_props = jena.list_datatype_properties(ontology_iri)
                obj_props = jena.list_object_properties(ontology_iri)
                count_data = {
                    **o,
                    "object_count": len(classes),
                    "data_property_count": len(data_props),
                    "object_property_count": len(obj_props),
                }
            except Exception:
                # Fall back to mock data
                data = ONTOLOGY_DATA.get(
                    ontology_id,
                    {"classes": [], "data_properties": [], "object_properties": []},
                )
                count_data = {
                    **o,
                    "object_count": len(data.get("classes", [])),
                    "data_property_count": len(data.get("data_properties", [])),
                    "object_property_count": len(data.get("object_properties", [])),
                }
        else:
            # Use mock data
            data = ONTOLOGY_DATA.get(
                ontology_id,
                {"classes": [], "data_properties": [], "object_properties": []},
            )
            count_data = {
                **o,
                "object_count": len(data.get("classes", [])),
                "data_property_count": len(data.get("data_properties", [])),
                "object_property_count": len(data.get("object_properties", [])),
            }

        result.append(OntologyResponse(**count_data))

    return result


async def get_ontology(ontology_id: str) -> Optional[OntologyResponse]:
    jena = _get_jena()
    for o in MOCK_ONTOLOGIES:
        if o["id"] == ontology_id:
            if jena and ontology_id in ONTOLOGY_IRI_MAP:
                ontology_iri = ONTOLOGY_IRI_MAP[ontology_id]
                try:
                    classes = jena.list_classes(ontology_iri)
                    data_props = jena.list_datatype_properties(ontology_iri)
                    obj_props = jena.list_object_properties(ontology_iri)
                    return OntologyResponse(
                        **{
                            k: v
                            for k, v in o.items()
                            if k != "object_count"
                            and k != "data_property_count"
                            and k != "object_property_count"
                        },
                        object_count=len(classes),
                        data_property_count=len(data_props),
                        object_property_count=len(obj_props),
                    )
                except Exception:
                    pass
            return OntologyResponse(**o)
    return None


async def get_ontology_detail(ontology_id: str) -> Optional[OntologyDetailResponse]:
    jena = _get_jena()
    for o in MOCK_ONTOLOGIES:
        if o["id"] == ontology_id:
            base = OntologyResponse(**o)

            if jena and ontology_id in ONTOLOGY_IRI_MAP:
                ontology_iri = ONTOLOGY_IRI_MAP[ontology_id]
                try:
                    classes = jena.list_classes(ontology_iri)
                    data_props = jena.list_datatype_properties(ontology_iri)
                    obj_props = jena.list_object_properties(ontology_iri)
                    return OntologyDetailResponse(
                        **base.model_dump(),
                        classes=classes,
                        data_properties=data_props,
                        object_properties=obj_props,
                        annotation_properties=[],
                        individuals=[],
                        axioms=[],
                        data_ranges=[],
                    )
                except Exception:
                    pass

            data = ONTOLOGY_DATA.get(
                ontology_id,
                {
                    "classes": [],
                    "data_properties": [],
                    "object_properties": [],
                    "annotation_properties": [],
                    "individuals": [],
                    "axioms": [],
                    "data_ranges": [],
                },
            )
            return OntologyDetailResponse(
                **base.model_dump(),
                classes=[OntologyClassResponse(**c) for c in data["classes"]],
                data_properties=[
                    DataPropertyResponse(**p) for p in data["data_properties"]
                ],
                object_properties=[
                    ObjectPropertyResponse(**p) for p in data["object_properties"]
                ],
                annotation_properties=[
                    AnnotationPropertyResponse(**p)
                    for p in data.get("annotation_properties", [])
                ],
                individuals=[
                    IndividualResponse(**i) for i in data.get("individuals", [])
                ],
                axioms=[AxiomResponse(**a) for a in data.get("axioms", [])],
                data_ranges=[
                    DataRangeResponse(**d) for d in data.get("data_ranges", [])
                ],
            )
    return None


async def get_ontology_classes(ontology_id: str) -> list[OntologyClassResponse]:
    jena = _get_jena()
    if jena and ontology_id in ONTOLOGY_IRI_MAP:
        ontology_iri = ONTOLOGY_IRI_MAP[ontology_id]
        try:
            return jena.list_classes(ontology_iri)
        except Exception:
            pass
    data = ONTOLOGY_DATA.get(ontology_id, {"classes": []})
    return [OntologyClassResponse(**c) for c in data["classes"]]


async def create_ontology_class(
    ontology_id: str,
    name: str,
    display_name: str = None,
    description: str = None,
    labels: dict = None,
    comments: dict = None,
    equivalent_to: list = None,
    disjoint_with: list = None,
    super_classes: list = None,
) -> OntologyClassResponse:
    jena = _get_jena()
    if jena and ontology_id in ONTOLOGY_IRI_MAP:
        ontology_iri = ONTOLOGY_IRI_MAP[ontology_id]
        super_class_iris = [
            f"{ONTOLOGY_IRI_MAP.get(ontology_id, '')}{sc}"
            for sc in (super_classes or [])
        ]
        try:
            return jena.create_class(
                ontology_iri=ontology_iri,
                name=name,
                display_name=display_name,
                description=description,
                super_classes=super_class_iris if super_class_iris else None,
            )
        except Exception:
            pass

    new_class = {
        "id": name,
        "ontology_id": ontology_id,
        "name": name,
        "display_name": display_name or name,
        "description": description,
        "labels": labels or {},
        "comments": comments or {},
        "equivalent_to": equivalent_to or [],
        "disjoint_with": disjoint_with or [],
        "super_classes": super_classes or [],
    }
    if ontology_id not in ONTOLOGY_DATA:
        _init_ontology_data(ontology_id)
    ONTOLOGY_DATA[ontology_id]["classes"].append(new_class)
    return OntologyClassResponse(**new_class)


def _init_ontology_data(ontology_id: str):
    ONTOLOGY_DATA[ontology_id] = {
        "classes": [],
        "data_properties": [],
        "object_properties": [],
        "annotation_properties": [],
        "individuals": [],
        "axioms": [],
        "data_ranges": [],
    }


async def get_data_properties(ontology_id: str) -> list[DataPropertyResponse]:
    jena = _get_jena()
    if jena and ontology_id in ONTOLOGY_IRI_MAP:
        ontology_iri = ONTOLOGY_IRI_MAP[ontology_id]
        try:
            return jena.list_datatype_properties(ontology_iri)
        except Exception:
            pass
    data = ONTOLOGY_DATA.get(ontology_id, {"data_properties": []})
    return [DataPropertyResponse(**p) for p in data["data_properties"]]


async def create_data_property(
    ontology_id: str,
    name: str,
    domain_ids: list,
    range_type: str = "string",
    display_name: str = None,
    description: str = None,
    characteristics: list = None,
    super_property_id: str = None,
) -> DataPropertyResponse:
    jena = _get_jena()
    if jena and ontology_id in ONTOLOGY_IRI_MAP:
        ontology_iri = ONTOLOGY_IRI_MAP[ontology_id]
        if domain_ids:
            domain_iri = f"{ontology_iri}{domain_ids[0]}"
            try:
                return jena.create_datatype_property(
                    ontology_iri=ontology_iri,
                    name=name,
                    domain_iri=domain_iri,
                    range_type=range_type,
                    display_name=display_name,
                    characteristics=characteristics,
                )
            except Exception:
                pass

    new_prop = {
        "id": f"dp-{len(ONTOLOGY_DATA.get(ontology_id, {}).get('data_properties', [])) + 1}",
        "ontology_id": ontology_id,
        "name": name,
        "display_name": display_name or name,
        "description": description,
        "labels": {},
        "comments": {},
        "domain_ids": domain_ids,
        "range_type": range_type,
        "characteristics": characteristics or [],
        "super_property_id": super_property_id,
    }
    if ontology_id not in ONTOLOGY_DATA:
        _init_ontology_data(ontology_id)
    ONTOLOGY_DATA[ontology_id]["data_properties"].append(new_prop)
    return DataPropertyResponse(**new_prop)


async def get_object_properties(ontology_id: str) -> list[ObjectPropertyResponse]:
    jena = _get_jena()
    if jena and ontology_id in ONTOLOGY_IRI_MAP:
        ontology_iri = ONTOLOGY_IRI_MAP[ontology_id]
        try:
            return jena.list_object_properties(ontology_iri)
        except Exception:
            pass
    data = ONTOLOGY_DATA.get(ontology_id, {"object_properties": []})
    return [ObjectPropertyResponse(**p) for p in data["object_properties"]]


async def create_object_property(
    ontology_id: str,
    name: str,
    domain_ids: list,
    range_ids: list,
    display_name: str = None,
    description: str = None,
    characteristics: list = None,
    super_property_id: str = None,
    inverse_of_id: str = None,
    property_chain: list = None,
) -> ObjectPropertyResponse:
    jena = _get_jena()
    if jena and ontology_id in ONTOLOGY_IRI_MAP:
        ontology_iri = ONTOLOGY_IRI_MAP[ontology_id]
        if domain_ids and range_ids:
            domain_iri = f"{ontology_iri}{domain_ids[0]}"
            range_iri = f"{ontology_iri}{range_ids[0]}"
            try:
                return jena.create_object_property(
                    ontology_iri=ontology_iri,
                    name=name,
                    domain_iri=domain_iri,
                    range_iri=range_iri,
                    display_name=display_name,
                    characteristics=characteristics,
                    inverse_of=f"{ontology_iri}{inverse_of_id}"
                    if inverse_of_id
                    else None,
                )
            except Exception:
                pass

    new_prop = {
        "id": f"op-{len(ONTOLOGY_DATA.get(ontology_id, {}).get('object_properties', [])) + 1}",
        "ontology_id": ontology_id,
        "name": name,
        "display_name": display_name or name,
        "description": description,
        "labels": {},
        "comments": {},
        "domain_ids": domain_ids,
        "range_ids": range_ids,
        "characteristics": characteristics or [],
        "super_property_id": super_property_id,
        "inverse_of_id": inverse_of_id,
        "property_chain": property_chain or [],
    }
    if ontology_id not in ONTOLOGY_DATA:
        _init_ontology_data(ontology_id)
    ONTOLOGY_DATA[ontology_id]["object_properties"].append(new_prop)
    return ObjectPropertyResponse(**new_prop)


async def get_annotation_properties(
    ontology_id: str,
) -> list[AnnotationPropertyResponse]:
    data = ONTOLOGY_DATA.get(ontology_id, {"annotation_properties": []})
    return [AnnotationPropertyResponse(**p) for p in data["annotation_properties"]]


async def create_annotation_property(
    ontology_id: str,
    name: str,
    display_name: str = None,
    description: str = None,
    domain_ids: list = None,
    range_ids: list = None,
    sub_property_of_id: str = None,
) -> AnnotationPropertyResponse:
    new_prop = {
        "id": f"ap-{len(ONTOLOGY_DATA.get(ontology_id, {}).get('annotation_properties', [])) + 1}",
        "ontology_id": ontology_id,
        "name": name,
        "display_name": display_name or name,
        "description": description,
        "domain_ids": domain_ids or [],
        "range_ids": range_ids or [],
        "sub_property_of_id": sub_property_of_id,
    }
    if ontology_id not in ONTOLOGY_DATA:
        _init_ontology_data(ontology_id)
    ONTOLOGY_DATA[ontology_id]["annotation_properties"].append(new_prop)
    return AnnotationPropertyResponse(**new_prop)


async def get_individuals(ontology_id: str) -> list[IndividualResponse]:
    data = ONTOLOGY_DATA.get(ontology_id, {"individuals": []})
    return [IndividualResponse(**i) for i in data["individuals"]]


async def create_individual(
    ontology_id: str,
    name: str,
    display_name: str = None,
    description: str = None,
    types: list = None,
    labels: dict = None,
    comments: dict = None,
    data_property_assertions: list = None,
    object_property_assertions: list = None,
) -> IndividualResponse:
    new_ind = {
        "id": f"ind-{len(ONTOLOGY_DATA.get(ontology_id, {}).get('individuals', [])) + 1}",
        "ontology_id": ontology_id,
        "name": name,
        "display_name": display_name or name,
        "description": description,
        "types": types or [],
        "labels": labels or {},
        "comments": comments or {},
        "data_property_assertions": data_property_assertions or [],
        "object_property_assertions": object_property_assertions or [],
    }
    if ontology_id not in ONTOLOGY_DATA:
        _init_ontology_data(ontology_id)
    ONTOLOGY_DATA[ontology_id]["individuals"].append(new_ind)
    return IndividualResponse(**new_ind)


async def get_axioms(ontology_id: str) -> list[AxiomResponse]:
    data = ONTOLOGY_DATA.get(ontology_id, {"axioms": []})
    return [AxiomResponse(**a) for a in data["axioms"]]


async def create_axiom(
    ontology_id: str,
    axiom_type: str,
    subject: str = None,
    assertions: dict = None,
    annotations: list = None,
) -> AxiomResponse:
    new_axiom = {
        "id": f"ax-{len(ONTOLOGY_DATA.get(ontology_id, {}).get('axioms', [])) + 1}",
        "ontology_id": ontology_id,
        "type": axiom_type,
        "subject": subject,
        "assertions": assertions or {},
        "annotations": annotations or [],
    }
    if ontology_id not in ONTOLOGY_DATA:
        _init_ontology_data(ontology_id)
    ONTOLOGY_DATA[ontology_id]["axioms"].append(new_axiom)
    return AxiomResponse(**new_axiom)


async def get_data_ranges(ontology_id: str) -> list[DataRangeResponse]:
    data = ONTOLOGY_DATA.get(ontology_id, {"data_ranges": []})
    return [DataRangeResponse(**d) for d in data["data_ranges"]]
