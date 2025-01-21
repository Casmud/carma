import reflex as rx
from ..template import template


@rx.page(route="/")
@template
def index() -> rx.Component:
    # Order pagina
    return rx.text("Hello World")
