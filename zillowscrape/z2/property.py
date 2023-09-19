import tkinter as tk
from tkinter import ttk, messagebox
import json
import csv

def calculate_ratio():
    try:
        with open("sanitized.json", "r") as file:
            data = json.load(file)
            listings = data.get('listings', [])

            # Use a set to filter out duplicates
            unique_entries = set()
            unique_listings = []

            for listing in listings:
                identifier = f"{listing['streetAddress']}_{listing['zipcode']}_{listing['city']}_{listing['state']}"
                if identifier not in unique_entries:
                    unique_entries.add(identifier)
                    unique_listings.append(listing)

            calculated_data = []
            for listing in unique_listings:
                price = listing['zestimate']
                rent = listing['rentZestimate']
                yearly_rent = rent * 12
                ratio = price / yearly_rent if yearly_rent else 0

                entry = {
                    'Street Address': listing['streetAddress'],
                    'Zipcode': listing['zipcode'],
                    'City': listing['city'],
                    'State': listing['state'],
                    'Price': price,
                    'Bedrooms': listing['bedrooms'],
                    'Bathrooms': listing['bathrooms'],
                    'Living Area': listing['livingArea'],
                    'Home Type': listing['homeType'],
                    'Home Status': listing['homeStatus'],
                    'Days On Zillow': listing['daysOnZillow'],
                    'Yearly Rent': yearly_rent,
                    'Payback Ratio (in years)': ratio
                }
                calculated_data.append(entry)

            calculated_data = sorted(calculated_data, key=lambda x: x["Payback Ratio (in years)"])

            # Write to CSV
            with open("output.csv", "w", newline='') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=calculated_data[0].keys())
                writer.writeheader()
                for row in calculated_data:
                    writer.writerow(row)

            return calculated_data

    except Exception as e:
        return f"Error: {e}"

def display_csv_in_tree(tree, data):
    for item in tree.get_children():
        tree.delete(item)

    for row in data:
        tree.insert('', 'end', values=tuple(row[col] for col in columns))

def on_calculate(tree):
    data = calculate_ratio()
    if isinstance(data, str) and "Error" in data:
        messagebox.showerror("Error", data)
    else:
        display_csv_in_tree(tree, data)
        messagebox.showinfo("Info", "Data calculated and displayed below.")

def main():
    global columns  # Making columns global for easy access in other functions

    root = tk.Tk()
    root.geometry("1500x800")  # Making the window larger
    root.title("Calculate Rent-to-Cost Ratio")

    label = tk.Label(root, text="Click the button to calculate the rent-to-cost ratio.")
    label.pack(pady=10)

    columns = ["Street Address", "Zipcode", "City", "State", "Price", "Bedrooms", "Bathrooms", "Living Area", 
               "Home Type", "Home Status", "Days On Zillow", "Yearly Rent", "Payback Ratio (in years)"]

    # Frame to hold the tree and scrollbar
    frame = ttk.Frame(root)
    frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

    # Add vertical scrollbar
    scrollbar = ttk.Scrollbar(frame, orient="vertical")
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    tree = ttk.Treeview(frame, columns=columns, show="headings", yscrollcommand=scrollbar.set)
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100, anchor=tk.W)
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar.config(command=tree.yview)
    # Pass 'tree' to the command
    btn = tk.Button(root, text="Calculate", command=lambda: on_calculate(tree))
    btn.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
