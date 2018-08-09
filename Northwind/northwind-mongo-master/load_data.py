from py2neo import Graph

# Connect to the graph. You will need to change this for your Sandbox
graph = Graph("bolt://18.207.142.251:34366",
              auth=("neo4j", "capitals-photodiode-winter"))

# Since the CSV filenames are all plural and we want the labels to be singular,
# this is just a simple map from plural to singularself.
# NOTE: names with dashes are escaped in the singular form with backquotes.
singular_form = {
    'categories': 'Category',
    'customers': 'Customer',
    'employee-territories': '`Employee-Territory`',
    'employees': 'Employee',
    'order-details': '`Order-Detail`',
    'orders': 'Order',
    'products': 'Product',
    'regions': 'Region',
    'shippers': 'Shipper',
    'suppliers': 'Supplier',
    'territories': 'Territory'
}

# This is just the headers from each of the CSV files. Easier to put them here than require each student to download all the files.
all_headers = {
    'categories': ['CategoryID', 'CategoryName', 'Description', 'Picture'],
    'customers': ['CustomerID', 'CompanyName', 'ContactName', 'ContactTitle', 'Address', 'City', 'Region', 'PostalCode', 'Country', 'Phone', 'Fax'],
    'employee-territories': ['EmployeeID', 'TerritoryID'],
    'employees': ['EmployeeID', 'LastName', 'FirstName', 'Title', 'TitleOfCourtesy', 'BirthDate', 'HireDate', 'Address', 'City', 'Region', 'PostalCode', 'Country', 'HomePhone', 'Extension', 'Photo', 'Notes', 'ReportsTo', 'PhotoPath'],
    'order-details': ['OrderID', 'ProductID', 'UnitPrice', 'Quantity', 'Discount'],
    'orders': ['OrderID', 'CustomerID', 'EmployeeID', 'OrderDate', 'RequiredDate', 'ShippedDate', 'ShipVia', 'Freight', 'ShipName', 'ShipAddress', 'ShipCity', 'ShipRegion', 'ShipPostalCode', 'ShipCountry'],
    'products': ['ProductID', 'ProductName', 'SupplierID', 'CategoryID', 'QuantityPerUnit', 'UnitPrice', 'UnitsInStock', 'UnitsOnOrder', 'ReorderLevel', 'Discontinued'],
    'regions': ['RegionID', 'RegionDescription'],
    'shippers': ['ShipperID', 'CompanyName', 'Phone'],
    'suppliers': ['SupplierID', 'CompanyName', 'ContactName', 'ContactTitle', 'Address', 'City', 'Region', 'PostalCode', 'Country', 'Phone', 'Fax', 'HomePage'],
    'territories': ['TerritoryID', 'TerritoryDescription', 'RegionID']
}

# Find all the filenames
for filename in singular_form:
    print(filename)

    headers = all_headers[filename]

    # Create a string for each node property in the form "Property: row.Property"
    property_strings = ["{0}: row.{0}".format(header) for header in headers]
    # This will produce: property_strings = [header1: row.header1, header2: row.header2, ...]

    node_label = singular_form.get(filename)

    # Create the string that goes after the CREATE statement.
    node_string = "(:{0} {{{1}}})".format(node_label, ", ".join(property_strings))
    # This will produce: node_string = "(:node_label {header1: row.header1, header2: row.header2, ...})"
    # print(node_string)

    # Build the full query, and run.
    query = """
    USING PERIODIC COMMIT
    LOAD CSV WITH HEADERS FROM "https://raw.githubusercontent.com/najarvis/DatabaseResearchCode/master/Northwind/northwind-mongo-master/{s_filename}.csv" AS row
    CREATE {n_string};
    """.format(s_filename=filename, n_string=node_string)
    # print(query)

    graph.run(query)

# Create the basic relationships
query = """
MATCH (od:`Order-Detail`), (o:Order)
WHERE od.OrderID = o.OrderID
CREATE (od)-[:PART_OF]->(o);
"""
graph.run(query)

query2 = """
MATCH (od:`Order-Detail`), (p:Product)
WHERE od.ProductID = p.ProductID
CREATE (od)-[:IS]->(p);
"""
graph.run(query2)

query3 = """
MATCH (p:Product), (c:Category)
WHERE p.CategoryID = c.CategoryID
CREATE (p)-[:IS_CATEGORY]->(c)
"""
graph.run(query3)
