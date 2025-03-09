import pytesseract
import re
import cv2
import numpy as np
import os
import pandas as pd
import time
from PIL import Image

# Set the Tesseract-OCR path
pytesseract.pytesseract.tesseract_cmd = r"K:\Softwares\Tesseract-OCR\tesseract.exe"

# Set the folder path where images are stored
image_folder = "images"
output_csv = "output.csv"

# Function to extract required details from an image
def extract_details_from_image(image_path):
    try:
        start_time = time.time()  # Start timing

        # Load the image
        image = Image.open(image_path)

        # Convert image to OpenCV format and preprocess for better OCR accuracy
        image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
        _, thresh_image = cv2.threshold(image_cv, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Convert back to PIL format for OCR
        processed_image = Image.fromarray(thresh_image)

        # Extract text using OCR
        extracted_text = pytesseract.image_to_string(processed_image)

        # Extract time at the top left (format: HH:MM)
        top_left_time_match = re.search(r'\b\d{1,2}:\d{2}\b', extracted_text)
        top_left_time = top_left_time_match.group() if top_left_time_match else "Not found"

        # Extract UberX price (format: BDT followed by numbers)
        uberx_price_match = re.search(r'UberX\s+BDT\s+(\d+\.\d+)', extracted_text)
        uberx_price = uberx_price_match.group(1) if uberx_price_match else "Not found"

        # Extract time below UberX (format: HH:MMam/pm - X min away)
        uberx_time_match = re.search(r'UberX.*?(\d{1,2}:\d{2}[ap]m\s*-\s*\d+\s*min away)', extracted_text, re.DOTALL)
        uberx_time = uberx_time_match.group(1) if uberx_time_match else "Not found"

        elapsed_time = time.time() - start_time  # Calculate elapsed time
        print(f"✅ Processed {os.path.basename(image_path)} in {elapsed_time:.2f} seconds")

        return [os.path.basename(image_path), uberx_price, top_left_time, uberx_time]

    except Exception as e:
        print(f"❌ Error processing {image_path}: {e}")
        return [os.path.basename(image_path), "Error", "Error", "Error"]


# Get list of image files in the folder
image_files = [os.path.join(image_folder, f) for f in os.listdir(image_folder) if
               f.lower().endswith(('.png', '.jpg', '.jpeg'))]

# Start timing the total processing time
total_start_time = time.time()

# Process each image and store the results
data = []
for index, image_file in enumerate(image_files, start=1):
    print(f"\n📌 Processing {index}/{len(image_files)}: {os.path.basename(image_file)}")
    data.append(extract_details_from_image(image_file))

# Create a DataFrame and save to CSV
df = pd.DataFrame(data, columns=["File Name", "Price", "Current Time", "ETA Time"])
df.to_csv(output_csv, index=False)

# Display total processing time
total_elapsed_time = time.time() - total_start_time
print(f"\n✅ Extraction completed in {total_elapsed_time:.2f} seconds.")
print(f"📄 CSV saved to: {output_csv}")
