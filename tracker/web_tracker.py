import os
import sqlite3
from datetime import datetime, timedelta

class WebTracker:
    def __init__(self):
        self.history_paths = self._find_browser_history_paths()
        print(f'[DEBUG] Browser history paths found: {self.history_paths}')

    def _find_browser_history_paths(self):
        # Chrome, Edge, Firefox, Opera (Windows default locations)
        paths = []
        user = os.getenv('USERNAME')
        chrome = f"C:/Users/{user}/AppData/Local/Google/Chrome/User Data/Default/History"
        edge = f"C:/Users/{user}/AppData/Local/Microsoft/Edge/User Data/Default/History"
        opera = f"C:/Users/{user}/AppData/Roaming/Opera Software/Opera Stable/History"
        firefox = f"C:/Users/{user}/AppData/Roaming/Mozilla/Firefox/Profiles/"
        paths.extend([chrome, edge, opera])
        # For Firefox, need to find profile folder
        if os.path.exists(firefox):
            for profile in os.listdir(firefox):
                paths.append(os.path.join(firefox, profile, 'places.sqlite'))
        return paths

    def get_recent_websites(self, since_minutes=10):
        now = datetime.now()
        results = []
        for path in self.history_paths:
            if os.path.exists(path):
                print(f'[DEBUG] Reading browser history from: {path}')
                try:
                    conn = sqlite3.connect(path)
                    cursor = conn.cursor()
                    if 'places.sqlite' in path:
                        # Firefox
                        cursor.execute("SELECT url, title, last_visit_date FROM moz_places WHERE last_visit_date > ?", 
                            ((now - timedelta(minutes=since_minutes)).timestamp()*1e6,))
                        for url, title, last_visit in cursor.fetchall():
                            results.append((url, title, datetime.fromtimestamp(last_visit/1e6)))
                    else:
                        # Chrome/Edge/Opera
                        cursor.execute("SELECT url, title, last_visit_time FROM urls WHERE last_visit_time > ?", 
                            ((now - timedelta(minutes=since_minutes)).timestamp()*1e6,))
                        for url, title, last_visit in cursor.fetchall():
                            results.append((url, title, datetime(1601,1,1) + timedelta(microseconds=last_visit)))
                    conn.close()
                except Exception as e:
                    print(f'[DEBUG] Error reading {path}: {e}')
                    continue
        return results 