from typing import Callable

import reflex as rx

from .components.navbar import navbar
from .components.sidebar import sidebar
from .components.footer import footer

def template(
    page: Callable[[], rx.Component]
) -> rx.Component:
    return rx.hstack(
        sidebar(),
        page(),
        width="100%",
        height="100%",
    )
