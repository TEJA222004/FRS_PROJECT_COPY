import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import pandas as pd
import os
import configparser
from datetime import datetime, timedelta

class Reports:
    def __init__(self, root, db, callback, mode):
        self.root = root
        self.db = db
        self.callback = callback
        self.mode = mode
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.csv_folder = self.config['Paths']['csv_folder']
        self.setup_ui()

    def setup_ui(self):
        self.root.configure(bg='#f8f9fa')
        style = ttk.Style()
        style.configure('TButton', font=('Helvetica', 10))
        style.configure('TLabel', font=('Helvetica', 12))
        style.configure('Treeview.Heading', font=('Helvetica', 10, 'bold'))
        style.configure('Treeview', rowheight=25)

        self.frame = ttk.Frame(self.root, padding=20, bootstyle=LIGHT)
        self.frame.pack(fill=BOTH, expand=True)

        ttk.Label(self.frame, text="Attendance Reports", font=('Helvetica', 18, 'bold'), bootstyle=PRIMARY).pack(pady=10)

        if self.mode == "records":
            filter_frame = ttk.Frame(self.frame, bootstyle=LIGHT)
            filter_frame.pack(pady=10)

            ttk.Label(filter_frame, text="Year:").pack(side=ttk.LEFT, padx=5)
            self.year_var = ttk.StringVar(value="1")
            ttk.OptionMenu(filter_frame, self.year_var, "1", "2", "3", "4").pack(side=ttk.LEFT, padx=5)

            ttk.Label(filter_frame, text="Branch:").pack(side=ttk.LEFT, padx=5)
            self.branch_var = ttk.StringVar(value="CSE")
            ttk.OptionMenu(filter_frame, self.branch_var, "CSE", "ECE", "CSE-AI", "CSE-AIML").pack(side=ttk.LEFT, padx=5)

            ttk.Button(filter_frame, text="Show Records", command=self.show_records, bootstyle=PRIMARY).pack(side=ttk.LEFT, padx=5)

        elif self.mode == "percentage":
            ttk.Button(self.frame, text="Generate Weekly Report", command=self.show_percentage, bootstyle=PRIMARY).pack(pady=10)

        self.tree = ttk.Treeview(self.frame, bootstyle=PRIMARY, show='headings')
        self.tree.pack(pady=10, fill=BOTH, expand=True)

        ttk.Button(self.frame, text="Back", command=self.back, bootstyle=SECONDARY).pack(pady=10)

    def show_records(self):
        year = self.year_var.get()
        branch = self.branch_var.get()

        for item in self.tree.get_children():
            self.tree.delete(item)

        self.tree["columns"] = ("Student_ID", "Name", "Roll", "Date", "Session", "Status")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)

        for csv_file in os.listdir(self.csv_folder):
            if csv_file.endswith(".csv"):
                df = pd.read_csv(os.path.join(self.csv_folder, csv_file))
                df_filtered = df[(df['Year'] == int(year)) & (df['Branch'] == branch)]
                for _, row in df_filtered.iterrows():
                    self.tree.insert("", ttk.END, values=(
                        row['Student_ID'],
                        row['Name'],
                        row['Roll'],
                        row['Date'],
                        row['Session'],
                        row['Status']
                    ))

    def show_percentage(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.tree["columns"] = ("Student_ID", "Name", "Roll", "Year", "Branch", "Section", "Percentage")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)

        today = datetime.now().date()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)

        students = self.db.get_all_students()
        for student in students:
            student_id, name, roll, year, branch, section = student
            records = self.db.get_attendance_by_student(student_id, week_start, week_end)
            total_sessions = len(records)
            present_sessions = sum(1 for r in records if r[3] == 'Present')
            percentage = (present_sessions / total_sessions * 100) if total_sessions > 0 else 0
            self.tree.insert("", ttk.END, values=(
                student_id,
                name,
                roll,
                year,
                branch,
                section,
                f"{percentage:.2f}%"
            ))

    def back(self):
        self.frame.destroy()
        self.callback()