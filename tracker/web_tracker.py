import os
import sqlite3
from datetime import datetime, timedelta

# List of known default/preloaded sites to ignore unless actually visited
DEFAULT_SITES = {
    'bing.com', 'www.bing.com', 'google.com', 'www.google.com', 'yahoo.com', 'www.yahoo.com',
    'duckduckgo.com', 'www.duckduckgo.com', 'baidu.com', 'www.baidu.com',
}

def extract_domain(url):
    from urllib.parse import urlparse
    try:
        netloc = urlparse(url).netloc
        return netloc.replace('www.', '') if netloc else url
    except Exception:
        return url

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
                            domain = extract_domain(url)
                            if domain in DEFAULT_SITES:
                                continue
                            results.append((url, title, datetime.fromtimestamp(last_visit/1e6)))
                    else:
                        # Chrome/Edge/Opera: Only include visit_count > 1
                        min_time = (now - timedelta(minutes=since_minutes))
                        min_time_webkit = int((min_time - datetime(1601,1,1)).total_seconds() * 1e6)
                        cursor.execute("SELECT url, title, last_visit_time, visit_count FROM urls WHERE last_visit_time > ? AND visit_count > 1", 
                            (min_time_webkit,))
                        for url, title, last_visit, visit_count in cursor.fetchall():
                            domain = extract_domain(url)
                            if domain in DEFAULT_SITES:
                                continue
                            visit_time = datetime(1601,1,1) + timedelta(microseconds=last_visit)
                            results.append((url, title, visit_time))
                    conn.close()
                except Exception as e:
                    print(f'[DEBUG] Error reading {path}: {e}')
                    continue
        return results 