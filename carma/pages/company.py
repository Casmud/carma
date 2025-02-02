import reflex as rx
from ..template import template
from ..models.company import Company
from sqlmodel import select


class State(rx.State):
    companies: list[Company] = []

    @rx.event
    def add_company(self, form_data: dict):
        with rx.session() as session:
            new_company = Company(
                name=form_data["name"],
                address=form_data["address"],
                is_gas_station=form_data.get("is_fuel_station", False),
                is_garage=form_data.get("is_garage", False),
            )
            session.add(new_company)
            session.commit()
            self.load_companies()

    @rx.event
    def load_companies(self) -> None:
        """Get all companies from the database."""
        with rx.session() as session:
            self.companies = list(
                session.exec(select(Company).order_by(Company.name)).all()
            )


def company_form():
    return rx.dialog.root(
        rx.dialog.trigger(rx.button("Add new company")),
        rx.dialog.content(
            rx.dialog.title("Add new company"),
            rx.form(
                rx.vstack(
                    rx.input(
                        placeholder="Name",
                        name="name",
                    ),
                    rx.hstack(
                        rx.text("Fuel Station: ", size="1"),
                        rx.switch(name="is_fuel_station", default_checked=True),
                    ),
                    rx.hstack(
                        rx.text("Garage:", size="1"),
                        rx.switch(
                            name="is_garage",
                        ),
                    ),
                    rx.input(
                        placeholder="Address",
                        name="address",
                    ),
                    rx.dialog.close(rx.button("Add", type="submit")),
                ),
                on_submit=State.add_company,
                reset_on_submit=False,
            ),
        ),
    )


def company_table():
    return rx.table.root(
        rx.table.header(
            rx.table.row(
                rx.table.column_header_cell("Name"),
                rx.table.column_header_cell("Address"),
                rx.table.column_header_cell("Services"),
            ),
        ),
        rx.table.body(rx.foreach(State.companies, show_company)),
        on_mount=State.load_companies,
        width="100%",
    )


def show_company(company: Company):
    """Show a company in a table row."""
    return rx.table.row(
        rx.table.cell(company.name),
        rx.table.cell(
            "No known address" if company.address is None else company.address
        ),
        rx.table.cell(
            rx.cond(company.is_gas_station, rx.badge("Gas Station")),
            rx.cond(company.is_garage, rx.badge("Garage")),
        ),
    )


@rx.page(route="/company", on_load=State.load_companies)
@template
def company_page() -> rx.Component:
    return rx.container(
        rx.vstack(
            company_form(),
            rx.heading("Current companies:"),
            company_table(),
        )
    )
