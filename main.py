import threading
import time
from tracker.app_tracker import AppTracker
from tracker.web_tracker import WebTracker
from tracker.productivity import categorize_app, categorize_site
from tracker.data_store import DataStore
from ui.dashboard import Dashboard


def app_tracking_loop(data_store):
    tracker = AppTracker()
    for app_name, start, end, duration in tracker.track():
        category = categorize_app(app_name)
        print(f"[DEBUG] Logging app usage: {app_name}, {start}, {end}, {duration}, {category}")
        data_store.log_app_usage(app_name, start.isoformat(), end.isoformat(), duration, category)


def web_tracking_loop(data_store):
    tracker = WebTracker()
    seen = set()
    while True:
        for url, title, visit_time in tracker.get_recent_websites():
            key = (url, visit_time)
            if key not in seen:
                seen.add(key)
                category = categorize_site(url)
                data_store.log_web_usage(url, title, visit_time.isoformat(), category)
        time.sleep(60)


def main():
    data_store = DataStore()
    threading.Thread(target=app_tracking_loop, args=(data_store,), daemon=True).start()
    threading.Thread(target=web_tracking_loop, args=(data_store,), daemon=True).start()
    dashboard = Dashboard(data_store)
    dashboard.mainloop()

if __name__ == '__main__':
    main() 