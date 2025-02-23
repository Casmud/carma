from typing import TYPE_CHECKING

import reflex as rx
from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship, select

from .base import CarmaBase

if TYPE_CHECKING:
    # See https://sqlmodel.tiangolo.com/tutorial/code-structure/
    from .fuel import Fuel


class Company(CarmaBase, table=True):
    __table_args__ = (UniqueConstraint("name", name="uix_company_name"),)

    name: str = Field(nullable=False)  # Alternate key -> needs UniqueConstraint and may not be null.
    address: str | None
    is_gas_station: bool = Field(default=True)
    is_garage: bool = Field(default=False)

    # Relationships are dynamically populated. So they are only available in the
    # backend in rx.events and not in the frontend. So grab them in an event and
    # then store them in the State as regular attributes.
    fuels: list["Fuel"] = Relationship(back_populates="company")

    @staticmethod
    def add_company(name, address, is_gas_station, is_garage):
        with rx.session() as session:
            new_company = Company(
                name=name,
                address=address,
                is_gas_station=is_gas_station,
                is_garage=is_garage,
            )
            session.add(new_company)
            session.commit()

    @staticmethod
    def load_companies() -> list["Company"]:
        """Get all companies from the database."""
        with rx.session() as session:
            companies = list(session.exec(select(Company).order_by(Company.name)).all())

            return companies
