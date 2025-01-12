from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime

class Invoice(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    date: datetime

    reference: int | None = None
    milage: int | None = None

    company_id: int | None = Field(default=None, foreign_key="company.id")
    items: list["InvoiceItem"] = Relationship(back_populates="invoiceitem", cascade_delete=True)
    scans: list["PdfScan"] = Relationship(back_populates="pdfscan", cascade_delete=True)

class InvoiceItem(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    amount: int
    vat_rate: float
    unit_price: float

    description: str | None = None

    invoice_id: int | None = Field(default=None, foreign_key="invoice.id", ondelete="CASCADE")
    part_id: int | None = Field(default=None, foreign_key="part.id")

class PdfScan(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    url: str

    invoice_id: int | None = Field(default=None, foreign_key="invoice.id")