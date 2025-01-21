import reflex as rx
from ..template import template
from ..models.general import Company
from sqlmodel import select

class State(rx.State):
    companies: list[Company] = []

    @rx.event
    def add_company(self, form_data: dict):
        with rx.session() as session:
            new_company = Company(friendly_name=form_data['friendly_name'],
                                     formal_name=form_data['formal_name'],
                                     address=form_data['address'])
            session.add(new_company)
            session.commit()
            self.load_companies()

    @rx.event
    def load_companies(self) -> list[Company]:
        """Get all companies from the database."""
        with rx.session() as session:
            self.companies = session.exec(
                select(Company)
            ).all()

def company_form():
    return rx.dialog.root(
            rx.dialog.trigger(rx.button("Add new company")),
            rx.dialog.content(
                rx.dialog.title("Add new company"),
                rx.form(
                    rx.vstack(
                        rx.input(
                            placeholder="Formal Name",
                            name="formal_name",
                        ),
                        rx.input(
                            placeholder="Friendly name",
                            name="friendly_name",
                        ),
                        rx.input(
                            placeholder="Address",
                            name="address",
                        ),
                        rx.dialog.close(
                            rx.button("Add", type="submit")
                        ),
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
                rx.table.column_header_cell("Friendly name"),
                rx.table.column_header_cell("Formal name"),
                rx.table.column_header_cell("Address"),
            ),
        ),
        rx.table.body(
            rx.foreach(
                State.companies, show_company
            )
        ),
        on_mount=State.load_companies,
        width="100%",
    )

def show_company(company: Company):
    """Show a company in a table row."""
    return rx.table.row(
        rx.table.cell(company.friendly_name),
        rx.table.cell(company.formal_name),
        rx.table.cell(company.address),
    )

@rx.page(route="/company", on_load=State.load_companies)
@template
def company() -> rx.Component:
    return rx.vstack(
        company_form(),
        rx.heading("Current companies:"),
        company_table()
    )