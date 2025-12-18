from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional

class IngestRequest(BaseModel):
    business_id: str = Field(default="demo-business-1")
    account_id: str = Field(default="bank-1")
    source: str = Field(default="bank")
    import_batch_id: str
    institution_name: str = Field(default="demo-bank")
    rows: List[Dict[str, Any]]

class IngestResponse(BaseModel):
    created: int
    updated: int
    skipped: int

class SummaryResponse(BaseModel):
    totals: Dict[str, float]
    by_category: Dict[str, float]
    top_vendors: List[Dict[str, float]]

class QARequest(BaseModel):
    question: str
    start_date: str
    end_date: str
    business_id: str = Field(default="demo-business-1")

class QAResponse(BaseModel):
    answer: str
