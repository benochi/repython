import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import csv

calculated_data = []
perfect_comps_data = []


def load_data(file_name):
    try:
        with open(file_name, "r") as file:
            data = json.load(file)
            return data.get("listings", [])
    except Exception as e:
        print(f"Error loading data from {file_name}: {e}")
        return []


def calculate_price_to_rent_ratio(for_sale, for_rent):
    price_to_rent_list = []
    for sale in for_sale:
        for rent in for_rent:
            if (
                sale["zipcode"] == rent["zipcode"]
                and sale["city"].lower() == rent["city"].lower()
                and sale["state"].lower() == rent["state"].lower()
            ):
                try:
                    sale_price = float(sale["price"])
                    rent_price = float(
                        rent["price"]
                        .replace("$", "")
                        .replace(",", "")
                        .replace("/mo", "")
                        .strip()
                    )
                    living_area = float(sale.get("livingArea", 0))
                    rent_area = float(rent.get("area", 0))
                    if living_area == 0 or rent_area == 0:
                        raise ValueError(
                            "Living area is zero, cannot calculate price per sqft."
                        )

                    price_to_rent_ratio = round(sale_price / (rent_price * 12), 2)
                    price_per_sqft = round(sale_price / living_area, 2)
                    rent_per_sqft = round(rent_price / rent_area, 2)
                    months_to_pay_off = round(sale_price / rent_price, 2)

                    price_to_rent_list.append(
                        {
                            "Street Address": sale["streetAddress"],
                            "Zipcode": sale["zipcode"],
                            "City/State": f"{sale['city']}/{sale['state']}",
                            "Sale Price": round(sale_price, 2),
                            "Rent Price": round(rent_price, 2),
                            "Beds/Baths (Sale)": f"{sale['bedrooms']}/{sale['bathrooms']}",
                            "Beds/Baths (Rent)": f"{rent['beds']}/{rent['baths']}",
                            "Sqft (Sale)": living_area,
                            "Area (Rent)": rent_area,
                            "Price/Rent (Months)": months_to_pay_off,
                            "Price per Sqft": price_per_sqft,
                            "Rent per Sqft": rent_per_sqft,
                            "Zestimate": sale.get("zestimate", "N/A"),
                            "Rent Zestimate": sale.get("rentZestimate", "N/A"),
                            "Rent Address": rent["streetAddress"],
                        }
                    )
                except (ValueError, KeyError, TypeError) as e:
                    print(f"Error processing data: {e}")
                    continue
    return sorted(price_to_rent_list, key=lambda x: x["Price/Rent (Months)"])


def display_data_in_tree(tree, data):
    for item in tree.get_children():
        tree.delete(item)

    for i, row in enumerate(data):
        values = tuple(row[col] for col in columns)
        tree.insert("", "end", values=values)

        # Highlight rows where Beds/Baths (Sale) matches Beds/Baths (Rent)
        if row["Beds/Baths (Sale)"] == row["Beds/Baths (Rent)"]:
            if abs(row["Sqft (Sale)"] - row["Area (Rent)"]) <= 100:
                tree.item(tree.get_children()[-1], tags=("perfect_match",))
            else:
                tree.item(tree.get_children()[-1], tags=("match",))

    tree.tag_configure("match", background="yellow")
    tree.tag_configure(
        "perfect_match", background="light green", font=("Helvetica", 10, "bold")
    )


def display_perfect_comps():
    global perfect_comps_data
    perfect_comps_data = [
        row
        for row in calculated_data
        if row["Beds/Baths (Sale)"] == row["Beds/Baths (Rent)"]
        and abs(row["Sqft (Sale)"] - row["Area (Rent)"]) <= 100
    ]

    if not perfect_comps_data:
        messagebox.showinfo("Info", "No perfect comps found.")
        return

    def create_popup():
        popup = tk.Toplevel()
        popup.title("Perfect Comps")
        popup.geometry("1600x900")

        frame = ttk.Frame(popup)
        frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(frame, orient="vertical")
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        tree = ttk.Treeview(
            frame, columns=columns, show="headings", yscrollcommand=scrollbar.set
        )

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor=tk.W)

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=tree.yview)

        display_data_in_tree(tree, perfect_comps_data)

    create_popup()


