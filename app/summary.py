from typing import Dict
from datetime import datetime, timezone

# ✅ IMPORTANT: import your Mongo collection
from app.db import bank_transactions


def _to_dt(s: str) -> datetime:
    """
    Convert YYYY-MM-DD string to UTC datetime
    """
    return datetime.strptime(s, "%Y-%m-%d").replace(tzinfo=timezone.utc)


def cashflow_summary(business_id: str, start_date: str, end_date: str) -> Dict:
    start = _to_dt(start_date).isoformat().replace("+00:00", "Z")
    end = _to_dt(end_date).isoformat().replace("+00:00", "Z")

    docs = list(
        bank_transactions.find(
            {
                "business_id": business_id,
                "posted_at": {"$gte": start, "$lte": end},
            },
            {
                "_id": 0,
                "amount": 1,
                "cashflow_type": 1,
                "category": 1,
                "vendor_name": 1,
            },
        )
    )

    inflows = sum(d["amount"] for d in docs if d.get("cashflow_type") == "INFLOW")
    outflows = sum(abs(d["amount"]) for d in docs if d.get("cashflow_type") == "OUTFLOW")
    net_cash = inflows - outflows

    by_category: Dict[str, float] = {}
    vendor_totals: Dict[str, float] = {}

    for d in docs:
        if d.get("cashflow_type") == "OUTFLOW":
            cat = d.get("category") or "UNKNOWN"
            amt = abs(float(d.get("amount", 0.0)))

            by_category[cat] = by_category.get(cat, 0.0) + amt

            vendor = d.get("vendor_name") or "UNKNOWN"
            vendor_totals[vendor] = vendor_totals.get(vendor, 0.0) + amt

    # ✅ Largest category (safe)
    largest_category = None
    largest_category_amount = 0.0

    if by_category:
        largest_category, largest_category_amount = max(
            by_category.items(), key=lambda kv: kv[1]
        )

    top_vendors = sorted(
        [{"vendor": v, "amount": a} for v, a in vendor_totals.items()],
        key=lambda x: x["amount"],
        reverse=True,
    )[:10]

    return {
        "totals": {
            "inflows": inflows,
            "outflows": outflows,
            "net_cash": net_cash,
        },
        "by_category": dict(
            sorted(by_category.items(), key=lambda kv: kv[1], reverse=True)
        ),
        "largest_category": largest_category,
        "largest_category_amount": largest_category_amount,
        "top_vendors": top_vendors,
    }
