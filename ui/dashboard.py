import tkinter as tk
from tkinter import ttk
from tracker.data_store import DataStore
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from collections import Counter, defaultdict
from urllib.parse import urlparse

plt.style.use('seaborn-v0_8-darkgrid')

def extract_domain(url):
    try:
        netloc = urlparse(url).netloc
        return netloc.replace('www.', '') if netloc else url
    except Exception:
        return url

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
        self.app_tree.pack(expand=1, fill='both')
        # --- Web Usage Tab ---
        # Chart frames for web usage
        self.web_charts_frame = ttk.Frame(self.web_tab)
        self.web_charts_frame.pack(fill='both', expand=0, pady=5)
        self.web_bar_canvas = None
        self.web_pie_canvas = None
        # Web usage table
        self.web_tree = ttk.Treeview(self.web_tab, columns=('Domain', 'Title', 'Visit Time', 'Category'), show='headings')
        for col in self.web_tree['columns']:
            self.web_tree.heading(col, text=col)
        self.web_tree.pack(expand=1, fill='both')
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
        self.total_time_label.config(text=f'Total Usage Time: {int(total_time)}s')
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
        web_times = defaultdict(float)
        for row in web_data:
            domain = extract_domain(row[1])
            web_times[domain] += 1
        self.update_web_charts(web_times)
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
        apps, times = zip(*top_apps)
        fig, ax = plt.subplots(figsize=(5,2))
        ax.bar(apps, times, color='skyblue')
        ax.set_ylabel('Seconds')
        ax.set_title('Top 5 Apps by Usage Time')
        fig.tight_layout()
        self.chart_canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        self.chart_canvas.draw()
        self.chart_canvas.get_tk_widget().pack(fill='both', expand=1)
        plt.close(fig)

    def update_web_charts(self, web_times):
        # Bar chart
        if self.web_bar_canvas:
            self.web_bar_canvas.get_tk_widget().destroy()
        top_sites = sorted(web_times.items(), key=lambda x: x[1], reverse=True)[:5]
        if top_sites:
            sites, counts = zip(*top_sites)
            fig_bar, ax_bar = plt.subplots(figsize=(5,2))
            ax_bar.bar(sites, counts, color='mediumseagreen')
            ax_bar.set_ylabel('Visits')
            ax_bar.set_title('Top 5 Sites by Visits')
            fig_bar.tight_layout()
            self.web_bar_canvas = FigureCanvasTkAgg(fig_bar, master=self.web_charts_frame)
            self.web_bar_canvas.draw()
            self.web_bar_canvas.get_tk_widget().pack(side='left', fill='both', expand=1, padx=10)
            plt.close(fig_bar)
        # Pie chart
        if self.web_pie_canvas:
            self.web_pie_canvas.get_tk_widget().destroy()
        if top_sites:
            fig_pie, ax_pie = plt.subplots(figsize=(3,3))
            wedges, texts, autotexts = ax_pie.pie(counts, labels=sites, autopct='%1.1f%%', startangle=140, pctdistance=0.85)
            for w in wedges:
                w.set_edgecolor('white')
            ax_pie.set_title('Site Visit Distribution')
            fig_pie.tight_layout()
            self.web_pie_canvas = FigureCanvasTkAgg(fig_pie, master=self.web_charts_frame)
            self.web_pie_canvas.draw()
            self.web_pie_canvas.get_tk_widget().pack(side='left', fill='both', expand=1, padx=10)
            plt.close(fig_pie)

    def auto_refresh(self):
        self.refresh_data()
        self.after(10000, self.auto_refresh)  # 10 seconds 