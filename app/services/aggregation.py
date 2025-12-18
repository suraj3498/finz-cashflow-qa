from datetime import datetime

def get_outflow_summary(collection, business_id, start_date, end_date):
    pipeline = [
        {
            "$match": {
                "business_id": business_id,
                "cashflow_type": "OUTFLOW",
                "posted_at": {
                    "$gte": start_date,
                    "$lte": end_date
                }
            }
        },
        {
            "$group": {
                "_id": "$category",
                "total": {"$sum": "$amount"}
            }
        }
    ]

    results = list(collection.aggregate(pipeline))
    return results
