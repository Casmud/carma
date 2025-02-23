import csv
from datetime import datetime

import reflex as rx

from carma.models.company import Company
from carma.models.fuel import Fuel

from ..template import template


class State(rx.State):
    @rx.event
    def add_company_data(self) -> None:
        # Read the CSV file and add records to the database
        with open("assets/mock_company_data.csv") as file:
            reader = csv.DictReader(file)
            for row in reader:
                name = str(row["name"])
                address = str(row["address"])
                is_garage = bool(row["is_garage"])
                is_gas_station = bool(row["is_gas_station"])

                Company.add_company(
                    name=name,
                    address=address,
                    is_garage=is_garage,
                    is_gas_station=is_gas_station,
                )

    @rx.event
    def add_fuel_data(self) -> None:
        # Read the CSV file and add records to the database
        with open("assets/mock_fuel_data.csv") as file:
            reader = csv.DictReader(file)
            for row in reader:
                date = datetime.strptime(row["date"], "%m/%d/%Y")
                milage = int(row["mileage"])
                liters = float(row["liters"])
                price = float(row["price"])
                company_id = int(row["company_id"])

                Fuel.add_fuel_record(
                    date=date,
                    milage=milage,
                    liters=liters,
                    price=price,
                    company=company_id,
                )


@rx.page(route="/mock_data")
@template
def mock_data_page() -> rx.Component:
    # Order pagina
    return rx.vstack(
        rx.button(
            "Add company mock data to db",
            color_scheme="grass",
            on_click=State.add_company_data,
        ),
        rx.button(
            "Add fuel mock data to db",
            color_scheme="grass",
            on_click=State.add_fuel_data,
        ),
    )
