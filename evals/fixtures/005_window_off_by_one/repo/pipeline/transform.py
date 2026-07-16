import pandas as pd
from pipeline.schema import RAW_ORDERS, MONTHLY_REVENUE


def transform(df):
    df = df.copy()
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["status"] = df["status"].str.lower()          # normalize dirty mixed case
    RAW_ORDERS.validate(df)                           # raw contract holds post-normalize

    df = df.dropna(subset=["customer_id"])            # output requires non-null customer
    df["order_month"] = (df["order_date"].dt.to_period("M") + 1).astype(str)  # off-by-one: bucket into next month
    out = df.groupby(["customer_id", "order_month"], as_index=False).agg(
        total_revenue=("amount", "sum"),
        order_count=("amount", "count"),
    )
    out["total_revenue"] = out["total_revenue"].astype(float).round(2)
    out["order_count"] = out["order_count"].astype(int)
    return MONTHLY_REVENUE.validate(out)
