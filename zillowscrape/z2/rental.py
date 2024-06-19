import tkinter as tk
from tkinter import ttk, messagebox
import json
import csv

calculated_data = []


def load_rentals_data():
    global calculated_data
    try:
        with open("rentals.json", "r") as file:
            data = json.load(file)
            listings = data.get("listings", [])

            unique_entries = set()
            unique_listings = []

            for listing in listings:
                identifier = f"{listing['streetAddress']}_{listing['zipcode']}_{listing['city']}_{listing['state']}"
                if identifier not in unique_entries:
                    unique_entries.add(identifier)
                    unique_listings.append(listing)

            # Calculate price per square foot and add it to each listing
            for listing in unique_listings:
                try:
                    price_value = float(
                        listing["price"]
                        .replace("$", "")
                        .replace(",", "")
                        .replace("/mo", "")
                        .strip()
                    )
                    area_value = float(listing["area"])
                    listing["price_per_sqft"] = round(price_value / area_value, 2)
                except (ValueError, KeyError):
                    listing["price_per_sqft"] = "N/A"

            calculated_data = unique_listings

            with open("rentals_output.csv", "w", newline="") as csv_file:
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
        tree.insert("", "end", values=tuple(row[col] for col in columns))


def on_load_data(tree):
    global calculated_data
    data = load_rentals_data()
    if isinstance(data, str) and "Error" in data:
        messagebox.showerror("Error", data)
    else:
        display_csv_in_tree(tree, data)


# Sorting function
def sort_column(tree, col, reverse):
    l = [(tree.set(k, col), k) for k in tree.get_children("")]
    l.sort(reverse=reverse)
    for index, (val, k) in enumerate(l):
        tree.move(k, "", index)
    tree.heading(col, command=lambda: sort_column(tree, col, not reverse))


def on_search(tree, search_term):
    global calculated_data
    filtered_data = []
    for entry in calculated_data:
        if search_term.lower() in entry["streetAddress"].lower():
            filtered_data.append(entry)
    display_csv_in_tree(tree, filtered_data)


def on_item_selected(event, selected_address_text):
    selected_item = event.widget.selection()[0]
    item_data = event.widget.item(selected_item)["values"]
    street_address = item_data[0]  # Assuming "Street Address" is the first column
    selected_address_text.config(state=tk.NORMAL)  # Enable editing
    selected_address_text.delete(1.0, tk.END)  # Clear the current content
    selected_address_text.insert(tk.END, street_address)  # Insert the new address
    selected_address_text.config(state=tk.DISABLED)


def calculate_average_rent_by_zipcode():
    zipcode_rent = {}
    zipcode_count = {}

    for entry in calculated_data:
        zipcode = entry["zipcode"]
        price = entry["price"]
        try:
            price_value = float(
                price.replace("$", "").replace(",", "").replace("/mo", "").strip()
            )
            if zipcode not in zipcode_rent:
                zipcode_rent[zipcode] = 0
                zipcode_count[zipcode] = 0
            zipcode_rent[zipcode] += price_value
            zipcode_count[zipcode] += 1
        except ValueError:
            continue

    avg_rent_by_zipcode = {
        zipcode: round(zipcode_rent[zipcode] / zipcode_count[zipcode], 2)
        for zipcode in zipcode_rent
    }
    return avg_rent_by_zipcode


def display_average_rent_by_zipcode(tree):
    avg_rent_by_zipcode = calculate_average_rent_by_zipcode()
    for item in tree.get_children():
        tree.delete(item)

    for zipcode, avg_rent in avg_rent_by_zipcode.items():
        tree.insert("", "end", values=(zipcode, avg_rent))


def main():
    global columns
    root = tk.Tk()
    root.geometry("1500x800")
    root.title("Rentals Data Viewer")

    label = tk.Label(root, text="Click the button to load the rentals data.")
    label.pack(pady=10)

    columns = [
        "streetAddress",
        "zipcode",
        "city",
        "state",
        "price",
        "beds",
        "baths",
        "area",
        "availabilityCount",
        "latitude",
        "longitude",
        "price_per_sqft",
    ]

    frame = ttk.Frame(root)
    frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

    scrollbar = ttk.Scrollbar(frame, orient="vertical")
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    tree = ttk.Treeview(
        frame, columns=columns, show="headings", yscrollcommand=scrollbar.set
    )

    # Updated column loop to include sorting binding
    for col in columns:
        tree.heading(
            col, text=col, command=lambda _col=col: sort_column(tree, _col, False)
        )
        tree.column(col, width=100, anchor=tk.W)

    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.config(command=tree.yview)

    # Text widget to display the selected street address
    selected_address_text = tk.Text(root, height=1, width=50)
    selected_address_text.pack(pady=10)

    # Bind the selection event to the on_item_selected function
    tree.bind(
        "<<TreeviewSelect>>",
        lambda event: on_item_selected(event, selected_address_text),
    )

    # Search bar and button
    search_label = tk.Label(root, text="Search Address:")
    search_label.pack(pady=10)

    search_entry = tk.Entry(root, width=50)
    search_entry.pack(pady=10)

    # Modify the search button to use the calculated_data
    search_btn = tk.Button(
        root, text="Search", command=lambda: on_search(tree, search_entry.get())
    )
    search_btn.pack(pady=10)

    load_btn = tk.Button(root, text="Load Data", command=lambda: on_load_data(tree))
    load_btn.pack(pady=10)

    avg_rent_btn = tk.Button(
        root,
        text="Show Average Rent by Zipcode",
        command=lambda: display_average_rent_by_zipcode(tree),
    )
    avg_rent_btn.pack(pady=10)

    root.mainloop()


if __name__ == "__main__":
    main()
