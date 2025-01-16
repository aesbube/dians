import os
from pymongo import MongoClient
from transformers import pipeline
from fundamental_analysis import get_fund_analysis
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client["stock_data"]
fundamental_collection = db["stock_fundamental"]
results = db["stocks_results"]

pipe = pipeline("text-classification",
                model="ProsusAI/finbert", max_length=512)
translator = pipeline(
    "translation", model="Helsinki-NLP/opus-mt-mk-en", max_length=512)

def save_to_database(seller, content):
    """
    Save the extracted text to MongoDB database.
    """
    update_data = {
        "$set": {
            "fundamental": content
        }
    }

    results.update_one(
        {"_id": seller},
        update_data,
        upsert=True
    )


def get_fundamental(stock_id: str):
    """
    Fetches the fundamental analysis for a specific stock ID.
    """
    stock = fundamental_collection.find_one({"_id": stock_id.upper()})
    if not stock:
        return None
    result = get_fund_analysis(
        stock['file'][:min(512, len(stock['file']))], translator, pipe)
    save_to_database(stock_id, result)
    return result

if __name__ == "__main__":
    for stock_id in fundamental_collection.find().distinct("_id"):
        get_fundamental(stock_id)
    client.close()