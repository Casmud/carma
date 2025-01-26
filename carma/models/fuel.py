from typing import TYPE_CHECKING

from .base import CarmaBase, Field, Relationship, datetime

if TYPE_CHECKING:
    from .company import Company


class Fuel(CarmaBase, table=True):
    date: datetime
    kilometrage: int
    liters: float
    price: float
    company_id: int | None = Field(default=None, foreign_key="company.id")

    # Relationships are dynamically populated. So they are only available in the
    # backend in rx.events and not in the frontend. So grab them in an event and
    # then store them in the State as regular attributes.
    company: "Company" = Relationship(back_populates="fuels")
