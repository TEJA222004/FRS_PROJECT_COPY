import ttkbootstrap as ttk
from tkinter import messagebox
from ttkbootstrap.constants import *
from student_registration import StudentRegistration
from reports import Reports
from attendance import start_attendance_scheduler
from update_student import UpdateStudent

class Dashboard:
    def __init__(self, root, db):
        self.root = root
        self.db = db
        self.setup_ui()
        start_attendance_scheduler(self.db)

    def setup_ui(self):
        # Set theme
        style = ttk.Style(theme='minty')
        
        # Configure custom styles
        style.configure('title.TLabel', font=('Helvetica', 16, 'bold'))
        style.configure('nav.TButton', font=('Helvetica', 11), width=20)
        style.configure('action.TButton', font=('Helvetica', 10, 'bold'), padding=10)

        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # Configure root layout grid to allow expansion
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        # Main container
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=BOTH, expand=YES)
        self.main_container.pack_propagate(False)

        # Sidebar
        self.sidebar = ttk.Frame(self.main_container, bootstyle=SECONDARY, width=220)
        self.sidebar.pack(side=LEFT, fill=Y)

        # Sidebar header
        ttk.Label(
            self.sidebar, 
            text="Attendance System", 
            style='title.TLabel',
            bootstyle=(SECONDARY, INVERSE)
        ).pack(pady=(20, 30), fill=X)

        # Navigation buttons
        nav_buttons = [
            ("🏠 Dashboard", lambda: self.show_frame('dashboard')),
            ("➕ New Student", self.new_student),
            ("✏️ Update Student", self.update_student),
            ("📋 Show Records", self.show_records),
            ("📊 Analytics", self.percentage_report),
            ("🚪 Logout", self.logout)
        ]

        for text, command in nav_buttons:
            btn = ttk.Button(
                self.sidebar,
                text=text,
                command=command,
                style='nav.TButton',
                bootstyle=(LINK if text == "🏠 Dashboard" else OUTLINE)
            )
            btn.pack(pady=5, padx=10, fill=X)

        # Main content area
        self.content = ttk.Frame(self.main_container, padding=(20, 20, 20, 20))
        self.content.pack(side=RIGHT, fill=BOTH, expand=YES)

        self.frames = {}
        self.setup_dashboard_frame()
        self.show_frame('dashboard')

    def setup_dashboard_frame(self):
        frame = ttk.Frame(self.content)
        self.frames['dashboard'] = frame

        # Header
        ttk.Label(
            frame, 
            text="Dashboard", 
            style='title.TLabel',
            bootstyle=PRIMARY
        ).pack(pady=(0, 20))

        # Simple welcome message
        welcome_msg = ttk.Label(
            frame,
            text="Welcome to the Student Attendance System\n\n"
                 "Use the navigation menu to manage students, view records,\n"
                 "or generate attendance reports.",
            font=('Helvetica', 12),
            justify=CENTER
        )
        welcome_msg.pack(pady=50)

    def show_frame(self, name):
        for frame in self.frames.values():
            frame.pack_forget()
        self.frames[name].pack(fill=BOTH, expand=YES)

    def new_student(self):
        self.clear_content()
        StudentRegistration(self.root, self.db, self.back_to_dashboard)

    def update_student(self):
        self.clear_content()
        UpdateStudent(self.root, self.db, self.back_to_dashboard)

    def show_records(self):
        self.clear_content()
        Reports(self.root, self.db, self.back_to_dashboard, mode="records")

    def percentage_report(self):
        self.clear_content()
        Reports(self.root, self.db, self.back_to_dashboard, mode="percentage")

    def clear_content(self):
        """Clear only the content area (right side)"""
        self.content.pack_forget()
        self.content = ttk.Frame(self.main_container, padding=(20, 20, 20, 20))
        self.content.pack(side=RIGHT, fill=BOTH, expand=YES)

    def back_to_dashboard(self):
        """Return to dashboard view"""
        self.clear_content()
        self.frames = {}
        self.setup_dashboard_frame()
        self.show_frame('dashboard')

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.root.destroy()
