from fastapi import APIRouter, HTTPException
from pymongo.errors import PyMongoError
from typing import Dict, Any

from app.db import bank_transactions
from app.normalize import normalize_row

router = APIRouter(prefix="/ingest", tags=["Ingest"])

@router.post("/bank-transactions")
def ingest_bank_transactions(payload: Dict[str, Any]):
    """
    Ingest raw bank or credit-card transactions.
    Performs:
    - normalization
    - categorization
    - idempotent Mongo upserts
    """

    created = 0
    updated = 0
    skipped = 0

    try:
        rows = payload["rows"]
        business_id = payload["business_id"]
        account_id = payload["account_id"]
        source = payload["source"]
        import_batch_id = payload["import_batch_id"]
        institution_name = payload["institution_name"]

        for row in rows:
            try:
                doc = normalize_row(
                    row=row,
                    business_id=business_id,
                    account_id=account_id,
                    source=source,
                    import_batch_id=import_batch_id,
                    institution_name=institution_name,
                )

                filt = {
                    "business_id": doc["business_id"],
                    "provider_txn_id": doc["provider_txn_id"],
                }

                created_at = doc["created_at"]
                doc_set = dict(doc)
                doc_set.pop("created_at", None)

                result = bank_transactions.update_one(
                    filt,
                    {
                        "$set": doc_set,
                        "$setOnInsert": {"created_at": created_at},
                    },
                    upsert=True,
                )

                if result.upserted_id:
                    created += 1
                else:
                    updated += 1

            except Exception:
                skipped += 1

        return {
            "created": created,
            "updated": updated,
            "skipped": skipped,
        }

    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Missing field: {e}")
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=str(e))
