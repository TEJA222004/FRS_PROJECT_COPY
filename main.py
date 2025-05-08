import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from wizard import Wizard
from login import Login
# In your main application file (e.g., main.py)
import configparser
from tkinter import messagebox, filedialog
from database import Database

def start_application():
    # Load configuration
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    # Initialize database
    try:
        if 'Paths' in config and 'db_path' in config['Paths']:
            db = Database(config['Paths']['db_path'])
        else:
            db = Database()
            # If no config, prompt for database path or show setup wizard
            db_path = filedialog.asksaveasfilename(
                defaultextension=".db",
                filetypes=[("Database files", "*.db"), ("All files", "*.*")],
                title="Select or create database file"
            )
            if db_path:
                db.connect(db_path)
                # Save the path to config for next time
                config['Paths'] = {'db_path': db_path}
                with open('config.ini', 'w') as configfile:
                    config.write(configfile)
            else:
                messagebox.showerror("Error", "Database path is required")
                return
        
        # Now proceed with your application
        # ...
        
    except ConnectionError as e:
        messagebox.showerror("Database Error", f"Failed to connect to database: {str(e)}")
        return
    except Exception as e:
        messagebox.showerror("Error", f"Initialization error: {str(e)}")
        return

if __name__ == "__main__":
    start_application()

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Attendance System")
        self.root.geometry("800x600")
        self.db = Database()
        self.show_wizard()

    def show_wizard(self):
        self.wizard = Wizard(self.root, self.db, self.show_login)

    def show_login(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.login = Login(self.root, self.db)

if __name__ == "__main__":
    root = ttk.Window(themename="litera")
    app = App(root)
    root.mainloop()