from datetime import datetime
from typing import Optional
from src.schemas.ontology import (
    OntologyClassResponse,
    DataPropertyResponse,
    ObjectPropertyResponse,
    OntologyRelationResponse,
    OntologyResponse,
    OntologyDetailResponse,
)

MOCK_ONTOLOGIES = [
    {
        "id": "1",
        "name": "客户360",
        "description": "企业客户全景视图",
        "status": "published",
        "object_count": 8,
        "property_count": 64,
        "relation_count": 14,
        "updated_at": "2 小时前",
        "version": "v2.1",
        "datasource": "ERP-Production",
    },
    {
        "id": "2",
        "name": "供应商网络",
        "description": "供应商关系与供应链视图",
        "status": "published",
        "object_count": 6,
        "property_count": 42,
        "relation_count": 9,
        "updated_at": "昨天",
        "version": "v1.3",
        "datasource": "SCM-SupplyChain",
    },
    {
        "id": "3",
        "name": "订单全景",
        "description": "订单、发票与物流追踪",
        "status": "draft",
        "object_count": 5,
        "property_count": 38,
        "relation_count": 7,
        "updated_at": "3 天前",
        "version": "v1.2-draft",
        "datasource": "ERP-Production",
    },
    {
        "id": "4",
        "name": "库存管理",
        "description": "仓库与库存状态追踪",
        "status": "draft",
        "object_count": 3,
        "property_count": 24,
        "relation_count": 5,
        "updated_at": "5 天前",
        "version": "v0.5-draft",
        "datasource": "ERP-Production",
    },
    {
        "id": "5",
        "name": "财务分析",
        "description": "财务报表与成本分析",
        "status": "archived",
        "object_count": 2,
        "property_count": 16,
        "relation_count": 3,
        "updated_at": "2 周前",
        "version": "v1.0",
        "datasource": "ERP-Production",
    },
]

