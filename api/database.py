"""Functions to connect to the database."""
import databases
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

from .utils import get_settings


settings = get_settings()

database = databases.Database(settings.database_url)

engine = create_engine(settings.database_url, connect_args={"check_same_thread": False}, echo=True)

Base = declarative_base()
