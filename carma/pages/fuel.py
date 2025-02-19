from typing import Dict

import reflex as rx
import pandas as pd
from ..template import template
from ..models.fuel import Fuel
from ..models.company import Company
from sqlmodel import select
from datetime import datetime

import reflex_chakra as rc

from ..components.dialog import CreateCompanyDialog


class State(rx.State):
    fuel_records: pd.DataFrame
    companies: Dict[str, Company] = {}
    time_range: str = "All time"

    @rx.event
    def change_time_range(self, range: str):
        """Change the select value var."""
        self.time_range = range

    @rx.event
    def add_fuel_record(self, form_data: dict):
        with rx.session() as session:
            new_fuel_record = Fuel(
                date=datetime.strptime(form_data["date"], "%Y-%m-%d"),
                milage=int(form_data["milage"]),
                liters=float(form_data["liters"]),
                price=float(form_data["price"]),
                company_id=float(form_data["company"]),
            )
            session.add(new_fuel_record)
            session.commit()
            self.load_fuel_records()

    @rx.event
    def init_fuel_page(self):
        self.load_fuel_records()
        self.load_companies()

    @rx.event
    def load_fuel_records(self) -> pd.DataFrame:
        """Get all fuel items from the database."""
        with rx.session() as session:
            fuel_records = session.exec(select(Fuel)).all()
        fuel_records_df = pd.DataFrame([vars(fuel_record) for fuel_record in fuel_records])
        self.fuel_records = fuel_records_df[["date","milage"]]



    @rx.event
    def load_companies(self) -> list[Company]:
        """Get all companies from the database."""
        with rx.session() as session:
            companies = session.exec(select(Company)).all()
            self.companies = {str(company.id): company for company in companies}

def select_time_range():
    return rx.center(
        rx.select(
            ["All time", "Last month", "Last year"],
            value=State.time_range,
            on_change=State.change_time_range,
        ),
        rx.badge(State.time_range),
    )

def fuel_form():
    create_company_dialog = CreateCompanyDialog.create
    return rx.dialog.root(
        rx.dialog.trigger(rx.button("Add new fuel record")),
        rx.dialog.content(
            rx.dialog.title("Add new fuel record"),
            create_company_dialog(rx.button("Add new company in fuel page!")),
            rx.form(
                rx.vstack(
                    rc.input(type_="date", name="date"),
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
                on_submit=State.add_fuel_record,
                reset_on_submit=False,
            ),
        ),
    )


def fuel_table():
    return rx.data_table(
        data = State.fuel_records,
    )
    # return rx.table.root(
    #     rx.table.header(
    #         rx.table.row(
    #             rx.table.column_header_cell("Date"),
    #             rx.table.column_header_cell("Milage"),
    #             rx.table.column_header_cell("Liters"),
    #             rx.table.column_header_cell("Price"),
    #             rx.table.column_header_cell("Gas station (ID)"),
    #         ),
    #     ),
    #     rx.table.body(rx.foreach(State.fuel_records, show_fuel_item)),
    #     on_mount=State.load_fuel_records,
    #     width="100%",
    # )


def show_fuel_item(item: Fuel):
    """Show a company in a table row."""
    return rx.table.row(
        rx.table.cell(rx.moment(item.date)),
        rx.table.cell(item.milage),
        rx.table.cell(item.liters),
        rx.table.cell(item.price),
        rx.table.cell(
            item.company.name
        ),  # item.company.friendly name is not working...
    )


@rx.page(route="/fuel", on_load=State.init_fuel_page)
@template
def fuel_page() -> rx.Component:
    return rx.container(
        rx.vstack(
            select_time_range(),
            fuel_form(),
            rx.heading("Historical fuel recordsss:")),
        fuel_table()
    )