ONTOLOGY_DATA: dict[str, dict] = {
    "1": {
        "classes": [
            {
                "id": "Product",
                "name": "Product",
                "display_name": "产品",
                "description": "商品实体",
            },
            {
                "id": "Order",
                "name": "Order",
                "display_name": "订单",
                "description": "订单实体",
            },
            {
                "id": "Customer",
                "name": "Customer",
                "display_name": "客户",
                "description": "客户实体",
            },
            {
                "id": "Supplier",
                "name": "Supplier",
                "display_name": "供应商",
                "description": "供应商实体",
            },
            {
                "id": "Shipment",
                "name": "Shipment",
                "display_name": "货运",
                "description": "货运实体",
            },
        ],
        "data_properties": [
            {
                "id": "p1",
                "name": "productName",
                "display_name": "产品名称",
                "domain_id": "Product",
                "range_type": "String",
            },
            {
                "id": "p2",
                "name": "price",
                "display_name": "价格",
                "domain_id": "Product",
                "range_type": "Float",
            },
            {
                "id": "p3",
                "name": "orderDate",
                "display_name": "订单日期",
                "domain_id": "Order",
                "range_type": "Date",
            },
            {
                "id": "p4",
                "name": "totalAmount",
                "display_name": "总金额",
                "domain_id": "Order",
                "range_type": "Float",
            },
            {
                "id": "p5",
                "name": "customerName",
                "display_name": "客户名称",
                "domain_id": "Customer",
                "range_type": "String",
            },
            {
                "id": "p6",
                "name": "tier",
                "display_name": "客户等级",
                "domain_id": "Customer",
                "range_type": "Enum",
            },
            {
                "id": "p7",
                "name": "supplierName",
                "display_name": "供应商名称",
                "domain_id": "Supplier",
                "range_type": "String",
            },
            {
                "id": "p8",
                "name": "shipmentDate",
                "display_name": "发货日期",
                "domain_id": "Shipment",
                "range_type": "Date",
            },
        ],
        "object_properties": [
            {
                "id": "op1",
                "name": "hasProduct",
                "display_name": "包含产品",
                "domain_id": "Order",
                "range_id": "Product",
            },
            {
                "id": "op2",
                "name": "placedBy",
                "display_name": "下单",
                "domain_id": "Order",
                "range_id": "Customer",
            },
            {
                "id": "op3",
                "name": "suppliedBy",
                "display_name": "供应方",
                "domain_id": "Product",
                "range_id": "Supplier",
            },
            {
                "id": "op4",
                "name": "ships",
                "display_name": "发货运",
                "domain_id": "Order",
                "range_id": "Shipment",
            },
            {
                "id": "op5",
                "name": "owns",
                "display_name": "拥有",
                "domain_id": "Customer",
                "range_id": "Order",
            },
        ],
        "relations": [
            {
                "id": "r1",
                "source_id": "Order",
                "target_id": "Product",
                "property_id": "op1",
            },
            {
                "id": "r2",
                "source_id": "Order",
                "target_id": "Customer",
                "property_id": "op2",
            },
            {
                "id": "r3",
                "source_id": "Product",
                "target_id": "Supplier",
                "property_id": "op3",
            },
            {
                "id": "r4",
                "source_id": "Order",
                "target_id": "Shipment",
                "property_id": "op4",
            },
            {
                "id": "r5",
                "source_id": "Customer",
                "target_id": "Order",
                "property_id": "op5",
            },
        ],
    },
    "2": {
        "classes": [
            {
                "id": "Supplier",
                "name": "Supplier",
                "display_name": "供应商",
                "description": "供应商实体",
            },
            {
                "id": "Warehouse",
                "name": "Warehouse",
                "display_name": "仓库",
                "description": "仓库实体",
            },
            {
                "id": "Product",
                "name": "Product",
                "display_name": "产品",
                "description": "产品实体",
            },
        ],
        "data_properties": [
            {
                "id": "p1",
                "name": "supplierName",
                "display_name": "供应商名称",
                "domain_id": "Supplier",
                "range_type": "String",
            },
            {
                "id": "p2",
                "name": "warehouseLocation",
                "display_name": "仓库位置",
                "domain_id": "Warehouse",
                "range_type": "String",
            },
            {
                "id": "p3",
                "name": "stockLevel",
                "display_name": "库存数量",
                "domain_id": "Product",
                "range_type": "Integer",
            },
        ],
        "object_properties": [
            {
                "id": "op1",
                "name": "supplies",
                "display_name": "供应",
                "domain_id": "Supplier",
                "range_id": "Product",
            },
            {
                "id": "op2",
                "name": "stores",
                "display_name": "存储",
                "domain_id": "Warehouse",
                "range_id": "Product",
            },
        ],
        "relations": [
            {
                "id": "r1",
                "source_id": "Supplier",
                "target_id": "Product",
                "property_id": "op1",
            },
            {
                "id": "r2",
                "source_id": "Warehouse",
                "target_id": "Product",
                "property_id": "op2",
            },
        ],
    },
    "3": {
        "classes": [
            {
                "id": "Order",
                "name": "Order",
                "display_name": "订单",
                "description": "订单实体",
            },
            {
                "id": "Invoice",
                "name": "Invoice",
                "display_name": "发票",
                "description": "发票实体",
            },
        ],
        "data_properties": [
            {
                "id": "p1",
                "name": "orderDate",
                "display_name": "订单日期",
                "domain_id": "Order",
                "range_type": "Date",
            },
            {
                "id": "p2",
                "name": "invoiceAmount",
                "display_name": "发票金额",
                "domain_id": "Invoice",
                "range_type": "Float",
            },
        ],
        "object_properties": [
            {
                "id": "op1",
                "name": "hasInvoice",
                "display_name": "包含发票",
                "domain_id": "Order",
                "range_id": "Invoice",
            },
        ],
        "relations": [
            {
                "id": "r1",
                "source_id": "Order",
                "target_id": "Invoice",
                "property_id": "op1",
            },
        ],
    },
}


async def list_ontologies() -> list[OntologyResponse]:
    return [OntologyResponse(**o) for o in MOCK_ONTOLOGIES]


async def get_ontology(ontology_id: str) -> Optional[OntologyResponse]:
    for o in MOCK_ONTOLOGIES:
        if o["id"] == ontology_id:
            return OntologyResponse(**o)
    return None


