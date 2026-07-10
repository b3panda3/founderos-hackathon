"""Entity and relation type definitions for the startup knowledge graph."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel


class EntityType(str, Enum):
    STARTUP = "startup"
    INVESTOR = "investor"
    MARKET = "market"
    TECHNOLOGY = "technology"
    PERSON = "person"
    PRODUCT = "product"


class RelationType(str, Enum):
    FUNDED_BY = "funded_by"
    INVESTED_IN = "invested_in"
    COMPETES_WITH = "competes_with"
    USES_TECH = "uses_tech"
    FOUNDED_BY = "founded_by"
    OPERATES_IN = "operates_in"
    ACQUIRED_BY = "acquired_by"
    PARTNERED_WITH = "partnered_with"
    WORKS_AT = "works_at"
    CREATED = "created"


class Entity(BaseModel):
    id: str
    type: EntityType
    name: str
    properties: dict = {}


class Relation(BaseModel):
    source_id: str
    target_id: str
    type: RelationType
    properties: dict = {}