import pandas as pd


def extract(path="data/orders.csv"):
    return pd.read_csv(path)


def extract_customers(path="data/customers.csv"):
    return pd.read_csv(path)
