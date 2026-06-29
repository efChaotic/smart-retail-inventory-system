CREATE DATABASE IF NOT EXISTS smart_retail;
USE smart_retail;

-- Categories Table
CREATE TABLE categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT
);

-- Suppliers Table
CREATE TABLE suppliers (
    supplier_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    contact_email VARCHAR(100),
    phone VARCHAR(20),
    address TEXT
);

-- Products Table
CREATE TABLE products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category_id INT,
    supplier_id INT,
    price DECIMAL(10, 2),
    unit VARCHAR(20),
    FOREIGN KEY (category_id) REFERENCES categories(category_id),
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
);

-- Inventory Table
CREATE TABLE inventory (
    inventory_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT UNIQUE,
    current_stock DECIMAL(10, 2),
    min_threshold DECIMAL(10, 2),
    max_capacity DECIMAL(10, 2),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Transactions Table
CREATE TABLE transactions (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT,
    type ENUM('sale', 'restock') NOT NULL,
    quantity DECIMAL(10, 2),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Sensor Alerts Table
CREATE TABLE sensor_alerts (
    alert_id INT AUTO_INCREMENT PRIMARY KEY,
    sensor_id VARCHAR(50),
    product_id INT,
    alert_type VARCHAR(50),
    message TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Populate Base Catalog Data
INSERT INTO categories (category_id, name, description) VALUES 
(1, 'Beverages', 'Drinks and juices'),
(2, 'Snacks', 'Chips and snacks'),
(3, 'Dairy', 'Milk and dairy products');

INSERT INTO suppliers (supplier_id, name, contact_email, phone, address) VALUES 
(1, 'FreshCo', 'freshco@email.com', '111', 'Address 1'),
(2, 'SnackWorld', 'snackworld@email.com', '222', 'Address 2'),
(3, 'DairyPlus', 'dairyplus@email.com', '333', 'Address 3');

INSERT INTO products (product_id, name, category_id, supplier_id, price, unit) VALUES 
(101, 'Orange Juice', 1, 1, 2.50, 'kg'),
(102, 'Chips', 2, 2, 1.99, 'kg'),
(103, 'Milk', 3, 3, 1.50, 'kg');

INSERT INTO inventory (product_id, current_stock, min_threshold, max_capacity) VALUES 
(101, 5.00, 1.00, 10.00),
(102, 3.00, 1.00, 5.00),
(103, 4.00, 1.00, 8.00);
