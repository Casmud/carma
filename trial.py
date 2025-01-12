from datetime import datetime, timedelta

from src.db import create_db_and_tables, engine

from src.models.general import Company
from src.models.part import Part, Category
from src.models.invoice import Invoice, InvoiceItem, PdfScan

from sqlmodel import Session, select

def add_invoice_1():
    with Session(engine) as session:
        lexus_den_haag = Company(friendly_name='Lexus Den Haag', formal_name='Louwman Lexus Den Haag B.V.', address="Hoofdweg 1, Den Haag")

        part1 = Part(name="Olie", milage_interval="10000", categories = [Category(name="Olie"),Category(name="Vloeistof")])
        part2 = Part(name="APK", date_interval=timedelta(days=365), categories=[Category(name="APK"), Category(name="Onderhoud")])

        item1 = InvoiceItem(amount=1,vat_rate=1.0,unit_price=10,part=part1, description="5W40")
        item2 = InvoiceItem(amount=1,vat_rate=1.0,unit_price=35,part=part2, description="gratis wintercheck")

        invoice1 = Invoice(date=datetime.now(), reference="#ref123", milage="10165", company=lexus_den_haag, items=[item1, item2])

        session.add(invoice1)
        session.commit()

def add_invoice_2():
    with Session(engine) as session:
        lexus_den_haag = Company(friendly_name='Vakgarage Merelstraat', formal_name='BOVAG Vakgarage Merelstraat 1 VOF', address="Merelstraat 1, Sliedrecht")

        part1 = Part(name="Band", milage_interval="70000", categories = [Category(name="Banden")])

        item1 = InvoiceItem(amount=4,vat_rate=1.21,unit_price=75,part=part1, description="Michelin  AllSeason")

        scan1 = PdfScan(url='fakepath/factuur.pdf')

        invoice1 = Invoice(date=datetime.now(), reference="#re7700", milage="10765", company=lexus_den_haag, items=[item1], scans=[scan1])

        session.add(invoice1)
        session.commit()

def delete_invoice(ref):
    with Session(engine) as session:
        statement = select(Invoice).where(Invoice.reference == ref)
        result = session.exec(statement)
        invoice = result.one()
        session.delete(invoice)
        session.commit()

create_db_and_tables(debug=True)
add_invoice_1()
add_invoice_2()
# delete_invoice(ref="#ref123")
# delete_invoice(ref="#re7700")




