from __future__ import annotations

from enum import Enum
from typing import NewType

PersonId = NewType("PersonId", int)


class Sex(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class EducationLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Region(str, Enum):
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"


class GovFunction(str, Enum):
    EDUCATION = "education"
    SOCIAL_PROTECTION = "social_protection"
    DEFENCE = "defence"
    HEALTH = "health"
    HOUSING = "housing"


class IncomeSource(str, Enum):
    LABOR = "labor"
    CAPITAL = "capital"
    TRANSFERS = "transfers"
