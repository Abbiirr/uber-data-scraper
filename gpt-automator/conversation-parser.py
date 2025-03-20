import re
import ast
import pandas as pd
from itertools import zip_longest


def extract_groups(text):
    """
    Extract groups of arrays for "Location Name", "Address", and "Classified Area"
    from the input text.
    """
    # This regex matches the key ("Location Name", "Address", or "Classified Area")
    # and captures the corresponding list (everything inside square brackets)
    pattern = r'"(Location Name|Address|Classified Area)"\s*:\s*(\[[^\]]*\])'
    matches = re.findall(pattern, text, re.DOTALL)

    groups = []
    current_group = {}
    # We assume that each group consists of 3 keys (order doesn't matter)
    for key, list_str in matches:
        try:
            # Use ast.literal_eval for safe conversion from string to list
            array = ast.literal_eval(list_str)
        except Exception as e:
            print(f"Error evaluating list for key {key}: {e}")
            array = []
        current_group[key] = array
        if len(current_group) == 3:
            groups.append(current_group)
            current_group = {}
    return groups


# Read the text file containing the data
with open("../conversation.txt", "r", encoding="utf-8") as f:
    text = f.read()

# Extract groups from the text file
groups = extract_groups(text)

# For each group, use zip_longest to handle any unequal list lengths
df_list = []
for group in groups:
    locs = group.get("Location Name", [])
    addrs = group.get("Address", [])
    cls = group.get("Classified Area", [])

    # Combine the three lists row-wise; fill missing values with None if needed
    rows = list(zip_longest(locs, addrs, cls, fillvalue=None))
    df = pd.DataFrame(rows, columns=["Location Name", "Address", "Classified Area"])
    df_list.append(df)

# Combine all group DataFrames into one
df_combined = pd.concat(df_list, ignore_index=True)

# Print the combined DataFrame
print(df_combined)
df_combined.to_csv("output.csv", index=False, encoding="utf-8")
