from typing import Callable

import reflex as rx

from .components.sidebar import sidebar


def template(page: Callable[[], rx.Component]) -> rx.Component:
    return rx.hstack(
        sidebar(),
        page(),
        width="100%",
        height="100%",
    )