def save_perfect_comps_csv():
    if not perfect_comps_data:
        messagebox.showerror("Error", "No perfect comps to export.")
        return

    try:
        with open("perfect_comps.csv", "w", newline="") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=columns)
            writer.writeheader()
            for row in perfect_comps_data:
                writer.writerow(row)
        messagebox.showinfo("Success", "Data exported to perfect_comps.csv")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to export data: {e}")


def on_load_data(tree):
    sale_file = filedialog.askopenfilename(
        title="Select For Sale JSON File", filetypes=[("JSON files", "*.json")]
    )
    rent_file = filedialog.askopenfilename(
        title="Select Rental JSON File", filetypes=[("JSON files", "*.json")]
    )

    if not sale_file or not rent_file:
        messagebox.showerror(
            "Error", "Please select both For Sale and Rental JSON files."
        )
        return

    for_sale = load_data(sale_file)
    for_rent = load_data(rent_file)

    if not for_sale:
        messagebox.showerror("Error", "Failed to load for sale data.")
        return
    if not for_rent:
        messagebox.showerror("Error", "Failed to load rental data.")
        return

    global calculated_data
    calculated_data = calculate_price_to_rent_ratio(for_sale, for_rent)
    display_data_in_tree(tree, calculated_data)


def export_to_csv():
    if not calculated_data:
        messagebox.showerror("Error", "No data to export.")
        return

    try:
        with open("investment_opportunities.csv", "w", newline="") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=columns)
            writer.writeheader()
            for row in calculated_data:
                writer.writerow(row)
        messagebox.showinfo("Success", "Data exported to investment_opportunities.csv")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to export data: {e}")


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
        if search_term.lower() in entry["Street Address"].lower():
            filtered_data.append(entry)
    display_data_in_tree(tree, filtered_data)


def on_item_selected(event, selected_address_text):
    selected_item = event.widget.selection()[0]
    item_data = event.widget.item(selected_item)["values"]
    street_address = item_data[0]  # Assuming "Street Address" is the first column
    selected_address_text.config(state=tk.NORMAL)  # Enable editing
    selected_address_text.delete(1.0, tk.END)  # Clear the current content
    selected_address_text.insert(tk.END, street_address)  # Insert the new address
    selected_address_text.config(state=tk.DISABLED)


def main():
    global columns
    root = tk.Tk()
    root.geometry("1600x900")
    root.title("Investment Opportunities Viewer")

    label = tk.Label(root, text="Click the button to load the data.")
    label.pack(pady=10)

    columns = [
        "Street Address",
        "Zipcode",
        "City/State",
        "Sale Price",
        "Rent Price",
        "Beds/Baths (Sale)",
        "Beds/Baths (Rent)",
        "Sqft (Sale)",
        "Area (Rent)",
        "Price/Rent (Months)",
        "Price per Sqft",
        "Rent per Sqft",
        "Zestimate",
        "Rent Zestimate",
        "Rent Address",
    ]

    frame = ttk.Frame(root)
    frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

    scrollbar = ttk.Scrollbar(frame, orient="vertical")
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    tree = ttk.Treeview(
        frame, columns=columns, show="headings", yscrollcommand=scrollbar.set
    )

    for col in columns:
        tree.heading(
            col, text=col, command=lambda _col=col: sort_column(tree, _col, False)
        )
        tree.column(col, width=100, anchor=tk.W)

    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.config(command=tree.yview)

    selected_address_text = tk.Text(root, height=1, width=50)
    selected_address_text.pack(pady=10)

    tree.bind(
        "<<TreeviewSelect>>",
        lambda event: on_item_selected(event, selected_address_text),
    )

    search_label = tk.Label(root, text="Search Address:")
    search_label.pack(pady=10)

    search_entry = tk.Entry(root, width=50)
    search_entry.pack(pady=10)

    search_btn = tk.Button(
        root, text="Search", command=lambda: on_search(tree, search_entry.get())
    )
    search_btn.pack(pady=10)

    load_btn = tk.Button(root, text="Load Data", command=lambda: on_load_data(tree))
    load_btn.pack(pady=10)

    export_btn = tk.Button(root, text="Export to CSV", command=export_to_csv)
    export_btn.pack(pady=10)

    view_comps_btn = tk.Button(
        root, text="View Perfect Comps", command=display_perfect_comps
    )
    view_comps_btn.pack(pady=10)

    save_comps_btn = tk.Button(
        root, text="Save Perfect Comps CSV", command=save_perfect_comps_csv
    )
    save_comps_btn.pack(pady=10)

    root.mainloop()


if __name__ == "__main__":
    main()
