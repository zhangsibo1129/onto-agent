"""
统一异常定义

所有自定义异常集中在此处管理
"""


class AppError(Exception):
    """应用层基础异常"""
    
    def __init__(self, message: str, code: str = "APP_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


# ==================== 资源相关 ====================

class OntologyNotFoundError(AppError):
    """本体不存在"""
    
    def __init__(self, ontology_id: str):
        super().__init__(
            message=f"Ontology not found: {ontology_id}",
            code="ONTOLOGY_NOT_FOUND"
        )
        self.ontology_id = ontology_id


class EntityNotFoundError(AppError):
    """实体不存在（类、属性、个体等）"""
    
    def __init__(self, entity_type: str, entity_id: str):
        super().__init__(
            message=f"{entity_type} not found: {entity_id}",
            code="ENTITY_NOT_FOUND"
        )
        self.entity_type = entity_type
        self.entity_id = entity_id


class DataSourceNotFoundError(AppError):
    """数据源不存在"""
    
    def __init__(self, datasource_id: str):
        super().__init__(
            message=f"DataSource not found: {datasource_id}",
            code="DATASOURCE_NOT_FOUND"
        )


# ==================== 验证相关 ====================

class ValidationError(AppError):
    """数据验证失败"""
    
    def __init__(self, message: str, field: str = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR"
        )
        self.field = field


class DuplicateError(AppError):
    """资源重复"""
    
    def __init__(self, resource_type: str, identifier: str):
        super().__init__(
            message=f"{resource_type} already exists: {identifier}",
            code="DUPLICATE_RESOURCE"
        )


# ==================== 服务相关 ====================

class JenaServiceError(AppError):
    """Jena/Fuseki 服务异常"""
    
    def __init__(self, message: str, endpoint: str = None):
        super().__init__(
            message=message,
            code="JENA_SERVICE_ERROR"
        )
        self.endpoint = endpoint


class JenaQueryError(JenaServiceError):
    """Jena SPARQL 查询异常"""
    
    def __init__(self, message: str, query: str = None):
        super().__init__(message)
        self.code = "JENA_QUERY_ERROR"
        self.query = query


class DatabaseError(AppError):
    """数据库操作异常"""
    
    def __init__(self, message: str, operation: str = None):
        super().__init__(
            message=message,
            code="DATABASE_ERROR"
        )
        self.operation = operation


# ==================== 事务相关 ====================

class SagaError(AppError):
    """Saga 事务异常"""
    
    def __init__(self, message: str, saga_id: str = None):
        super().__init__(
            message=message,
            code="SAGA_ERROR"
        )
        self.saga_id = saga_id


class CompensationError(SagaError):
    """补偿操作失败"""
    
    def __init__(self, message: str, saga_id: str = None):
        super().__init__(message, saga_id)
        self.code = "COMPENSATION_ERROR"
