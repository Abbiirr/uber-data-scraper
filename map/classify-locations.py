#!/usr/bin/env python
import pandas as pd

# List of Dhaka areas (adjust as needed)
AREAS = [
    "Banasree", "Banani", "Bangla Motor", "Bangshal", "Bashabo", "Bashundhara", "Beraid",
    "Buet Campus", "Chawkbazar", "Saralia", "Uttarkhan", "Baridhara", "Barua", "Nikunja",
    "Siddik Bazar", "Bakshi Bazar", "Darussalam", "Dayaganj", "Golapbagh", "Dhaka University Campus",
    "Dhaka Cantonment", "Gulshan", "Paribagh", "Dhanmondi", "Eskaton", "Gendaria", "Gopibagh",
    "Goran", "Shanir Akhra", "Hatirpool", "Hazaribagh", "Kamalapur", "Islampur", "Shekher Jayga",
    "Nawabpur", "Kafrul", "Kakrail", "Kalabagan", "Kalachandpur", "Khilkhet", "Kathalbagan",
    "Kawran Bazar", "Khilgaon", "Kotwali", "Moghbazar", "Kuril", "Lalbagh", "Meradia", "Lalmatia",
    "Malibagh", "Manda", "New Market", "Maniknagar", "Mohakhali", "Vatara", "Wari", "Mugda",
    "Biman Bandar", "Nadda", "Nandipara", "Sadarghat", "Shantibagh", "Joar Shahara", "Pilkhana",
    "Babu Bazar", "Dakkhingaon", "Green Model Town", "Baganbari", "Korail", "Motijheel", "New Eskaton",
    "Paltan", "Rajarbagh", "Sayedabad", "Ramna", "Shahidbagh", "Rampura", "Rayer Bazar", "Sabujbagh",
    "Donia", "Shahbagh", "Shahjadpur", "Shegunbagicha", "Shantinagar", "Sher E Bangla Nagar", "Shyamoli",
    "Shyampur", "Siddheshwari", "Rayerbagh", "Sutrapur", "Tejgaon", "Tikatuli", "Turag", "Aftabnagar",
    "Bhashantek", "Janatabagh", "Chankharpul", "Dholairpar", "Mohammadbagh", "Naya Bazar", "Postogola",
    "Agargaon", "Fulbaria", "Signboard", "Fakirapul", "Panthapath", "Muradpur", "Dumni", "Jurain",
    "Satarkul", "Madartek", "Meraj Nagar", "Islambagh", "Azimpur", "Dakkhinkhan", "Uttara", "Badda",
    "Jigatola", "Kadamtali", "Kallyanpur", "Gulisthan", "Jatrabari", "Patira", "Muradpur", "Shamibagh",
    "Shahjahanpur"
]


def classify_location(row, areas):
    """
    Attempt to match one of the areas from the list within the combined 'location' and
    'formatted_address' fields (if available). Returns the matching area name if found;
    otherwise returns "Unknown".
    """
    loc_field = str(row.get("location", ""))
    addr_field = str(row.get("formatted_address", ""))
    combined = f"{loc_field} {addr_field}".lower()
    for area in areas:
        if area.lower() in combined:
            return area
    return "Unknown"


def main():
    # Hardcoded input and output file paths
    input_file = "opencage_location_results-unique.csv"  # Your input file
    output_file = "classified_opencage_locations.csv"  # Output file with classifications

    # Read the CSV file
    df = pd.read_csv(input_file)

    # Clean quotes and whitespace from the 'location' and 'formatted_address' fields
    df["location"] = df["location"].astype(str).str.replace('"', '').str.strip()
    if "formatted_address" in df.columns:
        df["formatted_address"] = df["formatted_address"].astype(str).str.replace('"', '').str.strip()

    # Classify each row
    df["Classified Area"] = df.apply(lambda row: classify_location(row, AREAS), axis=1)

    # Save the results to the output CSV file
    df.to_csv(output_file, index=False)
    print(f"Classification complete. Results saved to {output_file}")


if __name__ == "__main__":
    main()
