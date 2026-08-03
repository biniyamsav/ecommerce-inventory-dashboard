from models.demand_forecast import demand_forecast_model
from components.db import product_weekly_sales
import streamlit as st

import pandas as pd
import plotly.express as px


def predictive_page():
    st.title("📈 Predictive Analytics")
    st.caption("Forecasted demand for the first week of next year, based on historical sales patterns.")

    data = product_weekly_sales()
    predictions = demand_forecast_model(data)

    # Convert predictions into a DataFrame for easier display
    df = pd.DataFrame(
        list(predictions.items()),
        columns=["Product", "Predicted Units Sold"]
    ).sort_values(by="Predicted Units Sold", ascending=False)

    # --- Top-level metrics ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Products Forecasted", len(df))
    col2.metric("Avg Predicted Units", f"{df['Predicted Units Sold'].mean():.1f}")
    col3.metric("Top Product", df.iloc[0]["Product"])

    st.divider()

    # --- Chart ---
    st.subheader("Top 10 Products by Predicted Demand")
    top10 = df.head(10)
    fig = px.bar(
        top10,
        x="Predicted Units Sold",
        y="Product",
        orientation="h",
        color="Predicted Units Sold",
        color_continuous_scale="Blues",
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"}, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # --- Full table ---
    st.subheader("Full Forecast Table")
    st.dataframe(
        df.style.format({"Predicted Units Sold": "{:.2f}"}),
        use_container_width=True,
        hide_index=True,
    )