from sqlmodel import Field, SQLModel
from datetime import datetime

class Fuel(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    date: datetime
    milage: int
    price: float

    company_id: int | None = Field(default=None, foreign_key="company.id")