from datetime import datetime

import reflex as rx
import reflex_chakra as rc
from sqlmodel import select

from ..models.company import Company
from ..models.fuel import Fuel


def dialog_header(title: str, sub_title: str, icon: str, color_scheme: str) -> rx.Component:
    """Template header for pop-up dialogs

    Parameters
    ----------
    title: Title of the dialog
    sub_title: Subtitle of the dialog
    icon: Icon (see https://reflex.dev/docs/library/data-display/icon/)
    color_scheme:

    Returns
    -------

    """
    return rx.box(
        rx.hstack(
            rx.badge(
                rx.icon(tag=icon, size=32),
                color_scheme=color_scheme,
                radius="full",
                padding="0.65rem",
            ),
            rx.vstack(
                rx.heading(
                    title,
                    size="4",
                    weight="bold",
                ),
                rx.text(
                    sub_title,
                    size="2",
                ),
                spacing="1",
                height="100%",
                align_items="start",
            ),
            height="100%",
            spacing="4",
            align_items="center",
            width="100%",
        )
    )


class CreateCompanyDialog(rx.ComponentState):
    @rx.event
    def validate_and_add_company(self, form_data: dict):
        """Validates the form input before submitting to database

        Parameters
        ----------
        form_data

        """
        valid = True
        existing_name = any(company.name == form_data["name"] for company in Company.load_companies())
        if existing_name:
            valid = False
            yield rx.toast.error("Name already exists!")
        if form_data["name"] == "":
            valid = False
            yield rx.toast.error("Name cannot be empty!")
        if form_data["is_gas_station"] is False and form_data["is_garage"] is False:
            valid = False
            yield rx.toast.error("At least one option should be selected!")
        if valid is True:
            Company.add_company(**form_data)
            yield rx.toast.success("Successfully added company {}".format(form_data["name"]))

    @classmethod
    def get_component(cls, *children, **props):
        """Creates reflex dialog component to add new company to the database

        Parameters
        ----------
        children: Used to pass a trigger for opening the dialog
        props: Can be used to pass additional properties to the dialog (for example on_close_auto_focus event)

        Returns
        -------

        """
        return rx.dialog.root(
            rx.dialog.trigger(*children),
            rx.dialog.content(
                rx.flex(
                    rx.vstack(
                        dialog_header(
                            title="Add new company",
                            sub_title="Companies can be used for registering maintenance (garage) and/or fuel records "
                                      "(gas station)",
                            icon="building-2",
                            color_scheme="mint",
                        ),
                        rx.form(
                            rx.flex(
                                rx.vstack(
                                    rx.text("Company Name"),
                                    rx.input(placeholder="Name", name="name", width="400px"),
                                ),
                                rx.vstack(
                                    rx.text("Type of facility"),
                                    rx.hstack(
                                        rx.checkbox(
                                            id="is_gas_station",
                                            default_checked=True,
                                            text="Gas Station",
                                        ),
                                        rx.checkbox(
                                            id="is_garage",
                                            text="Garage",
                                        ),
                                    ),
                                ),
                                rx.vstack(
                                    rx.text("Address details"),
                                    rx.input(
                                        placeholder="Address",
                                        name="address",
                                        width="400px",
                                    ),
                                ),
                                rx.dialog.close(rx.button("Add company", type="submit", width="400px")),
                                direction="column",
                                align="center",
                                spacing="2",
                            ),
                            reset_on_submit=False,
                            on_submit=cls.validate_and_add_company,
                        ),
                    )
                ),
                **props,
            ),
        )


