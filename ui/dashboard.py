import tkinter as tk
from tkinter import ttk
from tracker.data_store import DataStore

class Dashboard(tk.Tk):
    def __init__(self, data_store):
        super().__init__()
        self.title('Screen Time Analyzer')
        self.geometry('800x600')
        self.data_store = data_store
        self.create_widgets()
        self.refresh_data()

    def create_widgets(self):
        self.tabs = ttk.Notebook(self)
        self.app_tab = ttk.Frame(self.tabs)
        self.web_tab = ttk.Frame(self.tabs)
        self.tabs.add(self.app_tab, text='App Usage')
        self.tabs.add(self.web_tab, text='Web Usage')
        self.tabs.pack(expand=1, fill='both')
        self.app_tree = ttk.Treeview(self.app_tab, columns=('App', 'Start', 'End', 'Duration', 'Category'), show='headings')
        for col in self.app_tree['columns']:
            self.app_tree.heading(col, text=col)
        self.app_tree.pack(expand=1, fill='both')
        self.web_tree = ttk.Treeview(self.web_tab, columns=('URL', 'Title', 'Visit Time', 'Category'), show='headings')
        for col in self.web_tree['columns']:
            self.web_tree.heading(col, text=col)
        self.web_tree.pack(expand=1, fill='both')

    def refresh_data(self):
        for i in self.app_tree.get_children():
            self.app_tree.delete(i)
        for row in self.data_store.get_app_usage():
            self.app_tree.insert('', 'end', values=row[1:])
        for i in self.web_tree.get_children():
            self.web_tree.delete(i)
        for row in self.data_store.get_web_usage():
            self.web_tree.insert('', 'end', values=row[1:]) 