import os
from pymongo import MongoClient
from lstm_predictor import predictor
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client["stock_data"]
collection = db["stock_records"]
results = db["stocks_results"]


def save_to_database(seller, content):
    """
    Save the extracted text to MongoDB database.
    """
    update_data = {
        "$set": {
            "lstm": content
        }
    }

    results.update_one(
        {"_id": seller},
        update_data,
        upsert=True
    )


def get_lstm(stock_id: str):
    """
    Fetches the LSTM prediction for a specific stock ID.    
    """
    stock = collection.find_one({"_id": stock_id.upper()})
    if not stock:
        return None
    if len(stock["data"]) == 0:
        return None
    prediction = predictor(stock["data"])
    dates = prediction["dates"] + prediction["forecast_dates"]
    prices = prediction["prices"] + prediction["forecast"]
    result = [dates[-min(100, len(dates)):], prices[-min(100, len(prices)):]]
    save_to_database(stock_id, result)
    return result

if __name__ == "__main__":
    for stock_id in collection.find().distinct("_id"):
        get_lstm(stock_id)
    client.close()