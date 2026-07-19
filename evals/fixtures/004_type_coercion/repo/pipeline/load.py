"""Load stage: validate the final frame and write it out.

MUTABLE in fixtures, though bugs here are rarer.
"""
from pathlib import Path
import pandas as pd
from pipeline.schema import MONTHLY_REVENUE

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data"


def load(monthly: pd.DataFrame, path: Path | str | None = None) -> pd.DataFrame:
    validated = MONTHLY_REVENUE.validate(monthly)
    path = Path(path) if path else OUTPUT_DIR / "monthly_revenue.csv"
    validated.to_csv(path, index=False)
    return validated
