import psutil
import win32gui
import win32process
from datetime import datetime

class AppTracker:
    def __init__(self):
        self.active_app = None
        self.start_time = None

    def get_active_window(self):
        hwnd = win32gui.GetForegroundWindow()
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['pid'] == pid:
                return proc.info['name']
        return None

    def track(self):
        app = self.get_active_window()
        now = datetime.now()
        if app != self.active_app:
            if self.active_app:
                duration = (now - self.start_time).total_seconds()
                yield (self.active_app, self.start_time, now, duration)
            self.active_app = app
            self.start_time = now 