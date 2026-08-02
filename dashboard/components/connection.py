import psycopg2
from psycopg2.pool import SimpleConnectionPool
import streamlit as st
from typing import Any


@st.cache_resource
def _get_pool():
    # create a small pool shared by the Streamlit session
    return SimpleConnectionPool(
        1,
        10,
        host="localhost",
        dbname="E_commerce_db",
        user="postgres",
        password="112123",
        port=5432,
    )


def get_connection() -> Any:
    """Return a connection-like object sourced from a pooled connection.

    The returned object proxies to the raw psycopg2 connection but overrides
    `close()` to return the connection to the pool (so existing code that
    calls `con.close()` continues to work).
    """
    pool = _get_pool()
    raw = pool.getconn()

    class _PooledWrapper:
        def __init__(self, raw_conn, pool_ref):
            self._raw = raw_conn
            self._pool = pool_ref

        def cursor(self, *args, **kwargs):
            return self._raw.cursor(*args, **kwargs)

        def close(self):
            try:
                self._pool.putconn(self._raw)
            except Exception:
                try:
                    self._raw.close()
                except Exception:
                    pass

        def __getattr__(self, name):
            return getattr(self._raw, name)

    return _PooledWrapper(raw, pool)
# .venv\Scripts\activate
# Overview
# revenue_per_month_last_12_months (headline + trend)

# average_order_value
# low_stock_products / out_of_stock_products (count)
# top_revenue_category
# on_time_delivery_rate_per_supplier (worst one)
# new_customers_last_month

# Sales Performance

# top_10_products_by_revenue
# revenue_per_month_last_12_months
# top_revenue_category
# average_order_value
# top_revenue_region
# pct_cancelled_vs_delivered
# rolling_7_30_day_sales_per_product
# top_selling_product_per_month_last_12_months
# highest_order_volume_day_of_week
# highest_revenue_quarter

# Inventory Health

# stock_level_per_product_per_warehouse
# out_of_stock_products
# low_stock_products
# not_restocked_in_last_30_days
# overstocked_products
# stock_turnover_rate_per_product
# days_until_stockout
# discontinued_with_remaining_stock

# Warehouse Performance

# orders_fulfilled_per_warehouse
# revenue_fulfilled_per_warehouse
# warehouse_highest_stockout_frequency
# warehouse_most_dead_stock
# stock_level_comparison_across_warehouses
# warehouse_fastest_fulfillment

# Supplier Performance

# on_time_delivery_rate_per_supplier
# average_delay_days_per_supplier
# supplier_most_delayed_deliveries
# products_relying_on_least_reliable_suppliers
# supplier_on_time_rate_trend_last_6_months
# supplier_highest_total_quantity_delivered

# Customer Analytics

# top_20_customers_by_spend
# region_highest_avg_order_value
# new_customers_last_month
# one_time_customers
# order_frequency_distribution

# Product Analytics

# profit_margin_per_product
# category_highest_avg_profit_margin
# products_never_ordered
# product_rank_by_revenue_within_category