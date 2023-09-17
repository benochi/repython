import tkinter as tk
from tkinter import messagebox, filedialog
from selenium import webdriver
import json

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


def parse_html_to_json(filepath):
    with open(filepath, "r", encoding="utf-8") as file:
        content = file.read()

    start_index = content.find('"searchResults":') + len('"searchResults":')
    end_index = content.find('"totalResultCount"')

    data_str = content[start_index:end_index].strip(", \n\r")

    if not (data_str.startswith("{") and data_str.endswith("}")):
        return None, f"Extracted data is not in expected format. Extracted data: {data_str[:100]}..."
    try:
        data = json.loads(data_str)
        listings = data["listResults"]
        # Extract specific information from each listing
        extracted_data = []
        for listing in listings:
            address = listing["address"]
            price = listing["price"]
            image = listing["imgSrc"]
            extracted_data.append({
                "address": address,
                "price": price,
                "image": image
            })
        
        return extracted_data, None

    except json.JSONDecodeError as e:
        return None, f"Error while parsing the extracted data: {e}. Problematic data: {data_str[:100]}..."  


def main():
    root = tk.Tk()
    root.geometry("900x600")
    root.title("Zillow Scraper")

    city_label = tk.Label(root, text="Enter City:")
    city_label.pack(pady=10)
    city_input = tk.Entry(root)
    city_input.pack(pady=10)

    state_label = tk.Label(root, text="Enter State (e.g. tn):")
    state_label.pack(pady=10)
    state_input = tk.Entry(root)
    state_input.pack(pady=10)

    def on_scrape():
        try:
            content = scrape_zillow(city_input.get(), state_input.get())
            write_to_file(content)
            messagebox.showinfo("Info", "Zillow data saved to 'zillow_data.html'")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_parse():
        try:
            filepath = filedialog.askopenfilename(title="Select HTML File", filetypes=(("HTML files", "*.html"), ("All files", "*.*")))
            if not filepath:
                return
            extracted_data, error_msg = parse_html_to_json(filepath)
            if error_msg:
                messagebox.showerror("Error", error_msg)
                return
            with open("filtered.json", "w", encoding="utf-8") as out_file:
                json.dump(extracted_data, out_file, indent=4)
            messagebox.showinfo("Info", "Filtered data has been saved to 'filtered.json'")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    scrape_button = tk.Button(root, text="Scrape Zillow", command=on_scrape)
    scrape_button.pack(pady=20)

    parse_button = tk.Button(root, text="Parse HTML to JSON", command=on_parse)
    parse_button.pack(pady=20)

    root.mainloop()


if __name__ == "__main__":
    main()
