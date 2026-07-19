"""Data contracts for the pipeline.

This file is the CONTRACT. In fixtures it is PROTECTED (never edited by the
agent). A fixture whose only green path is loosening a check here is invalid —
the bug must live in extract.py / transform.py / load.py, not in the contract.
"""
import pandera.pandas as pa
from pandera.pandas import Column, DataFrameSchema, Check

# Raw orders as they arrive from upstream (already parsed into proper types).
RAW_ORDERS = DataFrameSchema(
    {
        "order_id": Column(str, unique=True),
        "customer_id": Column(str, nullable=True),   # nulls allowed on ingest; dropped in transform
        "order_date": Column("datetime64[ns]"),
        "amount": Column(float, Check.ge(0), nullable=True),  # nullable so a coerce-bug fails on totals, not here
    },
    strict=True,   # extra/renamed columns are a contract violation -> surfaces drift bugs
    coerce=False,
)

# Customer dimension.
CUSTOMERS = DataFrameSchema(
    {
        "customer_id": Column(str, unique=True),   # uniqueness here catches dup-key join bugs
        "region": Column(str),
    },
    strict=True,
    coerce=False,
)

# Final monthly revenue output.
MONTHLY_REVENUE = DataFrameSchema(
    {
        "customer_id": Column(str, nullable=False),   # no null customers in output
        "order_month": Column(str),                    # "YYYY-MM"
        "total_revenue": Column(float, Check.ge(0)),
        "order_count": Column(int, Check.gt(0)),
    },
    strict=True,
    coerce=False,
)
