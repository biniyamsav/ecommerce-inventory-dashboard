from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from dashboard.components.db import product_weekly_sales
def demand_forecast_model():
    data=product_weekly_sales()
    print(data)



demand_forecast_model()