async def get_ontology_detail(ontology_id: str) -> Optional[OntologyDetailResponse]:
    for o in MOCK_ONTOLOGIES:
        if o["id"] == ontology_id:
            base = OntologyResponse(**o)
            data = ONTOLOGY_DATA.get(
                ontology_id,
                {
                    "classes": [],
                    "data_properties": [],
                    "object_properties": [],
                    "relations": [],
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
                relations=[OntologyRelationResponse(**r) for r in data["relations"]],
            )
    return None


async def get_ontology_classes(ontology_id: str) -> list[OntologyClassResponse]:
    data = ONTOLOGY_DATA.get(ontology_id, {"classes": []})
    return [OntologyClassResponse(**c) for c in data["classes"]]


async def create_ontology_class(
    ontology_id: str, name: str, display_name: str = None, description: str = None
) -> OntologyClassResponse:
    new_class = {
        "id": name,
        "name": name,
        "display_name": display_name or name,
        "description": description,
    }
    if ontology_id not in ONTOLOGY_DATA:
        ONTOLOGY_DATA[ontology_id] = {
            "classes": [],
            "data_properties": [],
            "object_properties": [],
            "relations": [],
        }
    ONTOLOGY_DATA[ontology_id]["classes"].append(new_class)
    return OntologyClassResponse(**new_class)


async def get_data_properties(ontology_id: str) -> list[DataPropertyResponse]:
    data = ONTOLOGY_DATA.get(ontology_id, {"data_properties": []})
    return [DataPropertyResponse(**p) for p in data["data_properties"]]


async def create_data_property(
    ontology_id: str,
    name: str,
    domain_id: str,
    range_type: str = "String",
    display_name: str = None,
) -> DataPropertyResponse:
    new_prop = {
        "id": f"dp-{len(ONTOLOGY_DATA.get(ontology_id, {}).get('data_properties', [])) + 1}",
        "name": name,
        "display_name": display_name or name,
        "domain_id": domain_id,
        "range_type": range_type,
    }
    if ontology_id not in ONTOLOGY_DATA:
        ONTOLOGY_DATA[ontology_id] = {
            "classes": [],
            "data_properties": [],
            "object_properties": [],
            "relations": [],
        }
    ONTOLOGY_DATA[ontology_id]["data_properties"].append(new_prop)
    return DataPropertyResponse(**new_prop)


async def get_object_properties(ontology_id: str) -> list[ObjectPropertyResponse]:
    data = ONTOLOGY_DATA.get(ontology_id, {"object_properties": []})
    return [ObjectPropertyResponse(**p) for p in data["object_properties"]]


async def create_object_property(
    ontology_id: str,
    name: str,
    domain_id: str,
    range_id: str,
    display_name: str = None,
) -> ObjectPropertyResponse:
    new_prop = {
        "id": f"op-{len(ONTOLOGY_DATA.get(ontology_id, {}).get('object_properties', [])) + 1}",
        "name": name,
        "display_name": display_name or name,
        "domain_id": domain_id,
        "range_id": range_id,
    }
    if ontology_id not in ONTOLOGY_DATA:
        ONTOLOGY_DATA[ontology_id] = {
            "classes": [],
            "data_properties": [],
            "object_properties": [],
            "relations": [],
        }
    ONTOLOGY_DATA[ontology_id]["object_properties"].append(new_prop)
    return ObjectPropertyResponse(**new_prop)


async def get_relations(ontology_id: str) -> list[OntologyRelationResponse]:
    data = ONTOLOGY_DATA.get(ontology_id, {"relations": []})
    return [OntologyRelationResponse(**r) for r in data["relations"]]


async def create_relation(
    ontology_id: str,
    source_id: str,
    target_id: str,
    property_id: str,
) -> OntologyRelationResponse:
    new_rel = {
        "id": f"r-{len(ONTOLOGY_DATA.get(ontology_id, {}).get('relations', [])) + 1}",
        "source_id": source_id,
        "target_id": target_id,
        "property_id": property_id,
    }
    if ontology_id not in ONTOLOGY_DATA:
        ONTOLOGY_DATA[ontology_id] = {
            "classes": [],
            "data_properties": [],
            "object_properties": [],
            "relations": [],
        }
    ONTOLOGY_DATA[ontology_id]["relations"].append(new_rel)
    return OntologyRelationResponse(**new_rel)
