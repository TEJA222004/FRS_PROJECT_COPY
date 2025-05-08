import ttkbootstrap as ttk
from tkinter import messagebox, filedialog
from ttkbootstrap.constants import *
import cv2
import os
import configparser
from PIL import Image, ImageTk

class StudentRegistration:
    def __init__(self, root, db, callback):
        self.root = root
        self.db = db
        self.callback = callback
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.image_folder = self.config['Paths']['image_folder']
        self.image_count = 0
        self.images = []
        self.setup_ui()
        self.init_camera()

    def setup_ui(self):
        self.root.configure(bg='#f8f9fa')
        style = ttk.Style()
        style.configure('TButton', font=('Helvetica', 10))
        style.configure('TLabel', font=('Helvetica', 12))
        style.configure('TEntry', font=('Helvetica', 10))

        self.frame = ttk.Frame(self.root, padding=20, bootstyle=LIGHT)
        self.frame.pack(fill=BOTH, expand=True)

        # Left: Form
        self.form_frame = ttk.Frame(self.frame, padding=10, bootstyle=LIGHT)
        self.form_frame.pack(side=LEFT, padx=20, pady=20)

        ttk.Label(self.form_frame, text="Student Registration", font=('Helvetica', 16, 'bold'), bootstyle=PRIMARY).grid(row=0, columnspan=2, pady=10)

        ttk.Label(self.form_frame, text="Name:").grid(row=1, column=0, sticky=W, pady=5)
        self.name_entry = ttk.Entry(self.form_frame, width=30)
        self.name_entry.grid(row=1, column=1, pady=5)

        ttk.Label(self.form_frame, text="Roll Number:").grid(row=2, column=0, sticky=W, pady=5)
        self.roll_entry = ttk.Entry(self.form_frame, width=30)
        self.roll_entry.grid(row=2, column=1, pady=5)

        ttk.Label(self.form_frame, text="Year:").grid(row=3, column=0, sticky=W, pady=5)
        self.year_var = ttk.StringVar(value="1")
        ttk.OptionMenu(self.form_frame, self.year_var, "1", "2", "3", "4").grid(row=3, column=1, pady=5)

        ttk.Label(self.form_frame, text="Branch:").grid(row=4, column=0, sticky=W, pady=5)
        self.branch_var = ttk.StringVar(value="CSE")
        ttk.OptionMenu(self.form_frame, self.branch_var, "CSE", "ECE", "CSE-AI", "CSE-AIML").grid(row=4, column=1, pady=5)

        ttk.Label(self.form_frame, text="Section:").grid(row=5, column=0, sticky=W, pady=5)
        self.section_var = ttk.StringVar(value="A")
        ttk.OptionMenu(self.form_frame, self.section_var, "A", "B", "C", "D").grid(row=5, column=1, pady=5)

        ttk.Button(self.form_frame, text="Submit", command=self.submit, bootstyle=SUCCESS).grid(row=6, column=1, pady=20)

        # Right: Camera
        self.camera_frame = ttk.Frame(self.frame, padding=10, bootstyle=LIGHT)
        self.camera_frame.pack(side=RIGHT, padx=20, pady=20)

        self.canvas = ttk.Canvas(self.camera_frame, width=320, height=240)
        self.canvas.pack()

        ttk.Button(self.camera_frame, text="Capture Image", command=self.capture_image, bootstyle=INFO).pack(pady=10)
        self.image_label = ttk.Label(self.camera_frame, text="Images Captured: 0/5")
        self.image_label.pack()

        ttk.Button(self.camera_frame, text="Back", command=self.back, bootstyle=SECONDARY).pack(pady=10)

    def init_camera(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Error", "Cannot access camera!")
            return
        self.update_camera()

    def update_camera(self):
        if self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (320, 240))
                self.photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
                self.canvas.create_image(0, 0, image=self.photo, anchor=ttk.NW)
        self.root.after(10, self.update_camera)

    def capture_image(self):
        if self.image_count >= 5:
            messagebox.showinfo("Info", "Maximum 5 images captured!")
            return
        ret, frame = self.cap.read()
        if ret:
            self.image_count += 1
            self.images.append(frame)
            self.image_label.config(text=f"Images Captured: {self.image_count}/5")
            messagebox.showinfo("Success", f"Image {self.image_count} captured!")

    def submit(self):
        name = self.name_entry.get()
        roll = self.roll_entry.get()
        year = self.year_var.get()
        branch = self.branch_var.get()
        section = self.section_var.get()

        if not all([name, roll, year, branch, section]):
            messagebox.showerror("Error", "All fields are required!")
            return

        if self.image_count < 5:
            messagebox.showerror("Error", "Please capture 5 images!")
            return

        student_id = self.db.add_student(name, roll, year, branch, section)
        student_folder = os.path.join(self.image_folder, f"student_{student_id}")
        os.makedirs(student_folder, exist_ok=True)
        for i, img in enumerate(self.images):
            img_path = os.path.join(student_folder, f"image_{i+1}.jpg")
            cv2.imwrite(img_path, img)

        messagebox.showinfo("Success", "Student registered successfully!")
        try:
            if not self.db.is_connected():
                if hasattr(self, 'config') and 'Paths' in self.config and 'db_path' in self.config['Paths']:
                    self.db.connect(self.config['Paths']['db_path'])
                else:
                    raise ConnectionError("Database path not configured")
        
            student_id = self.db.add_student(name, roll, year, branch, section)
        # ... save images ...
        
        except ConnectionError as e:
            messagebox.showerror("Database Error", str(e))
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Registration failed: {str(e)}")
        self.frame.destroy()
        self.cap.release()
        self.callback()

    def back(self):
        self.frame.destroy()
        self.cap.release()
        self.callback()