import os
from pymongo import MongoClient, ASCENDING

from dotenv import load_dotenv, find_dotenv

# Load .env only if present to avoid warnings when running without a .env file
dotenv_path = find_dotenv()
if dotenv_path:
    load_dotenv(dotenv_path)

# Provide safe defaults so the module can be imported without a .env file
# 
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DB = os.getenv("MONGODB_DB", "finz")

client = MongoClient(MONGODB_URI)
db = client[MONGODB_DB]
bank_transactions = db["bank_transactions"]

def ensure_indexes() -> None:
    bank_transactions.create_index(
        [("business_id", ASCENDING), ("provider_txn_id", ASCENDING)],
        unique=True,
        name="uniq_business_provider_txn",
    )
    bank_transactions.create_index([("business_id", ASCENDING), ("posted_at", ASCENDING)])
