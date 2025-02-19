from typing import Dict, Sequence

import reflex as rx
import pandas as pd
from ..template import template
from ..models.fuel import Fuel
from ..models.company import Company
from sqlmodel import select
from datetime import datetime

import reflex_chakra as rc
import plotly.express as px
import plotly.graph_objects as go

from ..components.dialog import CreateCompanyDialog

def process_fuel_to_df(fuel_records: Sequence[Fuel]):
    fuel_records_df = pd.DataFrame([vars(fuel_record) for fuel_record in fuel_records])

    fuel_records_df = fuel_records_df[["date", "milage", "liters", "price"]]
    fuel_records_df["date"] = pd.to_datetime(fuel_records_df["date"])

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
    return fuel_records_df

class State(rx.State):
    fuel_records: pd.DataFrame =  pd.DataFrame(columns=["date", "milage", "liters", "price", "km_driven", "price_per_liter", "consumption"])
    companies: Dict[str, Company] = {}
    time_range: str = "All time"
    fuel_figure: go.Figure = px.line()
    fuel_price_figure: go.Figure = px.line()

    @rx.var
    def average_consumption(self) -> float:
        return self.fuel_records[self.fuel_records['consumption'] != 0]['consumption'].mean()

    @rx.var
    def average_fuel_price(self) -> float :
        return self.fuel_records["price_per_liter"].mean()

    @rx.event
    def fuel_consumption_graph(self):
        self.fuel_figure = px.line(
            self.fuel_records[self.fuel_records['consumption'] != 0],
            x="date",
            y="consumption",

        )

    @rx.event
    def fuel_price_graph(self):
        self.fuel_price_figure = px.line(
            self.fuel_records,
            x="date",
            y="price_per_liter",

        )

    @rx.event
    def change_time_range(self, time_range: str):
        """Change the select value var."""
        self.time_range = time_range

    @rx.event
    def validate_and_add_fuel_record(self, form_data: dict):
        valid = True
        first_entry = len(self.fuel_records)==0
        if form_data["milage"] =="":
            yield rx.toast.error("Milage cannot be empty")
            valid = False
        elif int(form_data["milage"]) < 0:
            yield rx.toast.error("Milage cannot be negative")
            valid = False

        if form_data["price"] =="":
            yield rx.toast.error("Price cannot be empty")
            valid = False
        elif float(form_data["price"]) <= 0:
            yield rx.toast.error("Price cannot be negative")
            valid = False

        if form_data["company"] =="":
            yield rx.toast.error("Company cannot be empty")
            valid = False

        if not first_entry:
            #TODO: add milage validation on neighbour entries (should not be lower or higher)
            pass

        if valid is True:
            Fuel.add_fuel_record(**form_data)
            self.load_fuel_records()
            self.fuel_consumption_graph()
            yield rx.toast.success("Fuel record added")

    @rx.event
    def init_fuel_page(self):
        self.load_fuel_records()
        self.load_companies()

    @rx.event
    def load_fuel_records(self) -> pd.DataFrame:
        """Get all fuel items from the database."""
        with rx.session() as session:
            fuel_records = session.exec(select(Fuel)).all()

        self.fuel_records = process_fuel_to_df(fuel_records)

    @rx.event
    def load_companies(self) -> list[Company]:
        """Get all companies from the database."""
        with rx.session() as session:
            companies = session.exec(select(Company)).all()
            self.companies = {str(company.id): company for company in companies}

def select_time_range():
    return rx.select(
            ["All time", "Last month", "Last year"],
            value=State.time_range,
            on_change=State.change_time_range,
        )


    return None

def fuel_form():
    create_company_dialog = CreateCompanyDialog.create
    return rx.dialog.root(
        rx.dialog.trigger(rx.button("Add new fuel record")),
        rx.dialog.content(
            rx.dialog.title("Add new fuel record"),
            create_company_dialog(rx.button("Add new company in fuel page!")),
            rx.form(
                rx.vstack(
                    rc.input(type_="datetime-local", name="date", default_value=datetime.now().strftime('%Y-%m-%dT%H:%M')),
                    rx.select.root(
                        rx.select.trigger(placeholder="Select gas station"),
                        rx.select.content(
                                rx.foreach(
                                    State.companies.items(),
                                    lambda item: rx.select.item(
                                        item[1].name,
                                        value=item[0],  # TOOD: Ask if this can neater
                                    ),
                                )
                        ),
                        name="company",
                        on_open_change=State.load_companies,
                    ),
                    rx.input(
                        placeholder="milage",
                        name="milage",
                    ),
                    rx.input(
                        placeholder="liters",
                        name="liters",
                    ),
                    rx.input(
                        placeholder="price",
                        name="price",
                    ),
                    rx.dialog.close(rx.button("Add record", type="submit")),
                ),
                on_submit=State.validate_and_add_fuel_record,
                reset_on_submit=False,
            ),
        ),
    )

def fuel_table():
    return rx.data_table(
        data = State.fuel_records,
        sort = True,
        pagination= True
    )

@rx.page(route="/fuel", on_load=State.init_fuel_page)
@template
def fuel_page() -> rx.Component:
    return rx.vstack(
            select_time_range(),
        rx.badge("Time range is not yet implemented, statistics based on all time data", color_scheme="red"),
            fuel_form(),
        rx.text(f"Average fuel consumption: {State.average_consumption} km/L"),
        rx.text(f"Average fuel cost: {State.average_fuel_price} eur/L"),
        rx.heading("Consumption over time"),
        rx.plotly(
            data=State.fuel_figure,
            on_mount=State.fuel_consumption_graph,
        ),
        rx.heading("Fuel price over time"),
        rx.plotly(
            data=State.fuel_price_figure,
            on_mount=State.fuel_price_graph,
        ),
            rx.heading("Historical fuel records:"),
        fuel_table())
