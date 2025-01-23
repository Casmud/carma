from sqlmodel import Field, Relationship
from datetime import datetime
from src.models.general import Company
from src.models.part import Part
import reflex as rx


class Invoice(rx.Model, table=True):
    id: int | None = Field(default=None, primary_key=True)

    date: datetime

    reference: int | None = None
    milage: int | None = None

    company_id: int | None = Field(default=None, foreign_key="company.id")
    company: Company = Relationship()

    items: list["InvoiceItem"] = Relationship(
        back_populates="invoice", cascade_delete=True
    )
    scans: list["PdfScan"] | None = Relationship(
        back_populates="invoice", cascade_delete=True
    )


class InvoiceItem(rx.Model, table=True):
    id: int | None = Field(default=None, primary_key=True)

    amount: int
    vat_rate: float
    unit_price: float

    description: str | None = None

    invoice_id: int | None = Field(
        default=None, foreign_key="invoice.id", ondelete="CASCADE"
    )
    invoice: Invoice = Relationship(back_populates="items")

    part_id: int | None = Field(default=None, foreign_key="part.id")
    part: Part = Relationship()

    def crate_invoice_item(self):
        pass


class PdfScan(rx.Model, table=True):
    id: int | None = Field(default=None, primary_key=True)

    url: str

    invoice_id: int | None = Field(default=None, foreign_key="invoice.id")
    invoice: Invoice = Relationship(back_populates="scans")
