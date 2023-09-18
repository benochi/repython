from selenium import webdriver
import json
from datetime import datetime

ZILLOW_BASE_URL = "https://www.zillow.com/"

def scrape_zillow(city, state):
    city = city.strip().lower()
    state = state.strip().lower()
    url = f"{ZILLOW_BASE_URL}{city}-{state}/"

    driver = webdriver.Chrome()
    driver.get(url)
    content = driver.page_source
    driver.quit()

    return content

def write_to_file(content, filename="zillow_data.html"):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

def extract_search_results_from_html(filepath):
    with open(filepath, "r", encoding="utf-8") as file:
        content = file.read()

    start_index = content.find('"searchResults":')
    end_index = content.find('"totalResultCount"') + len('"totalResultCount"')

    extracted_data = '{' + content[start_index:end_index] + ':1}}'
    output_filename = datetime.now().strftime("%Y-%m-%d") + ".txt"
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(extracted_data)
    
    return output_filename

def convert_txt_to_json(filepath):
    with open(filepath, "r", encoding="utf-8") as file:
        content = file.read()

    json_data = json.loads(content)

    output_filename = filepath.replace(".txt", ".json")
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=4)
        
    return output_filename

def sanitize_json_data(input_data):
    # Check if the input data is a string (filepath) and load the file if needed
    if isinstance(input_data, str):
        with open(input_data, "r", encoding="utf-8") as file:
            json_data = json.load(file)
    else:
        json_data = input_data

    sanitized_list = []
    
    # Loop through each listing in the search results
    try:
        for listing in json_data['searchResults']['listResults']:
            home_info = listing['hdpData']['homeInfo']
            sanitized_info = {
                "streetAddress": home_info.get("streetAddress", "N/A"),
                "zipcode": home_info.get("zipcode", "N/A"),
                "city": home_info.get("city", "N/A"),
                "state": home_info.get("state", "N/A"),
                "price": home_info.get("price", 0),  # Default to 0
                "bathrooms": home_info.get("bathrooms", 0),  # Default to 0
                "bedrooms": home_info.get("bedrooms", 0),  # Default to 0
                "livingArea": home_info.get("livingArea", 0),  # Default to 0
                "homeType": home_info.get("homeType", "N/A"),
                "homeStatus": home_info.get("homeStatus", "N/A"),
                "daysOnZillow": home_info.get("daysOnZillow", "N/A"),
                "zestimate": home_info.get("zestimate", 0),  # Default to 0
                "rentZestimate": home_info.get("rentZestimate", 0)  # Default to 0
            }
            sanitized_list.append(sanitized_info)
    except Exception as e:
        print(f"Error: {e}")
    return {"listings": sanitized_list, "count": len(sanitized_list)}

def save_sanitized_data_to_json(json_data):
    sanitized_filename = "sanitized.json"
    with open(sanitized_filename, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=4)
    return sanitized_filename