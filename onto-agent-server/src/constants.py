"""
常量定义

所有硬编码的配置值集中在此处管理
"""

# ==================== PostgreSQL ====================
POSTGRES_DEFAULT_HOST = "localhost"
POSTGRES_SYSTEM_PORT = 5432
POSTGRES_BUSINESS_PORT = 5433
POSTGRES_SYSTEM_DB = "system_db"
POSTGRES_BUSINESS_DB = "onto_agent"

# ==================== Jena/Fuseki ====================
JENA_DEFAULT_HOST = "localhost"
JENA_DEFAULT_PORT = 3030
JENA_DEFAULT_DATASET = "/onto-agent"
JENA_TIMEOUT_SECONDS = 30

# ==================== 分页默认值 ====================
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# ==================== OWL 内置数据类型 ====================
OWL_DATATYPES = {
    "string": "http://www.w3.org/2001/XMLSchema#string",
    "boolean": "http://www.w3.org/2001/XMLSchema#boolean",
    "integer": "http://www.w3.org/2001/XMLSchema#integer",
    "decimal": "http://www.w3.org/2001/XMLSchema#decimal",
    "float": "http://www.w3.org/2001/XMLSchema#float",
    "double": "http://www.w3.org/2001/XMLSchema#double",
    "date": "http://www.w3.org/2001/XMLSchema#date",
    "dateTime": "http://www.w3.org/2001/XMLSchema#dateTime",
    "time": "http://www.w3.org/2001/XMLSchema#time",
    "duration": "http://www.w3.org/2001/XMLSchema#duration",
    "anyURI": "http://www.w3.org/2001/XMLSchema#anyURI",
    "langString": "http://www.w3.org/1999/02/22-rdf-syntax-ns#langString",
}

# OWL 2 内置类
OWL_CLASSES = [
    "Thing",
    "Nothing",
]

# ==================== SPARQL 前缀 ====================
DEFAULT_PREFIXES = {
    "owl": "http://www.w3.org/2002/07/owl#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
}
