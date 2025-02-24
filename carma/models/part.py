from datetime import timedelta

import reflex as rx
from sqlmodel import Field, Relationship

from carma.models.base import CarmaBase


class PartCategoryLink(rx.Model, table=True):
    part_id: int | None = Field(default=None, foreign_key="part.id", primary_key=True)
    category_id: int | None = Field(default=None, foreign_key="category.id", primary_key=True)


class Part(CarmaBase, table=True):
    name: str

    mileage_interval: int | None = None
    date_interval: timedelta | None = None

    categories: list["Category"] | None = Relationship(back_populates="parts", link_model=PartCategoryLink)


class Category(CarmaBase, table=True):
    name: str

    parts: list["Part"] | None = Relationship(back_populates="categories", link_model=PartCategoryLink)
