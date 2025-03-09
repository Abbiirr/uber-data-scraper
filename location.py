import csv
from itertools import permutations

# Define the list of locations with their coordinates
locations = [
    {"name": "Gulshan 1", "latitude": 23.780636, "longitude": 90.419326},
    {"name": "Gulshan 2", "latitude": 23.791600, "longitude": 90.416787},
    {"name": "Banani", "latitude": 23.793584, "longitude": 90.404194},
    {"name": "Baridhara", "latitude": 23.810331, "longitude": 90.426283},
    {"name": "Uttara", "latitude": 23.875854, "longitude": 90.379249},
    {"name": "Dhanmondi", "latitude": 23.746466, "longitude": 90.376015},
    {"name": "Motijheel", "latitude": 23.731888, "longitude": 90.412521},
    {"name": "Mohakhali", "latitude": 23.777264, "longitude": 90.403492},
    {"name": "Farmgate", "latitude": 23.757547, "longitude": 90.391962},
    {"name": "Shahbagh", "latitude": 23.738064, "longitude": 90.394469}
]

# Generate all permutations of the locations taken 2 at a time
location_pairs = permutations(locations, 2)

# Define the CSV file header
header = ['Start Coordinates', 'End Coordinates', 'Start Location Name', 'End Location Name']

# Write the data to a CSV file
with open('location_pairs.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(header)
    for start, end in location_pairs:
        start_coords = f"({start['latitude']}, {start['longitude']})"
        end_coords = f"({end['latitude']}, {end['longitude']})"
        writer.writerow([start_coords, end_coords, start['name'], end['name']])

print("CSV file 'location_pairs.csv' has been created successfully.")
