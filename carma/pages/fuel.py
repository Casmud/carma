from datetime import datetime
from typing import Any

import reflex as rx
from sqlmodel import select

from ..models.company import Company
from ..models.fuel import Fuel
from ..template import template

FuelDisplay = dict[str, Any]


class State(rx.State):
    fuel_records: list[FuelDisplay] = []
    pumps: list[Company] = []

    @rx.event
    def add_fuel_record(self, form_data: dict) -> None:
        with rx.session() as session:
            company = session.exec(
                select(Company)
                .where(Company.friendly_name == form_data["company"])
                .order_by(Company.friendly_name)
            ).first()
            # TODO This is a bit janky, using the friendly name to find the company again...
            # Gijs: need to think of a solution. Haven't found one yet.
            assert company is not None, f"Company {form_data['company']} not found"

            new_fuel_record = Fuel(
                date=datetime.strptime(
                    form_data["date"], "%d-%m-%Y"
                ),  # need to find a date picker
                # TODO check out https://pypi.org/project/reflex-calendar/
                # and https://github.com/Lendemor/reflex-calendar
                # Demo at: https://projects.wojtekmaj.pl/react-calendar/
                kilometrage=int(form_data["kilometrage"]),
                liters=float(form_data["liters"]),
                price=float(form_data["price"]),
                company=company,
            )
            session.add(new_fuel_record)
            session.commit()
            self.load_fuel_records()

    @rx.event
    def init_fuel_page(self) -> None:
        self.load_fuel_records()
        self.load_pumps()

    @rx.event
    def load_fuel_records(self) -> None:
        """Get all fuel items from the database."""
        with rx.session() as session:
            self.fuel_records = [
                fuel_item.model_dump()
                | {"company_name": fuel_item.company.friendly_name}
                for fuel_item in session.exec(select(Fuel)).all()
            ]

    @rx.event
    def load_pumps(self) -> None:
        """Get all pumps from the database."""
        with rx.session() as session:
            self.pumps = list(
                session.exec(
                    select(Company)
                    .where(Company.is_pump)
                    .order_by(Company.friendly_name)
                ).all()
            )


# TODO Needs validation.  See: https://reflex.dev/docs/library/forms/form/low/#final-example
def fuel_form() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(rx.button("Add new fuel record")),
        rx.dialog.content(
            rx.dialog.title("Add new fuel record"),
            rx.form(
                rx.vstack(
                    rx.input(
                        placeholder="Date",
                        name="date",
                    ),
                    rx.select.root(
                        rx.select.trigger(placeholder="Select gas station"),
                        rx.select.content(
                            rx.foreach(
                                State.pumps,
                                lambda item: rx.select.item(
                                    item.friendly_name, value=item.friendly_name
                                ),
                            )
                        ),
                        name="company",
                    ),
                    rx.input(
                        placeholder="km",
                        name="kilometrage",
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
    return rx.table.root(
        rx.table.header(
            rx.table.row(
                rx.table.column_header_cell("Date"),
                rx.table.column_header_cell("Kilometers"),
                rx.table.column_header_cell("Liters"),
                rx.table.column_header_cell("Price"),
                rx.table.column_header_cell("Gas station"),
            ),
        ),
        rx.table.body(rx.foreach(State.fuel_records, show_fuel_item)),
        on_mount=State.load_fuel_records,
        width="100%",
        variant="surface",
    )


def show_fuel_item(item: FuelDisplay) -> rx.Component:
    """Show a company in a table row."""
    return rx.table.row(
        rx.table.cell(item["date"]),
        rx.table.cell(item["kilometrage"]),
        rx.table.cell(item["liters"]),
        rx.table.cell(item["price"]),
        rx.table.cell(item["company_name"]),
    )


@rx.page(route="/fuel", on_load=State.init_fuel_page)
@template
def fuel_page() -> rx.Component:
    return rx.container(
        rx.vstack(fuel_form(), rx.heading("Historical fuel records:"), fuel_table()),
    )
