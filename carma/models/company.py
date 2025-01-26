from typing import TYPE_CHECKING

from sqlalchemy import UniqueConstraint

from .base import CarmaBase, Relationship, Field

if TYPE_CHECKING:
    # See https://sqlmodel.tiangolo.com/tutorial/code-structure/
    from .fuel import Fuel


class Company(CarmaBase, table=True):
    __table_args__ = (
        UniqueConstraint("friendly_name", name="uix_company_friendly_name"),
    )
    friendly_name: str = Field(
        nullable=False
    )  # Alternate key -> needs UniqueConstraint and may not be null.
    formal_name: str  # TODO: Can this field be nullable?
    address: str | None
    is_pump: bool = Field(default=True)
    is_garage: bool = Field(default=False)

    # Relationships are dynamically populated. So they are only available in the
    # backend in rx.events and not in the frontend. So grab them in an event and
    # then store them in the State as regular attributes.
    fuels: list["Fuel"] = Relationship(back_populates="company")
