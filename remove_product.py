"""
remove_product.py
Removes a product from MySQL (inventory, transactions, sensor_alerts, products)
and Neo4j (node + all its relationships).
Remember to also remove it from publisher.py's `products` list afterward.
"""

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

# ── EDIT THIS VALUE ─────────────────────────────────────────
product_id = 104

# ── 1. MySQL: delete dependent rows first, then the product ─
mysql_cursor.execute("DELETE FROM sensor_alerts WHERE product_id = %s", (product_id,))
mysql_cursor.execute("DELETE FROM transactions WHERE product_id = %s", (product_id,))
mysql_cursor.execute("DELETE FROM inventory WHERE product_id = %s", (product_id,))
mysql_cursor.execute("DELETE FROM products WHERE product_id = %s", (product_id,))
mysql_conn.commit()
print(f"✅ MySQL: removed product id={product_id} and all related records")

# ── 2. Neo4j: delete node + all its relationships ────────────
with neo4j_driver.session() as session:
    session.run("""
        MATCH (p:Product {product_id: $pid})
        DETACH DELETE p
    """, pid=product_id)

print(f"✅ Neo4j: removed product node id={product_id} and its relationships")

mysql_conn.close()
neo4j_driver.close()

print(f"\nDone! Now remove product_id {product_id} from the `products` list in publisher.py.")
