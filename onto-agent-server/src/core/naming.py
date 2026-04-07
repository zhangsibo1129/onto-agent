from pydantic import BaseModel, ConfigDict
from humps import decamelize, camelize


def to_snake(name: str) -> str:
    return decamelize(name)


def to_camel(name: str) -> str:
    return camelize(name)


class CamelCaseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        by_alias=False,
    )


class SnakeCaseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_snake,
        populate_by_name=True,
        by_alias=False,
    )


def snake_dict(data: dict) -> dict:
    return {to_snake(k): v for k, v in data.items()}


def camel_dict(data: dict) -> dict:
    return {to_camel(k): v for k, v in data.items()}
