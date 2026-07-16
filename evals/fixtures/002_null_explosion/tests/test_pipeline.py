import runpy
from pathlib import Path

import duckdb
import pandas as pd
import pytest

from pipeline.extract import extract
from pipeline.transform import transform
from pipeline.load import load
from pipeline.schema import RAW_ORDERS, MONTHLY_REVENUE

CSV = "data/orders.csv"


@pytest.fixture(scope="module")
def orders_csv():
    if not Path(CSV).exists():          # self-contained: regenerate seeded data if missing
        runpy.run_path("data/make_data.py")
    return CSV


@pytest.fixture(scope="module")
def pipeline_output(orders_csv):
    return transform(extract(orders_csv))


def test_schemas_validate(orders_csv, pipeline_output):
    raw = extract(orders_csv).copy()
    raw["order_date"] = pd.to_datetime(raw["order_date"])
    raw["status"] = raw["status"].str.lower()
    RAW_ORDERS.validate(raw)            # raw contract holds after normalizing
    MONTHLY_REVENUE.validate(pipeline_output)


def test_row_counts_sane(orders_csv, pipeline_output):
    raw_rows = len(extract(orders_csv))
    assert 0 < len(pipeline_output) <= raw_rows
    assert pipeline_output["customer_id"].notna().all()
    assert (pipeline_output["order_count"] >= 1).all()


def test_known_aggregate(orders_csv, pipeline_output, tmp_path):
    # independently recompute cust_0's Dec-2025 total straight from the raw CSV
    raw = extract(orders_csv)
    raw["order_month"] = pd.to_datetime(raw["order_date"]).dt.strftime("%Y-%m")
    mask = (raw["customer_id"] == "cust_0") & (raw["order_month"] == "2025-12")
    expected_total = round(float(raw.loc[mask, "amount"].sum()), 2)
    expected_count = int(mask.sum())
    assert (expected_count, expected_total) == (3, 423.10)  # pinned to seed=42

    # transform output agrees
    row = pipeline_output[
        (pipeline_output["customer_id"] == "cust_0")
        & (pipeline_output["order_month"] == "2025-12")
    ].iloc[0]
    assert int(row["order_count"]) == expected_count
    assert round(float(row["total_revenue"]), 2) == expected_total

    # loaded DuckDB table agrees (round-trip through load)
    db_path = str(tmp_path / "warehouse.duckdb")
    load(pipeline_output, db_path=db_path)
    con = duckdb.connect(db_path)
    total, count = con.execute(
        "SELECT total_revenue, order_count FROM monthly_revenue "
        "WHERE customer_id = 'cust_0' AND order_month = '2025-12'"
    ).fetchone()
    con.close()
    assert int(count) == expected_count
    assert round(float(total), 2) == expected_total
