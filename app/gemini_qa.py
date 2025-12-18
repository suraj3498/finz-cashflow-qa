import json
from google import genai
from .config import GEMINI_API_KEY

if not GEMINI_API_KEY:
    raise RuntimeError("❌ GEMINI_API_KEY not found. Check your .env file.")

client = genai.Client(api_key=GEMINI_API_KEY)

MODEL = "gemini-2.5-flash"


def answer_question_with_gemini(*, question: str, context: dict) -> str:
    prompt = f"""
You are a financial assistant.
Answer ONLY using the numbers in the context.
Do NOT invent values.

Context:
{json.dumps(context, indent=2)}

Question:
{question}
"""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )

    return response.text
