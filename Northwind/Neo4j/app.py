"""
    Author: Nick Jarvis
    Date: 25 June 2018

    This program hosts a basic web server on localhost:5000, and interacts with a
    Neo4j Database running locally.
"""

import datetime

from flask import Flask, render_template, request, jsonify, redirect
from py2neo import Graph, Node, Relationship

graph = Graph("bolt://54.86.9.156:33227",
              auth=("neo4j", "trace-refurbishment-currency"))

app = Flask(__name__)

@app.route('/')
def index():
    return redirect('/search')

@app.route('/search', methods=['GET', 'POST'])
def search():
    """Search for and display products."""

    if request.method == 'GET':
        return render_template("search.html")

    # Execute the following code if it is a POST request.
    search_string = request.form.get('data')
    query = """
        MATCH (p:Product)
        WHERE p.productName =~ '(?i).*{}.*'
        RETURN p
    """.format(search_string)
    results = graph.run(query)

    # Render a template for each product, then combine them into one long string
    # and send to the user.
    printed = False
    rendered_sections = []
    for result in results:
        if not printed:
            print(dict(result[0]))
            printed = True
        rendered_sections.append(render_template('product.html', product=dict(result[0])))

    return jsonify("\n".join(rendered_sections))

@app.route('/raw/<collection>')
@app.route('/raw')
def raw(collection='orders'):
    """A raw view of the entire contents of a collection."""

    # Render a template for each document in the collection specified by the url.
    data_arr = []
    for result in mongo.db[collection].find({}, {"_id": 0}):
        data_arr.append(render_template("generic_document.html", document=result))
    raw_html = "\n".join(data_arr)

    collections = mongo.db.collection_names()

    return render_template("raw.html", data=raw_html, collections=collections)

@app.route('/order/<order_string>', methods=['GET', 'POST'])
@app.route('/order', methods=['GET', 'POST'])
def order(order_string=""):
    """Insert data into the database through a form."""

    if request.method == 'GET':
        return render_template('orders.html', order_string=order_string)

    # Parse date input
    date = request.form.get('req_date')
    # The date comes in the form 'YYYY-MM-DD', we need to convert it to ISO 8601 format
    req_date = datetime.datetime.strptime(date, '%Y-%m-%d').isoformat()

    # Parse customer ID to make sure it is valid. Search database for it.
    cust_id = request.form.get('cust_id')
    customer_data = mongo.db.customers.find_one({'CustomerID': cust_id})
    if customer_data is None:
        return "Customer not found!"

    # Find the largest order number and increment it to get the next order_number.
    # NOTE: This does not guaruntee that the OrderID is unique, if another user runs
    # this query before this route finishes.
    order_num = next(mongo.db.orders.find().sort('OrderID', -1).limit(1)).get('OrderID') + 1

    products_requested = request.form.get('prod_id')
    # Convert the string into individual ints.
    product_data = list(map(int, products_requested.split(',')))
    if len(product_data) % 2:
        return "Invalid input. There should be even number of products and quanities."

    # Build each of the product subdocuments, place them in a list
    products = []
    for i in range(len(product_data) // 2):
        product_id = product_data[2*i]
        quantity = product_data[2*i+1]
        product_doc = mongo.db.products.find_one({'ProductID': product_id})
        products.append({
            'ProductID': product_id,
            'UnitPrice': product_doc.get('UnitPrice'),
            'Quantity': quantity,
            'Discount': 0
        })

    # Create the document that will be inserted into the database.
    order_dict = {
        'OrderID': order_num,
        'CustomerID': cust_id,
        'EmployeeID': request.form.get('emp_id'),
        'OrderDate': datetime.datetime.today().isoformat(),
        'RequiredDate': req_date,
        'ShipVia': 0, # Not quite sure what these two values are.
        'Freight': 0,
        'ShipName': customer_data.get('CompanyName'),
        'ShipAddress': customer_data.get('Address'),
        'ShipCity': customer_data.get('City'),
        'ShipRegion': customer_data.get('Region'),
        'ShipPostalCode': customer_data.get('PostalCode'),
        'ShipCountry': customer_data.get('Country'),
        'Products': products
    }

    # Insert into the databse.
    mongo.db.mongo_orders.insert(order_dict)
    return redirect('/raw/mongo_orders')

@app.route('/render_cart', methods=['POST'])
def render_cart():
    """Renders a template for each item in the cart, then returns them
    concatonated together. Directly placed into page via JQuery."""

    # For some reason even though we specify "json" as the content type in
    # JavaScript, we still need to use 'force=True' to ignore headers and interpret as json.
    cart = request.get_json(force=True)
    rendered = []
    for cart_item in cart:
        quantity = cart_item.get('quantity')
        name = cart_item.get('name')
        rendered.append(render_template('cart_item.html',
                                        name=name,
                                        quantity=quantity))

    return jsonify("\n".join(rendered))
