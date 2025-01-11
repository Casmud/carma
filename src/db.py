from datetime import datetime

from sqlmodel import Field, SQLModel, create_engine


class Invoice(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    date: datetime
    company_id: int
    reference: str

class Company(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    friendly_name: str
    full_name: str
    adress: str

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True)

SQLModel.metadata.create_all(engine)