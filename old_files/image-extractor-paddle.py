import re
import cv2
import numpy as np
import os
import pandas as pd
import time
from paddleocr import PaddleOCR
from PIL import Image

# Initialize PaddleOCR with GPU support
ocr = PaddleOCR(use_angle_cls=True, use_gpu=True)  # Set use_gpu=False if you don't have a GPU

# Set the folder path where images are stored
image_folder = "images"
output_csv = "output2.csv"

# Function to extract required details from an image
def extract_details_from_image(image_path):
    try:
        start_time = time.time()  # Start timing

        # Load the image
        image = cv2.imread(image_path)

        # Convert to grayscale for better OCR accuracy
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, thresh_image = cv2.threshold(gray_image, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Perform OCR using PaddleOCR
        results = ocr.ocr(thresh_image)

        # Extract recognized text
        extracted_text = "\n".join([line[1][0] for result in results for line in result])

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
