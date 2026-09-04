import sqlite3

connection = sqlite3.connect("order_processing.db")
cursor = connection.cursor()

cursor.executescript("""
INSERT INTO products (id, name, price) VALUES
(1, 'MacBook Pro 14', 159999.00),
(2, 'iPhone 16', 79999.00),
(3, 'AirPods Pro', 24999.00),
(4, 'Dell XPS 15', 149999.00),
(5, 'Logitech MX Master 3S', 8999.00);

INSERT INTO inventory (product_id, quantity) VALUES
(1, 10),
(2, 25),
(3, 50),
(4, 0),
(5, 100);

INSERT INTO orders
(id, product_id, quantity, total_amount, status)
VALUES
(1, 1, 2, 319998.00, 'PENDING'),
(2, 2, 1, 79999.00, 'PENDING'),
(3, 3, 3, 74997.00, 'PENDING'),
(4, 4, 1, 149999.00, 'PENDING'),
(5, 5, 5, 44995.00, 'PENDING');

INSERT INTO payments
(id, order_id, amount, status)
VALUES
(1, 1, 319998.00, 'PENDING'),
(2, 2, 79999.00, 'PENDING'),
(3, 3, 74997.00, 'PENDING'),
(4, 4, 149999.00, 'PENDING'),
(5, 5, 44995.00, 'PENDING');

INSERT INTO shipments
(id, order_id, status)
VALUES
(1, 1, 'NOT_CREATED'),
(2, 2, 'NOT_CREATED'),
(3, 3, 'NOT_CREATED'),
(4, 4, 'NOT_CREATED'),
(5, 5, 'NOT_CREATED');
""")

connection.commit()
connection.close()

print("Data inserted successfully!")