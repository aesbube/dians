import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from lstm_predictor import predictor
from dotenv import load_dotenv

# path = os.path.join('../../../', '.env')
# load_dotenv(dotenv_path=path)

app = FastAPI()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client["stock_data"]
collection = db["stock_records"]


@app.get("/lstm_predict/{stock_id}")
def get_prediction(stock_id: str):
    """
    Fetches the LSTM prediction for a specific stock ID.    
    """
    stock = collection.find_one({"_id": stock_id.upper()})
    if not stock:
        raise HTTPException(status_code=404, detail=f"Stock ID {stock_id} not found")
    if len(stock["data"]) == 0:
        raise HTTPException(
            status_code=404, detail="No data available for this stock")
    prediction = predictor(stock["data"])
    dates = prediction["dates"] + prediction["forecast_dates"]
    prices = prediction["prices"] + prediction["forecast"]
    return [dates[-min(100, len(dates)):], prices[-min(100, len(prices)):]]
