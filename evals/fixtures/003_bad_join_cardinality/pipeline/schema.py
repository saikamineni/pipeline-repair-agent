import pandera.pandas as pa
from pandera.pandas import Column, Check

RAW_ORDERS = pa.DataFrameSchema({
    "order_id":    Column(str, unique=True),
    "customer_id": Column(str, nullable=True),   # raw data is dirty on purpose
    "amount":      Column(float, Check.ge(0)),
    "currency":    Column(str, Check.isin(["USD", "EUR", "INR"])),
    "order_date":  Column(pa.DateTime),
    "status":      Column(str, Check.isin(["placed", "shipped", "cancelled"])),
})

MONTHLY_REVENUE = pa.DataFrameSchema({
    "customer_id":   Column(str, nullable=False),
    "order_month":   Column(str, Check.str_matches(r"^\d{4}-\d{2}$")),
    "total_revenue": Column(float, Check.ge(0)),
    "order_count":   Column(int, Check.ge(1)),
})