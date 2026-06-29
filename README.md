# Smart Retail & Inventory Management System

An automated IoT-driven data pipeline that simulates real-time smart retail shelf weight sensors and store foot traffic counters. This project demonstrates a multi-database hybrid architecture (Polyglot Persistence), routing continuous high-velocity MQTT telemetry streams into optimized storage engines (**MySQL**, **MongoDB**, and **Neo4j**) based on data characteristics and analytical needs.

## 🏗️ System Architecture

```text
  [Python IoT Simulator] 
           │
           ▼ (MQTT Protocols)
   [Mosquitto Broker] (Port 1883)
           │
           ▼
 [Python Subscriber App]
   ├── 📊 MySQL      -> Structured Relational Store (Inventory, Sales, Alerts)
   ├── 🍃 MongoDB    -> High-Velocity Document Store (Raw Telemetry Streams)
   └── 🕸️ Neo4j      -> Dynamic Graph Network Engine (Supply Chain Analytics)
   ```
🗄️ Database Responsibilities

Instead of relying on a single database, this project distributes data tasks based on each system's native strengths:

    MySQL (Relational/Transactional): Manages core business records requiring strict data integrity and transactional safety. This includes exact product data, active suppliers, current stock thresholds, financial sales ledgers, and critical administrative system alerts.

    MongoDB (NoSQL Document): Seamlessly absorbs high-volume, rapid-fire JSON telemetry streams emitted from shelf weight scales and entry thresholds without introducing read/write bottlenecks to the main business app.

    Neo4j (Graph Network): Acts as an intelligent supply-chain dependency engine. It maps connections among Product, Category, and Supplier nodes. When a product's shelf weight drops below a critical threshold, the backend dynamically generates a volatile LOW_STOCK graph relationship, instantly flagging which upstream supplier must be contacted for immediate restocking.

🚀 Getting Started (Windows Setup)
Prerequisites

Ensure you have the following background services installed and running natively on Windows:

    Mosquitto MQTT Broker (Running on port 1883)

    XAMPP / MySQL (Apache & MySQL services active)

    MongoDB Community Server & Mongosh Shell

    Neo4j Desktop (Database active with your user configuration)

1. Database Configurations

    MySQL: Create a database named smart_retail. Import the table layouts provided in schema.sql via phpMyAdmin, and populate the base catalog details.

    Neo4j: Launch your local DBMS instance and execute the structural Cypher queries to build out your base product-to-vendor relational maps.

2. Dependencies

Install the required library modules using Python's package installer:
Bash

pip install paho-mqtt pymysql pymongo neo4j

3. Execution

Open two terminal windows side-by-side to launch the operational live loops:

    Start the central listening pipeline:
    Bash

    python subscriber.py

    Initiate the automated sensor broadcasting streams:
    Bash

    python publisher.py

📊 Live Demonstration & Queries

During active execution, verify your multi-database updates using the following commands:

    MySQL Ledger:
    SQL

    SELECT t.transaction_id, p.name, t.type, t.quantity, t.timestamp, i.current_stock 
    FROM transactions t
    JOIN products p ON t.product_id = p.product_id
    JOIN inventory i ON p.product_id = i.product_id
    ORDER BY t.timestamp DESC 
    LIMIT 10;

    MongoDB Aggregation: Run inside mongosh to isolate customer congestion milestones:
    JavaScript

    use smart_retail;
    db.foot_traffic.find({ count: { $gt: 10 } }).sort({ timestamp: -1 }).limit(5);

    Neo4j Graph Inference: View reactive automated retail restock alerts:
    Cypher

    MATCH (c:Category)<-[:BELONGS_TO]-(p:Product)-[r:LOW_STOCK]->(s:Supplier)
    RETURN c.name AS Category, p.name AS LowStockProduct, r.detected_at AS AlertTime, s.name
