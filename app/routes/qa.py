from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from app.summary import cashflow_summary
from app.gemini_qa import answer_question_with_gemini

router = APIRouter(prefix="/qa", tags=["Gemini QA"])

def format_k(x: float) -> str:
    return f"{int(x / 1000)}k" if x >= 1000 else str(int(x))

def is_deterministic_question(question: str) -> bool:
    q = question.lower()
    keywords = [
        "total outflow",
        "total outflows",
        "largest category",
        "how much",
        "amount",
        "spend",
    ]
    return any(k in q for k in keywords)

@router.post("")
def qa_endpoint(payload: Dict[str, Any]):
    """
    Financial Q&A with deterministic math + optional Gemini
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

        # ✅ SAFE access (NO KeyError)
        totals = summary.get("totals", {})
        total_outflows = totals.get("outflows", 0)

        largest_category = summary.get("largest_category", "UNKNOWN")
        largest_amount = summary.get("largest_category_amount", 0)

        deterministic_answer = (
            f"Your total outflows were {format_k(total_outflows)}. "
            f"Largest category was {largest_category} "
            f"at {format_k(largest_amount)}."
        )

        # 🚀 FAST PATH (no Gemini → no latency)
        if is_deterministic_question(question):
            return {"answer": deterministic_answer}

        # 🤖 Gemini only for non-deterministic questions
        answer = answer_question_with_gemini(
            question=question,
            context=deterministic_answer,
        )

        return {"answer": answer}

    except Exception as e:
        # ✅ ALWAYS return JSON (never plain text)
        raise HTTPException(status_code=500, detail=str(e))
