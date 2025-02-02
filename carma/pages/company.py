import reflex as rx
from ..template import template
from ..models.company import Company
from sqlmodel import select

from ..components.dialog import CreateCompanyDialog


class State(rx.State):
    companies: list[Company] = []

    @rx.event
    def load_companies(self) -> None:
        """Get all companies from the database."""
        self.companies = Company.load_companies()

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
    create_company_dialog = CreateCompanyDialog.create
    return rx.container(
        rx.vstack(
            create_company_dialog(on_close_auto_focus=State.load_companies),
            rx.heading("Current companies:"),
            company_table(),
        )
    )
