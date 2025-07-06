from operator import index
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String)
    price = Column(Float)
    category = Column(String)
    stock = Column(Integer)
    sku = Column(String, unique=True)
    supplier_id = Column(Integer, ForeignKey('suppliers.id'), nullable=True)
    status = Column(String)

class Supplier(Base):
    __tablename__ = 'suppliers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    contact_info = Column(String)
    address = Column(String)
    phone_number = Column(String)
    email = Column(String)

