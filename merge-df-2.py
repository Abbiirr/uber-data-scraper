import pandas as pd

# Load df2 from CSV
df2 = pd.read_csv("last_part_with_original_pickup_locations_lowercase.csv")

# Drop duplicates based on the 'last part' column
df2_unique = df2.drop_duplicates(subset=['last part'])

# Save the unique last part values to a new CSV file
df2_unique.to_csv("unique_last_part.csv", index=False)

# Print the count of rows
print(df2_unique.count())
