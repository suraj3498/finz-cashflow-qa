from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from app.summary import cashflow_summary
from app.gemini_qa import answer_question_with_gemini

router = APIRouter(prefix="/qa", tags=["Gemini QA"])


# ---------- Helpers ----------

def format_k(x: float) -> str:
    return f"{int(x / 1000)}k" if x >= 1000 else str(int(x))


def get_question_intent(question: str) -> str:
    """
    Classify user question into a supported financial intent
    """
    q = question.lower()

    if "total outflow" in q or "total outflows" in q:
        return "TOTAL_OUTFLOWS"

    if "total inflow" in q or "total inflows" in q:
        return "TOTAL_INFLOWS"

    if "net cash" in q or "net cashflow" in q:
        return "NET_CASH"

    if "largest category" in q or "highest category" in q:
        return "LARGEST_CATEGORY"

    if "top vendor" in q or "top vendors" in q:
        return "TOP_VENDORS"

    return "UNKNOWN"


# ---------- API ----------

@router.post("")
def qa_endpoint(payload: Dict[str, Any]):
    """
    Financial Q&A with deterministic computation + optional Gemini fallback
    """

    try:
        business_id = payload["business_id"]
        question = payload["question"]
        start_date = payload["start_date"]
        end_date = payload["end_date"]

        summary = cashflow_summary(
            business_id=business_id,
            start_date=start_date,
            end_date=end_date,
        )

        totals = summary.get("totals", {})
        intent = get_question_intent(question)

        # ---------- Deterministic answers ----------

        if intent == "TOTAL_OUTFLOWS":
            answer = f"Your total outflows were {format_k(totals.get('outflows', 0))}."

        elif intent == "TOTAL_INFLOWS":
            answer = f"Your total inflows were {format_k(totals.get('inflows', 0))}."

        elif intent == "NET_CASH":
            answer = f"Your net cashflow was {format_k(totals.get('net_cash', 0))}."

        elif intent == "LARGEST_CATEGORY":
            category = summary.get("largest_category", "UNKNOWN")
            amount = summary.get("largest_category_amount", 0)
            answer = (
                f"Your largest expense category was {category} "
                f"at {format_k(amount)}."
            )

        elif intent == "TOP_VENDORS":
            vendors = summary.get("top_vendors", [])[:3]
            if not vendors:
                answer = "No vendor spending found for this period."
            else:
                vendor_text = ", ".join(
                    f"{v['vendor']} ({format_k(v['amount'])})"
                    for v in vendors
                )
                answer = f"Your top vendors were {vendor_text}."

        else:
            # ---------- Gemini fallback ----------
            answer = answer_question_with_gemini(
                question=question,
                context=summary,
            )

        return {"answer": answer}

    except Exception as e:
        # Always return JSON
        raise HTTPException(status_code=500, detail=str(e))
