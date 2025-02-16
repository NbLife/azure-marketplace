import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from dotenv import load_dotenv
from pymongo import MongoClient
from azure.storage.blob import BlobServiceClient
from pathlib import Path
from starlette.middleware.cors import CORSMiddleware

# Inicjalizacja aplikacji FastAPI
app = FastAPI()

# Wczytanie zmiennych środowiskowych
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

# Pobranie zmiennych środowiskowych
COSMOS_DB_URL = os.getenv("COSMOS_DB_URL")
COSMOS_DB_NAME = os.getenv("COSMOS_DB_NAME")
AZURE_STORAGE_CONN_STRING = os.getenv("AZURE_STORAGE_CONN_STRING")
AZURE_BLOB_CONTAINER_NAME = os.getenv("AZURE_BLOB_CONTAINER_NAME")
SECRET_KEY = os.getenv("SECRET_KEY")

# Konfiguracja CORS
otpas = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=otpas,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Połączenie z CosmosDB
try:
    client = MongoClient(COSMOS_DB_URL)
    db = client[COSMOS_DB_NAME]
    products_collection = db["products"]
    print("Połączono z bazą CosmosDB")
except Exception as e:
    print(f"Błąd połączenia z CosmosDB: {str(e)}")
    raise HTTPException(status_code=500, detail="Błąd połączenia z bazą danych")

# Połączenie z Azure Blob Storage
try:
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONN_STRING)
    container_client = blob_service_client.get_container_client(AZURE_BLOB_CONTAINER_NAME)
    print("Połączono z Azure Blob Storage")
except Exception as e:
    print(f"Błąd połączenia z Azure Blob Storage: {str(e)}")
    raise HTTPException(status_code=500, detail="Błąd połączenia z Azure Storage")


@app.get("/")
def home():
    return {"message": "Marketplace API działa!"}


@app.get("/api/status")
def status():
    return {"status": "OK"}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        blob_client = container_client.get_blob_client(file.filename)
        blob_client.upload_blob(file.file.read(), overwrite=True)
        return {"message": "Plik przesłany pomyślnie!", "file": file.filename}
    except Exception as e:
        return {"error": str(e)}


@app.post("/items")
async def create_item(name: str = Form(...), price: float = Form(...)):
    try:
        product = {"name": name, "price": price}
        products_collection.insert_one(product)
        return {"message": "Produkt dodany!", "product": product}
    except Exception as e:
        return {"error": str(e)}
