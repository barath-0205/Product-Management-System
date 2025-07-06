from hmac import new
from random import sample
import stat
from typing import Annotated, Optional

from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
import model
from model import Product, Supplier, User
from database import SessionLocal, engine
from sqlalchemy.orm import Session
from starlette import status
from pydantic import Field
import auth
from auth import hash_password

app = FastAPI()

model.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

user_dependency = Annotated[str, Depends(auth.get_current_user)]

db_dependency = Annotated[Session, Depends(get_db)]

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class ProductData():
    id: Optional[int] = None
    name: str
    price: float
    category: str
    stock: int
    sku: str
    supplier_id: int
    status: str

    def __init__(self, id: Optional[int], name, category, price, stock=0, sku=None, supplier_id=None, status=None):
        self.id = id
        self.name = name
        self.price = price
        self.category = category
        self.stock = stock
        self.sku = sku
        self.supplier_id = supplier_id
        self.status = status

class ProductModel(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    category: str = Field(..., min_length=1, max_length=100)
    price: float = Field(...)
    stock: int = Field(..., gt=0, le=1000)
    sku: str = Field(..., min_length=1, max_length=100)
    supplier_id: int = Field(..., gt=0, le=1000)
    status: str = Field(..., min_length=1, max_length=100)

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Sample Product",
                "category": "Electronics",
                "price": 99.99,
                "stock": 10,
                "sku": "SP12345",
                "supplier_id": 1,
                "status": "available"
            }
        }
    }

class SupplierData():
    id: Optional[int] = None
    name: str
    contact_info: str
    address: str
    phone_number: str
    email: str

    def __init__(self, id, name, contact_info, address, phone_number, email):
        self.id = id
        self.name = name
        self.contact_info = contact_info
        self.address = address
        self.phone_number = phone_number
        self.email = email

class SupplierModel(BaseModel):
    name: str
    contact_info: str
    address: str
    phone_number: str
    email: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Sample Supplier",
                "contact_info": "123-456-7890",
                "address": "123 Sample St, Sample City, SC 12345",
                "phone_number": "123-456-7890",
                "email": "abc@gmail.com"
            }
        }
    }

@app.post("/register")
def register(user: UserLogin, db: Session = Depends(get_db)):
    hashed_pw = hash_password(user.password)
    db_user = User(email=user.email, hashed_password=hashed_pw)
    db.add(db_user)
    db.commit()
    return {"message": "User registered successfully"}

@app.get("/users", status_code=status.HTTP_200_OK)
def get_users(db: db_dependency):
    users = db.query(User).all()
    return users

@app.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not auth.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = auth.create_access_token({"sub": db_user.email})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/products", status_code=status.HTTP_200_OK)
async def get_products(db: db_dependency, user: user_dependency):
    products = db.query(Product).all()
    return products

@app.get("/suppliers")
async def get_suppliers(db: db_dependency):
    suppliers = db.query(Supplier).all()
    return suppliers

@app.post("/createProduct", status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductModel, db: db_dependency, user: user_dependency):
    try:
        new_product = Product(**product.model_dump())
        db.add(new_product)
        db.commit()
        db.refresh(new_product)
        return new_product
    except Exception as e:
        db.rollback()
        print("DB Error:", e)  # You can replace with proper logging
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/createSupplier", response_model=SupplierModel)
async def create_supplier(supplier: SupplierModel, db: db_dependency, user: user_dependency):
    new_supplier = Supplier(
        name=supplier.name,
        contact_info=supplier.contact_info,
        address=supplier.address,
        phone_number=supplier.phone_number,
        email=supplier.email
    )
    db.add(new_supplier)
    db.commit()
    db.refresh(new_supplier)
    supplierData = db.query(Supplier).all()
    if supplierData is not None:
        return {"update": "Data inserted successfully", "data" : supplierData}

@app.put("/updateProduct/{product_id}", response_model=ProductModel)
async def update_product(product_id: int, updated_product: ProductModel, db: db_dependency, user: user_dependency):
    product_model = db.query(Product).filter(Product.id == product_id).first()
    if product_model is None:
        raise HTTPException(status_code=404, detail="Product not found")

    for key, value in updated_product.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(product_model, key, value)

    db.commit()
    db.refresh(product_model)
    productData = db.query(Product).all()
    return {"update": "Data updated successfully", "data" : productData}

@app.put("/updateSupplier/{supplier_id}")
async def update_supplier(supplier_id: int, updated_supplier: SupplierModel, db: db_dependency):
    supplier_model = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if supplier_model is None:
        raise HTTPException(status_code=404, detail= "Supplier not found")

    for key, value in update_supplier.model_dump(exclude_unset=True).items():
        setattr(supplier_model, key, value)

    db.commit()
    db.refresh(supplier_model)
    supplier_data = db.query(Supplier).all()
    return {"update": "Data updated successfully", "data" : supplier_data}

@app.delete("/deleteProduct/{product_id}")
async def delete_product(product_id: int, db: db_dependency):
    product_model = db.query(Product).filter(Product.id == product_id).first()
    if product_model is None:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product_model)
    db.commit()
    productData = db.query(Product).all()
    return  {"update": "Data deleted successfully", "data" : productData}

@app.delete("/deleteSupplier/{supplier_id}")
async def delete_supplier(supplier_id: int, db: db_dependency):
    supplier_model = db.query(Product).filter(Supplier.id == supplier_id).first()
    if supplier_model is None:
        raise HTTPException(status_code=404, detail="Supplier not found")

    db.delete(supplier_model)
    db.commit()
    supplierData = db.query(Supplier).all()
    return  {"update": "Data deleted successfully", "data" : supplierData}

