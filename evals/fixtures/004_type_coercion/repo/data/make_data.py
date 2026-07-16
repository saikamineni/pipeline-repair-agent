import numpy as np, pandas as pd
rng = np.random.default_rng(42)

n = 200
df = pd.DataFrame({
    "order_id":    [f"ord_{i:04d}" for i in range(n)],
    "customer_id": rng.choice([f"cust_{i}" for i in range(20)], n),
    "amount":      rng.uniform(5, 500, n).round(2),
    "currency":    rng.choice(["USD", "EUR", "INR"], n, p=[.6, .2, .2]),
    "order_date":  pd.to_datetime("2025-01-01") + pd.to_timedelta(rng.integers(0, 365, n), "D"),
    "status":      rng.choice(["placed", "SHIPPED", "shipped", "cancelled"], n),  # dirty case on purpose
})
df.loc[rng.choice(n, 8, replace=False), "customer_id"] = None  # dirty nulls on purpose

df["amount"] = df["amount"].astype(object)
dirty_idx = rng.choice(n, 5, replace=False)
df.loc[dirty_idx, "amount"] = df.loc[dirty_idx, "amount"].apply(lambda v: f"${v:.2f}")  # dirty currency-prefixed amounts on purpose

df.to_csv("data/orders.csv", index=False)