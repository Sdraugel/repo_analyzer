import os
import json
import tkinter as tk
from tkinter import ttk, scrolledtext
from threading import Thread
import openai

from system_explorer.web_page_generator import WebPageGenerator
from system_explorer.file_utils import find_common_terms, group_files_by_functionality
from analysis.qpid_analyzer import analyze_qpid_usage
from system_explorer.diagram_generator import DiagramGenerator  # Import the new DiagramGenerator

# Load API key
with open('apikey.json') as f:
    api_data = json.load(f)
api_key = api_data['key']

# Set up OpenAI API key
openai.api_key = api_key

# Load combined descriptions JSON
with open('analysis_files/combined_descriptions.json') as f:
    data = json.load(f)

# Function to start processing in a separate thread
def start_processing_thread():
    global stop_processing
    stop_processing = False
    start_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.NORMAL)

    total_tasks = 2 if generate_system_explorer_var.get() and analyze_qpid_usage_var.get() else 1

    if generate_system_explorer_var.get():
        common_terms = find_common_terms(data)
        grouped_files = group_files_by_functionality(data, common_terms)
        selected_groups = [group for group, var in checkboxes.items() if var.get()]
        generator = WebPageGenerator(directory="system_pages")
        
        progress_label.config(text="Generating System Explorer...")
        generator.save_all_pages(grouped_files, selected_groups)
        progress_var.set(50 / total_tasks)
        log_box.insert(tk.END, "System Explorer generation completed.\n")
        log_box.see(tk.END)

    if analyze_qpid_usage_var.get():
        progress_label.config(text="Analyzing Qpid Usage...")
        output_file_path = os.path.join('analysis_files', 'qpid_usage_summary.json')
        analyze_qpid_usage(data, progress_var, progress_label, log_box, stop_processing)
        
        # Generate system diagram
        diagram_generator = DiagramGenerator(output_file_path)
        diagram_path = diagram_generator.generate_diagram()
        
        # Log the path of the generated diagram
        log_box.insert(tk.END, f"System diagram generated: {diagram_path}\n")
        log_box.see(tk.END)
        
        progress_var.set(100)
        log_box.insert(tk.END, "Qpid analysis and diagram generation completed.\n")
        log_box.see(tk.END)

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

# Function to show/hide checkboxes based on user selection
def toggle_functionality_group_options():
    if generate_system_explorer_var.get():
        checkbox_frame.pack(pady=10)
        select_all_checkbox.pack(pady=5)
    else:
        checkbox_frame.pack_forget()
        select_all_checkbox.pack_forget()

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

# Generate System Explorer option
generate_system_explorer_var = tk.BooleanVar()
generate_system_explorer_checkbox = tk.Checkbutton(root, text="Generate System Explorer", variable=generate_system_explorer_var, command=toggle_functionality_group_options)
generate_system_explorer_checkbox.pack(pady=5)

# Analyze Qpid Usage option
analyze_qpid_usage_var = tk.BooleanVar()
analyze_qpid_usage_checkbox = tk.Checkbutton(root, text="Analyze Qpid Usage", variable=analyze_qpid_usage_var)
analyze_qpid_usage_checkbox.pack(pady=5)

# Group selection checkboxes
common_terms = find_common_terms(data)
grouped_files = group_files_by_functionality(data, common_terms)
checkboxes = {}
checkbox_frame = ttk.Labelframe(root, text="Select Functionality Groups")

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

# Start button
start_button = ttk.Button(root, text="Start", command=lambda: Thread(target=start_processing_thread).start(), width=20)
start_button.pack(pady=10)

# Stop button
stop_button = ttk.Button(root, text="Stop", command=stop_processing_command, width=20, state=tk.DISABLED)
stop_button.pack(pady=10)

# Run the application
root.mainloop()
