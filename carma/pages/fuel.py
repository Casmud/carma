from typing import Dict

import reflex as rx
import pandas as pd

from ..components.dialog import CreateFuelRecordDialog
from ..template import template
from ..models.fuel import Fuel
from ..models.company import Company
from sqlmodel import select, desc

import plotly.express as px
import plotly.graph_objects as go


class State(rx.State):
    fuel_records: pd.DataFrame = pd.DataFrame(
        columns=[
            "milage",
            "liters",
            "price",
            "km_driven",
            "price_per_liter",
            "consumption",
        ]
    )
    companies: Dict[str, Company] = {}
    time_range: str = "All time"
    fuel_figure: go.Figure = px.line()
    fuel_price_figure: go.Figure = px.line()
    latest_fuel_record: Fuel = None

    @rx.var
    def average_consumption(self) -> float:
        average = self.fuel_records[self.fuel_records["consumption"] != 0][
            "consumption"
        ].mean()
        return round(average, 2)

    @rx.var
    def average_fuel_price(self) -> float:
        average = self.fuel_records["price_per_liter"].mean()
        return round(average, 2)

    @rx.event
    def fuel_consumption_graph(self):
        self.fuel_figure = px.line(
            self.fuel_records[self.fuel_records["consumption"] != 0],
            x=self.fuel_records.index[self.fuel_records["consumption"] != 0],
            y="consumption",
            line_shape="spline",
            title="Average consumption (KM/L)",
        )

    @rx.event
    def get_latest_fuel_record(self):
        with rx.session() as session:
            stmt = select(Fuel).order_by(desc(Fuel.date))
            self.latest_fuel_record = session.exec(stmt).first()

    @rx.event
    def fuel_price_graph(self):
        self.fuel_price_figure = px.line(
            self.fuel_records,
            x=self.fuel_records.index,
            y="price_per_liter",
            line_shape="spline",
            title="Liter fuel price (EU/L)",
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
        self.get_latest_fuel_record()

    @rx.event
    def load_fuel_records(self):
        """Get all fuel items from the database."""
        with (
            rx.session() as session
        ):  # i tried moving this as a static method of Fuel, but it returns something different then?
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
    return rx.data_table(data=State.fuel_records, sort=True, pagination=True)


def general_stat_card(description, unit, value, icon, color) -> rx.Component:
    return rx.box(
        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.badge(
                        rx.icon(tag=icon, size=34),
                        radius="full",
                        color=color,
                        padding="0.7rem",
                    ),
                    rx.vstack(
                        rx.heading(
                            f"{value:.2f} {unit}",
                            size="6",
                            weight="bold",
                        ),
                        rx.text(description, size="4", weight="medium"),
                        spacing="1",
                        height="100%",
                        align_items="start",
                        width="100%",
                    ),
                    height="100%",
                    spacing="4",
                    align="center",
                    width="100%",
                ),
                spacing="3",
            ),
            size="3",
            width="400px",
        )
    )


def average_fuel_price_card():
    pass


def latest_fuel_visit_card():
    return rx.card(
        rx.heading("Last fuel record"),
        rx.data_list.root(
            rx.data_list.item(
                rx.data_list.label("Date"),
                rx.data_list.value(rx.moment(State.latest_fuel_record.date)),
            ),
            rx.data_list.item(
                rx.data_list.label("Location"),
                rx.data_list.value(State.latest_fuel_record.company.name),
            ),
            rx.data_list.item(
                rx.data_list.label("Amount"),
                rx.data_list.value(State.latest_fuel_record.liters),
            ),
            rx.data_list.item(
                rx.data_list.label("Price"),
                rx.data_list.value(State.latest_fuel_record.price),
            ),
            rx.data_list.item(
                rx.data_list.label("Milage"),
                rx.data_list.value(State.latest_fuel_record.milage),
            ),
            align="center",
        ),
    )


@rx.page(route="/fuel", on_load=State.init_fuel_page)
@template
def fuel_page() -> rx.Component:
    create_fuel_record_dialog = CreateFuelRecordDialog.create
    fuel_consumption_card = general_stat_card(
        description="Average Fuel Consumption",
        value=State.average_consumption,
        icon="gauge",
        unit="KM/L",
        color="cyan",
    )
    fuel_price_card = general_stat_card(
        description="Average Fuel Price",
        value=State.average_fuel_price,
        icon="euro",
        unit="EU/L",
        color="orange",
    )
    return rx.container(
        rx.vstack(
            rx.heading("Quick Statistics"),
            rx.hstack(
                select_time_range(),
                rx.badge(
                    "Time range is not yet implemented, statistics based on all time data",
                    color_scheme="red",
                ),
            ),
            rx.hstack(
                rx.vstack(fuel_consumption_card, fuel_price_card),
                latest_fuel_visit_card(),
            ),
            create_fuel_record_dialog(
                rx.button("Add new fuel record in fuel page!"),
                on_close_auto_focus=State.init_fuel_page,
            ),
            rx.heading("Historical graphs"),
            rx.hstack(
                rx.plotly(
                    data=State.fuel_figure,
                    on_mount=State.fuel_consumption_graph,
                ),
                rx.plotly(
                    data=State.fuel_price_figure,
                    on_mount=State.fuel_price_graph,
                ),
            ),
            rx.heading("Historical fuel records:"),
            fuel_table(),
        ),
        size="4",
    )
