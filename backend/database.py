# This file contains the database connection string for the Product Management System.

from requests import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession


SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./product_management.db"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False})

AsyncSessionLocal = sessionmaker(autocommit= False, autoflush= False,bind=engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()