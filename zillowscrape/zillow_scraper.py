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
