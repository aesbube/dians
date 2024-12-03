from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from typing import List

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

MONGO_URI = "mongodb://localhost:27017"  
client = MongoClient(MONGO_URI)
db = client["stock_data"]  
collection = db["stock_records"] 


@app.get("/")
def read_root():
    return {"message": "Welcome to the Stock API!"}


@app.get("/stocks", response_model=List[str])
def get_stock_ids():
    """
    Fetches all unique stock IDs (_id) from the collection.
    """
    stock_ids = collection.find().distinct("_id")
    if not stock_ids:
        raise HTTPException(status_code=404, detail="No stock data found")
    return stock_ids


@app.get("/stocks/{stock_id}")
def get_stock_data(stock_id: str):
    """
    Fetches the data array for a specific stock ID.
    """
    stock = collection.find_one({"_id": stock_id.upper()})
    if not stock:
        raise HTTPException(status_code=404, detail=f"Stock ID {stock_id} not found")
    return stock["data"]

@app.get("/stocks/{stock_id}/chart")
def get_date_price(stock_id: str):
    """
    Fetches the date and price for a specific stock ID.
    """
    stock = collection.find_one({"_id": stock_id.upper()})
    if not stock:
        raise HTTPException(status_code=404, detail=f"Stock ID {stock_id} not found")
    dates = []
    prices = []
    for data in stock["data"]:
        dates.append(data["date"])
        prices.append(int(data["last_transaction"][:-8].replace('.', '')))
    return (dates[::-1], prices[::-1])
