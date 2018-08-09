"""Sample bigtable interaction. Creates a table, adds data, reads data, deletes table."""

from google.cloud import bigtable

#$ source bigtableenv/Scripts/activate
#$ GOOGLE_APPLICATION_CREDENTIALS=/a/Code/Research/Databases/Code/Redis/auth.json python main.py

def main():
    """Main func, does what the module docstring says."""
    client = bigtable.Client(project='example-big-table-209918', admin=True)
    instance = client.instance('main-bigtable')

    table_id = 'test_table'
    print("Creating the {} table.".format(table_id))
    table = instance.table(table_id)
    table.create()

    column_family_id = 'cf1'
    cf1 = table.column_family(column_family_id)
    cf1.create()

    print("Writing some greetings to the table.")
    column_id = 'greeting'.encode('utf-8')
    greetings = [
        'Hello, World!',
        'Hello, Cloud Bigtable',
        'Hello, Python'
    ]

    for i, value in enumerate(greetings):
        # i will be the index of the current value
        row_key = 'greeting{}'.format(i)
        row = table.row(row_key)
        row.set_cell(
            column_family_id,
            column_id,
            value.encode('utf-8')
        )
        row.commit()

    print('Getting a single greeting by row key.')
    key = 'greeting0'
    row = table.read_row(key.encode('utf-8'))
    value = row.cells[column_family_id][column_id][0].value
    print('\t{}: {}'.format(key, value.decode('utf-8')))

    print('Scanning for all greetings:')
    partial_rows = table.read_rows()
    partial_rows.consume_all()

    for row_key, row in partial_rows.rows.items():
        key = row_key.decode('utf-8')
        cell = row.cells[column_family_id][column_id][0]
        value = cell.value.decode('utf-8')
        print('\t{}: {}'.format(key, value))

    print('Deleting the {} table.'.format(table_id))
    table.delete()

if __name__ == "__main__":
    main()
