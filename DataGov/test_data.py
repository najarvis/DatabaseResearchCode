import json
import math
import pprint
import pygame

def distance(coord1, coord2):
    """Gets the distance between two lat/lon points."""
    # Adapted from https://www.movable-type.co.uk/scripts/latlong.html
    R = 6371e3
    phi1 = math.radians(coord1[0])
    phi2 = math.radians(coord2[0])
    dphi = math.radians(coord2[0]-coord1[0])
    dlam = math.radians(coord2[1]-coord1[1])

    a = math.sin(dphi / 2) * math.sin(dphi / 2) + \
        math.cos(phi1) * math.cos(phi2) * \
        math.sin(dlam / 2) * math.sin(dlam / 2)

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    return R * c

def simple_distance(coord1, coord2):
    # Gets the squared distance between two points on a 2d plane. Not as
    # accurate but given a small enough section on a sphere it should work alright.
    # This will only be incorrect where the curvature of the earth causes a point
    # to be closer to one point than if it were on a flat plane, which shouldn't come up often.
    x_diff = coord1[1] - coord2[1]
    y_diff = coord1[0] - coord2[0]
    return x_diff ** 2 + y_diff ** 2

def get_closest(all_coords, coord):
    closest = sorted(all_coords, key=lambda x: simple_distance(coord, x[0]))[0]
    return closest

def lerp(a, b, t):
    return (1 - t) * a + t * b

def check_rainfall(year):
    with open('test.json') as f:
        data = json.load(f)

    bottom_left = (31.8717, -92.5064)
    top_right = (43.5, -73.0014)
    num_x = 256
    num_y = 256
    rain_data = [0 for i in range(num_x * num_y)]
    max_val = 0

    all_coords = [(data[region][i]['coordinates'],
                   region,
                   i) for region in data for i in range(len(data[region])-1)]


    print("Setting data")
    for y in range(num_y):
        if y % 16 == 0:
            print(y)
        y_coord = lerp(bottom_left[0], top_right[0], y / num_y)
        for x in range(num_x):
            x_coord = lerp(bottom_left[1], top_right[1], x / num_x)

            # For each pixel, find the closest data point (by coordinate) and get the data there.
            c = get_closest(all_coords, (y_coord, x_coord)) # Slow
            rainfall = data[c[1]][c[2]]['data'].get(str(year))
            if rainfall is not None:
                max_val = max(max_val, rainfall)
                rainfall = None if rainfall < 0 else rainfall
            rain_data[num_x * x + y] = rainfall

    # Create an image from the normalized data and save it
    print("Initializing PyGame...")
    pygame.init()
    surf = pygame.Surface((num_x, num_y))

    print("Rendering")
    for y in range(num_y):
        for x in range(num_x):
            v = rain_data[num_x * x + y]
            color = int(lerp(0, 255, v / max_val)) if v is not None else 0
            surf.set_at((x, y), (color, 0, 0))

    pygame.image.save(surf, "{}.png".format(year))
    pygame.quit()

def save_data():
    """Write the data into a form that can be imported into MongoDB."""
    with open('7dMaxParcipitation.txt') as f:
        with open('data.json', 'w') as json_file:
            while True:
                header = f.readline()
                if not header:
                    break
                num_docs = int(header.split()[0])
                region = header.split(',')[3].strip()
                # data["region"] = region
                # data[region] = []
                # data["stations"] = []
                for _ in range(num_docs):
                    data = {}
                    data['region'] = region
                    fixed = f.readline().split()

                    # Start of a session
                    sub_header = " ".join(fixed)
                    info = sub_header.split(",")[1].split()
                    coords = [*map(float, info[1:3])][::-1] # MongoDB wants these in a psuedo x,y form, rather than the standard N,W form.
                    coords[0] = -coords[0]
                    data['location'] = {
                        'type': 'Point',
                        'coordinates': coords
                    }
                    data['data'] = {}

                    num_lines = int(f.readline())
                    for _ in range(num_lines):
                        data_line = f.readline().split()
                        year, amount = int(data_line[0]), float(data_line[1])
                        data['data'][year] = amount

                    json.dump(data, json_file)
                    json_file.write("\n")

def bounding_boxes():
    """Get the top left and bottom right coordinates for a bounding box around
    all coordinates in the dataset. Coordinate errors (with zeros) are ignored."""
    with open('test.json') as f:
        data = json.load(f)

    min_x = min_y = 180
    max_x = max_y = -180
    for region in data:
        for point in range(len(data[region])):
            if 0 in data[region][point]['coordinates']:
                print(data[region][point]['coordinates'])
                continue
            min_x = min(min_x, data[region][point]['coordinates'][1])
            min_y = min(min_y, data[region][point]['coordinates'][0])
            max_x = max(max_x, data[region][point]['coordinates'][1])
            max_y = max(max_y, data[region][point]['coordinates'][0])

    print("({}, {}), ({}, {})".format(min_y, min_x, max_y, max_x))

if __name__ == "__main__":
    save_data()
    # check_rainfall(1975)
    # bounding_boxes()
