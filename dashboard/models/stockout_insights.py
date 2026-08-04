import pandas as pd

from components.db import stockout_and_predicted_income


def get_stockout_insights_df():
    """Return a pandas DataFrame with columns:
    - product_name
    - days_remaining (float)
    - stockout_risk (int, 0/1)
    - predicted_income (float)
    """
    rows = stockout_and_predicted_income()
    # rows expected as tuples in order: product_name, days_remaining, stockout_risk, predicted_income
    df = pd.DataFrame(rows, columns=["product_name", "days_remaining", "stockout_risk", "predicted_income"])
    # ensure types
    df["days_remaining"] = pd.to_numeric(df["days_remaining"], errors="coerce").fillna(0)
    df["stockout_risk"] = pd.to_numeric(df["stockout_risk"], errors="coerce").fillna(0).astype(int)
    df["predicted_income"] = pd.to_numeric(df["predicted_income"], errors="coerce").fillna(0.0)
    return df
