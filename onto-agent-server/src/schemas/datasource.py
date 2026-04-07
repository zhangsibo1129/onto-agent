from pydantic import Field
from typing import Optional
from datetime import datetime
from src.core.naming import CamelCaseModel


class DatasourceBase(CamelCaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    type: str = Field(..., min_length=1, max_length=50)
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    db_schema: Optional[str] = Field(default=None, alias="schema")
    username: Optional[str] = None
    password: Optional[str] = None
    ssl_mode: Optional[str] = None
    description: Optional[str] = None


class DatasourceCreate(DatasourceBase):
    pass


class DatasourceUpdate(CamelCaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    db_schema: Optional[str] = Field(default=None, alias="schema")
    username: Optional[str] = None
    password: Optional[str] = None
    ssl_mode: Optional[str] = None
    description: Optional[str] = None


class DatasourceResponse(CamelCaseModel):
    id: str
    name: str
    type: str
    status: str
    table_count: int
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    db_schema: Optional[str] = Field(default=None, alias="schema")
    username: Optional[str] = None
    ssl_mode: Optional[str] = None
    description: Optional[str] = None
    last_sync_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class TableInfo(CamelCaseModel):
    name: str
    columns: int
    row_count: int


class ColumnInfo(CamelCaseModel):
    name: str
    type: str
    nullable: bool
    primary_key: bool
    default_value: Optional[str] = None


class TestResult(CamelCaseModel):
    connected: bool
    latency: Optional[str] = None
    version: Optional[str] = None
    table_count: Optional[int] = None
    error: Optional[str] = None


class TestConnectionRequest(CamelCaseModel):
    type: str = Field(..., min_length=1, max_length=50)
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    db_schema: Optional[str] = Field(default=None, alias="schema")
    username: Optional[str] = None
    password: Optional[str] = None
    ssl_mode: Optional[str] = None


class ApiResponse(CamelCaseModel):
    success: bool = True
    data: Optional[dict] = None
    error: Optional[dict] = None
