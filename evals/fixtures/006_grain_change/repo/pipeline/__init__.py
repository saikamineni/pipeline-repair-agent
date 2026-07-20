"""Pipeline orchestrator: extract -> transform -> load."""
from pipeline.extract import extract_orders, extract_customers
from pipeline.transform import transform
from pipeline.load import load
from pipeline.schema import RAW_ORDERS, CUSTOMERS, MONTHLY_REVENUE


def run_pipeline():
    orders = extract_orders()
    customers = extract_customers()
    # Validate inputs against the contract before transforming.
    RAW_ORDERS.validate(orders)
    CUSTOMERS.validate(customers)
    monthly = transform(orders, customers)
    return load(monthly)


__all__ = [
    "extract_orders",
    "extract_customers",
    "transform",
    "load",
    "run_pipeline",
    "RAW_ORDERS",
    "CUSTOMERS",
    "MONTHLY_REVENUE",
]
