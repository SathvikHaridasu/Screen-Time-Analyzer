import sqlite3
from datetime import datetime

class DataStore:
    def __init__(self, db_path='screen_time.db'):
        self.conn = sqlite3.connect(db_path)
        self._create_tables()

    def _create_tables(self):
        c = self.conn.cursor()
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
        self.conn.commit()

    def log_app_usage(self, app_name, start_time, end_time, duration, category):
        c = self.conn.cursor()
        c.execute('INSERT INTO app_usage (app_name, start_time, end_time, duration, category) VALUES (?, ?, ?, ?, ?)',
                  (app_name, start_time, end_time, duration, category))
        self.conn.commit()

    def log_web_usage(self, url, title, visit_time, category):
        c = self.conn.cursor()
        c.execute('INSERT INTO web_usage (url, title, visit_time, category) VALUES (?, ?, ?, ?)',
                  (url, title, visit_time, category))
        self.conn.commit()

    def get_app_usage(self):
        c = self.conn.cursor()
        c.execute('SELECT * FROM app_usage')
        return c.fetchall()

    def get_web_usage(self):
        c = self.conn.cursor()
        c.execute('SELECT * FROM web_usage')
        return c.fetchall() 