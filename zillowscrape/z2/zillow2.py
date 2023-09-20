import tkinter as tk
from tkinter import messagebox
from selenium import webdriver
import json
from time import sleep

ZILLOW_BASE_URL = "https://www.zillow.com/"

def scrape_zillow(city, state, page_number=1):
    city = city.strip().lower()  or "clarksville"
    state = state.strip().lower() or "tn"
    driver = webdriver.Chrome()

    current_url = f"{ZILLOW_BASE_URL}{city}-{state}/" if page_number == 1 else f"{ZILLOW_BASE_URL}{city}-{state}/{page_number}_p/"
    
    try:
        driver.get(current_url)
        print(f"Scraping from URL: {current_url}")  # Feedback

        sleep(30)  # Wait for 10 seconds to manually handle CAPTCHA

        content = driver.page_source

        # Your extraction, conversion, sanitization logic here
        txt_output = extract_search_results_from_html_content(content)
        json_output = convert_txt_to_json_content(txt_output)
        sanitized_json_output = sanitize_json_data(json_output)
        save_sanitized_data_to_json(sanitized_json_output)

    except Exception as e:
        print(f"Error (URL: {current_url}): {e}")

    driver.quit()


def extract_search_results_from_html_content(content):
    start_index = content.find('"searchResults":')
    end_index = content.find('"totalResultCount"') + len('"totalResultCount"')
    extracted_data = '{' + content[start_index:end_index] + ':1}}'
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
        for listing in json_data['searchResults']['listResults']:
            home_info = listing['hdpData']['homeInfo']
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
                "rentZestimate": home_info.get("rentZestimate", 0)
            }
            sanitized_list.append(sanitized_info)
    except Exception as e:
        print(f"Error: {e}")

    return {"listings": sanitized_list, "count": len(sanitized_list)}


def save_sanitized_data_to_json(json_data):
    sanitized_filename = "sanitized.json"
    try:
        # Check if the file exists and has content
        with open(sanitized_filename, 'r', encoding="utf-8") as f:
            existing_data = json.load(f)

            # Update the listings and the count
            existing_data['listings'].extend(json_data['listings'])
            existing_data['count'] = len(existing_data['listings'])
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

    page_label = tk.Label(root, text="Enter Page Number:")
    page_label.pack(pady=10)
    page_input = tk.Entry(root)
    page_input.pack(pady=10)

    def on_scrape():
        try:
            scrape_zillow(city_input.get(), state_input.get(), int(page_input.get()))
            messagebox.showinfo("Info", "Data scraped and sanitized data saved to 'sanitized.json'")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    scrape_button = tk.Button(root, text="Scrape Zillow", command=on_scrape)
    scrape_button.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    main()