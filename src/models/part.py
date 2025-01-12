from sqlmodel import Field, SQLModel, Relationship
from datetime import timedelta

class PartCategoryLink(SQLModel, table=True):
    part_id: int | None = Field(default=None, foreign_key="part.id", primary_key=True)
    category_id: int | None = Field(default=None, foreign_key="category.id", primary_key=True)

class Part(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    name: str

    milage_interval: int | None = None
    date_interval: timedelta | None = None

    categories: list["Category"] | None = Relationship(back_populates="parts", link_model=PartCategoryLink)

class Category(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    name: str

    parts: list["Part"] | None = Relationship(back_populates="categories",link_model=PartCategoryLink)