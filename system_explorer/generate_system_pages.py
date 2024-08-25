import json
import openai
import tkinter as tk
from tkinter import ttk, scrolledtext
from threading import Thread
import os
from collections import Counter
import re
from web_page_generator import WebPageGenerator

# Load API key
with open('../apikey.json') as f:
    api_data = json.load(f)
api_key = api_data['key']

# Set up OpenAI API key
openai.api_key = api_key

# Load combined descriptions JSON
with open('../analysis_files/combined_descriptions.json') as f:
    data = json.load(f)

# Function to find common terms in the descriptions
def find_common_terms(data, min_length=5, min_count=2):
    all_words = []
    for item in data:
        description = item['description'].lower()
        words = re.findall(r'\b\w+\b', description)
        all_words.extend([word for word in words if len(word) >= min_length])

    # Count the frequency of each word
    word_counts = Counter(all_words)

    # Filter out words that don't appear often enough
    common_terms = [word for word, count in word_counts.items() if count >= min_count]
    
    return common_terms

# Function to dynamically group files based on their descriptions
def group_files_by_functionality(data, common_terms):
    functionality_groups = {}

    for item in data:
        filename = item['filename']
        description = item['description']
        
        # Dynamically determine the group based on the filename
        group = extract_functionality_group(filename)
        
        if group not in functionality_groups:
            functionality_groups[group] = []
        
        functionality_groups[group].append({'filename': filename, 'description': description})
    
    return functionality_groups

# Function to extract or determine the group based on the filename
def extract_functionality_group(filename):
    directory_path = os.path.dirname(filename)
    functionality_group = os.path.basename(directory_path)
    
    return functionality_group.capitalize()

# Function to start processing in a separate thread
def start_processing_thread():
    global stop_processing
    stop_processing = False
    start_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.NORMAL)
    
    # Find common terms to use as functional group names
    common_terms = find_common_terms(data)

    # Group files based on dynamically determined functionality groups
    grouped_files = group_files_by_functionality(data, common_terms)
    
    # Get selected groups
    selected_groups = [group for group, var in checkboxes.items() if var.get()]

    # Initialize the WebPageGenerator and save all pages
    generator = WebPageGenerator(directory="system_pages")
    generator.save_all_pages(grouped_files, selected_groups)
    
    start_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.DISABLED)

# Function to stop processing
def stop_processing_command():
    global stop_processing
    stop_processing = True

# Function to select/deselect all groups
def toggle_select_all():
    select_all_state = select_all_var.get()
    for var in checkboxes.values():
        var.set(select_all_state)

# Create the main window
root = tk.Tk()
root.title("System Overview Generator")
root.geometry("2400x1200")  # Set window size to be larger

# Create a progress bar and label
progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100, length=700)  # Make the bar wider
progress_bar.pack(pady=20)

progress_label = tk.Label(root, text="Starting...", font=("Helvetica", 14))
progress_label.pack(pady=10)

# Create a scrolled text box for logs
log_box = scrolledtext.ScrolledText(root, width=90, height=20, wrap=tk.WORD, font=("Helvetica", 10))
log_box.pack(pady=10)

# Group selection checkboxes
common_terms = find_common_terms(data)
grouped_files = group_files_by_functionality(data, common_terms)
checkboxes = {}
checkbox_frame = ttk.Labelframe(root, text="Select Functionality Groups")
checkbox_frame.pack(pady=10)

# Display checkboxes in columns of 10 rows
row = 0
col = 0
for i, group in enumerate(grouped_files.keys()):
    var = tk.BooleanVar(value=True)
    checkboxes[group] = var
    cb = tk.Checkbutton(checkbox_frame, text=group, variable=var)
    cb.grid(row=row, column=col, sticky='w', padx=5, pady=2)
    
    row += 1
    if row >= 10:
        row = 0
        col += 1

# "Select All" checkbox
select_all_var = tk.BooleanVar(value=True)
select_all_checkbox = tk.Checkbutton(root, text="Select/Deselect All", variable=select_all_var, command=toggle_select_all)
select_all_checkbox.pack(pady=5)

# Start button
start_button = ttk.Button(root, text="Start", command=lambda: Thread(target=start_processing_thread).start(), width=20)
start_button.pack(pady=10)

# Stop button
stop_button = ttk.Button(root, text="Stop", command=stop_processing_command, width=20, state=tk.DISABLED)
stop_button.pack(pady=10)

# Run the application
root.mainloop()
