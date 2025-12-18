import hashlib
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from .rules import (
    classify_cashflow_type,
    classify_outflow_category,
    classify_transfer_category,
    classify_withdrawal_category,
)

def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

def _sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def _coalesce(*vals):
    for v in vals:
        if v is None:
            continue
        if isinstance(v, str) and v.strip() == "":
            continue
        return v
    return None

def build_provider_txn_id(
    business_id: str,
    account_id: str,
    posted_at: str,
    amount: float,
    raw_description: str,
    raw_id: Optional[str] = None
) -> str:
    if raw_id:
        return str(raw_id)
    base = f"{business_id}|{account_id}|{posted_at}|{amount:.2f}|{raw_description}"
    return _sha256(base)

def build_transaction_id(business_id: str, provider_txn_id: str) -> str:
    return _sha256(f"{business_id}|{provider_txn_id}")

def normalize_row(
    row: Dict[str, Any],
    *,
    business_id: str,
    account_id: str,
    source: str,
    import_batch_id: str,
    institution_name: str,
    currency_default: str = "USD",
) -> Dict[str, Any]:
    """
    Converts a raw row (already parsed from CSV or JSON) into the canonical schema.
    Expected minimally: posted_at/date, amount, description.
    """

    # Flexible field mapping (supports different CSV headers)
    raw_description = str(_coalesce(
        row.get("raw_description"),
        row.get("description"),
        row.get("memo"),
        row.get("name"),
        row.get("transaction_description"),
        ""
    ))

    vendor_name = _coalesce(
        row.get("vendor_name"),
        row.get("merchant"),
        row.get("payee"),
        row.get("vendor"),
    )
    if vendor_name is not None:
        vendor_name = str(vendor_name)

    amount = float(_coalesce(row.get("amount"), row.get("amt"), 0.0))

    posted_at_raw = _coalesce(
        row.get("posted_at"),
        row.get("date"),
        row.get("transaction_date"),
        row.get("posted_date"),
    )
    if not posted_at_raw:
        raise ValueError("Missing posted_at/date in row")

    # Accept ISO or simple date; normalize to UTC ISO string
    posted_at_dt = None
    if isinstance(posted_at_raw, datetime):
        posted_at_dt = posted_at_raw
    else:
        s = str(posted_at_raw).strip()
        try:
            posted_at_dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        except Exception:
            # try YYYY-MM-DD
            posted_at_dt = datetime.strptime(s, "%Y-%m-%d").replace(tzinfo=timezone.utc)

    posted_at = _iso(posted_at_dt)

    raw_id = _coalesce(row.get("provider_txn_id"), row.get("id"), row.get("txn_id"), row.get("transaction_id"))
    provider_txn_id = build_provider_txn_id(
        business_id, account_id, posted_at, amount, raw_description, raw_id=str(raw_id) if raw_id else None
    )
    transaction_id = build_transaction_id(business_id, provider_txn_id)

    cashflow_type = classify_cashflow_type(raw_description, amount)

    # Categories:
    # - TRANSFER/WITHDRAWAL handled BEFORE P&L mapping (your requirement)
    if cashflow_type == "TRANSFER":
        category = classify_transfer_category(raw_description)  # TRANSFER_INTERNAL / TRANSFER_EXTERNAL
    elif cashflow_type == "WITHDRAWAL":
        category = classify_withdrawal_category(raw_description)  # WITHDRAWAL_ATM / WITHDRAWAL_OWNER_DRAW
    elif cashflow_type == "OUTFLOW":
        category = classify_outflow_category(raw_description, vendor_name)
    else:
        category = "INFLOW"

    now = _iso(datetime.now(timezone.utc))

    doc = {
        "transaction_id": transaction_id,
        "business_id": business_id,
        "account_id": account_id,
        "provider_txn_id": provider_txn_id,
        "posted_at": posted_at,
        "amount": amount,
        "currency": str(_coalesce(row.get("currency"), currency_default)),
        "cashflow_type": cashflow_type,
        "category": category,
        "vendor_name": vendor_name,
        "raw_description": raw_description,
        "source": source,
        "meta": {
            "import_batch_id": import_batch_id,
            "institution_name": institution_name,
        },
        "created_at": now,   # will be set only on insert via $setOnInsert
        "updated_at": now,   # will always be updated via $set
        "raw": row,          # keep full original for audit/debug
    }
    return doc
