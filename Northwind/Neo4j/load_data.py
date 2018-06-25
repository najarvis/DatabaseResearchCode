import csv
import glob

for csv_filename in glob.glob('../northwind-mongo-master/*.csv'):
    object = csv_filename.split('\\')[-1][:-4]
    print(object)
    with open(csv_filename, newline='') as csvfile:
        headers = [header.strip() for header in csvfile.readline().split(',')]

        # Go back to the beginning of the file
        csvfile.seek(0, 0)
        reader = csv.DictReader(csvfile)
        for row in reader:
            ...
    print()
