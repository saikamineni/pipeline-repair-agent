"""One-time data generator. NOT part of the fixture surface.

Run this ONCE to produce data/orders.csv and data/customers.csv, then commit
those CSVs as immutable artifacts. The agent never sees or runs this file.
Tests read the committed CSVs; they do NOT regenerate.

    python -m evals.make_data
"""
from pathlib import Path
import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
SEED = 42


def make_customers(n: int = 20) -> pd.DataFrame:
    rng = np.random.default_rng(SEED)
    regions = ["us-east", "us-west", "eu", "apac"]
    return pd.DataFrame(
        {
            "customer_id": [f"cust_{i}" for i in range(n)],
            "region": rng.choice(regions, size=n),
        }
    )


def make_orders(n: int = 200, n_customers: int = 20) -> pd.DataFrame:
    rng = np.random.default_rng(SEED)
    customer_ids = [f"cust_{i}" for i in range(n_customers)]

    # ~15% of orders have a null customer_id (dropped in transform).
    cust = rng.choice(customer_ids, size=n).astype(object)
    null_mask = rng.random(n) < 0.15
    cust[null_mask] = np.nan

    dates = pd.to_datetime("2025-01-01") + pd.to_timedelta(
        rng.integers(0, 365, size=n), unit="D"
    )
    amounts = np.round(rng.uniform(5, 500, size=n), 2)

    return pd.DataFrame(
        {
            "order_id": [f"ord_{i:04d}" for i in range(n)],
            "customer_id": cust,
            "order_date": dates.strftime("%Y-%m-%d"),
            "amount": amounts,
        }
    )


def main():
    DATA_DIR.mkdir(exist_ok=True)
    make_customers().to_csv(DATA_DIR / "customers.csv", index=False)
    make_orders().to_csv(DATA_DIR / "orders.csv", index=False)
    print(f"Wrote customers.csv and orders.csv to {DATA_DIR}")


if __name__ == "__main__":
    main()
