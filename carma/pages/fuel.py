from typing import Dict, Sequence
from typing import TYPE_CHECKING

import reflex as rx
import pandas as pd

from ..components.dialog import CreateFuelRecordDialog
from ..template import template
from ..models.fuel import Fuel
from ..models.company import Company
from sqlmodel import select

import plotly.express as px
import plotly.graph_objects as go


class State(rx.State):
    fuel_records: pd.DataFrame =  pd.DataFrame(columns=["milage", "liters", "price", "km_driven", "price_per_liter", "consumption"])
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
            x=self.fuel_records.index[self.fuel_records['consumption'] != 0],
            y="consumption",

        )

    @rx.event
    def fuel_price_graph(self):
        self.fuel_price_figure = px.line(
            self.fuel_records,
            x=self.fuel_records.index,
            y="price_per_liter",

        )

    @rx.event
    def change_time_range(self, time_range: str):
        """Change the select value var."""
        self.time_range = time_range

    @rx.event
    def init_fuel_page(self):
        self.load_fuel_records()
        self.fuel_consumption_graph()
        self.fuel_price_graph()

    @rx.event
    def load_fuel_records(self):
        """Get all fuel items from the database."""
        with rx.session() as session: # i tried moving this as a static method of Fuel, but it returns something different then?
            results = session.exec(select(Fuel))
            fuel_records = results.all()
        self.fuel_records = Fuel.process_fuel_to_df(fuel_records)

def select_time_range():
    return rx.select(
            ["All time", "Last month", "Last year"],
            value=State.time_range,
            on_change=State.change_time_range,
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
    create_fuel_record_dialog = CreateFuelRecordDialog.create
    return rx.vstack(
            select_time_range(),
        rx.badge("Time range is not yet implemented, statistics based on all time data", color_scheme="red"),

        create_fuel_record_dialog(rx.button("Add new fuel record in fuel page!"), on_close_auto_focus=State.init_fuel_page),

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
