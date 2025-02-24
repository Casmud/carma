import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import reflex as rx
from sqlmodel import desc, select

from ..components.dialog import CreateFuelRecordDialog
from ..models.company import Company
from ..models.fuel import Fuel
from ..template import template


class State(rx.State):
    fuel_records: pd.DataFrame = pd.DataFrame(
        columns=[
            "Date",
            "Company",
            "Mileage",
            "Liters",
            "Price",
            "KM Driven",
            "Price per Liter",
            "Consumption",
        ]
    )
    companies: dict[str, Company] = {}
    time_range: str = "All time"
    fuel_figure: go.Figure = px.line()
    fuel_price_figure: go.Figure = px.line()
    latest_fuel_record: Fuel = None

# COMPUTED VARS
    @rx.var
    def average_consumption(self) -> float:
        """Calculates average fuel consumption over all data, returns rounded off value (2 decimals)"""
        average = self.fuel_records[self.fuel_records["Consumption"] != 0]["Consumption"].mean()
        return round(average, 2)

    @rx.var
    def average_fuel_price(self) -> float:
        """Calculates average fuel price over all data, returns rounded off value (2 decimals)"""
        average = self.fuel_records["Price per Liter"].mean()
        return round(average, 2)

##EVENTS

#GRAPHS
    @rx.event
    def fuel_consumption_graph(self):
        """Generates graph of fuel consumption over time"""
        self.fuel_figure = px.line(
            self.fuel_records[self.fuel_records["Consumption"] != 0],
            x=self.fuel_records.index[self.fuel_records["Consumption"] != 0],
            y="Consumption",
            line_shape="spline",
            title="Average consumption (KM/L)",
        )

    @rx.event
    def fuel_price_graph(self):
        """Generates graph of fuel price over time"""
        self.fuel_price_figure = px.line(
            self.fuel_records,
            x=self.fuel_records.index,
            y="Price per Liter",
            line_shape="spline",
            title="Liter fuel price (EU/L)",
        )


# DB REQUESTS
    @rx.event
    def get_latest_fuel_record(self):
        """Get most recent fuel record from database"""
        with rx.session() as session:
            stmt = select(Fuel).order_by(desc(Fuel.date))
            self.latest_fuel_record = session.exec(stmt).first()

    @rx.event
    def load_fuel_records(self):
        """Get all data from the database"""
        with rx.session() as session:
            results = session.exec(select(Fuel))
            fuel_records = results.all()

        # TODO: I tried moving *EXACT* same function as a static method to Fuel (repo model?) but then it seems to
        #  change the output?! -see line below
        # fuel_records = Fuel.load_all_fuel_records()

        self.fuel_records = Fuel.process_fuel_to_df(fuel_records)

# CALLBACKS
    @rx.event
    def change_time_range(self, time_range: str):
        """Select time range of statistics (not in use yet)"""
        self.time_range = time_range

# PAGE INITIALIZE
    @rx.event
    def init_fuel_page(self):
        """Used to initialize the fuel page and variables. Also used for 'reloading' after data has been updated."""
        self.load_fuel_records()
        self.fuel_consumption_graph()
        self.fuel_price_graph()
        self.get_latest_fuel_record()

## UI ELEMENTS

# GENERAL ELEMENTS
def general_stat_card(description, unit, value, icon, color) -> rx.Component:
    """General card to show statistics in fuel page

    Parameters
    ----------
    description: description of the statistic
    unit: unit of the statistic
    value: value of the statistic
    icon: icon of the statics
    color: color of the icon

    """
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


# SPECIFIC ELEMENTS

def select_time_range():
    """Selection drop down for selecting time period for statistics (not used yet)"""
    return rx.select(
        ["All time", "Last month", "Last year"],
        value=State.time_range,
        on_change=State.change_time_range,
    )


def fuel_table() -> rx.Component:
    """Fuel table of all historical fuel records"""
    return rx.data_table(data=State.fuel_records, sort=True, pagination=True)


def latest_fuel_visit_card() -> rx.Component:
    """Card with an overview of the latest (most recent) fuel record"""
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
                rx.data_list.label("Mileage"),
                rx.data_list.value(State.latest_fuel_record.mileage),
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
