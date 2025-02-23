from datetime import datetime

import reflex as rx
from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, Relationship  # noqa: F401


class CarmaBase(rx.Model):
    # This is the base class for all models in the project
    # It is used to add common fields to all database tables
    # The timestamp fields are set by the database; we use Column for that.
    link_table = bool

    inserted_at: datetime | None = Field(sa_column=Column(DateTime, server_default=func.now()))
    updated_at: datetime | None = Field(sa_column=Column(DateTime, server_default=func.now(), onupdate=func.now()))
