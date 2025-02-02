from sqlmodel import Field, Relationship
from datetime import datetime

from typing import TYPE_CHECKING
from .base import CarmaBase
from .company import Company

# if TYPE_CHECKING: #chrashes if i do it like this
#   from .company import Company


class Fuel(CarmaBase, table=True):
    date: datetime
    milage: int
    liters: float
    price: float

    company_id: int | None = Field(default=None, foreign_key="company.id")
    company: "Company" = Relationship(
        back_populates="fuels", sa_relationship_kwargs={"lazy": "selectin"}
    )
