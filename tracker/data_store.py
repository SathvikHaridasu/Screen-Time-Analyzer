import sqlite3
from datetime import datetime

class DataStore:
    def __init__(self, db_path='screen_time.db'):
        self.db_path = db_path
        self._create_tables()

    def _create_tables(self):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS app_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                app_name TEXT,
                start_time TEXT,
                end_time TEXT,
                duration REAL,
                category TEXT
            )''')
            c.execute('''CREATE TABLE IF NOT EXISTS web_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT,
                title TEXT,
                visit_time TEXT,
                category TEXT
            )''')
            conn.commit()

    def log_app_usage(self, app_name, start_time, end_time, duration, category):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute('INSERT INTO app_usage (app_name, start_time, end_time, duration, category) VALUES (?, ?, ?, ?, ?)',
                      (app_name, start_time, end_time, duration, category))
            conn.commit()

    def log_web_usage(self, url, title, visit_time, category):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute('INSERT INTO web_usage (url, title, visit_time, category) VALUES (?, ?, ?, ?)',
                      (url, title, visit_time, category))
            conn.commit()

    def get_app_usage(self):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM app_usage')
            return c.fetchall()

    def get_web_usage(self):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM web_usage')
            return c.fetchall() 