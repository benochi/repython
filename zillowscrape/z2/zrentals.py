import os
import time
import requests
import json
import tkinter as tk
from tkinter import messagebox

# API Key for ScraperAPI
api_key = "31fecb85a35e9ccb447ede630e4caf32"

# Base URL for Zillow
ZILLOW_BASE_URL = "https://www.zillow.com/"


# Function to scrape Zillow using ScraperAPI
def scrape_zillow_rentals(city, state, num_pages=10):
    city = city.strip().lower() or "clarksville"
    state = state.strip().lower() or "tn"

    listings = []

    for page_number in range(1, num_pages + 1):
        # Construct the URL
        current_url = (
            f"{ZILLOW_BASE_URL}{city}-{state}/rentals/"
            if page_number == 1
            else f"{ZILLOW_BASE_URL}{city}-{state}/rentals/{page_number}_p/"
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
                txt_output = extract_search_results_from_html_content(content)
                json_output = convert_txt_to_json_content(txt_output)
                sanitized_json_output = sanitize_json_data(json_output)
                listings.extend(sanitized_json_output["listings"])
            else:
                print(
                    f"Error: Unable to scrape the URL {current_url} with status code {response.status_code}"
                )

        except Exception as e:
            print(f"Error (URL: {current_url}): {e}")

    # Save the combined sanitized data
    save_sanitized_data_to_json({"listings": listings, "count": len(listings)})


def extract_search_results_from_html_content(content):
    start_index = content.find('"searchResults":')
    end_index = content.find('"totalResultCount"') + len('"totalResultCount"')
    extracted_data = "{" + content[start_index:end_index] + ":1}}"
    return extracted_data


def convert_txt_to_json_content(txt_content):
    return json.loads(txt_content)


def sanitize_json_data(input_data):
    if isinstance(input_data, str):
        json_data = json.loads(input_data)
    else:
        json_data = input_data

    sanitized_list = []
    try:
        for listing in json_data["searchResults"]["listResults"]:
            home_info = listing["hdpData"]["homeInfo"]
            sanitized_info = {
                "streetAddress": home_info.get("streetAddress", "N/A"),
                "zipcode": home_info.get("zipcode", "N/A"),
                "city": home_info.get("city", "N/A"),
                "state": home_info.get("state", "N/A"),
                "price": home_info.get("price", 0),
                "bathrooms": home_info.get("bathrooms", 0),
                "bedrooms": home_info.get("bedrooms", 0),
                "livingArea": home_info.get("livingArea", 0),
                "homeType": home_info.get("homeType", "N/A"),
                "homeStatus": home_info.get("homeStatus", "N/A"),
                "daysOnZillow": home_info.get("daysOnZillow", "N/A"),
                "rentZestimate": home_info.get("rentZestimate", 0),
            }
            sanitized_list.append(sanitized_info)
    except Exception as e:
        print(f"Error: {e}")

    return {"listings": sanitized_list, "count": len(sanitized_list)}


def save_sanitized_data_to_json(json_data):
    sanitized_filename = "rentals.json"
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
    root.title("Zillow Rentals Scraper")

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

    def on_scrape():
        try:
            num_pages = int(page_input.get()) if page_input.get() else 10
            scrape_zillow_rentals(city_input.get(), state_input.get(), num_pages)
            messagebox.showinfo(
                "Info", "Data scraped and sanitized data saved to 'rentals.json'"
            )
        except Exception as e:
            messagebox.showerror("Error", str(e))

    scrape_button = tk.Button(root, text="Scrape Zillow Rentals", command=on_scrape)
    scrape_button.pack(pady=20)

    root.mainloop()


if __name__ == "__main__":
    main()
