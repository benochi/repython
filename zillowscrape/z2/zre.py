import os
import requests
import json
import tkinter as tk
from tkinter import messagebox

# API Key for ScraperAPI
api_key = "31fecb85a35e9ccb447ede630e4caf32"

# Base URL for Zillow
ZILLOW_BASE_URL = "https://www.zillow.com/"


# Function to scrape Zillow using ScraperAPI
def scrape_zillow(city, state, num_pages=10, scrape_type="sale"):
    city = city.strip().lower() or "clarksville"
    state = state.strip().lower() or "tn"
    scrape_type = scrape_type.lower()

    listings = []

    for page_number in range(1, num_pages + 1):
        # Construct the URL
        if scrape_type == "sale":
            current_url = (
                f"{ZILLOW_BASE_URL}{city}-{state}/"
                if page_number == 1
                else f"{ZILLOW_BASE_URL}{city}-{state}/{page_number}_p/"
            )
        elif scrape_type == "rent":
            current_url = (
                f"{ZILLOW_BASE_URL}{city}-{state}/rent-houses/"
                if page_number == 1
                else f"{ZILLOW_BASE_URL}{city}-{state}/rent-houses/{page_number}_p/"
            )
        else:
            raise ValueError("Invalid scrape type. Use 'sale' or 'rent'.")

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
                if scrape_type == "sale":
                    json_output = extract_search_results_from_html_content(content)
                    sanitized_json_output = sanitize_json_data_sale(json_output)
                elif scrape_type == "rent":
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
        {"listings": listings, "count": len(listings)}, city, state, scrape_type
    )


def extract_search_results_from_html_content(content):
    start_index = content.find('"searchResults":')
    end_index = content.find(',"totalResultCount"')
    extracted_data = content[start_index:end_index] + "}"
    return json.loads("{" + extracted_data + "}")


def sanitize_json_data_sale(json_data):
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
                "zestimate": home_info.get("zestimate", 0),
                "rentZestimate": home_info.get("rentZestimate", 0),
            }
            sanitized_list.append(sanitized_info)
    except Exception as e:
        print(f"Error: {e}")

    return {"listings": sanitized_list, "count": len(sanitized_list)}


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


def save_sanitized_data_to_json(json_data, city, state, scrape_type):
    sanitized_filename = f"{city}_{state}_{scrape_type}.json"
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
    root.title("Zillow Scraper")

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

    def on_scrape(scrape_type):
        try:
            num_pages = int(page_input.get()) if page_input.get() else 10
            scrape_zillow(city_input.get(), state_input.get(), num_pages, scrape_type)
            messagebox.showinfo(
                "Info",
                f"Data scraped and sanitized data saved to '{city_input.get().strip().lower()}_{state_input.get().strip().lower()}_{scrape_type}.json'",
            )
        except Exception as e:
            messagebox.showerror("Error", str(e))

    scrape_sale_button = tk.Button(
        root, text="Scrape Zillow for Sale", command=lambda: on_scrape("sale")
    )
    scrape_sale_button.pack(pady=10)

    scrape_rent_button = tk.Button(
        root, text="Scrape Zillow Rentals", command=lambda: on_scrape("rent")
    )
    scrape_rent_button.pack(pady=10)

    root.mainloop()


if __name__ == "__main__":
    main()
