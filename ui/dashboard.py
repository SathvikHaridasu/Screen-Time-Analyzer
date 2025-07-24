import tkinter as tk
from tkinter import ttk
from tracker.data_store import DataStore
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from collections import Counter, defaultdict
from urllib.parse import urlparse
import mplcursors

plt.style.use('seaborn-v0_8-darkgrid')

def extract_domain(url):
    try:
        netloc = urlparse(url).netloc
        return netloc.replace('www.', '') if netloc else url
    except Exception:
        return url

def format_time(minutes):
    if minutes < 60:
        return f"{minutes:.1f} min"
    else:
        hours = minutes / 60
        return f"{hours:.1f} hr"

class Dashboard(tk.Tk):
    def __init__(self, data_store):
        super().__init__()
        self.title('Screen Time Analyzer')
        self.geometry('1100x800')
        self.data_store = data_store
        self.create_widgets()
        self.refresh_data()
        self.auto_refresh()

    def create_widgets(self):
        self.tabs = ttk.Notebook(self)
        self.app_tab = ttk.Frame(self.tabs)
        self.web_tab = ttk.Frame(self.tabs)
        self.tabs.add(self.app_tab, text='App Usage')
        self.tabs.add(self.web_tab, text='Web Usage')
        self.tabs.pack(expand=1, fill='both')
        # Summary frame
        self.summary_frame = ttk.Frame(self.app_tab)
        self.summary_frame.pack(fill='x', pady=5)
        self.total_time_label = ttk.Label(self.summary_frame, text='Total Usage Time: 0s')
        self.total_time_label.pack(side='left', padx=10)
        self.most_used_label = ttk.Label(self.summary_frame, text='Most Used App: N/A')
        self.most_used_label.pack(side='left', padx=10)
        # Chart frame for app usage
        self.chart_frame = ttk.Frame(self.app_tab)
        self.chart_frame.pack(fill='both', expand=0, pady=5)
        self.chart_canvas = None
        # App usage table
        self.app_tree = ttk.Treeview(self.app_tab, columns=('App', 'Start', 'End', 'Duration', 'Category'), show='headings')
        for col in self.app_tree['columns']:
            self.app_tree.heading(col, text=col)
        # Add vertical scrollbar for app usage table
        self.app_tree_scrollbar = ttk.Scrollbar(self.app_tab, orient='vertical', command=self.app_tree.yview)
        self.app_tree.configure(yscrollcommand=self.app_tree_scrollbar.set)
        self.app_tree.pack(side='left', expand=1, fill='both')
        self.app_tree_scrollbar.pack(side='right', fill='y')
        # --- Web Usage Tab ---
        # Chart frames for web usage
        # (Web usage graphs removed)
        # Web usage table
        self.web_tree = ttk.Treeview(self.web_tab, columns=('Domain', 'Title', 'Visit Time', 'Category'), show='headings')
        for col in self.web_tree['columns']:
            self.web_tree.heading(col, text=col)
        # Add vertical scrollbar for web usage table
        self.web_tree_scrollbar = ttk.Scrollbar(self.web_tab, orient='vertical', command=self.web_tree.yview)
        self.web_tree.configure(yscrollcommand=self.web_tree_scrollbar.set)
        self.web_tree.pack(side='left', expand=1, fill='both')
        self.web_tree_scrollbar.pack(side='right', fill='y')
        # Add Refresh button
        self.refresh_button = ttk.Button(self, text='Refresh', command=self.refresh_data)
        self.refresh_button.pack(pady=10)

    def refresh_data(self):
        print('[DEBUG] Fetching app usage data from database...')
        app_data = self.data_store.get_app_usage()
        print(f'[DEBUG] App usage data fetched: {app_data}')
        # Update summary
        total_time = 0
        app_times = defaultdict(float)
        for row in app_data:
            app, duration = row[1], row[4]
            if duration:
                app_times[app] += duration
                total_time += duration
        total_hours = total_time / 3600
        self.total_time_label.config(text=f'Total Usage Time: {total_hours:.1f} hr')
        if app_times:
            most_used = max(app_times, key=app_times.get)
            self.most_used_label.config(text=f'Most Used App: {most_used}')
        else:
            self.most_used_label.config(text='Most Used App: N/A')
        # Update chart
        self.update_chart(app_times)
        # Update app usage table
        for i in self.app_tree.get_children():
            self.app_tree.delete(i)
        for row in app_data:
            print(f'[DEBUG] Inserting row into app_tree: {row[1:]}')
            self.app_tree.insert('', 'end', values=row[1:])
        # --- Web Usage ---
        web_data = self.data_store.get_web_usage()
        # Sort web_data by visit_time (column 3) descending so recent is first
        web_data = sorted(web_data, key=lambda row: row[3], reverse=True)
        # Only aggregate domains from web_data (recent visits)
        web_times = defaultdict(float)
        for row in web_data:
            domain = extract_domain(row[1])
            web_times[domain] += 1
        # Only keep domains that appear in web_data
        web_times = {domain: count for domain, count in web_times.items() if count > 0}
        # (Web usage graphs removed)
        # Update web usage table
        for i in self.web_tree.get_children():
            self.web_tree.delete(i)
        for row in web_data:
            domain = extract_domain(row[1])
            self.web_tree.insert('', 'end', values=(domain, row[2], row[3], row[4]))

    def update_chart(self, app_times):
        if self.chart_canvas:
            self.chart_canvas.get_tk_widget().destroy()
        top_apps = sorted(app_times.items(), key=lambda x: x[1], reverse=True)[:5]
        if not top_apps:
            return
        apps, times_sec = zip(*top_apps)
        times_min = [t/60 for t in times_sec]
        fig, ax = plt.subplots(figsize=(5,2))
        bars = ax.bar(apps, times_min, color='skyblue')
        ax.set_ylabel('Usage Time (min)')
        ax.set_title('Top 5 Apps by Usage Time')
        ax.set_ylim(bottom=0)
        # Add interactive tooltips
        cursor = mplcursors.cursor(bars, hover=True)
        @cursor.connect("add")
        def on_add(sel):
            idx = sel.index
            sel.annotation.set(text=format_time(times_min[idx]), fontsize=10, backgroundcolor='white')
            sel.annotation.arrow_patch.set(visible=False)
        fig.tight_layout()
        self.chart_canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        self.chart_canvas.draw()
        self.chart_canvas.get_tk_widget().pack(fill='both', expand=1)
        plt.close(fig)

    # (update_web_charts removed)

    def auto_refresh(self):
        self.refresh_data()
        self.after(10000, self.auto_refresh)  # 10 seconds 