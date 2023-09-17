import tkinter as tk
from tkinter import messagebox, filedialog
from zillow_scraper import scrape_zillow, write_to_file, extract_search_results_from_html, convert_txt_to_json

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

    def on_extract():
        try:
            filepath = filedialog.askopenfilename(title="Select HTML File", filetypes=(("HTML files", "*.html"), ("All files", "*.*")))
            if not filepath:
                return
            txt_output = extract_search_results_from_html(filepath)
            messagebox.showinfo("Info", f"Extracted data has been saved to '{txt_output}'")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_convert():
        try:
            filepath = filedialog.askopenfilename(title="Select TXT File", filetypes=(("TXT files", "*.txt"), ("All files", "*.*")))
            if not filepath:
                return
            json_output = convert_txt_to_json(filepath)
            messagebox.showinfo("Info", f"TXT data has been converted and saved to '{json_output}'")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    scrape_button = tk.Button(root, text="Scrape Zillow", command=on_scrape)
    scrape_button.pack(pady=20)

    extract_button = tk.Button(root, text="Extract to TXT", command=on_extract)
    extract_button.pack(pady=20)

    convert_button = tk.Button(root, text="Convert TXT to JSON", command=on_convert)
    convert_button.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    main()
