import pandas as pd


def extract(path="data/orders.csv"):
    return pd.read_csv(path)
