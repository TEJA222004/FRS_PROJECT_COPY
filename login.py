import ttkbootstrap as ttk
from tkinter import messagebox
from ttkbootstrap.constants import *
from dashboard import Dashboard

class Login:
    def __init__(self, root, db):
        self.root = root
        self.db = db
        self.setup_ui()

    def setup_ui(self):
        self.root.configure(bg='#f8f9fa')
        style = ttk.Style()
        style.configure('TButton', font=('Helvetica', 10))
        style.configure('TLabel', font=('Helvetica', 12))
        style.configure('TEntry', font=('Helvetica', 10))

        self.frame = ttk.Frame(self.root, padding=20, bootstyle=LIGHT)
        self.frame.place(relx=0.5, rely=0.5, anchor=CENTER)

        ttk.Label(self.frame, text="Login", font=('Helvetica', 16, 'bold'), bootstyle=PRIMARY).grid(row=0, columnspan=2, pady=10)

        ttk.Label(self.frame, text="Username:").grid(row=1, column=0, sticky=W, pady=5)
        self.username_entry = ttk.Entry(self.frame)
        self.username_entry.grid(row=1, column=1, pady=5)

        ttk.Label(self.frame, text="Password:").grid(row=2, column=0, sticky=W, pady=5)
        self.password_entry = ttk.Entry(self.frame, show="*")
        self.password_entry.grid(row=2, column=1, pady=5)

        ttk.Button(self.frame, text="Login", command=self.validate_login, bootstyle=PRIMARY).grid(row=3, column=1, pady=20)

    def validate_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username == "admin" and password == "password":
            self.frame.destroy()
            Dashboard(self.root, self.db)
        else:
            messagebox.showerror("Error", "Invalid credentials!")