from sqlmodel import Field, SQLModel

class Company(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    friendly_name: str
    formal_name: str

    address: str | None = None