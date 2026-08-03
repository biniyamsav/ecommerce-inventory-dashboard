import random
from dashboard.components.connection import get_connection
from faker import Faker

fake = Faker()
connect = get_connection()
cur = connect.cursor()

cur.execute("TRUNCATE TABLE order_items, orders, restock_events, inventory, products, warehouses, suppliers, customers RESTART IDENTITY CASCADE;")

categories = ["Electronics", "Clothing", "Home & Kitchen", "Toys", "Sports", "Beauty", "Books"]
statuses_order = ["pending", "shipped", "delivered", "cancelled"]
statuses_restock = ["delivered", "delayed"]

# customers
customer_ids = []
for i in range(2000):
    name = fake.name()
    region = fake.state()
    signup_date = fake.date_between(start_date="-2y", end_date="today")
    cur.execute("INSERT INTO customers (name, region, signup_date) VALUES (%s,%s,%s) RETURNING id", (name, region, signup_date))
    customer_ids.append(cur.fetchone()[0])

# suppliers
supplier_ids = []
for i in range(30):
    name = fake.company()
    cur.execute("INSERT INTO suppliers (name) VALUES (%s) RETURNING id", (name,))
    supplier_ids.append(cur.fetchone()[0])

# warehouses
warehouse_ids = []
for i in range(8):
    name = fake.city() + " Warehouse"
    region = fake.state()
    cur.execute("INSERT INTO warehouses (name, region) VALUES (%s,%s) RETURNING id", (name, region))
    warehouse_ids.append(cur.fetchone()[0])

# products
product_ids = []
for i in range(300):
    name = fake.word().capitalize() + " " + fake.word().capitalize()
    category = random.choice(categories)
    unit_cost = round(random.uniform(2, 200), 2)
    unit_price = round(unit_cost * random.uniform(1.2, 2.5), 2)
    discontinued = random.random() < 0.05
    cur.execute("INSERT INTO products (name, category, unit_cost, unit_price, discontinued) VALUES (%s,%s,%s,%s,%s) RETURNING id", (name, category, unit_cost, unit_price, discontinued))
    product_ids.append(cur.fetchone()[0])

# inventory
for product_id in product_ids:
    for warehouse_id in warehouse_ids:
        stock_level = random.randint(0, 500)
        last_restocked = fake.date_between(start_date="-90d", end_date="today")
        cur.execute("INSERT INTO inventory (product_id, warehouse_id, stock_level, last_restocked) VALUES (%s,%s,%s,%s)", (product_id, warehouse_id, stock_level, last_restocked))

# restock_events
for i in range(8000):
    supplier_id = random.choice(supplier_ids)
    product_id = random.choice(product_ids)
    warehouse_id = random.choice(warehouse_ids)
    quantity = random.randint(10, 1000)
    expected_date = fake.date_between(start_date="-1y", end_date="today")
    status = random.choice(statuses_restock)
    actual_date = expected_date if status == "delivered" else fake.date_between(start_date=expected_date, end_date="+10d")
    cur.execute("INSERT INTO restock_events (supplier_id, product_id, warehouse_id, quantity, expected_date, actual_date, status) VALUES (%s,%s,%s,%s,%s,%s,%s)", (supplier_id, product_id, warehouse_id, quantity, expected_date, actual_date, status))

# orders
order_ids = []
for i in range(40000):
    customer_id = random.choice(customer_ids)
    order_date = fake.date_between(start_date="-1y", end_date="today")
    status = random.choices(statuses_order, weights=[10, 15, 70, 5])[0]
    cur.execute("INSERT INTO orders (customer_id, order_date, status) VALUES (%s,%s,%s) RETURNING id", (customer_id, order_date, status))
    order_ids.append(cur.fetchone()[0])

# order_items
for order_id in order_ids:
    num_items = random.randint(1, 4)
    for j in range(num_items):
        product_id = random.choice(product_ids)
        warehouse_id = random.choice(warehouse_ids)
        quantity = random.randint(1, 5)
        cur.execute("SELECT unit_price FROM products WHERE id=%s", (product_id,))
        price_at_sale = cur.fetchone()[0]
        cur.execute("INSERT INTO order_items (order_id, product_id, quantity, price_at_sale, warehouse_fulfilled_from) VALUES (%s,%s,%s,%s,%s)", (order_id, product_id, quantity, price_at_sale, warehouse_id))

connect.commit()
cur.close()
connect.close()

print("done")