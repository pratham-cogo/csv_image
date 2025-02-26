from peewee import PostgresqlDatabase, Model
from fastapi import Depends
from contextvars import ContextVar
import time
import importlib
import pkgutil

from configs.env import DATABASE_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT

db_state_default = {"closed": None, "conn": None, "ctx": None, "transactions": None}
db_state = ContextVar("db_state", default=db_state_default.copy())

db = PostgresqlDatabase(
    DATABASE_NAME,
    user=DATABASE_USER,
    password=DATABASE_PASSWORD,
    host=DATABASE_HOST,
    port=DATABASE_PORT,
    autorollback=True,
)

def initialize_db():
    """Initialize the database and create tables for all models."""
    # from services.contacts.models.contact import Contact
    # from services.key_account_managers.models.key_account_manager import KeyAccountManager
    # from services.restaurants.models.restaurant import Restaurant
    # from services.interactions.models.interaction import Interaction

    # models = [KeyAccountManager, Restaurant, Contact, Interaction]
    from services.users.models.users import User
    from services.images.models.processed_images import ProcessedImages

    models = [User, ProcessedImages]
    try:
        db.connect(reuse_if_open=True)
        # create_tables(models)
        # print("Database initialized and tables created.")
    except Exception as e:
        print(f"Error during database initialization: {e}")
        raise
    finally:
        db.close()

async def reset_db_state():
    """Reset the database state."""
    db._state._state.set(db_state_default.copy())
    db._state.reset()

def get_db(db_state=Depends(reset_db_state)):
    """Dependency for managing database connections."""
    try:
        db.connect(reuse_if_open=True)
        yield
    finally:
        if not db.is_closed():
            db.close()

def create_tables(models):
    """Create tables for the given models."""
    try:
        with db:
            db.create_tables(models)
        print("Tables created successfully.")
    except Exception as e:
        print(f"Exception while creating tables: {e}")
        raise

def drop_tables(models):
    """Drop tables for the given models."""
    try:
        with db:
            db.drop_tables(models)
        print("Tables dropped successfully.")
    except Exception as e:
        print(f"Exception while dropping tables: {e}")
        raise
