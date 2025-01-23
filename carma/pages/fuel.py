import reflex as rx
from ..template import template
from ..models.fuel import Fuel
from ..models.general import Company
from sqlmodel import select
from datetime import datetime


class State(rx.State):
    fuel_records: list[Fuel] = []
    companies: list[Company] = []

    @rx.event
    def add_fuel_record(self, form_data: dict):
        with rx.session() as session:
            company = session.exec(
                select(Company).where(Company.friendly_name == form_data["company"])
            ).first()  # This is a bit janky, using the friendly name to find the company again...

            new_fuel_record = Fuel(
                date=datetime.strptime(
                    form_data["date"], "%d-%m-%Y"
                ),  # need to find a date picker
                milage=int(form_data["milage"]),
                liters=float(form_data["liters"]),
                price=float(form_data["price"]),
                company=company,
            )
            session.add(new_fuel_record)
            session.commit()
            self.load_fuel_records()

    @rx.event
    def init_fuel_page(self):
        self.load_fuel_records()
        self.load_companies()

    @rx.event
    def load_fuel_records(self) -> list[Fuel]:
        """Get all fuel items from the database."""
        with rx.session() as session:
            self.fuel_records = session.exec(select(Fuel)).all()

    @rx.event
    def load_companies(self) -> list[Company]:
        """Get all companies from the database."""
        with rx.session() as session:
            self.companies = session.exec(select(Company)).all()


def fuel_form():
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
                            rx.select.group(
                                rx.foreach(
                                    State.companies,
                                    lambda item: rx.select.item(
                                        item.friendly_name, value=item.friendly_name
                                    ),
                                )
                            ),
                        ),
                        name="company",
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
    return rx.table.root(
        rx.table.header(
            rx.table.row(
                rx.table.column_header_cell("Date"),
                rx.table.column_header_cell("Milage"),
                rx.table.column_header_cell("Liters"),
                rx.table.column_header_cell("Price"),
                rx.table.column_header_cell("Gas station (ID)"),
            ),
        ),
        rx.table.body(rx.foreach(State.fuel_records, show_fuel_item)),
        on_mount=State.load_fuel_records,
        width="100%",
    )


def show_fuel_item(item: Fuel):
    """Show a company in a table row."""
    return rx.table.row(
        rx.table.cell(rx.moment(item.date)),
        rx.table.cell(item.milage),
        rx.table.cell(item.liters),
        rx.table.cell(item.price),
        rx.table.cell(item.company_id),  # item.company.friendly name is not working...
    )


@rx.page(route="/fuel", on_load=State.init_fuel_page)
@template
def fuel_page() -> rx.Component:
    return rx.container(
        rx.vstack(fuel_form(), rx.heading("Historical fuel records:"), fuel_table())
    )
