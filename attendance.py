import schedule
import time
import datetime
import pandas as pd
import os
import configparser
import random
import pytz
from threading import Thread

def start_attendance_scheduler(db):
    config = configparser.ConfigParser()
    config.read('config.ini')
    csv_folder = config['Paths']['csv_folder']

    def mark_attendance(session):
        today = datetime.datetime.now(pytz.timezone('Asia/Kolkata')).date()
        students = db.get_all_students()
        attendance_data = []

        for student in students:
            student_id, name, roll, year, branch, section = student
            # Simulate attendance (random for demo)
            status = random.choice(['Present', 'Absent'])
            db.add_attendance(student_id, today, session, status)
            attendance_data.append({
                'Student_ID': student_id,
                'Name': name,
                'Roll': roll,
                'Year': year,
                'Branch': branch,
                'Section': section,
                'Date': today,
                'Session': session,
                'Status': status
            })

        # Save to CSV
        df = pd.DataFrame(attendance_data)
        week_number = today.isocalendar()[1]
        year = today.year
        csv_path = os.path.join(csv_folder, f"week_{week_number}_{year}_{session}.csv")
        df.to_csv(csv_path, index=False)
        print(f"Attendance saved for {session} on {today}")

    def schedule_attendance():
        ist = pytz.timezone('Asia/Kolkata')
        schedule.every().day.at("08:00", ist).do(mark_attendance, session="Morning")
        schedule.every().day.at("15:00", ist).do(mark_attendance, session="Evening")

        while True:
            schedule.run_pending()
            time.sleep(60)

    # Run scheduler in a separate thread
    Thread(target=schedule_attendance, daemon=True).start()