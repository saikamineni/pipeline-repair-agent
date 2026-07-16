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
df.loc[rng.choice(n, 60, replace=False), "customer_id"] = None  # dirty nulls on purpose
df.to_csv("data/orders.csv", index=False)