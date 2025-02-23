import reflex as rx
from ..template import template
from ..components.dialog import CreateFuelRecordDialog


@rx.page(route="/")
@template
def index_page() -> rx.Component:
    # Order pagina
    create_fuel_record_dialog = CreateFuelRecordDialog.create
    return rx.vstack(rx.text("Hello World"),
                     rx.text('Quick actions'),
            create_fuel_record_dialog(rx.button("Add new fuel record from home page!")))