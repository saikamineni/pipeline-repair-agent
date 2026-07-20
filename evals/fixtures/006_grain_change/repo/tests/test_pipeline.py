"""Golden test suite.

This file is PROTECTED in fixtures — byte-identical to this baseline in every
fixture. Bugs are injected into pipeline/, never here. Reads the committed
static CSVs; never regenerates data.

Known-answer values below are hand-computed against the committed
data/orders.csv + data/customers.csv (SEED=42). If you regenerate data with a
different seed or row count, these numbers change and must be recomputed.
"""
import pytest
import pandas as pd
from pipeline import extract_orders, extract_customers, transform
from pipeline.schema import RAW_ORDERS, CUSTOMERS, MONTHLY_REVENUE


@pytest.fixture
def pipeline_output() -> pd.DataFrame:
    orders = extract_orders()
    customers = extract_customers()
    RAW_ORDERS.validate(orders)
    CUSTOMERS.validate(customers)
    return transform(orders, customers)


def test_schemas_validate(pipeline_output):
    # Output conforms to the contract (types, ranges, no null customers).
    MONTHLY_REVENUE.validate(pipeline_output)


def test_no_null_customers_in_output(pipeline_output):
    assert pipeline_output["customer_id"].notna().all()


def test_row_counts_sane(pipeline_output):
    # Grain is (customer, month); with 20 customers over 2025 this is bounded.
    assert 1 <= len(pipeline_output) <= 240
    assert (pipeline_output["order_count"] > 0).all()


def test_known_aggregate_overall(pipeline_output):
    # Hand-computed from the committed CSVs (nulls excluded).
    assert round(pipeline_output["total_revenue"].sum(), 2) == 41356.08


def test_known_aggregate_customer(pipeline_output):
    # cust_0 total revenue across all months.
    c0 = pipeline_output[pipeline_output["customer_id"] == "cust_0"]
    assert round(c0["total_revenue"].sum(), 2) == 381.23


def test_known_aggregate_cell(pipeline_output):
    # A single pinned (customer, month) cell.
    cell = pipeline_output[
        (pipeline_output["customer_id"] == "cust_0")
        & (pipeline_output["order_month"] == "2025-05")
    ]
    assert len(cell) == 1
    assert round(cell["total_revenue"].iloc[0], 2) == 86.06
    assert int(cell["order_count"].iloc[0]) == 1

def test_output_grain(pipeline_output):
    # grain is (customer, month); grain bugs collapse this
    assert len(pipeline_output) == 112
