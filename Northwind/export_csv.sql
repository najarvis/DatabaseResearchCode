COPY (SELECT * FROM customers) TO 'CSV_Files/customers.csv' WITH CSV header;
COPY (SELECT * FROM suppliers) TO 'CSV_Files/suppliers.csv' WITH CSV header;
COPY (SELECT * FROM products)  TO 'CSV_Files/products.csv' WITH CSV header;
COPY (SELECT * FROM employees) TO 'CSV_Files/employees.csv' WITH CSV header;
COPY (SELECT * FROM categories) TO 'CSV_Files/categories.csv' WITH CSV header;

COPY (SELECT * FROM orders
      LEFT OUTER JOIN order_details ON order_details.OrderID = orders.OrderID) TO 'CSV_Files/orders.csv' WITH CSV header;
