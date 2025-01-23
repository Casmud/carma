from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime
from carma.models.general import Company
import reflex as rx


class Fuel(rx.Model, table=True):
    id: int | None = Field(default=None, primary_key=True)

    date: datetime
    milage: int
    liters: float
    price: float

    company_id: int | None = Field(default=None, foreign_key="company.id")
    company: Company = Relationship()
