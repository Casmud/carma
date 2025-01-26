import reflex as rx
from ..template import template
from ..models.company import Company
from sqlmodel import select


class State(rx.State):
    companies: list[Company] = []

    @rx.event
    def add_company(self, form_data: dict) -> None:
        with rx.session() as session:
            new_company = Company(
                friendly_name=form_data["friendly_name"],
                formal_name=form_data["formal_name"],
                address=form_data["address"],
                # Switches are only added if true, so we need to check if they are present
                is_pump=form_data.get("is_pump", False),
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
                session.exec(select(Company).order_by(Company.formal_name)).all()
            )


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
                    rx.hstack(
                        rx.text("Petrol: ", size="1"),
                        rx.switch(name="is_pump", default_checked=True),
                    ),
                    rx.hstack(
                        rx.text("Garage:", size="1"),
                        rx.switch(
                            name="is_garage",
                        ),
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
                rx.table.column_header_cell("Friendly name"),
                rx.table.column_header_cell("Formal name"),
                rx.table.column_header_cell("Address"),
                rx.table.column_header_cell("Provides"),
            ),
        ),
        rx.table.body(rx.foreach(State.companies, show_company)),
        on_mount=State.load_companies,
        width="100%",
        variant="surface",
    )


def show_company(company: Company):
    """Show a company in a table row."""
    return rx.table.row(
        rx.table.cell(company.friendly_name),
        rx.table.cell(company.formal_name),
        rx.table.cell(
            "No known address" if company.address is None else company.address
        ),
        rx.table.cell(
            rx.cond(company.is_pump, rx.badge("Pump")),
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
