import paho.mqtt.client as mqtt
import json
import time
import random
from datetime import datetime

BROKER = "localhost"
PORT = 1883

products = [
    {"product_id": 101, "name": "Orange Juice", "sensor_id": "SHELF-A1", "min": 0.5, "max": 5.0},
    {"product_id": 102, "name": "Chips",        "sensor_id": "SHELF-B1", "min": 0.3, "max": 3.0},
    {"product_id": 103, "name": "Milk",         "sensor_id": "SHELF-C1", "min": 0.5, "max": 4.0},
]

client = mqtt.Client()
client.connect(BROKER, PORT)

print("Publisher started. Sending sensor data every 3 seconds...\n")

while True:
    # Shelf weight sensor readings
    for product in products:
        weight = round(random.uniform(product["min"], product["max"]), 2)
        payload = {
            "sensor_id": product["sensor_id"],
            "type": "weight",
            "product_id": product["product_id"],
            "product_name": product["name"],
            "value": weight,
            "unit": "kg",
            "timestamp": datetime.now().isoformat()
        }
        client.publish("retail/sensors/weight", json.dumps(payload))
        print(f"[WEIGHT] {product['name']} → {weight} kg")

    # Foot traffic sensor
    foot_traffic = {
        "sensor_id": "ENTRY-01",
        "type": "foot_traffic",
        "count": random.randint(1, 20),
        "timestamp": datetime.now().isoformat()
    }
    client.publish("retail/sensors/traffic", json.dumps(foot_traffic))
    print(f"[TRAFFIC] Entry count → {foot_traffic['count']}")

    print("---")
    time.sleep(3)