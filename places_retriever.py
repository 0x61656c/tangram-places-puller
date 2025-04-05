import requests
import csv
import os
from dotenv import load_dotenv
import logging

# --- Configuration ---
# Load environment variables from .env file
load_dotenv()
API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
INPUT_FILENAME = "input.csv"  # Assumes input file is in the same directory
OUTPUT_FILENAME = "output.csv"
BUSINESS_NAME_COLUMN = "Business Name" # Header of the column containing business names in input.csv
PLACES_API_URL = "https://places.googleapis.com/v1/places:searchText"
# Fields to request from the Places API (ensure these cover needed data)
# See: https://developers.google.com/maps/documentation/places/web-service/search-text#fields
FIELD_MASK = "places.rating,places.userRatingCount,places.photos"

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Helper Functions ---
def get_place_details(business_name: str):
    """Queries the Google Places API for a given business name."""
    if not API_KEY:
        logging.error("GOOGLE_PLACES_API_KEY not found in environment variables.")
        return None
    if not business_name:
        logging.warning("Skipping empty business name.")
        return None

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": API_KEY,
        "X-Goog-FieldMask": FIELD_MASK
    }
    data = {
        "textQuery": business_name
    }

    try:
        response = requests.post(PLACES_API_URL, json=data, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        results = response.json()
        # The API might return multiple places; we usually want the first/most relevant one.
        if results and "places" in results and len(results["places"]) > 0:
            # Return the first place found
            return results["places"][0]
        else:
            logging.warning(f"No place found for '{business_name}'. Response: {results}")
            return None
    except requests.exceptions.RequestException as e:
        logging.error(f"API request failed for '{business_name}': {e}")
        if hasattr(e, 'response') and e.response is not None:
            logging.error(f"Response status: {e.response.status_code}")
            logging.error(f"Response text: {e.response.text}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred processing '{business_name}': {e}")
        return None

def construct_photo_url(photo_name: str, max_width: int = 400) -> str:
    """Constructs the photo URL using the photo name and API key."""
    # The photo name format is typically 'places/{place_id}/photos/{photo_reference}'
    # The API URL format is https://places.googleapis.com/v1/{photo_name}/media?key=API_KEY&maxWidthPx={max_width}
    if not API_KEY:
        logging.error("Cannot construct photo URL without API key.")
        return ""
    if not photo_name:
        return ""
    return f"https://places.googleapis.com/v1/{photo_name}/media?key={API_KEY}&maxWidthPx={max_width}"

# --- Main Script Logic ---
def main():
    logging.info("Starting script...")

    if not API_KEY:
        logging.critical("GOOGLE_PLACES_API_KEY environment variable is not set. Please create a .env file with this variable. Exiting.")
        return

    business_names = []
    try:
        with open(INPUT_FILENAME, 'r', newline='', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            if BUSINESS_NAME_COLUMN not in reader.fieldnames:
                logging.critical(f"Input file '{INPUT_FILENAME}' does not contain the column '{BUSINESS_NAME_COLUMN}'. Exiting.")
                return
            for row in reader:
                business_names.append(row[BUSINESS_NAME_COLUMN].strip())
        logging.info(f"Read {len(business_names)} business names from '{INPUT_FILENAME}'.")
    except FileNotFoundError:
        logging.critical(f"Input file '{INPUT_FILENAME}' not found. Please create it in the same directory as the script. Exiting.")
        return
    except Exception as e:
        logging.critical(f"Error reading '{INPUT_FILENAME}': {e}. Exiting.")
        return

    all_results = []
    max_photos = 0 # Track the maximum number of photos found for any place

    for i, name in enumerate(business_names):
        logging.info(f"Processing {i+1}/{len(business_names)}: '{name}'")
        details = get_place_details(name)
        result_row = {
            BUSINESS_NAME_COLUMN: name,
            "review count": "",
            "rating": "",
            "image_attributions": ""
        }

        if details:
            result_row["review count"] = str(details.get("userRatingCount", ""))
            result_row["rating"] = str(details.get("rating", ""))

            photos_data = details.get("photos", [])
            photo_urls = []
            attributions = []

            if photos_data:
                 # Limit to a reasonable number, e.g., 10, if necessary
                current_photo_count = 0
                for photo in photos_data:
                    photo_name = photo.get("name")
                    if photo_name:
                        photo_url = construct_photo_url(photo_name)
                        photo_urls.append(photo_url)
                        # Add attribution for this photo if available
                        author_attributions = photo.get("authorAttributions", [])
                        if author_attributions:
                           # Combine attributions for this photo (usually just one)
                           photo_attrib_text = "; ".join([a.get('displayName', '') + ': ' + a.get('uri', '') for a in author_attributions if a])
                           attributions.append(photo_attrib_text)
                        current_photo_count += 1

                # Update max_photos if this place has more photos than previously seen
                if current_photo_count > max_photos:
                    max_photos = current_photo_count

                # Add photo URLs to the row
                for idx, url in enumerate(photo_urls):
                     result_row[f"photos_{idx}"] = url

                # Compile all attributions into a single string
                result_row["image_attributions"] = " | ".join(filter(None, attributions)) # Join non-empty attributions

        all_results.append(result_row)

    # --- Write Output ---
    if not all_results:
        logging.warning("No results to write to output file.")
        return

    # Define output headers dynamically based on max_photos
    output_headers = [BUSINESS_NAME_COLUMN, "review count", "rating"]
    output_headers.extend([f"photos_{i}" for i in range(max_photos)])
    output_headers.append("image_attributions")

    try:
        with open(OUTPUT_FILENAME, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=output_headers, extrasaction='ignore') # Ignore extra fields in dict if any
            writer.writeheader()
            writer.writerows(all_results)
        logging.info(f"Successfully wrote {len(all_results)} rows to '{OUTPUT_FILENAME}'.")
    except Exception as e:
        logging.error(f"Error writing to '{OUTPUT_FILENAME}': {e}")

    logging.info("Script finished.")

if __name__ == "__main__":
    main()
