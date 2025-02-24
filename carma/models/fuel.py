# if TYPE_CHECKING: #chrashes if i do it like this
#   from .company import Company
from collections.abc import Sequence
from datetime import datetime

import pandas as pd
import reflex as rx
from sqlalchemy import select
from sqlmodel import Field, Relationship

from .base import CarmaBase
from .company import Company


class Fuel(CarmaBase, table=True):
    date: datetime
    mileage: int
    liters: float
    price: float

    company_id: int | None = Field(default=None, foreign_key="company.id")
    company: "Company" = Relationship(back_populates="fuels", sa_relationship_kwargs={"lazy": "selectin"})

    @staticmethod
    def add_fuel_record(date, mileage, liters, price, company):
        """Add new fuel record to the database"""
        with rx.session() as session:
            new_fuel_record = Fuel(date=date, mileage=mileage, liters=liters, price=price, company_id=company)
            session.add(new_fuel_record)
            session.commit()

    @staticmethod
    def load_all_fuel_records():
        """Add new fuel record to the database"""
        with rx.session() as session:
            results = session.exec(select(Fuel))
            fuel_records = results.all()

        return fuel_records

    @staticmethod
    def process_fuel_to_df(fuel_records: Sequence["Fuel"]):
        """Process list of fuel records into sorted dataframe with add derivative statistics:
        - Distance driven since previous record
        - Price per liter per record
        - Average consumption per record

        Parameters
        ----------
        fuel_records: Sequence["Fuel"]

        Returns
        -------
        pd.DataFrame

        """
        fuel_records_df = pd.DataFrame([vars(fuel_record) for fuel_record in fuel_records])

        # Extract company names and add to temp_df
        fuel_records_df["company_name"] = fuel_records_df["company"].apply(lambda x: x.name)

        fuel_records_df = fuel_records_df[["date", "company_name", "mileage", "liters", "price"]]
        fuel_records_df["date"] = pd.to_datetime(fuel_records_df["date"])
        fuel_records_df["date_copy"] = fuel_records_df["date"]
        fuel_records_df.set_index("date", inplace=True)

        # Calculate km_driven
        fuel_records_df["km_driven"] = fuel_records_df["mileage"].diff()
        fuel_records_df["km_driven"] = fuel_records_df["km_driven"].fillna(0)  # First entry has no previous mileage

        # Calculate price_per_liter
        fuel_records_df["price_per_liter"] = fuel_records_df["price"] / fuel_records_df["liters"]
        fuel_records_df["price_per_liter"] = fuel_records_df["price_per_liter"].fillna(0)

        # Calculate consumption (km/L)
        fuel_records_df["consumption"] = fuel_records_df["km_driven"] / fuel_records_df["liters"]
        fuel_records_df["consumption"] = (
            fuel_records_df["consumption"].replace([float("inf"), -float("inf")], 0).fillna(0)
        )

        # Reorder and rename columns
        fuel_records_df = fuel_records_df.rename(
            columns={
                "date_copy": "Date",
                "company_name": "Company",
                "mileage": "Mileage",
                "liters": "Liters",
                "price": "Price",
                "km_driven": "KM Driven",
                "price_per_liter": "Price per Liter",
                "consumption": "Consumption",
            }
        )

        # Ensure 'Date' is the first column
        columns_order = [
            "Date",
            "Company",
            "Mileage",
            "Liters",
            "Price",
            "KM Driven",
            "Price per Liter",
            "Consumption",
        ]

        fuel_records_df = fuel_records_df[columns_order]

        fuel_records_df = fuel_records_df.sort_index()
        return fuel_records_df
