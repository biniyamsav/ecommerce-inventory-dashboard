import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression


def demand_forecast_model(data):
    df = pd.DataFrame(
        data,
        columns=[
            "product_id",
            "product_name",
            "week_start",
            "units_sold",
            "revenue",
        ],
    )
    df["week_start"] = pd.to_datetime(df["week_start"])
    df["month"] = df["week_start"].dt.month
    df["week_of_year"] = df["week_start"].dt.isocalendar().week

    prediction_with_name = {}

    # Group by product_id and product_name together
    grouped = df.groupby(["product_id", "product_name"])

    for (product_id, product_name), product_df in grouped:
        # Sort chronologically by date
        product_df = product_df.sort_values(by="week_start")

        # Guard Clause: Need at least 2 data points for a line fit
        if len(product_df) < 2:
            # Fallback to mean sales if not enough history to fit a trend
            fallback_val = (
                product_df["units_sold"].iloc[0] if len(product_df) == 1 else 0
            )
            prediction_with_name[product_name] = max(0, round(fallback_val, 2))
            continue

        X = product_df[["month", "week_of_year"]]
        y = product_df["units_sold"]

        # Train on all historical data for this product (no train_test_split inside small groups)
        model = LinearRegression()
        model.fit(X, y)

        future_weeks = pd.DataFrame({"month": [1], "week_of_year": [1]})

        future_pred = model.predict(future_weeks)[0]

        # Prevent negative demand predictions
        prediction_with_name[product_name] = max(0, round(future_pred, 2))

    return prediction_with_name