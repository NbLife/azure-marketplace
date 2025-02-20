from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional
from uuid import uuid4
import shutil
import os

app = FastAPI()


class User(BaseModel):
    id: str
    username: str
    email: str


class Product(BaseModel):
    id: str
    name: str
    description: str
    price: float
    owner_id: str
    image_url: Optional[str] = None


users_db = []
products_db = []

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.get("/")
def root():
    return {"message": "Welcome to the Marketplace API"}


@app.post("/register", response_model=User)
def register_user(username: str, email: str):
    user = User(id=str(uuid4()), username=username, email=email)
    users_db.append(user)
    return user


@app.post("/add_product", response_model=Product)
def add_product(name: str, description: str, price: float, owner_id: str):
    if not any(user.id == owner_id for user in users_db):
        raise HTTPException(status_code=404, detail="User not found")

    product = Product(
        id=str(uuid4()),
        name=name,
        description=description,
        price=price,
        owner_id=owner_id
    )
    products_db.append(product)
    return product


@app.get("/products", response_model=List[Product])
def get_products():
    return products_db


@app.get("/product/{product_id}", response_model=Product)
def get_product(product_id: str):
    for product in products_db:
        if product.id == product_id:
            return product
    raise HTTPException(status_code=404, detail="Product not found")


@app.get("/search")
def search_products(query: str):
    results = [product for product in products_db if query.lower()
               in product.name.lower()]
    return results


@app.post("/upload_image/{product_id}")
def upload_image(product_id: str, file: UploadFile = File(...)):
    for product in products_db:
        if product.id == product_id:
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            product.image_url = file_path
            return {"filename": file.filename, "url": file_path}

    raise HTTPException(status_code=404, detail="Product not found")