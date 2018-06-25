from pymongo import MongoClient

client = MongoClient()
db = client.Northwind

# Orders and products in those orders are stored in two different collections,
# this combines them into one.

for order in db.orders.find():
    order_id = order.get('OrderID')
    products = []
    for detail in db['order-details'].find({'OrderID': order_id}):
        products.append({
            'ProductID': detail.get('ProductID'),
            'UnitPrice': detail.get('UnitPrice'),
            'Quantity': detail.get('Quantity'),
            'Discount': detail.get('Discount')
        })

    new_order = order.copy()
    new_order.update({'Products': products})
    db.mongo_orders.insert(new_order)
