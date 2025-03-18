import pandas as pd

# Load the CSV files
df1 = pd.read_csv("last_part_with_original_pickup_locations_lowercase.csv")
df2 = pd.read_csv("Pickup_Point_Modified_Lowercase.csv")

# Sanitize quotations and convert the 'last part' column to lowercase
df1['last part'] = df1['last part'].str.replace(r'["\']', '', regex=True).str.lower()
df2['last part'] = df2['last part'].str.replace(r'["\']', '', regex=True).str.lower()

# Merge DataFrames on the 'last part' column
merged_df = pd.merge(df1, df2, on='last part', how='inner')

# Export the merged DataFrame to a CSV file
merged_df.to_csv("merged_output.csv", index=False)
