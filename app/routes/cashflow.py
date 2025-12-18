from fastapi import APIRouter, Query
from app.summary import cashflow_summary

router = APIRouter(prefix="/cashflow", tags=["Cashflow"])

@router.get("/summary")
def get_cashflow_summary(
    business_id: str = Query(...),
    start_date: str = Query(...),
    end_date: str = Query(...)
):
    """
    Returns:
    - totals (inflows, outflows, net cash)
    - spend by category
    - top vendors
    """
    return cashflow_summary(
        business_id=business_id,
        start_date=start_date,
        end_date=end_date,
    )