class CreateFuelRecordDialog(rx.ComponentState):
    companies: dict[str, Company] = {}

    @rx.event
    def load_companies(self):
        """Load all companies in dict format {company_id: Company Object}. used for value/text select"""
        with rx.session() as session:
            companies = session.exec(select(Company)).all()
            self.companies = {str(company.id): company for company in companies}

    @rx.event
    def validate_and_add_fuel_record(self, form_data: dict):
        """Validates the form input before submitting to database.

        Parameters
        ----------
        form_data

        """
        if "liters" not in form_data:
            # check for nested dialog forms, if event is triggered for actually validation of fuel data
            pass
        else:
            valid = True
            with rx.session() as session:
                results = session.exec(select(Fuel))
                fuel_records = results.all()

            # Validate input
            if form_data["mileage"] == "":
                yield rx.toast.error("Mileage cannot be empty")
                valid = False
            elif int(form_data["mileage"]) < 0:
                yield rx.toast.error("Mileage cannot be negative")
                valid = False
            if form_data["price"] == "":
                yield rx.toast.error("Price cannot be empty")
                valid = False
            elif float(form_data["price"]) <= 0:
                yield rx.toast.error("Price cannot be negative")
                valid = False
            if form_data["company"] == "":
                yield rx.toast.error("Company cannot be empty")
                valid = False

            # Validate logic (with respect to existing data)
            df_fuel_records = Fuel.process_fuel_to_df(fuel_records)
            new_date = datetime.strptime(form_data["date"], "%Y-%m-%dT%H:%M")

            if new_date in df_fuel_records.index:
                yield rx.toast.error("Already a record in database for this exact moment.")
                valid = False

            # Check if previous (date) record is lower
            previous_dates = df_fuel_records.index[df_fuel_records.index < new_date]
            if not previous_dates.empty:
                previous_mileage = df_fuel_records.loc[previous_dates[-1], "Mileage"]
                if int(form_data["mileage"]) < previous_mileage:
                    yield rx.toast.error("Mileage must be greater than the previous recorded mileage.")
                    valid = False

            # Check if next (date) record is higher
            next_dates = df_fuel_records.index[df_fuel_records.index > new_date]
            if not next_dates.empty:
                next_mileage = df_fuel_records.loc[next_dates[0], "Mileage"]
                if int(form_data["mileage"]) > next_mileage:
                    yield rx.toast.error("Mileage must be less than the next recorded mileage.")
                    valid = False

            if valid is True:
                Fuel.add_fuel_record(
                    date=form_data["date"],
                    mileage=form_data["mileage"],
                    liters=form_data["liters"],
                    price=form_data["price"],
                    company=form_data["company"],
                )
                yield rx.toast.success("Fuel record added")

    @classmethod
    def get_component(cls, *children, **props):
        """Creates nested reflex dialog component to add new fuel record to the database. The dialog includes a button
        to add a new company as well.

        Parameters
        ----------
        children: Used to pass a trigger for opening the dialog
        props: Can be used to pass additional properties to the dialog (for example on_close_auto_focus event)

        Returns
        -------

        """
        create_company_dialog = CreateCompanyDialog.create

        return rx.dialog.root(
            rx.dialog.trigger(*children),
            rx.dialog.content(
                rx.flex(
                    rx.vstack(
                        dialog_header(
                            title="Add new fuel record",
                            sub_title="Fill details on fuel station visit below",
                            icon="fuel",
                            color_scheme="orange",
                        ),
                        rx.form(
                            rx.vstack(
                                rx.vstack(
                                    rx.text("Time of visit"),
                                    rc.input(
                                        type_="datetime-local",
                                        name="date",
                                        default_value=datetime.now().strftime("%Y-%m-%dT%H:%M"),
                                    ),
                                ),
                                rx.vstack(
                                    rx.text("Location"),
                                    rx.hstack(
                                        rx.select.root(
                                            rx.select.trigger(placeholder="Select gas station"),
                                            rx.select.content(
                                                rx.foreach(
                                                    cls.companies.items(),
                                                    lambda item: rx.select.item(
                                                        item[1].name,
                                                        value=item[0],
                                                    ), #TODO: I already spend too much time on this, is there not a neater way to do this?
                                                )
                                            ),
                                            name="company",
                                            on_open_change=cls.load_companies,
                                        ),
                                        create_company_dialog(rx.button("New Gas Station")),
                                    ),
                                ),
                                rx.vstack(
                                    rx.text("Mileage"),
                                    rc.number_input(
                                        name="mileage",
                                    ),
                                ),
                                rx.vstack(
                                    rx.text("Liters"),
                                    rx.input(
                                        name="liters",
                                    ),
                                ),
                                rx.vstack(
                                    rx.text("Price"),
                                    rx.input(
                                        name="price",
                                    ),
                                ),
                                rx.dialog.close(rx.button("Add fuel record", type="submit", width="400px")),
                                direction="column",
                                align="center",
                                spacing="2",
                            ),
                            reset_on_submit=False,
                            on_submit=cls.validate_and_add_fuel_record,
                        ),
                    )
                ),
                **props,
            ),
        )
