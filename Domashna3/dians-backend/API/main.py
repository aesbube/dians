from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from typing import List
from dotenv import load_dotenv
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    # allow_origins=["https://dians.azurewebsites.net"],
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = os.getenv("API_KEY")

api_key_header = APIKeyHeader(name="x-api-key")

def validate_api_key(api_key: str = Depends(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(
            status_code=403, detail="Forbidden: Invalid API Key")


MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client["stock_data"]
collection = db["stock_records"]
results = db["stocks_results"]


@app.get("/")
def read_root():
    return {"message": "Welcome to the Stock API!"}


@app.get("/stocks", response_model=List[str])
def get_stock_ids(api_key: str = Depends(validate_api_key)):
    """
    Fetches all unique stock IDs (_id) from the collection.
    """
    stock_ids = collection.find().distinct("_id")
    if not stock_ids:
        raise HTTPException(status_code=404, detail="No stock data found")
    return stock_ids


@app.get("/stocks/{stock_id}")
def get_stock_data(stock_id: str, api_key: str = Depends(validate_api_key)):
    """
    Fetches the data array for a specific stock ID.
    """
    stock = collection.find_one({"_id": stock_id.upper()})
    if not stock:
        raise HTTPException(status_code=404, detail=f"Stock ID {stock_id} not found")
    return stock["data"]


@app.get("/stocks/{stock_id}/chart")
def get_date_price(stock_id: str, api_key: str = Depends(validate_api_key)):
    """
    Fetches the date and price for a specific stock ID.
    """
    stock = collection.find_one({"_id": stock_id.upper()})
    if not stock:
        raise HTTPException(status_code=404, detail=f"Stock ID {stock_id} not found")
    dates, prices = [], []
    for data in stock["data"]:
        dates.append(data["date"])
        prices.append(int(data["last_transaction"][:-8].replace('.', '')))
    return (dates[::-1], prices[::-1])


@app.get("/fundamental/{stock_id}")
def get_fundamental(stock_id: str, api_key: str = Depends(validate_api_key)):
    """
    Fetches the fundamental analysis for a specific stock ID.
    """
    stock = results.find_one({"_id": stock_id.upper()})
    if not stock:
        raise HTTPException(status_code=404, detail=f"Stock ID {stock_id} not found")
    result = stock["fundamental"]
    if result is None:
        raise HTTPException(status_code=404, detail=f"Stock ID {stock_id} fundamental not found")
    return result


@app.get("/technical/{stock_id}")
def get_technical(stock_id: str, api_key: str = Depends(validate_api_key)):
    """
    Fetches the technical analysis for a specific stock ID.
    """
    stock = results.find_one({"_id": stock_id.upper()})
    if not stock:
        raise HTTPException(status_code=404, detail=f"Stock ID {stock_id} not found")
    result = stock["technical"]
    if not result:
        raise HTTPException(status_code=404, detail=f"Stock ID {stock_id} technical not found")
    return result


@app.get("/lstm/{stock_id}")
def get_lstm(stock_id: str, api_key: str = Depends(validate_api_key)):
    """
    Fetches the lstm analysis for a specific stock ID.
    """
    stock = results.find_one({"_id": stock_id.upper()})
    if not stock:
        raise HTTPException(status_code=404, detail=f"Stock ID {stock_id} not found")
    result = stock["lstm"]
    if result is None:
        raise HTTPException(status_code=404, detail=f"Stock ID {stock_id} lstm not found")
    return result
