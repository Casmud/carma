from sqlmodel import Field, Relationship
from datetime import datetime

from typing import TYPE_CHECKING
from .base import CarmaBase
from .company import Company
import reflex as rx
import pandas as pd

from sqlalchemy import select

# if TYPE_CHECKING: #chrashes if i do it like this
#   from .company import Company
from typing import Sequence

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

    @staticmethod
    def load_all_fuel_records():
        """Get all fuel items from the database."""
        with rx.session() as session:
            results = session.exec(select(Fuel))
            fuel_records = results.all()

        return fuel_records

    @staticmethod
    def process_fuel_to_df(fuel_records: Sequence["Fuel"]):
        fuel_records_df = pd.DataFrame([vars(fuel_record) for fuel_record in fuel_records])

        fuel_records_df = fuel_records_df[["date", "milage", "liters", "price"]]
        fuel_records_df["date"] = pd.to_datetime(fuel_records_df["date"])
        fuel_records_df.set_index("date", inplace=True)

        # Calculate km_driven
        fuel_records_df["km_driven"] = fuel_records_df["milage"].diff()
        fuel_records_df["km_driven"] = fuel_records_df["km_driven"].fillna(0)  # First entry has no previous mileage

        # Calculate price_per_liter
        fuel_records_df["price_per_liter"] = fuel_records_df["price"] / fuel_records_df[
            "liters"]
        fuel_records_df["price_per_liter"] = fuel_records_df["price_per_liter"].fillna(
            0)

        # Calculate consumption (km/L)
        fuel_records_df["consumption"] = fuel_records_df["km_driven"] / fuel_records_df[
            "liters"]
        fuel_records_df["consumption"] = fuel_records_df["consumption"].replace([float('inf'), -float('inf')],
                                                                                0).fillna(0)

        fuel_records_df = fuel_records_df.sort_index()
        return fuel_records_df