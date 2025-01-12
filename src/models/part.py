from sqlmodel import Field, SQLModel, Relationship
from datetime import timedelta

class PartCategoryLink(SQLModel, table=True):
    part_id: int | None = Field(default=None, foreign_key="part.id", primary_key=True)
    category_id: int | None = Field(default=None, foreign_key="company.id", primary_key=True)

class Part(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    part_name: str

    milage_interval: int | None = None
    date_interval: timedelta | None = None

    categories: list["Category"] = Relationship(back_populates="category", link_model=PartCategoryLink)

class Category(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    name: str

    parts: list["Part"] = Relationship(back_populates="part", link_model=PartCategoryLink)