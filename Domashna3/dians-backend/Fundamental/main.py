import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from transformers import pipeline
from fundamental_analysis import get_fund_analysis
from dotenv import load_dotenv
import os

# path = os.path.join('../../../', '.env')
# load_dotenv(dotenv_path=path)

pipe = pipeline("text-classification",
                model="ProsusAI/finbert", max_length=512)
translator = pipeline(
    "translation", model="Helsinki-NLP/opus-mt-mk-en", max_length=512)


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
fundamental_collection = db["stock_fundamental"]


@app.get("/fundamental_analysis/{stock_id}")
def get_fundamental_analysis(stock_id: str):
    """
    Fetches the fundamental analysis for a specific stock ID.
    """
    stock = fundamental_collection.find_one({"_id": stock_id.upper()})
    if not stock:
        raise HTTPException(status_code=404, detail=f"Stock ID {stock_id} not found")
    return get_fund_analysis(stock['file'][:min(512, len(stock['file']))], translator, pipe)
