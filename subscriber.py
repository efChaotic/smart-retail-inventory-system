import paho.mqtt.client as mqtt
import json
import pymysql
import pymongo
from neo4j import GraphDatabase
from datetime import datetime

# ── MySQL ──────────────────────────────────────────
mysql_conn = pymysql.connect(
    host="localhost",
    user="root",
    password="",
    database="smart_retail"
)
mysql_cursor = mysql_conn.cursor()

# ── MongoDB ────────────────────────────────────────
mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
mongo_db = mongo_client["smart_retail"]

# ── Neo4j ──────────────────────────────────────────
neo4j_driver = GraphDatabase.driver(
    "neo4j://127.0.0.1:7687",
    auth=("neo4j", "blasterdark1_")
)

LOW_STOCK_THRESHOLD = 1.0

# ── Simulated supplier notification ────────────────
def notify_supplier(supplier_name, supplier_email, product_name, current_value):
    """
    Simulates contacting a supplier to request restock.
    In a real deployment this would call an email API (e.g. SendGrid) or SMS service.
    For this project, it logs the action and writes a record to MySQL for traceability.
    """
    print(f"  📧 SUPPLIER NOTIFIED: {supplier_name} ({supplier_email}) "
          f"— restock request for '{product_name}' (currently {current_value} kg)")

    try:
        mysql_cursor.execute("""
            INSERT INTO sensor_alerts (sensor_id, product_id, alert_type, message, timestamp)
            VALUES (%s, %s, 'SUPPLIER_NOTIFIED', %s, %s)
        """, ("SYSTEM", None, f"Notified {supplier_name} ({supplier_email}) to restock {product_name}",
              datetime.now().isoformat()))
        mysql_conn.commit()
    except Exception as e:
        print(f"❌ Failed to log supplier notification: {e}")

# ── Handlers ───────────────────────────────────────
def handle_weight(data):
    product_id = data["product_id"]
    value      = data["value"]
    sensor_id  = data["sensor_id"]
    timestamp  = data["timestamp"]

    # MongoDB — store raw reading
    try:
        mongo_db["sensor_readings"].insert_one(data)
    except Exception as e:
        print(f"❌ MongoDB Error: {e}")

    # MySQL — update inventory
    try:
        mysql_cursor.execute("""
            UPDATE inventory SET current_stock = %s, last_updated = %s
            WHERE product_id = %s
        """, (value, timestamp, product_id))

        # MySQL — log as transaction
        mysql_cursor.execute("""
            INSERT INTO transactions (product_id, type, quantity, timestamp)
            VALUES (%s, 'sale', %s, %s)
        """, (product_id, value, timestamp))

        mysql_conn.commit()
    except Exception as e:
        print(f"❌ MySQL Error (Inventory/Transaction): {e}")

    # Low stock alert
    if value < LOW_STOCK_THRESHOLD:
        print(f"  ⚠ LOW STOCK: product {product_id} at {value} kg")

        # MySQL — log alert
        try:
            mysql_cursor.execute("""
                INSERT INTO sensor_alerts (sensor_id, product_id, alert_type, message, timestamp)
                VALUES (%s, %s, 'LOW_STOCK', %s, %s)
            """, (sensor_id, product_id, f"Stock below threshold: {value} kg", timestamp))
            mysql_conn.commit()
        except Exception as e:
            print(f"❌ MySQL Error (Alert logging): {e}")

        # Neo4j — create LOW_STOCK relationship safely, then fetch supplier to "contact"
        try:
            with neo4j_driver.session() as session:
                session.run("""
                    MATCH (p:Product {product_id: $pid})-[:BELONGS_TO]->(c:Category)
                    MATCH (s:Supplier)-[:SUPPLIES]->(p)
                    MERGE (p)-[:LOW_STOCK {detected_at: $ts}]->(s)
                """, pid=product_id, ts=timestamp)

                # Fetch the supplier's contact info so we can "notify" them
                result = session.run("""
                    MATCH (s:Supplier)-[:SUPPLIES]->(p:Product {product_id: $pid})
                    RETURN s.name AS name, s.email AS email
                """, pid=product_id)
                supplier = result.single()
                if supplier:
                    notify_supplier(supplier["name"], supplier["email"], data.get("product_name", "Unknown"), value)
        except Exception as e:
            print(f"❌ Failed to log low stock to Neo4j: {e}")

def handle_traffic(data):
    # MongoDB only
    try:
        mongo_db["foot_traffic"].insert_one(data)
    except Exception as e:
        print(f"❌ MongoDB Traffic Log Error: {e}")

# ── MQTT Callbacks ─────────────────────────────────
def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker")
    client.subscribe("retail/sensors/weight")
    client.subscribe("retail/sensors/traffic")

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        topic = msg.topic

        if topic == "retail/sensors/weight":
            handle_weight(data)
            print(f"  [DB] Stored weight reading for product {data['product_id']}")
        elif topic == "retail/sensors/traffic":
            handle_traffic(data)
            print(f"  [DB] Stored foot traffic count: {data['count']}")
    except Exception as e:
        print(f"❌ Error parsing incoming MQTT message: {e}")

# ── Start ──────────────────────────────────────────
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

try:
    client.connect("localhost", 1883)
    print("Subscriber started. Waiting for sensor data...\n")
    client.loop_forever()
except Exception as e:
    print(f"❌ Failed to start MQTT Subscriber: {e}")