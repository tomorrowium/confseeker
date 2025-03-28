import tkinter as tk
from tkinter import ttk, messagebox
import json
from typing import List, Dict
import os
from datetime import datetime
import requests

API_URL = os.getenv('API_URL', 'http://localhost:5000/api')

class ModernButton(ttk.Button):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(style='Modern.TButton')
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)

    def on_enter(self, e):
        self.configure(style='Modern.TButton.Hover')

    def on_leave(self, e):
        self.configure(style='Modern.TButton')

class ConferenceTrackerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Conference Tracker")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f5f5f7')
        
        # Configure styles
        self.setup_styles()
        
        self.editing_id = None  # Track which conference is being edited
        
        # Create main container with padding
        self.main_container = ttk.Frame(self.root, padding="20")
        self.main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_container.columnconfigure(1, weight=1)
        
        # Create title
        self.create_title()
        
        # Create input fields
        self.create_input_fields()
        
        # Create conference list
        self.create_conference_list()
        
        # Create search results section
        self.create_search_results()
        
        # Load existing conferences
        self.load_conferences()

    def setup_styles(self):
        # Configure ttk styles
        style = ttk.Style()
        style.configure('Modern.TFrame', background='#f5f5f7')
        style.configure('Title.TLabel', 
                       font=('SF Pro Display', 24, 'bold'),
                       foreground='#1d1d1f',
                       background='#f5f5f7')
        
        style.configure('Subtitle.TLabel',
                       font=('SF Pro Text', 14),
                       foreground='#86868b',
                       background='#f5f5f7')
        
        style.configure('Input.TLabel',
                       font=('SF Pro Text', 12),
                       foreground='#1d1d1f',
                       background='#f5f5f7')
        
        # Modern button style
        style.configure('Modern.TButton',
                       font=('SF Pro Text', 12),
                       padding=10,
                       background='#0071e3',
                       foreground='white')
        
        style.configure('Modern.TButton.Hover',
                       background='#0077ed')
        
        # Treeview style
        style.configure('Modern.Treeview',
                       font=('SF Pro Text', 11),
                       rowheight=30,
                       background='white',
                       fieldbackground='white',
                       foreground='#1d1d1f')
        
        style.configure('Modern.Treeview.Heading',
                       font=('SF Pro Text', 12, 'bold'),
                       background='#f5f5f7',
                       foreground='#1d1d1f')
        
        # Entry style
        style.configure('Modern.TEntry',
                       font=('SF Pro Text', 12),
                       padding=5)
        
        # Status indicator style
        style.configure('Status.TLabel',
                       font=('SF Pro Text', 10),
                       padding=5)

    def create_title(self):
        title_frame = ttk.Frame(self.main_container, style='Modern.TFrame')
        title_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        
        title_label = ttk.Label(title_frame, 
                              text="Conference Tracker",
                              style='Title.TLabel')
        title_label.grid(row=0, column=0, sticky=tk.W)
        
        subtitle_label = ttk.Label(title_frame,
                                 text="Track and discover academic conferences",
                                 style='Subtitle.TLabel')
        subtitle_label.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))

    def create_input_fields(self):
        # Input container with shadow effect
        input_frame = ttk.Frame(self.main_container, style='Modern.TFrame')
        input_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Conference name
        ttk.Label(input_frame, 
                 text="Conference Name",
                 style='Input.TLabel').grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(input_frame, 
                                  textvariable=self.name_var,
                                  style='Modern.TEntry',
                                  width=40)
        self.name_entry.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Year
        ttk.Label(input_frame,
                 text="Year",
                 style='Input.TLabel').grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        self.year_var = tk.StringVar()
        self.year_entry = ttk.Entry(input_frame,
                                  textvariable=self.year_var,
                                  style='Modern.TEntry',
                                  width=10)
        self.year_entry.grid(row=3, column=0, sticky=tk.W, pady=(0, 10))
        
        # Keywords
        ttk.Label(input_frame,
                 text="Keywords (comma-separated)",
                 style='Input.TLabel').grid(row=4, column=0, sticky=tk.W, pady=(0, 5))
        self.keywords_var = tk.StringVar()
        self.keywords_entry = ttk.Entry(input_frame,
                                      textvariable=self.keywords_var,
                                      style='Modern.TEntry',
                                      width=40)
        self.keywords_entry.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Link
        ttk.Label(input_frame,
                 text="Link (optional)",
                 style='Input.TLabel').grid(row=6, column=0, sticky=tk.W, pady=(0, 5))
        self.link_var = tk.StringVar()
        self.link_entry = ttk.Entry(input_frame,
                                  textvariable=self.link_var,
                                  style='Modern.TEntry',
                                  width=40)
        self.link_entry.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Button frame
        button_frame = ttk.Frame(input_frame, style='Modern.TFrame')
        button_frame.grid(row=8, column=0, columnspan=2, pady=(10, 0))
        
        # Add/Update button
        self.add_button = ModernButton(button_frame,
                                     text="Add Conference",
                                     command=self.add_conference)
        self.add_button.grid(row=0, column=0, padx=5)
        
        # Cancel edit button
        self.cancel_button = ModernButton(button_frame,
                                        text="Cancel Edit",
                                        command=self.cancel_edit,
                                        state='disabled')
        self.cancel_button.grid(row=0, column=1, padx=5)

    def create_conference_list(self):
        # List container
        list_frame = ttk.Frame(self.main_container, style='Modern.TFrame')
        list_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # List title and controls
        title_frame = ttk.Frame(list_frame, style='Modern.TFrame')
        title_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(title_frame,
                 text="Tracked Conferences",
                 style='Title.TLabel').grid(row=0, column=0, sticky=tk.W)
        
        # Filter frame
        filter_frame = ttk.Frame(title_frame, style='Modern.TFrame')
        filter_frame.grid(row=0, column=1, sticky=tk.E)
        
        ttk.Label(filter_frame,
                 text="Filter:",
                 style='Input.TLabel').grid(row=0, column=0, padx=5)
        
        self.filter_var = tk.StringVar()
        self.filter_var.trace('w', self.apply_filter)
        self.filter_entry = ttk.Entry(filter_frame,
                                    textvariable=self.filter_var,
                                    style='Modern.TEntry',
                                    width=20)
        self.filter_entry.grid(row=0, column=1, padx=5)
        
        # Create treeview with modern style
        columns = ("Name", "Year", "Keywords", "Link", "Last Checked", "Status")
        self.tree = ttk.Treeview(list_frame,
                                columns=columns,
                                show="headings",
                                style='Modern.Treeview')
        
        # Set column headings and bind sorting
        for col in columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_treeview(c))
            self.tree.column(col, width=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Grid layout
        self.tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        
        # Button frame
        button_frame = ttk.Frame(list_frame, style='Modern.TFrame')
        button_frame.grid(row=2, column=0, columnspan=2, pady=(10, 0))
        
        # Delete button
        self.delete_button = ModernButton(button_frame,
                                        text="Delete Selected",
                                        command=self.delete_conference)
        self.delete_button.grid(row=0, column=0, padx=5)
        
        # Edit button
        self.edit_button = ModernButton(button_frame,
                                      text="Edit Selected",
                                      command=self.edit_conference)
        self.edit_button.grid(row=0, column=1, padx=5)
        
        # Check now button
        self.check_button = ModernButton(button_frame,
                                       text="Check Now",
                                       command=self.check_conferences_now)
        self.check_button.grid(row=0, column=2, padx=5)

    def create_search_results(self):
        # Search results container
        results_frame = ttk.Frame(self.main_container, style='Modern.TFrame')
        results_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(20, 0))
        
        # Results title
        ttk.Label(results_frame,
                 text="Search Results",
                 style='Title.TLabel').grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        # Create results treeview
        columns = ("Title", "Source", "Link", "Similarity")
        self.results_tree = ttk.Treeview(results_frame,
                                       columns=columns,
                                       show="headings",
                                       style='Modern.Treeview',
                                       height=5)
        
        # Set column headings
        for col in columns:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=150)
        
        # Add scrollbar
        results_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=results_scrollbar.set)
        
        # Grid layout
        self.results_tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))

    def load_conferences(self):
        try:
            response = requests.get(f"{API_URL}/conferences")
            conferences = response.json()
            
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Load conferences from API
            for conf in conferences:
                self.tree.insert("", tk.END, values=(
                    conf["name"],
                    conf["year"],
                    ", ".join(conf["keywords"]),
                    conf.get("link", ""),
                    conf["last_checked"],
                    conf["status"]
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load conferences: {str(e)}")

    def add_conference(self):
        try:
            data = {
                "name": self.name_var.get().strip(),
                "year": int(self.year_var.get().strip()),
                "keywords": [k.strip() for k in self.keywords_var.get().split(",")],
                "link": self.link_var.get().strip() or None
            }
            
            if not data["name"] or not data["year"] or not data["keywords"]:
                messagebox.showerror("Error", "Please fill in all required fields")
                return
            
            if self.editing_id is not None:
                # Update existing conference
                response = requests.put(f"{API_URL}/conferences/{self.editing_id}", json=data)
                if response.status_code != 200:
                    raise Exception("Failed to update conference")
            else:
                # Add new conference
                response = requests.post(f"{API_URL}/conferences", json=data)
                if response.status_code != 201:
                    raise Exception("Failed to add conference")
            
            self.editing_id = None
            self.add_button.configure(text="Add Conference")
            self.cancel_button.configure(state='disabled')
            self.load_conferences()
            self.clear_input_fields()
            messagebox.showinfo("Success", "Conference saved successfully!")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid year")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def clear_input_fields(self):
        self.name_var.set("")
        self.year_var.set("")
        self.keywords_var.set("")
        self.link_var.set("")

    def edit_conference(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a conference to edit")
            return
        
        item = selected[0]
        values = self.tree.item(item)["values"]
        
        # Get conference details from API
        try:
            response = requests.get(f"{API_URL}/conferences")
            conferences = response.json()
            
            for conf in conferences:
                if conf["name"] == values[0]:
                    self.editing_id = conf["id"]
                    self.name_var.set(conf["name"])
                    self.year_var.set(str(conf["year"]))
                    self.keywords_var.set(", ".join(conf["keywords"]))
                    self.link_var.set(conf.get("link", ""))
                    self.add_button.configure(text="Update Conference")
                    self.cancel_button.configure(state='normal')
                    break
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load conference details: {str(e)}")

    def cancel_edit(self):
        self.editing_id = None
        self.clear_input_fields()
        self.add_button.configure(text="Add Conference")
        self.cancel_button.configure(state='disabled')

    def delete_conference(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a conference to delete")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete the selected conference(s)?"):
            try:
                for item in selected:
                    values = self.tree.item(item)["values"]
                    name = values[0]
                    
                    # Get conference ID from API
                    response = requests.get(f"{API_URL}/conferences")
                    conferences = response.json()
                    
                    for conf in conferences:
                        if conf["name"] == name:
                            delete_response = requests.delete(f"{API_URL}/conferences/{conf['id']}")
                            if delete_response.status_code != 204:
                                raise Exception(f"Failed to delete conference: {name}")
                
                self.load_conferences()
                messagebox.showinfo("Success", "Selected conference(s) deleted successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete conferences: {str(e)}")

    def sort_treeview(self, col):
        """Sort treeview when clicking on column headers."""
        items = [(self.tree.set(item, col), item) for item in self.tree.get_children('')]
        items.sort()
        
        for index, (val, item) in enumerate(items):
            self.tree.move(item, '', index)

    def apply_filter(self, *args):
        """Filter treeview based on search text."""
        search_text = self.filter_var.get().lower()
        
        for item in self.tree.get_children():
            values = self.tree.item(item)["values"]
            if any(search_text in str(value).lower() for value in values):
                self.tree.reattach(item, '', 'end')
            else:
                self.tree.detach(item)

    def check_conferences_now(self):
        """Check all conferences immediately and show results."""
        try:
            # Clear previous results
            for item in self.results_tree.get_children():
                self.results_tree.delete(item)
            
            # Trigger conference check
            response = requests.post(f"{API_URL}/conferences/check")
            if response.status_code != 200:
                raise Exception("Failed to check conferences")
            
            results = response.json()
            
            # Update results tree
            for result in results:
                self.results_tree.insert("", tk.END, values=(
                    result['title'],
                    result['source'],
                    result['link'],
                    f"{result['similarity']:.2f}"
                ))
            
            # Reload conferences to update status
            self.load_conferences()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to check conferences: {str(e)}")

def main():
    root = tk.Tk()
    app = ConferenceTrackerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 