
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import sqlite3

## @file main.py
## @brief Garment Inventory Management System - GUI and Database logic.
##
## This file contains the main application logic for managing garment inventory using a Tkinter GUI and SQLite database.
## It provides classes for database operations and the graphical user interface, including CSV import, CRUD, and filtering.

DB_NAME = 'garments.db'


class GarmentDB:
    """
    @class GarmentDB
    @brief Handles all database operations for garment inventory.
    """

    def __init__(self):
        """
        @brief Initialize the GarmentDB and create the garments table if it doesn't exist.
        """
        self.conn = sqlite3.connect(DB_NAME)
        self.create_table()

    def create_table(self):
        """
        @brief Create the garments table and add the quantity column if upgrading from an old DB.
        """
        self.conn.execute('''CREATE TABLE IF NOT EXISTS garments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            size TEXT NOT NULL,
            color TEXT NOT NULL,
            style TEXT NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 0
        )''')
        # Add quantity column if upgrading from old DB
        try:
            self.conn.execute('ALTER TABLE garments ADD COLUMN quantity INTEGER NOT NULL DEFAULT 0')
        except sqlite3.OperationalError:
            pass
        self.conn.commit()

    def add_garment(self, name, size, color, style, quantity):
        """
        @brief Add a new garment to the database.
        @param name Name of the garment.
        @param size Size of the garment.
        @param color Color of the garment.
        @param style Style of the garment.
        @param quantity Quantity in stock.
        """
        self.conn.execute('INSERT INTO garments (name, size, color, style, quantity) VALUES (?, ?, ?, ?, ?)', (name, size, color, style, quantity))
        self.conn.commit()

    def update_garment(self, garment_id, name, size, color, style, quantity):
        """
        @brief Update an existing garment in the database by ID.
        @param garment_id ID of the garment to update.
        @param name Updated name.
        @param size Updated size.
        @param color Updated color.
        @param style Updated style.
        @param quantity Updated quantity.
        """
        self.conn.execute('UPDATE garments SET name=?, size=?, color=?, style=?, quantity=? WHERE id=?', (name, size, color, style, quantity, garment_id))
        self.conn.commit()

    def delete_garment(self, garment_id):
        """
        @brief Delete a garment from the database by ID.
        @param garment_id ID of the garment to delete.
        """
        self.conn.execute('DELETE FROM garments WHERE id=?', (garment_id,))
        self.conn.commit()

    def fetch_garments(self, filters=None):
        """
        @brief Fetch garments from the database, optionally filtered by the provided criteria.
        @param filters Dictionary of filter criteria (name, size, color, style).
        @return List of garment records.
        """
        query = 'SELECT * FROM garments'
        params = []
        if filters:
            clauses = []
            for key, value in filters.items():
                if value:
                    if key == 'name':
                        clauses.append(f"{key} = ?")
                        params.append(value)
                    else:
                        clauses.append(f"{key} LIKE ?")
                        params.append(f"%{value}%")
            if clauses:
                query += ' WHERE ' + ' AND '.join(clauses)
        cursor = self.conn.execute(query, params)
        return cursor.fetchall()


