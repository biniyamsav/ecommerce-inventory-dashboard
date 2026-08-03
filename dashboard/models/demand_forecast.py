from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from components.db import product_weekly_sales
import pandas as pd
import numpy as np


def demand_forecast_model(data):
    df = pd.DataFrame(
        data,
        columns=[
            "product_id",
            "product_name",
            "week_start",
            "units_sold",
            "revenue"
        ]
    )
    df["week_start"] = pd.to_datetime(df["week_start"])
    df["month"] = df["week_start"].dt.month
    df["week_of_year"] = df["week_start"].dt.isocalendar().week
    grouped = df.groupby("product_id")
    predictions = {}
    for product_id, product_df in grouped:
        product_df = product_df.sort_values(by=["month", "week_of_year"])
        X = product_df[["month", "week_of_year"]]
        y = product_df["units_sold"]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = LinearRegression()
        model.fit(X_train, y_train)
        future_weeks = pd.DataFrame({
            "month": [1],
            "week_of_year": [1]
        })
        future_predictions = model.predict(future_weeks)
        predictions[product_id] = future_predictions
    prediction_with_name={}
    for product_id, prediction in predictions.items():
        product_name = df[df["product_id"] == product_id]["product_name"].iloc[0]
        prediction_with_name[product_name] = prediction[0]
        print(f"Product: {product_name}, Predicted Units Sold for Week 1 of Next Year: {prediction[0]}")
    return prediction_with_name



