import csv
import uuid
import requests

API_URL = "http://127.0.0.1:8000/ingest/bank-transactions"

BUSINESS_ID = "demo-business-1"
INSTITUTION = "demo-bank"

CHECKING_CSV = r"C:\Users\suraj tamboli\Desktop\finz internship task\Raw Data\The Winslow_Checking.csv"
CREDIT_CSV = r"C:\Users\suraj tamboli\Desktop\finz internship task\Raw Data\Winslow cc_Credit_card.csv"

def read_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))

def ingest(rows, account_id, source):
    payload = {
        "business_id": BUSINESS_ID,
        "account_id": account_id,
        "source": source,
        "import_batch_id": str(uuid.uuid4()),
        "institution_name": INSTITUTION,
        "rows": rows,
    }
    r = requests.post(API_URL, json=payload)
    r.raise_for_status()
    return r.json()

def main():
    print("Ingesting checking CSV...")
    res1 = ingest(read_csv(CHECKING_CSV), "bank-checking-1", "bank")
    print(res1)

    print("Ingesting credit card CSV...")
    res2 = ingest(read_csv(CREDIT_CSV), "credit-card-1", "credit_card")
    print(res2)

if __name__ == "__main__":
    main()
