import db
import pandas as pd


total=db.average_order_value()
total_df = pd.DataFrame(total, columns=['Average Order Value'])


print(total_df)