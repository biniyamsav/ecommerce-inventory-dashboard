import random
from dashboard.components.connection import get_connection
from faker import Faker
from psycopg2.extras import execute_values

fake = Faker()

print("\n🔌 Connecting to Supabase PostgreSQL database...")
connect = get_connection()
cur = connect.cursor()

# -------------------------------------------------------------
# 0. TRUNCATE OLD DATA
# -------------------------------------------------------------
print("🧹 Cleaning out existing table data...")
cur.execute(
    "TRUNCATE TABLE order_items, orders, restock_events, inventory, products, warehouses, suppliers, customers RESTART IDENTITY CASCADE;"
)
connect.commit()
print("   ✓ All tables truncated successfully.")

# -------------------------------------------------------------
# CONFIG & SEED DATA
# -------------------------------------------------------------
categories = ["Electronics", "Clothing", "Home & Kitchen", "Toys", "Sports", "Beauty", "Books"]
statuses_order = ["pending", "shipped", "delivered", "cancelled"]
statuses_restock = ["delivered", "delayed"]

product_names = {
    "Electronics": [
        "Wireless Headphones", "USB-C Cable", "Phone Charger", "Laptop Stand", "Mechanical Keyboard",
        "Wireless Mouse", "Monitor Light Bar", "USB Hub", "Portable Speaker", "Smart Watch",
        "Bluetooth Earbuds", "Screen Protector", "Phone Case", "Power Bank", "External SSD",
        "Graphics Card", "Motherboard", "CPU Cooler", "RAM Memory Kit", "NVME Drive",
        "Camera Tripod", "Webcam HD", "Microphone", "Audio Interface", "HDMI Cable"
    ],
    "Clothing": [
        "Cotton T-Shirt", "Denim Jeans", "Wool Sweater", "Running Shoes", "Winter Jacket",
        "Summer Dress", "Sports Shorts", "Casual Polo", "Thermal Socks", "Hiking Boots",
        "Yoga Pants", "Sports Bra", "Baseball Cap", "Beanie Hat", "Leather Belt",
        "Flannel Shirt", "Cargo Pants", "Hoodie", "V-Neck Shirt", "Cargo Shorts"
    ],
    "Home & Kitchen": [
        "Coffee Maker", "Blender", "Toaster", "Rice Cooker", "Pressure Cooker",
        "Knife Set", "Cutting Board", "Mixing Bowls", "Baking Tray", "Kitchen Scale",
        "Pillow", "Bed Sheets", "Mattress Pad", "Bath Towel", "Shower Curtain",
        "Trash Can", "Vacuum Cleaner", "Mop Set", "Dish Rack", "Storage Organizer"
    ],
    "Toys": [
        "LEGO Set", "Puzzle Game", "Action Figure", "Teddy Bear", "Board Game",
        "Toy Car Set", "Building Blocks", "Doll House", "Remote Control Drone", "Inflatable Ball",
        "Yo-Yo", "Spinning Top", "Card Game", "Model Plane", "Wooden Train"
    ],
    "Sports": [
        "Dumbbells", "Yoga Mat", "Resistance Bands", "Jump Rope", "Running Belt",
        "Water Bottle", "Gym Bag", "Foam Roller", "Weight Plates", "Kettlebell",
        "Tennis Racket", "Basketball", "Soccer Ball", "Cycling Helmet", "Running Shoes"
    ],
    "Beauty": [
        "Face Moisturizer", "Shampoo", "Body Lotion", "Lip Balm", "Face Mask",
        "Eye Cream", "Foundation", "Mascara", "Lipstick", "Sunscreen SPF 50",
        "Hair Serum", "Face Wash", "Conditioner", "Night Cream", "Exfoliating Scrub"
    ],
    "Books": [
        "Python Programming", "Data Science Guide", "Fantasy Novel", "Mystery Thriller", "Self-Help Book",
        "Biography", "Science Fiction", "History Book", "Art Coffee Table", "Cookbook",
        "Travel Guide", "Business Strategy", "Graphic Novel", "Poetry Collection", "Children's Story"
    ]
}

# -------------------------------------------------------------
# 1. CUSTOMERS
# -------------------------------------------------------------
print("\n👤 Generating 2,000 Customers...")
customers_data = [
    (fake.name(), fake.state(), fake.date_between(start_date="-2y", end_date="today"))
    for _ in range(2000)
]
execute_values(
    cur,
    "INSERT INTO customers (name, region, signup_date) VALUES %s RETURNING id;",
    customers_data
)
customer_ids = [row[0] for row in cur.fetchall()]
connect.commit()
print("   ✓ Inserted 2,000 Customers.")

# -------------------------------------------------------------
# 2. SUPPLIERS
# -------------------------------------------------------------
print("🏭 Generating 30 Suppliers...")
suppliers_data = [(fake.company(),) for _ in range(30)]
execute_values(
    cur,
    "INSERT INTO suppliers (name) VALUES %s RETURNING id;",
    suppliers_data
)
supplier_ids = [row[0] for row in cur.fetchall()]
connect.commit()
print("   ✓ Inserted 30 Suppliers.")

