import duckdb


def load(df, db_path="data/warehouse.duckdb", table="monthly_revenue"):
    con = duckdb.connect(db_path)
    con.execute(f"CREATE OR REPLACE TABLE {table} AS SELECT * FROM df")
    con.close()
    return db_path
