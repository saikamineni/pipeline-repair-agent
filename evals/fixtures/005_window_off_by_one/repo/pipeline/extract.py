"""Extract stage: read raw CSVs into typed DataFrames.

MUTABLE in fixtures. Drift/parsing bugs are injected here.
Reads from committed static CSVs in data/ — never regenerates them.
"""
from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def extract_orders(path: Path | str | None = None) -> pd.DataFrame:
    path = Path(path) if path else DATA_DIR / "orders.csv"
    df = pd.read_csv(path, dtype={"order_id": str, "customer_id": str})
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["amount"] = df["amount"].astype(float)
    return df


def extract_customers(path: Path | str | None = None) -> pd.DataFrame:
    path = Path(path) if path else DATA_DIR / "customers.csv"
    df = pd.read_csv(path, dtype={"customer_id": str, "region": str})
    return df
