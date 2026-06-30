
import pymysql
from neo4j import GraphDatabase

# ── Connections ──────────────────────────────────────────
mysql_conn = pymysql.connect(
    host="localhost", user="root", password="", database="smart_retail"
)
mysql_cursor = mysql_conn.cursor()

neo4j_driver = GraphDatabase.driver(
    "bolt://127.0.0.1:7687",
    auth=("neo4j", "blasterdark1_")
)

# ── EDIT THESE VALUES FOR THE NEW PRODUCT ──────────────────
product_id     = 105
name           = "Cola"
price          = 2.20
unit           = "kg"
category_name  = "Beverages"   # must already exist in MySQL + Neo4j
supplier_id    = 1             # must already exist in MySQL
supplier_name  = "FreshCo"     # must already exist in Neo4j (matching name)
current_stock  = 3.0
min_threshold  = 1.0
max_capacity   = 5.0

# ── 1. MySQL: insert into products + inventory ─────────────
mysql_cursor.execute("""
    SELECT category_id FROM categories WHERE name = %s
""", (category_name,))
category_row = mysql_cursor.fetchone()
if not category_row:
    raise Exception(f"Category '{category_name}' not found in MySQL.")
category_id = category_row[0]

mysql_cursor.execute("""
    INSERT INTO products (product_id, name, category_id, supplier_id, price, unit)
    VALUES (%s, %s, %s, %s, %s, %s)
""", (product_id, name, category_id, supplier_id, price, unit))

mysql_cursor.execute("""
    INSERT INTO inventory (product_id, current_stock, min_threshold, max_capacity)
    VALUES (%s, %s, %s, %s)
""", (product_id, current_stock, min_threshold, max_capacity))

mysql_conn.commit()
print(f"✅ MySQL: added product '{name}' (id={product_id}) to products + inventory")

# ── 2. Neo4j: create node + relationships ──────────────────
with neo4j_driver.session() as session:
    session.run("""
        CREATE (:Product {product_id: $pid, name: $name, price: $price})
    """, pid=product_id, name=name, price=price)

    session.run("""
        MATCH (p:Product {product_id: $pid}), (c:Category {name: $cat})
        CREATE (p)-[:BELONGS_TO]->(c)
    """, pid=product_id, cat=category_name)

    session.run("""
        MATCH (s:Supplier {name: $sup}), (p:Product {product_id: $pid})
        CREATE (s)-[:SUPPLIES]->(p)
    """, sup=supplier_name, pid=product_id)

print(f"✅ Neo4j: created node + relationships for '{name}'")

mysql_conn.close()
neo4j_driver.close()

print(f"\nDone! Now add this to the `products` list in publisher.py to start generating sensor data:\n")
print(f'{{"product_id": {product_id}, "name": "{name}", "sensor_id": "SHELF-D1", "min": 0.3, "max": {max_capacity}}}')
