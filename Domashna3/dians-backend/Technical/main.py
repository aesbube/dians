import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from tech_analysis import tech_results
from dotenv import load_dotenv

# path = os.path.join('../../../', '.env')
# load_dotenv(dotenv_path=path)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client["stock_data"]
collection = db["stock_records"]


@app.get("/technical_analysis/{stock_id}")
def get_technical_analysis(stock_id: str):
    """
    Fetches the technical analysis for a specific stock ID.
    """
    stock = collection.find_one({"_id": stock_id.upper()})

    if not stock:
        raise HTTPException(status_code=404, detail=f"Stock ID {stock_id} not found")

    if len(stock["data"]) < 2:
        raise HTTPException(
            status_code=404, detail="No data available for this stock")

    periods = {
        "day": 2,
        "week": 7,
        "month": 30
    }

    results = dict()

    for period, num in periods.items():
        days = min(num, len(stock["data"]))
        result = tech_results(stock["data"][:days], days)
        results[period] = result

    return results
