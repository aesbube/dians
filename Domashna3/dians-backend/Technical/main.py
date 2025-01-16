import os
from pymongo import MongoClient
from tech_analysis import tech_results
from dotenv import load_dotenv

# path = os.path.join('../../', '.env')
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
            "technical": content
        }
    }

    results.update_one(
        {"_id": seller},
        update_data,
        upsert=True
    )


def get_technical(stock_id: str):
    """
    Fetches the technical analysis for a specific stock ID.
    """
    stock = collection.find_one({"_id": stock_id.upper()})

    if not stock:
        return None

    if len(stock["data"]) < 2:
        return None

    periods = {
        "day": 2,
        "week": 7,
        "month": 30
    }

    result = dict()

    for period, num in periods.items():
        days = min(num, len(stock["data"]))
        result_period = tech_results(stock["data"][:days], days)
        result[period] = result_period

    save_to_database(stock_id, result)
    return result


if __name__ == "__main__":
    for stock in collection.find().distinct("_id"):
        get_technical(stock)
    client.close()
