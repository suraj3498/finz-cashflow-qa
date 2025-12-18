# Finz_internship_task
# Finz Ledger (MongoDB + FastAPI + Gemini QA)

## What this does
1) Ingests raw bank/CC transactions as rows (JSON-parsed from CSV or any source)
2) Normalizes into a canonical schema
3) Categorizes deterministically (no LLM for categories)
4) Upserts into MongoDB idempotently using (business_id, provider_txn_id)
5) Exposes:
   - POST /ingest/bank-transactions
   - GET  /cashflow/summary
   - POST /qa (Gemini answers using only computed numbers)

## Setup
### 1) Create env
Copy `.env.example` to `.env` and fill values:
- MONGODB_URI
- GEMINI_API_KEY

### 2) Install
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

