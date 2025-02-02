import reflex as rx

from ..models.company import Company


class CreateCompanyDialog(rx.ComponentState):
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
                            rx.switch(name="is_gas_station", default_checked=True),
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
                    **props,
                    reset_on_submit=False,
                ),
            ),
        )
