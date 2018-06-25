from py2neo import Graph

# Connect to the graph. You will need to change this for your Sandbox
graph = Graph("bolt://54.86.9.156:33227",
              auth=("neo4j", "trace-refurbishment-currency"))

# Since the CSV filenames are all plural and we want the labels to be singular,
# this is just a simple map from plural to singular
singular_form = {
    'categories': 'Category',
    'customers': 'Customer',
    'employee-territories': 'Employee-Territory',
    'employees': 'Employee',
    'order-details': 'Order-Detail',
    'orders': 'Order',
    'products': 'Product',
    'regions': 'Region',
    'shippers': 'Shipper',
    'suppliers': 'Supplier',
    'territories': 'Territory'
}

# Find all the filenames
for filename in singular_form:
    print(filename)

    # Here I choose to ignore all files with dashes in them, only because the application
    # doesn't use them and Neo4j doesn't support dashes in labels. A simple underscore
    # replace should work, however it is not needed for this demonstration.
    if filename.find('-') != -1:
        print("Skipping")
        continue

    # Read the first line of the file and grab the header data.
    with open(filename + ".csv", newline='') as csvfile:
        headers = [header.strip() for header in csvfile.readline().split(',')]

    # Create a string for each node property in the form "Property: row.Property"
    property_strings = ["{0}: row.{0}".format(header) for header in headers]
    node_label = singular_form.get(filename)

    # Create the string that goes after the CREATE statement.
    node_string = "(:{0} {{{1}}})".format(node_label, ", ".join(property_strings))
    # print(node_string)

    # Build the full query, and run.
    query = """
    USING PERIODIC COMMIT
    LOAD CSV WITH HEADERS FROM "https://raw.githubusercontent.com/najarvis/DatabaseResearchCode/master/Northwind/northwind-mongo-master/{s_filename}.csv" AS row
    CREATE {node_string};
    """.format(s_filename=filename, node_string=node_string)
    # print(query)

    graph.run(query)
