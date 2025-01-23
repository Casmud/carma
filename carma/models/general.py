from sqlmodel import Field
import reflex as rx


class Company(rx.Model, table=True):
    id: int | None = Field(default=None, primary_key=True)

    friendly_name: str
    formal_name: str

    address: str | None = None
