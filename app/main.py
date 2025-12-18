from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from app.routes.qa import router as qa_router

from fastapi.staticfiles import StaticFiles


# ✅ CREATE APP FIRST
app = FastAPI(title="Finz Ledger API")

# ✅ MOUNT STATIC FILES IF NEEDED
app.mount("/static", StaticFiles(directory="app/static"), name="static")


# ✅ THEN USE DECORATORS
@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Finz Ledger – Cashflow Q&A</title>
        <style>

         * {
        box-sizing: border-box;
    }

            body {
                margin: 0;
                height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea, #764ba2);
            }
            .card {
                width: 420px;
                background: white;
                padding: 30px;
                border-radius: 12px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.2);
            }
            h2 {
                margin-top: 0;
                text-align: center;
                color: #1f2937;
            }
            label {
                font-size: 13px;
                color: #6b7280;
            }
            input, textarea {
                width: 100%;
                padding: 10px;
                margin-top: 6px;
                margin-bottom: 14px;
                border-radius: 6px;
                border: 1px solid #d1d5db;
                font-size: 14px;
            }
            textarea {
                resize: none;
                height: 60px;
            }
            button {
                width: 100%;
                padding: 12px;
                background: linear-gradient(135deg, #6366f1, #4f46e5);
                color: white;
                font-size: 15px;
                border: none;
                border-radius: 8px;
                cursor: pointer;
            }
            .answer {
                margin-top: 18px;
                padding: 14px;
                background: #f3f4f6;
                border-left: 4px solid #6366f1;
                border-radius: 6px;
                color: #111827;
                font-weight: 500;
                min-height: 40px;
            }
            .footer {
                text-align: center;
                margin-top: 14px;
                font-size: 12px;
                color: #9ca3af;
            }
        </style>
    </head>
    <body>
        <div class="card">
            <div style="text-align:center; margin-bottom: 10px;">
    <img src="/static/finz_logo.jpeg" alt="Finz Logo" style="height:60px;" />
    <h2>Finz Cashflow Q&A</h2>
</div>


            <label>Business ID</label>
            <input id="business_id" value="demo-business-1" />

            <label>Question</label>
            <textarea id="question">What were my total outflows?</textarea>

            <label>Start Date</label>
            <input id="start_date" type="date" value="2025-11-01" />

            <label>End Date</label>
            <input id="end_date" type="date" value="2025-11-30" />

            <button onclick="ask()">Ask Question</button>

            <div class="answer" id="answer"></div>

            <div class="footer">
                Finz Ledger API • Demo UI by Suraj
            </div>
        </div>

        <script>
            async function ask() {
                document.getElementById("answer").innerText = "Analyzing cashflows...";

                const payload = {
                    business_id: document.getElementById("business_id").value,
                    question: document.getElementById("question").value,
                    start_date: document.getElementById("start_date").value,
                    end_date: document.getElementById("end_date").value
                };

                const res = await fetch("/qa", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });

                const data = await res.json();
                document.getElementById("answer").innerText =
                    data.answer || "No answer returned.";
            }
        </script>
    </body>
    </html>
    """

# ✅ INCLUDE ROUTERS AT THE END
app.include_router(qa_router)