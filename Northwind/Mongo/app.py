"""
    Author: Nick Jarvis
    Date: 21 June 2018

    This program hosts a basic web server on localhost:5000, and interacts with a
    MongoDB Database hosted by Mongo Atlas.
"""

import datetime
import os

from flask import Flask, render_template, request, jsonify, redirect
from flask_pymongo import PyMongo

# Since I'm not a huge fan of putting passwords in plain code,
# I've placed it in a environment variable saved under 'mongo_atlas_password'
password = os.environ.get('mongo_atlas_password')
username = 'najarvis'

app = Flask(__name__)
# Connect to Atlas. These lines need to come before we initialize PyMongo.
app.config['MONGO_HOST'] = 'mongodb+srv://' + username + ':' + password + \
                           '@learningatlas01-1cf8c.gcp.mongodb.net/test?retryWrites=true'
app.config['MONGO_DBNAME'] = 'Northwind'

mongo = PyMongo(app)

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
    regex = {"$regex": '.*' + search_string + '.*', '$options': 'i'}
    results = mongo.db.products.find({"ProductName": regex}, {'_id': 0})

    # Render a template for each product, then combine them into one long string
    # and send to the user.
    rendered_sections = []
    for result in results:
        rendered_sections.append(render_template('product.html', product=result))

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

@app.route('/expand_order/<order_id>')
@app.route('/expand_order')
def expand_order(order_id=None):
    """This route is pretty basic. Going to it the first time only shows a text
    input field. If you put an orderID in that field and hit the button, that
    order will be broken up and displayed."""

    if order_id is None:
        return render_template("expand.html", data=None)

    order_data = mongo.db.mongo_orders.find_one({"OrderID": int(order_id)}, {"_id": 0})
    print(order_data)
    products = order_data.get('Products')
    id_dict = {product.get('ProductID'): product for product in products}
    products_data = mongo.db.products.find({"ProductID": {"$in": list(id_dict)}}, {"_id": 0})

    order_template = render_template("generic_document.html", document=order_data)
    templates = []
    for pd in products_data:
        full_doc = {}
        full_doc.update(pd)
        full_doc.update(id_dict.get(pd.get('ProductID')))
        templates.append(render_template("generic_document.html", document=full_doc))

    return render_template("expand.html", order=order_template, products="\n".join(templates))

    # We grab the inital order node
    order_data = graph.nodes.match("Order", OrderID=order_id).first()
    # Then grab all order-detail nodes and product nodes related to it.
    query = """
        MATCH (od:`Order-Detail` {OrderID: {o_id}})-[:IS]->(p)
        RETURN p, od;
    """
    results = graph.run(query, o_id=order_id)

    order_temp = render_template("generic_document.html", document=dict(order_data))
    templates = []
    for result in results:
        # Combine both the product node and order-detail node into one, then display it.
        full_doc = {}
        full_doc.update(result['p'])
        full_doc.update(result['od'])
        templates.append(render_template("generic_document.html", document=dict(full_doc)))

    return render_template("expand.html", order=order_temp, products="\n".join(templates))
