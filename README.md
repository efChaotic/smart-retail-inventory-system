# Smart Retail & Inventory Management System

An automated IoT-driven data pipeline that simulates real-time smart retail shelf weight sensors and store foot traffic counters. This project demonstrates a multi-database hybrid architecture (Polyglot Persistence), routing continuous high-velocity MQTT telemetry streams into optimized storage engines (**MySQL**, **MongoDB**, and **Neo4j**) based on data characteristics and analytical needs. A live dashboard visualizes all three databases updating in real time.

## 🏗️ System Architecture

```
 [Python IoT Simulator] (publisher.py)
          │
          ▼ (MQTT Protocol)
  [Mosquitto Broker] (Port 1883)
          │
          ▼
[Python Subscriber App] (subscriber.py)
  ├── 📊 MySQL      -> Structured Relational Store (Inventory, Sales, Alerts)
  ├── 🍃 MongoDB    -> High-Velocity Document Store (Raw Telemetry Streams)
  └── 🕸️ Neo4j      -> Dynamic Graph Network Engine (Supply Chain Analytics)
          │
          ▼
  [Flask API] (app.py) ──► [Live Dashboard] (index.html)
```

## 🗄️ Database Responsibilities

Instead of relying on a single database, this project distributes data tasks based on each system's native strengths:

- **MySQL (Relational/Transactional):** Manages core business records requiring strict data integrity and transactional safety. This includes product data, active suppliers, current stock thresholds, sales/restock transaction ledgers, and low-stock system alerts.

- **MongoDB (NoSQL Document):** Absorbs high-volume, rapid-fire JSON telemetry streams from shelf weight sensors and entry traffic counters without introducing read/write bottlenecks to the relational layer.

- **Neo4j (Graph Network):** Acts as a supply-chain dependency engine, mapping connections among `Product`, `Category`, and `Supplier` nodes. When a product's shelf weight drops below threshold, the backend dynamically creates a timestamped `LOW_STOCK` relationship between the product and its supplier, flagging exactly who to contact for restocking.

## 📁 Project Files

| File | Purpose |
|---|---|
| `publisher.py` | Simulates IoT sensors — publishes weight + foot traffic readings via MQTT every 3 seconds |
| `subscriber.py` | Subscribes to MQTT topics, routes data into MySQL, MongoDB, and Neo4j |
| `schema.sql` | MySQL table definitions (categories, suppliers, products, inventory, transactions, sensor_alerts) |
| `app.py` | Flask API serving live data from all three databases |
| `index.html` | Live dashboard — visualizes inventory, sensor feed, supplier graph, transactions, alerts in real time |
| `add_product.py` | Adds a new product to MySQL + Neo4j in one run |
| `remove_product.py` | Removes a product and all its related records from MySQL + Neo4j |

## 🚀 Getting Started (Windows Setup)

### Prerequisites

Ensure you have the following installed and running natively on Windows:

- **Mosquitto MQTT Broker** (running on port 1883)
- **XAMPP / MySQL** (Apache & MySQL services active)
- **MongoDB Community Server** & **mongosh** shell
- **Neo4j Desktop** (local DBMS instance active)
- **Python 3** with required libraries

### 1. Database Configuration

**MySQL:** Create a database named `smart_retail`. Import the table layout from `schema.sql` via phpMyAdmin, then populate base catalog data (categories, suppliers, products, inventory).

**Neo4j:** Launch your local DBMS instance and run the Cypher setup queries to build the base `Product` → `Category`/`Supplier` relationship graph.

### 2. Install Dependencies

```bash
pip install paho-mqtt pymysql pymongo neo4j flask flask-cors
```

### 3. Run the Pipeline

Open separate terminals (or Windows Terminal tabs) for each process:

```bash
# Terminal 1 — start the listener first
python subscriber.py

# Terminal 2 — start the sensor simulator
python publisher.py

# Terminal 3 — start the dashboard API
python app.py
```

Then open `index.html` in your browser to view the live control room dashboard.

### 4. Managing Products

Add a new product across MySQL and Neo4j in one step:
```bash
python add_product.py
```

Remove a product and all related records:
```bash
python remove_product.py
```

After either, manually update the `products` list inside `publisher.py` to start/stop sensor simulation for that product.

## 📊 Live Demonstration & Queries

**MySQL — Transaction ledger with live stock levels:**
```sql
SELECT t.transaction_id, p.name, t.type, t.quantity, t.timestamp, i.current_stock
FROM transactions t
JOIN products p ON t.product_id = p.product_id
JOIN inventory i ON p.product_id = i.product_id
ORDER BY t.timestamp DESC
LIMIT 10;
```

**MongoDB — Recent foot traffic spikes:**
```javascript
use smart_retail;
db.foot_traffic.find({ count: { $gt: 10 } }).sort({ timestamp: -1 }).limit(5);
```

**Neo4j — Active low-stock supplier alerts:**
```cypher
MATCH (c:Category)<-[:BELONGS_TO]-(p:Product)-[r:LOW_STOCK]->(s:Supplier)
RETURN c.name AS Category, p.name AS LowStockProduct, r.detected_at AS AlertTime, s.name AS Supplier
ORDER BY r.detected_at DESC
LIMIT 10;
```

## 🖥️ Live Dashboard

The dashboard (`index.html` + `app.py`) shows six live panels, refreshing every 3 seconds:
- Shelf Inventory (MySQL)
- Raw Sensor Feed (MongoDB)
- Supplier Links (Neo4j)
- Transaction Log (MySQL)
- Foot Traffic (MongoDB)
- Low Stock Alerts (MySQL)

A pulse strip at the top ticks on every refresh — amber when an active low-stock alert exists, cyan otherwise.

## ⚠️ Notes
- `LOW_STOCK` relationships accumulate over time as the subscriber runs continuously — periodically clear them with `MATCH ()-[r:LOW_STOCK]->() DELETE r` if the graph becomes visually cluttered.
