# Google Places Data Retriever

This script retrieves business information from the Google Places API based on a list of business names provided in an input CSV file. It outputs the results, including review count, rating, photo URLs, and photo attributions, into an output CSV file.

## Features

*   Reads business names from `input.csv`.
*   Queries the Google Places API (`searchText` endpoint).
*   Extracts review count, rating, photo URLs, and attributions.
*   Handles variable numbers of photos per place.
*   Outputs results to `output.csv`.
*   Uses environment variables for secure API key management.
*   Includes basic logging for progress and errors.

## Setup

1.  **Clone the Repository (if applicable):**
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Create a Virtual Environment:**
    Create a virtual environment to manage dependencies.
    ```bash
    python -m venv env
    ```
    Activate the virtual environment:
    - On macOS/Linux:
      ```bash
      source env/bin/activate
      ```
    - On Windows:
      ```bash
      .\env\Scripts\activate
      ```

3.  **Install Dependencies:**
    Ensure you have Python 3 installed. Then, install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set Up API Key:**
    *   Rename the `.env.example` file to `.env`.
    *   Open the `.env` file and replace `YOUR_API_KEY_HERE` with your actual Google Places API key.
        ```
        GOOGLE_PLACES_API_KEY=YOUR_API_KEY_HERE
        ```
    *   **Important:** Keep the `.env` file private. Add `.env` to your `.gitignore` file if using version control.

5.  **Prepare Input File:**
    *   Create a CSV file named `input.csv` in the project's root directory.
    *   This file must contain at least one column with the header `Business Name`. Each row under this header should contain the name of a business you want to look up.
    *   Example `input.csv`:
        ```csv
        Business Name
        "Example Cafe, Springfield"
        "Another Business Inc."
        "Local Shop on Main St"
        ```

## Usage

Run the script from the command line in the project's root directory:

```bash
python places_retriever.py
```

The script will:
*   Read names from `input.csv`.
*   Log its progress to the console.
*   Query the Google Places API for each business.
*   Generate an `output.csv` file in the same directory containing the results.

### CSV Merger Utility

The project also includes a utility for merging CSV files:

```bash
python merger.py file1.csv file2.csv output.csv [--merge-type TYPE]
```

Parameters:
- `file1.csv`: Path to the first CSV file
- `file2.csv`: Path to the second CSV file
- `output.csv`: Path for the output merged CSV file
- `--merge-type`: Optional. Type of merge to perform (default: inner)
  - Options: inner, left, right, outer

Example:
```bash
python merger.py input.csv enriched_data.csv final_output.csv --merge-type left
```

This will merge the two CSV files based on the 'Business Name' column using the specified merge type.

**Note:** Both CSV files must contain a 'Business Name' column for the merge to work. This is designed to work with the output from the Places Retriever script and other business data files that follow the same format.

## Output File (`output.csv`)

The output file will contain the following columns:

*   `Business Name`: The original business name from the input file.
*   `review count`: The number of user reviews (as text).
*   `rating`: The average user rating (as text).
*   `photos_0`, `photos_1`, ...: Columns containing URLs for retrieved photos. The number of columns depends on the maximum number of photos found for any single place in the input list.
*   `image_attributions`: A single column containing combined attribution text for all photos of that place, separated by " | ".

## Configuration (Optional)

You can modify the following constants at the top of `places_retriever.py`:

*   `INPUT_FILENAME`: Change if your input file has a different name.
*   `OUTPUT_FILENAME`: Change if you want a different output file name.
*   `BUSINESS_NAME_COLUMN`: Change if the header for business names in your `input.csv` is different.
*   `FIELD_MASK`: Modify to request different fields from the Google Places API. See the [Google Places API documentation](https://developers.google.com/maps/documentation/places/web-service/search-text#fields) for available fields.
