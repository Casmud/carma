import logging

import reflex as rx

from ..models.company import Company

class CreateCompanyDialog(rx.ComponentState):

    @rx.event
    def validate_and_add_company(self, form_data: dict):
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
    def get_component(cls, **props):
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
                            rx.text("Gas Station: ", size="1"),
                            rx.switch(id="is_gas_station", default_checked=True),
                        ),
                        rx.hstack(
                            rx.text("Garage:", size="1"),
                            rx.switch(
                                id="is_garage",
                            ),
                        ),
                        rx.input(
                            placeholder="Address",
                            name="address",
                        ),
                        rx.dialog.close(rx.button("Add", type="submit")),
                    ),
                    reset_on_submit=False,
                    on_submit=cls.validate_and_add_company,
                )
            ,**props)
        )

