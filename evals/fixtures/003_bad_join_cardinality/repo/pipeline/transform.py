"""Transform stage: join orders to customers, aggregate to monthly revenue.

MUTABLE in fixtures. Most logic bugs (null handling, join cardinality,
window boundaries, aggregation) are injected here.
"""
import pandas as pd


def transform(orders: pd.DataFrame, customers: pd.DataFrame) -> pd.DataFrame:
    # Drop orders with no customer_id — they can't be attributed.
    orders = orders.dropna(subset=["customer_id"]).copy()

    # Attach region via a left join on the unique customer key.
    enriched = orders.merge(customers, on="customer_id", how="left")
    region_counts = customers[["region"]].copy()
    enriched = enriched.merge(region_counts, on="region", how="left")  

    # Bucket into calendar months.
    enriched["order_month"] = enriched["order_date"].dt.strftime("%Y-%m")

    # Aggregate revenue per customer per month.
    monthly = (
        enriched.groupby(["customer_id", "order_month"], dropna=True)
        .agg(
            total_revenue=("amount", "sum"),
            order_count=("order_id", "count"),
        )
        .reset_index()
    )

    monthly["total_revenue"] = monthly["total_revenue"].round(2)
    monthly["order_count"] = monthly["order_count"].astype(int)
    return monthly
