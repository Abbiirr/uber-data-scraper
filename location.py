import csv
from itertools import permutations

# Define the list of locations with their coordinates
locations = [
    {"name": "Gulshan 1", "latitude": 23.780378917169333, "longitude": 90.41672810537362},
    {"name": "Gulshan 2", "latitude": 23.794761328207716, "longitude": 90.41431025769957},
    {"name": "Banani", "latitude": 23.795632264992097, "longitude": 90.40082773269607},
    {"name": "Baridhara", "latitude": 23.7977160735167, "longitude": 90.42333172053618},
    {"name": "Uttara", "latitude": 23.87096277222152, "longitude": 90.40028249779219},
    {"name": "Dhanmondi", "latitude": 23.739543382478974, "longitude": 90.3831857005473},
    {"name": "Motijheel", "latitude": 23.730200638200436, "longitude": 90.41019959557929},
    {"name": "Mohakhali", "latitude": 23.781145352505032, "longitude": 90.39818465826089},
    {"name": "Farmgate", "latitude": 23.75780240225943, "longitude": 90.39003129024594},
    {"name": "Shahbagh", "latitude": 23.738125033603566, "longitude": 90.39582712625963},
]

# Generate all permutations of the locations taken 2 at a time
location_pairs = permutations(locations, 2)

# Define the CSV file header
header = ['Start Coordinates', 'End Coordinates', 'Start Location Name', 'End Location Name']

# Write the data to a CSV file
with open('uber/location_pairs.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(header)
    for start, end in location_pairs:
        start_coords = f"({start['latitude']}, {start['longitude']})"
        end_coords = f"({end['latitude']}, {end['longitude']})"
        writer.writerow([start_coords, end_coords, start['name'], end['name']])

print("CSV file 'location_pairs.csv' has been created successfully.")
