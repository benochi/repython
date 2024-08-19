import os
import requests
import json
import tkinter as tk
from tkinter import messagebox
import urllib.parse

# API Key for ScraperAPI
api_key = "31fecb85a35e9ccb447ede630e4caf32"

# Base URL for Zillow
ZILLOW_BASE_URL = "https://www.zillow.com/"


# Function to scrape Zillow using ScraperAPI
def scrape_zillow(city, state, num_pages=10, price_min=None, price_max=None):
    city = city.strip().lower() or "clarksville"
    state = state.strip().lower() or "tn"
    listings = []

    # Encode the searchQueryState with price filtering
    search_query_state = {
        "pagination": {},
        "mapBounds": {},
        "regionSelection": [{"regionId": 44269, "regionType": 6}],
        "filterState": {
            "fr": {"value": True},
            "fsba": {"value": False},
            "fsbo": {"value": False},
            "nc": {"value": False},
            "cmsn": {"value": False},
            "auc": {"value": False},
            "fore": {"value": False},
            "mf": {"value": False},
            "land": {"value": False},
            "manu": {"value": False},
            "mp": {"min": price_min, "max": price_max},
        },
        "isListVisible": True,
        "mapZoom": 12,
        "usersSearchTerm": f"{city} {state}",
    }

    encoded_query = urllib.parse.quote(json.dumps(search_query_state))

    for page_number in range(1, num_pages + 1):
        # Construct the URL with searchQueryState
        current_url = (
            f"{ZILLOW_BASE_URL}{city}-{state}/rentals/?searchQueryState={encoded_query}"
            if page_number == 1
            else f"{ZILLOW_BASE_URL}{city}-{state}/rentals/{page_number}_p/?searchQueryState={encoded_query}"
        )

        payload = {"api_key": api_key, "url": current_url}

        try:
            # Request the page through ScraperAPI
            response = requests.get(
                "https://api.scraperapi.com/", params=payload, timeout=60
            )

            if response.status_code == 200:
                print(f"Scraping from URL: {current_url}")  # Feedback
                content = response.text

                # Extract and sanitize the data
                json_output = extract_search_results_from_html_content(content)
                sanitized_json_output = sanitize_json_data_rent(json_output)

                listings.extend(sanitized_json_output["listings"])
            else:
                print(
                    f"Error: Unable to scrape the URL {current_url} with status code {response.status_code}"
                )

        except Exception as e:
            print(f"Error (URL: {current_url}): {e}")

    # Save the combined sanitized data
    save_sanitized_data_to_json(
        {"listings": listings, "count": len(listings)}, city, state
    )


def extract_search_results_from_html_content(content):
    start_index = content.find('"searchResults":')
    end_index = content.find(',"totalResultCount"')
    extracted_data = content[start_index:end_index] + "}"
    return json.loads("{" + extracted_data + "}")


def sanitize_json_data_rent(json_data):
    sanitized_list = []
    try:
        for listing in json_data["searchResults"]["listResults"]:
            sanitized_info = {
                "streetAddress": listing.get("addressStreet", "N/A"),
                "zipcode": listing.get("addressZipcode", "N/A"),
                "city": listing.get("addressCity", "N/A"),
                "state": listing.get("addressState", "N/A"),
                "latitude": listing.get("latLong", {}).get("latitude", "N/A"),
                "longitude": listing.get("latLong", {}).get("longitude", "N/A"),
                "price": listing.get("price", "N/A"),
                "beds": listing.get("beds", "N/A"),
                "baths": listing.get("baths", "N/A"),
                "area": listing.get("area", "N/A"),
                "availabilityCount": listing.get("availabilityCount", "N/A"),
            }
            sanitized_list.append(sanitized_info)
    except Exception as e:
        print(f"Error: {e}")

    return {"listings": sanitized_list, "count": len(sanitized_list)}


def save_sanitized_data_to_json(json_data, city, state):
    sanitized_filename = f"{city}_{state}_rentals.json"
    try:
        # Check if the file exists and has content
        with open(sanitized_filename, "r", encoding="utf-8") as f:
            existing_data = json.load(f)

            # Update the listings and the count
            existing_data["listings"].extend(json_data["listings"])
            existing_data["count"] = len(existing_data["listings"])
    except (FileNotFoundError, json.JSONDecodeError):
        # If the file doesn't exist or is empty, set the existing_data as the new data
        existing_data = json_data

    # Write back the combined/updated data
    with open(sanitized_filename, "w", encoding="utf-8") as f:
        json.dump(existing_data, f, indent=4)


def main():
    root = tk.Tk()
    root.geometry("800x600")
    root.title("Zillow Rental Scraper")

    city_label = tk.Label(root, text="Enter City:")
    city_label.pack(pady=10)
    city_input = tk.Entry(root)
    city_input.pack(pady=10)

    state_label = tk.Label(root, text="Enter State (e.g. tn):")
    state_label.pack(pady=10)
    state_input = tk.Entry(root)
    state_input.pack(pady=10)

    page_label = tk.Label(root, text="Enter Number of Pages (default 10):")
    page_label.pack(pady=10)
    page_input = tk.Entry(root)
    page_input.pack(pady=10)

    min_price_label = tk.Label(root, text="Enter Minimum Price (optional):")
    min_price_label.pack(pady=10)
    min_price_input = tk.Entry(root)
    min_price_input.pack(pady=10)

    max_price_label = tk.Label(root, text="Enter Maximum Price (optional):")
    max_price_label.pack(pady=10)
    max_price_input = tk.Entry(root)
    max_price_input.pack(pady=10)

    def on_scrape():
        try:
            num_pages = int(page_input.get()) if page_input.get() else 10
            price_min = int(min_price_input.get()) if min_price_input.get() else None
            price_max = int(max_price_input.get()) if max_price_input.get() else None
            scrape_zillow(
                city_input.get(), state_input.get(), num_pages, price_min, price_max
            )
            messagebox.showinfo(
                "Info",
                f"Data scraped and sanitized data saved to '{city_input.get().strip().lower()}_{state_input.get().strip().lower()}_rentals.json'",
            )
        except Exception as e:
            messagebox.showerror("Error", str(e))

    scrape_rent_button = tk.Button(
        root, text="Scrape Zillow Rentals", command=on_scrape
    )
    scrape_rent_button.pack(pady=10)

    root.mainloop()


if __name__ == "__main__":
    main()
