import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
from scraper import scrape_web
from exporter import export_to_csv

class ScraperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Web Scraper with GUI")

        # URL Entry
        self.url_label = tk.Label(root, text="Enter URL:")
        self.url_label.pack()
        self.url_entry = tk.Entry(root, width=50)
        self.url_entry.pack()

        # Tag/Class Entry
        self.tag_label = tk.Label(root, text="Enter Tag/Class (comma-separated for multiple tags):")
        self.tag_label.pack()
        self.tag_entry = tk.Entry(root, width=50)
        self.tag_entry.pack()

        # Buttons
        self.scrape_button = tk.Button(root, text="Scrape", command=self.scrape)
        self.scrape_button.pack()

        self.add_column_button = tk.Button(root, text="Add Column", command=self.add_column)
        self.add_column_button.pack()

        self.rename_column_button = tk.Button(root, text="Rename Selected Column", command=self.prepare_rename_column)
        self.rename_column_button.pack()

        self.delete_column_button = tk.Button(root, text="Delete Selected Column", command=self.delete_column)
        self.delete_column_button.pack()

        self.export_button = tk.Button(root, text="Export to CSV", command=self.export_csv)
        self.export_button.pack()

        # Treeview to Display Data
        self.tree = ttk.Treeview(root, columns=[], show="headings")
        self.tree.pack()
        self.tree.bind("<Button-1>", self.select_column)  # Bind left-click to select column
        self.tree.bind("<B1-Motion>", self.drag_column)  # Bind mouse drag for column reordering

        self.selected_column = None  # To keep track of the selected column
        self.rename_mode = False  # To track if we are in renaming mode

        # Initialize with one column
        self.add_column()

    def refresh_column_headers(self):
        """Refreshes the column headers after adding or renaming columns."""
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)

    def add_column(self):
        # Prompt user for column name
        column_name = simpledialog.askstring("Input", "Enter column name:", parent=self.root)
        if column_name:
            if column_name in self.tree["columns"]:
                messagebox.showerror("Error", "Column already exists!")
                return
            # Add column to Treeview and refresh headers
            self.tree["columns"] = (*self.tree["columns"], column_name)
            self.refresh_column_headers()

    def prepare_rename_column(self):
        """Prepare to rename a column after clicking the button."""
        self.rename_mode = True
        messagebox.showinfo("Info", "Click on the column you want to rename.")

    def rename_column(self):
        if not self.selected_column:
            messagebox.showerror("Error", "No column selected!")
            return

        new_name = simpledialog.askstring("Input", f"Enter new name for column '{self.selected_column}':", parent=self.root)
        if new_name:
            if new_name in self.tree["columns"]:
                messagebox.showerror("Error", "Column with this name already exists!")
                return

            columns = list(self.tree["columns"])
            index = columns.index(self.selected_column)
            columns[index] = new_name

            self.tree["columns"] = columns
            self.refresh_column_headers()
            self.selected_column = None  # Reset selected column
            self.rename_mode = False  # Exit renaming mode

    def delete_column(self):
        if not self.selected_column:
            messagebox.showerror("Error", "No column selected!")
            return

        confirm = messagebox.askyesno("Confirm", f"Are you sure you want to delete the column '{self.selected_column}'?")
        if confirm:
            columns = list(self.tree["columns"])
            columns.remove(self.selected_column)
            self.tree["columns"] = columns
            self.refresh_column_headers()
            self.selected_column = None  # Reset selected column

    def select_column(self, event):
        """Handles column selection when clicking on the column header."""
        region = self.tree.identify("region", event.x, event.y)
        if region == "heading":
            column = self.tree.identify_column(event.x)
            column_index = int(column.replace('#', '')) - 1  # Get the column index
            self.selected_column = self.tree["columns"][column_index]
            # Highlight the selected column header
            self.refresh_column_headers()
            if self.rename_mode:
                self.rename_column()
            else:
                self.tree.heading(self.selected_column, text=f"{self.selected_column} (Selected)")

    def drag_column(self, event):
        """Handles column reordering with drag and drop."""
        region = self.tree.identify("region", event.x, event.y)
        if region == "heading":
            column = self.tree.identify_column(event.x)
            column_index = int(column.replace('#', '')) - 1  # Get the column index
            if self.selected_column:
                columns = list(self.tree["columns"])
                current_index = columns.index(self.selected_column)
                if column_index != current_index:
                    # Swap columns
                    columns.insert(column_index, columns.pop(current_index))
                    self.tree["columns"] = columns
                    self.refresh_column_headers()

    def scrape(self):
        url = self.url_entry.get().strip()
        tags = self.tag_entry.get().strip()

        if not url:
            messagebox.showerror("Error", "URL cannot be empty!")
            return

        if not tags:
            messagebox.showerror("Error", "Tag/Class cannot be empty!")
            return

        if not self.selected_column:
            messagebox.showerror("Error", "No column selected!")
            return

        tag_list = tags.split(",")
        for tag in tag_list:
            tag = tag.strip()
            if not tag:
                continue

            try:
                print(f"Scraping data for tag: {tag}")  # Debugging line
                data = scrape_web(url, tag)
                print(f"Scraped data: {data}")  # Debugging line

                # Insert scraped data into the selected column
                for i, item in enumerate(data):
                    if len(self.tree.get_children()) > i:
                        self.tree.set(self.tree.get_children()[i], self.selected_column, item)
                    else:
                        self.tree.insert("", "end", values=([""] * len(self.tree["columns"])))
                        self.tree.set(self.tree.get_children()[-1], self.selected_column, item)

            except Exception as e:
                messagebox.showerror("Error", f"An error occurred while scraping: {e}")


    def export_csv(self):
        data = {col: [self.tree.set(item, col) for item in self.tree.get_children()] for col in self.tree["columns"]}
        if not data:
            messagebox.showwarning("No Data", "No data to export!")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                 filetypes=[("CSV files", "*.csv")])
        if file_path:
            export_to_csv(data, file_path)
            messagebox.showinfo("Success", "Data exported successfully!")

if __name__ == "__main__":
    root = tk.Tk()
    gui = ScraperGUI(root)
    root.mainloop()
