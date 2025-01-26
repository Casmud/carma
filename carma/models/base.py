from datetime import datetime

import reflex as rx
from sqlmodel import Field, Relationship  # noqa: F401
from sqlalchemy import Column, DateTime, func


class CarmaBase(rx.Model):
    # This is the base class for all models in the project
    # It is used to add common fields to all database tables
    # The timestamp fields are set by the database; we use Column for that.
    id: int | None = Field(default=None, primary_key=True)
    inserted_at: datetime | None = Field(
        sa_column=Column(DateTime, server_default=func.now())
    )
    updated_at: datetime | None = Field(
        sa_column=Column(DateTime, server_default=func.now(), onupdate=func.now())
    )
