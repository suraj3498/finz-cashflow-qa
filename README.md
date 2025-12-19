# Finz Cashflow Q&A API

A FastAPI-based backend application that answers business cashflow questions
using deterministic financial aggregation, with optional LLM (Gemini) support
for natural language explanations.

This project was built as part of the **Finz Internship Task**.

---

## Features

- Cashflow aggregation from bank transaction data
- Deterministic computation of:
  - Total inflows
  - Total outflows
  - Net cashflow
  - Largest spending category
- FastAPI REST API
- Interactive demo UI (HTML + CSS + JavaScript)
- Optional Gemini integration for natural language responses
- MongoDB backend
- Defensive API responses with consistent schema

---

## Tech Stack

- **Python 3.11+**
- **FastAPI**
- **MongoDB**
- **Uvicorn**
- HTML / CSS / JavaScript
- Google Gemini API (optional)

---

## Project Structure

finz-cashflow-qa/
├── app/
│ ├── main.py # FastAPI app + UI
│ ├── summary.py # Cashflow aggregation logic
│ ├── gemini_qa.py # Gemini integration (optional)
│ ├── routes/
│ │ └── qa.py # /qa API endpoint
│ ├── db/
│ │ └── init.py # MongoDB connection
│ └── static/
│ └── finz_logo.jpeg # Logo for UI
├── .env.example # Environment variable template
├── README.md # Project documentation
├── requirements.txt # Python dependencies
└── .gitignore

---

## Setup Instructions

### Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/finz-cashflow-qa.git
cd finz-cashflow-qa

Create a virtual environment
python -m venv venv

Activate it:
venv\Scripts\activate

Install dependencies
pip install -r requirements.txt

Environment Variables (Gemini API)
Create a .env file in the project root:
GEMINI_API_KEY=AIzaSyARpRMEozz3TiT1FbJNWZAw7AmafZ4FQtI

Run the application
uvicorn app.main:app --reload

Open in browser:
http://127.0.0.1:8000

Example API Call
POST /qa
Request
{
  "business_id": "demo-business-1",
  "question": "What were my total outflows?",
  "start_date": "2025-11-01",
  "end_date": "2025-11-30"
}


Response:
{
  "answer": "Your total outflows were 33k. Largest category was COGS at 12k."
}