# -------------------------------------------------------------
# 3. WAREHOUSES
# -------------------------------------------------------------
print("🏢 Generating 8 Warehouses...")
warehouses_data = [(fake.city() + " Warehouse", fake.state()) for _ in range(8)]
execute_values(
    cur,
    "INSERT INTO warehouses (name, region) VALUES %s RETURNING id;",
    warehouses_data
)
warehouse_ids = [row[0] for row in cur.fetchall()]
connect.commit()
print("   ✓ Inserted 8 Warehouses.")

# -------------------------------------------------------------
# 4. PRODUCTS
# -------------------------------------------------------------
print("📦 Generating 300 Products...")
products_data = []
for _ in range(300):
    category = random.choice(categories)
    name = random.choice(product_names[category])
    unit_cost = round(random.uniform(2, 200), 2)
    unit_price = round(unit_cost * random.uniform(1.2, 2.5), 2)
    discontinued = random.random() < 0.05
    products_data.append((name, category, unit_cost, unit_price, discontinued))

execute_values(
    cur,
    "INSERT INTO products (name, category, unit_cost, unit_price, discontinued) VALUES %s RETURNING id, unit_price;",
    products_data
)
inserted_products = cur.fetchall()
product_ids = [p[0] for p in inserted_products]
# Cache unit prices locally in Python so we do not need to query database in order_items
product_prices = {p[0]: p[1] for p in inserted_products}
connect.commit()
print("   ✓ Inserted 300 Products.")

# -------------------------------------------------------------
# 5. INVENTORY
# -------------------------------------------------------------
print("📊 Generating Inventory Records across all Warehouses...")
inventory_data = [
    (p_id, w_id, random.randint(0, 500), fake.date_between(start_date="-90d", end_date="today"))
    for p_id in product_ids
    for w_id in warehouse_ids
]
execute_values(
    cur,
    "INSERT INTO inventory (product_id, warehouse_id, stock_level, last_restocked) VALUES %s;",
    inventory_data
)
connect.commit()
print(f"   ✓ Inserted {len(inventory_data)} Inventory Records.")

# -------------------------------------------------------------
# 6. RESTOCK EVENTS
# -------------------------------------------------------------
print("🚚 Generating 8,000 Restock Events...")
restock_data = []
for _ in range(8000):
    supplier_id = random.choice(supplier_ids)
    product_id = random.choice(product_ids)
    warehouse_id = random.choice(warehouse_ids)
    quantity = random.randint(10, 1000)
    expected_date = fake.date_between(start_date="-1y", end_date="today")
    status = random.choice(statuses_restock)
    actual_date = expected_date if status == "delivered" else fake.date_between(start_date=expected_date, end_date="+10d")
    restock_data.append((supplier_id, product_id, warehouse_id, quantity, expected_date, actual_date, status))

execute_values(
    cur,
    "INSERT INTO restock_events (supplier_id, product_id, warehouse_id, quantity, expected_date, actual_date, status) VALUES %s;",
    restock_data
)
connect.commit()
print("   ✓ Inserted 8,000 Restock Events.")

# -------------------------------------------------------------
# 7. ORDERS
# -------------------------------------------------------------
print("🛒 Generating 40,000 Orders...")
orders_data = [
    (
        random.choice(customer_ids),
        fake.date_between(start_date="-1y", end_date="today"),
        random.choices(statuses_order, weights=[10, 15, 70, 5])[0]
    )
    for _ in range(40000)
]
execute_values(
    cur,
    "INSERT INTO orders (customer_id, order_date, status) VALUES %s RETURNING id;",
    orders_data
)
order_ids = [row[0] for row in cur.fetchall()]
connect.commit()
print("   ✓ Inserted 40,000 Orders.")

# -------------------------------------------------------------
# 8. ORDER ITEMS (BATCHED)
# -------------------------------------------------------------
print("🧾 Generating Order Line Items...")
order_items_data = []
for order_id in order_ids:
    num_items = random.randint(1, 4)
    for _ in range(num_items):
        product_id = random.choice(product_ids)
        warehouse_id = random.choice(warehouse_ids)
        quantity = random.randint(1, 5)
        price_at_sale = product_prices[product_id]  # Fetch directly from local cache
        order_items_data.append((order_id, product_id, quantity, price_at_sale, warehouse_id))

total_items = len(order_items_data)
print(f"   ↳ Bulk inserting ~{total_items:,} order items in chunks...")

# Insert order items in chunks of 20,000 to keep memory optimal
chunk_size = 20000
for i in range(0, total_items, chunk_size):
    chunk = order_items_data[i : i + chunk_size]
    execute_values(
        cur,
        "INSERT INTO order_items (order_id, product_id, quantity, price_at_sale, warehouse_fulfilled_from) VALUES %s;",
        chunk
    )
    connect.commit()
    inserted_so_far = min(i + chunk_size, total_items)
    print(f"     -> {inserted_so_far:,} / {total_items:,} items inserted...")

print(f"   ✓ Inserted all {total_items:,} Order Line Items.")

# -------------------------------------------------------------
# CLEANUP
# -------------------------------------------------------------
cur.close()
connect.close()

print("\n🚀 SUCCESS: Database successfully populated with realistic fake data!\n")