import ttkbootstrap as ttk
from tkinter import messagebox, filedialog
from ttkbootstrap.constants import *
import cv2
import os
import configparser
from PIL import Image, ImageTk
import shutil

class UpdateStudent:
    def __init__(self, root, db, callback):
        self.root = root
        self.db = db
        self.callback = callback
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.image_folder = self.config['Paths']['image_folder']
        self.current_student_id = None
        self.images = []
        self.setup_ui()
        
    def setup_ui(self):
        self.root.configure(bg='#f8f9fa')
        style = ttk.Style()
        style.configure('TButton', font=('Helvetica', 10))
        style.configure('TLabel', font=('Helvetica', 12))
        style.configure('TEntry', font=('Helvetica', 10))

        self.frame = ttk.Frame(self.root, padding=20, bootstyle=LIGHT)
        self.frame.pack(fill=BOTH, expand=True)

        # Search Frame
        self.search_frame = ttk.Frame(self.frame, padding=10, bootstyle=LIGHT)
        self.search_frame.pack(fill=X, pady=10)

        ttk.Label(self.search_frame, text="Search by Roll Number:").pack(side=LEFT, padx=5)
        self.search_entry = ttk.Entry(self.search_frame, width=20)
        self.search_entry.pack(side=LEFT, padx=5)
        ttk.Button(
            self.search_frame, 
            text="Search", 
            command=self.search_student,
            bootstyle=INFO
        ).pack(side=LEFT, padx=5)

        # Main Content Frame
        self.content_frame = ttk.Frame(self.frame, padding=10, bootstyle=LIGHT)
        self.content_frame.pack(fill=BOTH, expand=True)

        # Left: Form
        self.form_frame = ttk.Frame(self.content_frame, padding=10, bootstyle=LIGHT)
        self.form_frame.pack(side=LEFT, padx=20, pady=20)

        ttk.Label(self.form_frame, text="Update Student", font=('Helvetica', 16, 'bold'), bootstyle=PRIMARY).grid(row=0, columnspan=2, pady=10)

        ttk.Label(self.form_frame, text="Name:").grid(row=1, column=0, sticky=W, pady=5)
        self.name_entry = ttk.Entry(self.form_frame, width=30)
        self.name_entry.grid(row=1, column=1, pady=5)

        ttk.Label(self.form_frame, text="Roll Number:").grid(row=2, column=0, sticky=W, pady=5)
        self.roll_entry = ttk.Entry(self.form_frame, width=30, state='readonly')
        self.roll_entry.grid(row=2, column=1, pady=5)

        ttk.Label(self.form_frame, text="Year:").grid(row=3, column=0, sticky=W, pady=5)
        self.year_var = ttk.StringVar()
        self.year_menu = ttk.OptionMenu(self.form_frame, self.year_var, "1", "1", "2", "3", "4")
        self.year_menu.grid(row=3, column=1, pady=5)

        ttk.Label(self.form_frame, text="Branch:").grid(row=4, column=0, sticky=W, pady=5)
        self.branch_var = ttk.StringVar()
        self.branch_menu = ttk.OptionMenu(
            self.form_frame, 
            self.branch_var, 
            "CSE", 
            "CSE", "ECE", "CSE-AI", "CSE-AIML"
        )
        self.branch_menu.grid(row=4, column=1, pady=5)

        ttk.Label(self.form_frame, text="Section:").grid(row=5, column=0, sticky=W, pady=5)
        self.section_var = ttk.StringVar()
        self.section_menu = ttk.OptionMenu(
            self.form_frame, 
            self.section_var, 
            "A", 
            "A", "B", "C", "D"
        )
        self.section_menu.grid(row=5, column=1, pady=5)

        ttk.Button(
            self.form_frame, 
            text="Update", 
            command=self.update_student,
            bootstyle=SUCCESS
        ).grid(row=6, column=1, pady=20)

        # Right: Images
        self.images_frame = ttk.Frame(self.content_frame, padding=10, bootstyle=LIGHT)
        self.images_frame.pack(side=RIGHT, padx=20, pady=20)

        ttk.Label(self.images_frame, text="Student Images", font=('Helvetica', 12, 'bold')).pack(pady=5)

        self.image_canvas = ttk.Canvas(self.images_frame, width=320, height=200)
        self.image_canvas.pack()

        self.image_controls = ttk.Frame(self.images_frame)
        self.image_controls.pack(pady=10)

        ttk.Button(
            self.image_controls, 
            text="Add New Image", 
            command=self.add_new_image,
            bootstyle=INFO
        ).pack(side=LEFT, padx=5)

        ttk.Button(
            self.image_controls, 
            text="Remove All Images", 
            command=self.remove_all_images,
            bootstyle=DANGER
        ).pack(side=LEFT, padx=5)

        # Back Button
        ttk.Button(
            self.frame, 
            text="Back", 
            command=self.back,
            bootstyle=SECONDARY
        ).pack(pady=10)

        # Initially disable form until student is found
        self.set_form_state(False)

    def set_form_state(self, state):
        widgets = [
            self.name_entry, 
            self.year_menu, 
            self.branch_menu, 
            self.section_menu
        ]
        for widget in widgets:
            if state:
                widget['state'] = 'normal'
            else:
                widget['state'] = 'disabled'

    def search_student(self):
        roll_number = self.search_entry.get().strip()
        if not roll_number:
            messagebox.showerror("Error", "Please enter a roll number")
            return

        student = self.db.get_student_by_roll(roll_number)
        if not student:
            messagebox.showerror("Error", "Student not found")
            return

        self.current_student_id = student[0]
        self.name_entry.delete(0, ttk.END)
        self.name_entry.insert(0, student[1])
        self.roll_entry.config(state='normal')
        self.roll_entry.delete(0, ttk.END)
        self.roll_entry.insert(0, student[2])
        self.roll_entry.config(state='readonly')
        self.year_var.set(str(student[3]))
        self.branch_var.set(student[4])
        self.section_var.set(student[5])

        # Load student images
        self.load_student_images()

        self.set_form_state(True)

    def load_student_images(self):
        # Clear existing images
        self.images = []
        self.image_canvas.delete("all")
        
        student_folder = os.path.join(self.image_folder, f"student_{self.current_student_id}")
        if os.path.exists(student_folder):
            image_files = [f for f in os.listdir(student_folder) if f.endswith('.jpg')]
            if image_files:
                # Display first image
                img_path = os.path.join(student_folder, image_files[0])
                img = Image.open(img_path)
                img.thumbnail((300, 200))
                self.current_image = ImageTk.PhotoImage(img)
                self.image_canvas.create_image(10, 10, anchor='nw', image=self.current_image)
                
                # Store all image paths
                self.images = [os.path.join(student_folder, f) for f in image_files]

    def add_new_image(self):
        if not self.current_student_id:
            messagebox.showerror("Error", "Please search for a student first")
            return

        filepath = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png")]
        )
        if filepath:
            student_folder = os.path.join(self.image_folder, f"student_{self.current_student_id}")
            os.makedirs(student_folder, exist_ok=True)
            
            # Find next available image number
            existing_images = [f for f in os.listdir(student_folder) if f.startswith('image_')]
            next_num = len(existing_images) + 1
            dest_path = os.path.join(student_folder, f"image_{next_num}.jpg")
            
            # Copy and convert image to JPG if needed
            img = Image.open(filepath)
            img.convert('RGB').save(dest_path, "JPEG")
            
            messagebox.showinfo("Success", "New image added successfully")
            self.load_student_images()

    def remove_all_images(self):
        if not self.current_student_id:
            messagebox.showerror("Error", "Please search for a student first")
            return

        if messagebox.askyesno("Confirm", "Delete all images for this student?"):
            student_folder = os.path.join(self.image_folder, f"student_{self.current_student_id}")
            if os.path.exists(student_folder):
                shutil.rmtree(student_folder)
                messagebox.showinfo("Success", "All images removed")
                self.load_student_images()

    def update_student(self):
        if not self.current_student_id:
            messagebox.showerror("Error", "Please search for a student first")
            return

        name = self.name_entry.get()
        year = self.year_var.get()
        branch = self.branch_var.get()
        section = self.section_var.get()

        if not all([name, year, branch, section]):
            messagebox.showerror("Error", "All fields are required!")
            return

        try:
            # Update database
            self.db.update_student(
                self.current_student_id,
                name,
                year,
                branch,
                section
            )
            messagebox.showinfo("Success", "Student updated successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update student: {str(e)}")

    def back(self):
        self.frame.destroy()
        self.callback()