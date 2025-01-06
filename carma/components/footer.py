import reflex as rx

def footer() -> rx.Component:
    return rx.hstack(
            # The logo.
            rx.logo(),
        rx.text('Copyright 2025'),
            align="center",
            width="100%",
            padding_y="1.25em",
            padding_x=["1em", "1em", "2em"],
        )