class GarmentApp:
    """
    @class GarmentApp
    @brief Main application class for the Garment Inventory Management GUI.
    """

    def __init__(self, root):
        """
        @brief Initialize the GarmentApp GUI and database connection.
        @param root Tkinter root window.
        """
        self.db = GarmentDB()
        self.root = root
        self.root.title('Garment Inventory Management')
        self.create_widgets()
        self.refresh_table()

    def create_widgets(self):
        """
        @brief Create and layout all GUI widgets for the application.
        """
        frame = ttk.Frame(self.root, padding=10)
        frame.pack(fill='both', expand=True)

        # Search/Filter
        filter_frame = ttk.LabelFrame(frame, text='Search/Filter Garments')
        filter_frame.pack(fill='x', pady=5)
        self.filter_name = tk.StringVar()
        self.filter_size = tk.StringVar()
        self.filter_color = tk.StringVar()
        self.filter_style = tk.StringVar()
        ttk.Label(filter_frame, text='Name:').grid(row=0, column=0, sticky='e')
        ttk.Entry(filter_frame, textvariable=self.filter_name, width=15).grid(row=0, column=1, padx=2)
        ttk.Label(filter_frame, text='Size:').grid(row=0, column=2, sticky='e')
        ttk.Entry(filter_frame, textvariable=self.filter_size, width=10).grid(row=0, column=3, padx=2)
        ttk.Label(filter_frame, text='Color:').grid(row=0, column=4, sticky='e')
        ttk.Entry(filter_frame, textvariable=self.filter_color, width=10).grid(row=0, column=5, padx=2)
        ttk.Label(filter_frame, text='Style:').grid(row=0, column=6, sticky='e')
        ttk.Entry(filter_frame, textvariable=self.filter_style, width=10).grid(row=0, column=7, padx=2)
        ttk.Button(filter_frame, text='Search', command=self.apply_filter).grid(row=0, column=8, padx=5)
        ttk.Button(filter_frame, text='Clear', command=self.clear_filter).grid(row=0, column=9, padx=5)

        # Form
        form_frame = ttk.LabelFrame(frame, text='Garment Details')
        form_frame.pack(fill='x', pady=5)
        ttk.Label(form_frame, text='Name:').grid(row=0, column=0, sticky='e')
        ttk.Label(form_frame, text='Size:').grid(row=0, column=2, sticky='e')
        ttk.Label(form_frame, text='Color:').grid(row=1, column=0, sticky='e')
        ttk.Label(form_frame, text='Style:').grid(row=1, column=2, sticky='e')
        self.name_var = tk.StringVar()
        self.size_var = tk.StringVar()
        self.color_var = tk.StringVar()
        self.style_var = tk.StringVar()
        self.quantity_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.name_var, width=20).grid(row=0, column=1, padx=5, pady=2)
        ttk.Entry(form_frame, textvariable=self.size_var, width=20).grid(row=0, column=3, padx=5, pady=2)
        ttk.Entry(form_frame, textvariable=self.color_var, width=20).grid(row=1, column=1, padx=5, pady=2)
        ttk.Entry(form_frame, textvariable=self.style_var, width=20).grid(row=1, column=3, padx=5, pady=2)
        ttk.Label(form_frame, text='Quantity:').grid(row=2, column=0, sticky='e')
        ttk.Entry(form_frame, textvariable=self.quantity_var, width=20).grid(row=2, column=1, padx=5, pady=2)
        ttk.Button(form_frame, text='Add', command=self.add_garment).grid(row=3, column=0, pady=5)
        ttk.Button(form_frame, text='Update', command=self.update_garment).grid(row=3, column=1, pady=5)
        ttk.Button(form_frame, text='Delete', command=self.delete_garment).grid(row=3, column=2, pady=5)
        ttk.Button(form_frame, text='Clear', command=self.clear_form).grid(row=3, column=3, pady=5)

        # Import Button
        import_btn = ttk.Button(frame, text='Import CSV', command=self.import_csv)
        import_btn.pack(pady=5)

        # Table
        self.tree = ttk.Treeview(frame, columns=('ID', 'Name', 'Size', 'Color', 'Style', 'Quantity'), show='headings')
        for col in ('ID', 'Name', 'Size', 'Color', 'Style', 'Quantity'):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor='center')
        self.tree.pack(fill='both', expand=True, pady=10)
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)

    def import_csv(self):
        """
        @brief Open a file dialog to import garments from a CSV file and add them to the database.
        """
        file_path = filedialog.askopenfilename(
            title='Select CSV File',
            filetypes=[('CSV Files', '*.csv'), ('All Files', '*.*')]
        )
        if not file_path:
            return
        count = 0
        try:
            with open(file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if len(row) != 5:
                        continue  # skip invalid rows
                    name, size, color, style, quantity = row
                    if not quantity.isdigit():
                        continue
                    self.db.add_garment(name.strip(), size.strip(), color.strip(), style.strip(), int(quantity))
                    count += 1
            self.refresh_table()
            messagebox.showinfo('Import Complete', f'Successfully imported {count} garments.')
        except Exception as e:
            messagebox.showerror('Import Failed', f'Error: {e}')

    def add_garment(self):
        """
        @brief Add a new garment to the database from the form fields.
        """
        name = self.name_var.get().strip()
        size = self.size_var.get().strip()
        color = self.color_var.get().strip()
        style = self.style_var.get().strip()
        quantity = self.quantity_var.get().strip()
        if not (name and size and color and style and quantity):
            messagebox.showwarning('Input Error', 'All fields are required.')
            return
        if not quantity.isdigit() or int(quantity) < 0:
            messagebox.showwarning('Input Error', 'Quantity must be a non-negative integer.')
            return
        self.db.add_garment(name, size, color, style, int(quantity))
        self.refresh_table()
        self.clear_form()

    def update_garment(self):
        """
        @brief Update the selected garment in the database with the form field values.
        """
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning('Select a record', 'No garment selected.')
            return
        garment_id = self.tree.item(selected[0])['values'][0]
        name = self.name_var.get().strip()
        size = self.size_var.get().strip()
        color = self.color_var.get().strip()
        style = self.style_var.get().strip()
        quantity = self.quantity_var.get().strip()
        if not (name and size and color and style and quantity):
            messagebox.showwarning('Input Error', 'All fields are required.')
            return
        if not quantity.isdigit() or int(quantity) < 0:
            messagebox.showwarning('Input Error', 'Quantity must be a non-negative integer.')
            return
        self.db.update_garment(garment_id, name, size, color, style, int(quantity))
        self.refresh_table()
        self.clear_form()

    def delete_garment(self):
        """
        @brief Delete the selected garment from the database.
        """
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning('Select a record', 'No garment selected.')
            return
        garment_id = self.tree.item(selected[0])['values'][0]
        if messagebox.askyesno('Confirm Delete', 'Delete selected garment?'):
            self.db.delete_garment(garment_id)
            self.refresh_table()
            self.clear_form()

    def clear_form(self):
        """
        @brief Clear all form fields and selection in the table.
        """
        self.name_var.set('')
        self.size_var.set('')
        self.color_var.set('')
        self.style_var.set('')
        self.quantity_var.set('')
        self.tree.selection_remove(self.tree.selection())

    def refresh_table(self, filters=None):
        """
        @brief Refresh the table view with garments from the database, optionally filtered.
        @param filters Dictionary of filter criteria (optional).
        """
        for row in self.tree.get_children():
            self.tree.delete(row)
        for garment in self.db.fetch_garments(filters):
            self.tree.insert('', 'end', values=garment)

    def apply_filter(self):
        """
        @brief Apply the current filter fields to the garment table view.
        """
        filters = {
            'name': self.filter_name.get().strip(),
            'size': self.filter_size.get().strip(),
            'color': self.filter_color.get().strip(),
            'style': self.filter_style.get().strip()
        }
        self.refresh_table(filters)

    def clear_filter(self):
        """
        @brief Clear all filter fields and refresh the table view.
        """
        self.filter_name.set('')
        self.filter_size.set('')
        self.filter_color.set('')
        self.filter_style.set('')
        self.refresh_table()

    def on_tree_select(self, event):
        """
        @brief Populate the form fields with the selected garment's data from the table.
        @param event Tkinter event object.
        """
        selected = self.tree.selection()
        if not selected:
            return
        garment = self.tree.item(selected[0])['values']
        self.name_var.set(garment[1])
        self.size_var.set(garment[2])
        self.color_var.set(garment[3])
        self.style_var.set(garment[4])
        self.quantity_var.set(str(garment[5]))


## @brief Main entry point for the Garment Inventory Management application.
if __name__ == '__main__':
    root = tk.Tk()
    app = GarmentApp(root)
    root.mainloop()
