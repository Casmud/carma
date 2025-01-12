import os
from .models import fuel, part, invoice, general
from sqlmodel import SQLModel, create_engine

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, echo=False)

def create_db_and_tables(debug=False):
    engine.echo = debug
    SQLModel.metadata.create_all(engine)

def delete_db():
    if os.path.exists(sqlite_file_name):
        os.remove(sqlite_file_name)
        print(f"Database file '{sqlite_file_name}' deleted.")
    else:
        print("Database file does not exist.")

if __name__ == "__main__":
    create_db_and_tables(debug = True)