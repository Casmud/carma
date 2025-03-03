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
        # TODO (Gijs comment): Fuel is a Pydantic subclass, so you should use fuel_record.model_dump() instead of vars(fuel_record)
        # This also will make sure that only the "defined payload attributes" are included in the DataFrame

        # Extract company names and add to temp_df
        fuel_records_df["company_name"] = fuel_records_df["company"].apply(lambda x: x.name)
        # TODO (Gijs comment): This may get costly. Firstly the lambda function is executed for 
        # every row in the DataFrame, jumping from Python to C and back. Secondly, this may result
        # in a lot of queries to the database. It is better to use a join in the original query to
        # get the company name in the same query.

        fuel_records_df = fuel_records_df[["date", "company_name", "mileage", "liters", "price"]]
        fuel_records_df["date"] = pd.to_datetime(fuel_records_df["date"])
        fuel_records_df["date_copy"] = fuel_records_df["date"]
        fuel_records_df.set_index("date", inplace=True)

        # Calculate km_driven
        fuel_records_df["km_driven"] = fuel_records_df["mileage"].diff()
        fuel_records_df["km_driven"] = fuel_records_df["km_driven"].fillna(0)  # First entry has no previous mileage
        # TODO (Gijs comment): Here you replace all NaN values with 0, not only the first one.
        # This may not be a problem, but they should not be there. Also what about negative and zero values?

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

# TODO (Gijs comment): Alternative get all fuel records you need with all computed stuff in one query. It may need a bit of further tweaking
# to get it to work, but it should be possible. This way you can avoid the pandas processing step.
def get_augmented_fuel_records(from_date: datetime.date | None = None, to_date: datetime.date | None = None):
    with rx.session() as session:
        query = select(
            Fuel, 
            (Fuel.mileage - rx.func.lag(Fuel.mileage).over(order_by=Fuel.date)).label("delta_mileage"),
            (Fuel.price / Fuel.liters).label("price_per_liter"),
            Company.name.label("company_name"),
            (rx.func.coalesce((Fuel.mileage - rx.func.lag(Fuel.mileage).over(order_by=Fuel.date)) / Fuel.liters, 0)).label("consumption")
        ).join(Company, Fuel.company_id == Company.id)
        
        if from_date is not None:
            query = query.where(Fuel.date >= from_date)
        
        if to_date is not None:
            query = query.where(Fuel.date <= to_date)
        
        results = session.exec(query)
        fuel_records = results.all()
        
        return fuel_records
