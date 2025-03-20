import os
import reflex as rx

db_url = os.getenv("DB_URL")  # Default to local database

config = rx.Config(
    app_name="carma",
    db_url=db_url,
)
