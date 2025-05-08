import sqlite3
from datetime import date
from typing import Optional, List, Tuple

class Database:
    def __init__(self, db_path: Optional[str] = "students.db"):
        """
        Initialize the Database class. Automatically connects to the database
        if a path is provided or uses default "students.db".
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.connect(self.db_path)

    def connect(self, db_path: str) -> None:
        """Connect to the database at the specified path."""
        try:
            self.db_path = db_path
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            self.initialize_db()
        except sqlite3.Error as e:
            raise ConnectionError(f"Failed to connect to database: {str(e)}")

    def is_connected(self) -> bool:
        return self.conn is not None and self.cursor is not None

    def check_connection(self) -> None:
        if not self.is_connected():
            raise ConnectionError("Database not connected. Call connect() first.")

    def initialize_db(self) -> None:
        """Create tables if they don't exist."""
        self.check_connection()
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    roll TEXT NOT NULL UNIQUE,
                    year INTEGER NOT NULL,
                    branch TEXT NOT NULL,
                    section TEXT NOT NULL
                )
            ''')
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS attendance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL,
                    date TEXT NOT NULL,
                    session TEXT NOT NULL,
                    status TEXT NOT NULL,
                    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
                )
            ''')
            self.cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_students_roll ON students(roll)
            ''')
            self.conn.commit()
        except sqlite3.Error as e:
            self.conn.rollback()
            raise RuntimeError(f"Failed to initialize database: {str(e)}")

    def add_student(self, name: str, roll: str, year: int, branch: str, section: str) -> int:
        self.check_connection()
        try:
            self.cursor.execute('''
                INSERT INTO students (name, roll, year, branch, section)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, roll, year, branch, section))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            raise ValueError(f"Student with roll number {roll} already exists")
        except sqlite3.Error as e:
            self.conn.rollback()
            raise RuntimeError(f"Failed to add student: {str(e)}")

    def get_all_students(self) -> List[Tuple]:
        self.check_connection()
        try:
            self.cursor.execute('SELECT * FROM students ORDER BY name')
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to fetch students: {str(e)}")

    def get_student_by_roll(self, roll: str) -> Optional[Tuple]:
        self.check_connection()
        try:
            self.cursor.execute('SELECT * FROM students WHERE roll = ?', (roll,))
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to fetch student: {str(e)}")

    def update_student(self, student_id: int, name: str, year: int, branch: str, section: str) -> None:
        self.check_connection()
        try:
            self.cursor.execute('''
                UPDATE students 
                SET name = ?, year = ?, branch = ?, section = ?
                WHERE id = ?
            ''', (name, year, branch, section, student_id))
            self.conn.commit()
        except sqlite3.Error as e:
            self.conn.rollback()
            raise RuntimeError(f"Failed to update student: {str(e)}")

    def add_attendance(self, student_id: int, date: str, session: str, status: str) -> None:
        self.check_connection()
        try:
            self.cursor.execute('''
                INSERT INTO attendance (student_id, date, session, status)
                VALUES (?, ?, ?, ?)
            ''', (student_id, date, session, status))
            self.conn.commit()
        except sqlite3.Error as e:
            self.conn.rollback()
            raise RuntimeError(f"Failed to add attendance: {str(e)}")

    def get_attendance_by_student(self, student_id: int, start_date: str, end_date: str) -> List[Tuple]:
        self.check_connection()
        try:
            self.cursor.execute('''
                SELECT * FROM attendance
                WHERE student_id = ? AND date BETWEEN ? AND ?
                ORDER BY date, session
            ''', (student_id, start_date, end_date))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to fetch attendance: {str(e)}")

    def close(self) -> None:
        if self.conn:
            try:
                self.conn.close()
            except sqlite3.Error:
                pass
            finally:
                self.conn = None
                self.cursor = None

    def __del__(self):
        self.close()
