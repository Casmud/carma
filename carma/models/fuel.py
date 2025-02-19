from sqlmodel import Field, Relationship
from datetime import datetime

from typing import TYPE_CHECKING
from .base import CarmaBase
from .company import Company
import reflex as rx

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

    @staticmethod
    def add_fuel_record(date, milage, liters, price, company):
        with rx.session() as session:
            new_fuel_record = Fuel(
                date=date,
                milage=milage,
                liters=liters,
                price=price,
                company_id=company
            )
            session.add(new_fuel_record)
            session.commit()