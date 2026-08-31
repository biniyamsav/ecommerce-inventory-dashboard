# E-Commerce Inventory & Performance Analytics System

A full-stack analytics dashboard for e-commerce operations, built end to end: PostgreSQL schema design, 40+ SQL analytics queries, a multi-page Streamlit dashboard, and machine learning models for demand forecasting and stockout risk.

## Overview

This project analyzes a simulated e-commerce business (2,000 customers, 300 products, 40,000+ orders across 8 warehouses and 30 suppliers) to answer real operational questions: What's selling? What's about to run out? Which suppliers are unreliable? What will demand look like next week?

The system moves through three layers — Analysis, Management, and Predictive — mirroring how a real analytics team would work: understand the data, act on it, then forecast ahead of it.

## Features

**Analysis**
- Sales performance: revenue trends, top products, seasonal patterns, rolling sales windows
- Product insights: profit margins, category performance, unordered stock
- Customer insights: top spenders, order frequency, regional trends

**Management**
- Inventory health: stock levels, stockout risk, overstocked products, turnover rates
- Warehouse performance: fulfillment volume, dead stock, delivery speed by location
- Supplier performance: on-time delivery rates, delay trends, reliability scoring

**Predictive**
- Demand forecasting: predicts next-week sales per product using historical weekly sales, built with scikit-learn linear regression
- Stockout risk classification: flags products likely to run out based on current stock, sales velocity, and supplier lead times

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| Database | PostgreSQL (hosted on Supabase) |
| Backend | Python, psycopg2 (connection pooling) |
| ML | scikit-learn |
| Data processing | Pandas, NumPy |
| Visualization | Plotly |
| Test data | Faker |

## Database Schema

Eight tables: `products`, `warehouses`, `suppliers`, `inventory`, `restock_events`, `orders`, `order_items`, `customers`. Designed with composite primary keys for inventory tracking, `NUMERIC` types for monetary precision, and separate `expected_date`/`actual_date` fields on restock events to support delay analysis.

## Project Structure

```
E_commerceInventoryPerformanceAnalyticsSystem/
├── fake.py                    # Test data generator
├── dashboard/
│   ├── app.py                 # Entry point
│   ├── app_pages/             # One file per dashboard page
│   ├── components/            # DB connection, queries, charts, shared UI
│   ├── models/                # ML models (demand forecast, stockout risk)
│   ├── utils/                 # Styling and helpers
│   └── .streamlit/
│       └── secrets.toml       # Database credentials (gitignored)
```

## Getting Started

**Prerequisites:** Python 3.9+, a PostgreSQL database (a free Supabase project works well)

```bash
git clone https://github.com/yourusername/ecommerce-inventory-analytics.git
cd ecommerce-inventory-analytics

python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
```

Create `dashboard/.streamlit/secrets.toml`:
```toml
[db]
host = "your-db-host"
port = 5432
dbname = "postgres"
user = "your-db-user"
password = "your-db-password"
```

Generate test data (optional, if starting from an empty database):
```bash
python fake.py
```

Run the dashboard:
```bash
cd dashboard
streamlit run app.py
```

## Design Notes

- **Connection pooling**: uses `psycopg2.pool.SimpleConnectionPool` wrapped in a Streamlit-cached resource, so every query correctly returns its connection after use rather than opening a new one each time.
- **Query design**: analytics queries favor dynamic thresholds (percentiles, rolling averages) over hardcoded cutoffs, so results stay meaningful as the underlying data changes.
- **Forecast horizon**: the demand model predicts one week ahead rather than further out — with 12 months of historical data, short-horizon forecasts are more defensible than long-range ones, and the output directly supports the stockout-risk workflow.

## Roadmap

- Customer churn prediction and lifetime value estimation
- Supplier delay prediction
- Deployed live demo link

## Author

Your Name — [GitHub](https://github.com/biniyamsav) · [LinkedIn](linkedin.com/in/biniyam-worku-663a1432b)
