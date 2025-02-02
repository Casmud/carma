import reflex as rx
from ..template import template
from ..models.company import Company
from sqlmodel import select

from ..components.dialog import CreateCompanyDialog


class State(rx.State):
    companies: list[Company] = []

    @rx.event
    def add_company(self, form_data: dict):
        form_data["is_gas_station"] = form_data.get("is_gas_station", False)
        form_data["is_garage"] = form_data.get("is_garage", False)
        Company.add_company(**form_data)
        self.load_companies()

    @rx.event
    def load_companies(self) -> None:
        """Get all companies from the database."""
        with rx.session() as session:
            self.companies = list(
                session.exec(select(Company).order_by(Company.name)).all()
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

create_company_dialog = CreateCompanyDialog.create


@rx.page(route="/company", on_load=State.load_companies)
@template
def company_page() -> rx.Component:
    return rx.container(
        rx.vstack(
            create_company_dialog(on_submit=State.add_company),
            rx.heading("Current companies:"),
            company_table(),
        )
    )
