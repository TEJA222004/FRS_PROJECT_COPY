import ttkbootstrap as ttk
from tkinter import filedialog, messagebox
from ttkbootstrap.constants import *
import configparser
import os
from database import Database

class Wizard:
    def __init__(self, root, db, callback):
        self.root = root
        self.db = db
        self.callback = callback
        self.config = configparser.ConfigParser()
        self.config_file = 'config.ini'
        
        # Check if config already exists
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
            # Skip wizard if config is valid
            if self.validate_config():
                self.callback()
                return
        
        # Initialize new config if needed
        self.config['Paths'] = {'image_folder': '', 'db_path': '', 'csv_folder': ''}
        self.setup_ui()

    def validate_config(self):
        """Check if existing config has all required paths"""
        try:
            required = ['image_folder', 'db_path', 'csv_folder']
            return all(self.config['Paths'].get(key) for key in required)
        except (KeyError, configparser.Error):
            return False

    def setup_ui(self):
        self.root.configure(bg='#f8f9fa')
        style = ttk.Style()
        style.configure('TButton', font=('Helvetica', 10))
        style.configure('TLabel', font=('Helvetica', 12))
        style.configure('TEntry', font=('Helvetica', 10))

        self.frame = ttk.Frame(self.root, padding=20, bootstyle=LIGHT)
        self.frame.place(relx=0.5, rely=0.5, anchor=CENTER)

        ttk.Label(self.frame, text="Setup Wizard", font=('Helvetica', 16, 'bold'), bootstyle=PRIMARY).grid(row=0, columnspan=3, pady=10)

        # Image Folder
        ttk.Label(self.frame, text="Image Folder:").grid(row=1, column=0, sticky=W, pady=5)
        self.image_entry = ttk.Entry(self.frame, width=50)
        self.image_entry.grid(row=1, column=1, pady=5)
        ttk.Button(self.frame, text="Browse", command=self.browse_image_folder, bootstyle=INFO).grid(row=1, column=2, padx=5)

        # Database Path
        ttk.Label(self.frame, text="Database Path:").grid(row=2, column=0, sticky=W, pady=5)
        self.db_entry = ttk.Entry(self.frame, width=50)
        self.db_entry.grid(row=2, column=1, pady=5)
        ttk.Button(self.frame, text="Browse", command=self.browse_db_path, bootstyle=INFO).grid(row=2, column=2, padx=5)

        # CSV Folder
        ttk.Label(self.frame, text="CSV Folder:").grid(row=3, column=0, sticky=W, pady=5)
        self.csv_entry = ttk.Entry(self.frame, width=50)
        self.csv_entry.grid(row=3, column=1, pady=5)
        ttk.Button(self.frame, text="Browse", command=self.browse_csv_folder, bootstyle=INFO).grid(row=3, column=2, padx=5)

        # Finish Button
        ttk.Button(self.frame, text="Finish Setup", command=self.save_config, bootstyle=SUCCESS).grid(row=4, column=1, pady=20)

    def browse_image_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.image_entry.delete(0, ttk.END)
            self.image_entry.insert(0, folder)

    def browse_db_path(self):
        file = filedialog.asksaveasfilename(
            defaultextension=".db",
            filetypes=[("SQLite Database", "*.db"), ("All files", "*.*")]
        )
        if file:
            self.db_entry.delete(0, ttk.END)
            self.db_entry.insert(0, file)

    def browse_csv_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.csv_entry.delete(0, ttk.END)
            self.csv_entry.insert(0, folder)

    def save_config(self):
        image_folder = self.image_entry.get()
        db_path = self.db_entry.get()
        csv_folder = self.csv_entry.get()

        if not all([image_folder, db_path, csv_folder]):
            messagebox.showerror("Error", "All fields are required!")
            return

        # Create directories if they don't exist
        os.makedirs(image_folder, exist_ok=True)
        os.makedirs(csv_folder, exist_ok=True)

        self.config['Paths'] = {
            'image_folder': image_folder,
            'db_path': db_path,
            'csv_folder': csv_folder
        }

        try:
            with open(self.config_file, 'w') as configfile:
                self.config.write(configfile)
            
            # Initialize database with the new path
            self.db.set_db_path(db_path)
            self.db.initialize_db()
            
            messagebox.showinfo("Success", "Setup completed successfully!")
            self.frame.destroy()
            self.callback()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")