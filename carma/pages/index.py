import reflex as rx
from ..template import template


@rx.page(route="/")
@template
def index() -> rx.Component:
    # Order pagina
    return rx.container(
        rx.vstack(
            rx.hstack(
                rx.card(
                    rx.data_list.root(
                        rx.data_list.item(
                            rx.data_list.value(rx.text.strong("Lexus Den Haag"))),
                        rx.data_list.item(
                            rx.data_list.label("Datum"),
                            rx.data_list.value("10-07-2021"),
                        ),
                        rx.data_list.item(
                            rx.data_list.label("KM-Stand"),
                            rx.data_list.value("307.048"),
                            align="center",
                        ),
                    ),
                ),
                rx.spacer(),
                rx.avatar(fallback="DW"),
                width="100%"),
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Aantal"),
                        rx.table.column_header_cell("Categorie"),
                        rx.table.column_header_cell("Omschrijving"),
                        rx.table.column_header_cell("Prijs"),
                        rx.table.column_header_cell("BTW"),
                        rx.table.column_header_cell("Totaal"),
                    ),
                ),
                rx.table.body(
                    rx.table.row(
                        rx.table.cell("1"),
                        rx.table.cell(rx.badge("Remmen")),
                        rx.table.cell("Remvloeistof"),
                        rx.table.cell("€ 70"),
                        rx.table.cell("19%"),
                        rx.table.cell("€ 70"),
                    ),
                    rx.table.row(
                        rx.table.cell("1"),
                        rx.table.cell(rx.badge("Remmen"), rx.badge("Olie")),
                        rx.table.cell(rx.text.strong("Remvloeistof")),
                        rx.table.cell("€ 70"),
                        rx.table.cell("19%"),
                        rx.table.cell("€ 70"),
                    ),
                    rx.table.row(
                        rx.table.cell("1"),
                        rx.table.cell(rx.badge("Remmen")),
                        rx.table.cell("Remvloeistof"),
                        rx.table.cell("€ 70"),
                        rx.table.cell("19%"),
                        rx.table.cell("€ 70"),
                    ),
                ),
                rx.table.header(
                    rx.table.row(
                        rx.table.cell(col_span=4),
                        rx.table.column_header_cell("BTW"),
                        rx.table.column_header_cell("€ 70"),
                    ),
                ),
                rx.table.header(
                    rx.table.row(
                        rx.table.cell(col_span=4),
                        rx.table.column_header_cell("Totaal"),
                        rx.table.column_header_cell("€ 870"),
                    ),
                ),
                width="100%",
                variant="surface"
            )

        ))
