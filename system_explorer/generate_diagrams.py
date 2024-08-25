import json
import openai
import tkinter as tk
from tkinter import ttk, scrolledtext
from threading import Thread
import os
from collections import Counter
import re

# Load API key
with open('apikey.json') as f:
    api_data = json.load(f)
api_key = api_data['key']

# Set up OpenAI API key
openai.api_key = api_key

# Load combined descriptions JSON
with open('analysis_files/combined_descriptions.json') as f:
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
        group = extract_functionality_group(description, common_terms, filename)
        
        if group not in functionality_groups:
            functionality_groups[group] = []
        
        functionality_groups[group].append({'filename': filename, 'description': description})
    
    return functionality_groups

# Function to extract or determine the group based on the description
def extract_functionality_group(description, common_terms, filename):
    # Extract the functionality group from the directory name in the file path
    # Assuming the directory name just before the filename is the functionality group
    directory_path = os.path.dirname(filename)
    functionality_group = os.path.basename(directory_path)
    
    return functionality_group.capitalize()

# Function to create a directory for saving diagrams
def create_directory(directory_name="diagrams"):
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)
    return directory_name

# Function to save a Mermaid diagram to an HTML file
def save_mermaid_to_html(mermaid_text, output_file, directory="diagrams"):
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Mermaid Diagram</title>
        <script type="module">
            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
            mermaid.initialize({{ startOnLoad: true, maxEdges: 2000 }});
        </script>
    </head>
    <body>
        <div class="mermaid">
            {mermaid_text}
        </div>
    </body>
    </html>
    """

    full_path = os.path.join(directory, output_file)
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"Mermaid diagram saved to {full_path}")

# Function to break the Mermaid diagram into smaller parts and create interactive links
def break_down_diagram(functionality_groups, selected_groups, max_groups_per_diagram=5):
    mermaid_parts = []
    current_part = "graph TD\n"

    part_count = 1
    groups_in_current_part = 0

    for group in selected_groups:
        group_node = group.replace(' ', '_')
        if groups_in_current_part >= max_groups_per_diagram:
            mermaid_parts.append(current_part)
            current_part = "graph TD\n"
            groups_in_current_part = 0
            part_count += 1
        
        current_part += f"    {group_node}[{group}]\n"
        groups_in_current_part += 1

    if current_part:
        mermaid_parts.append(current_part)

    return mermaid_parts

# Function to create the main HTML file with a table of buttons
def create_main_html_with_table(selected_groups, directory="diagrams"):
    table_rows = ""

    for i, group in enumerate(selected_groups):
        group_name = group.replace(' ', '_')
        part_file = f"part_{i+1}.html"
        table_rows += f"""
        <tr>
            <td>{group}</td>
            <td><a href="{part_file}" target="_blank"><button>View {group}</button></a></td>
        </tr>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Main Diagram</title>
        <style>
            table {{
                width: 50%;
                margin: 50px auto;
                border-collapse: collapse;
            }}
            th, td {{
                padding: 15px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }}
            th {{
                background-color: #f2f2f2;
            }}
            button {{
                padding: 10px 20px;
                background-color: #4CAF50;
                color: white;
                border: none;
                cursor: pointer;
            }}
            button:hover {{
                background-color: #45a049;
            }}
        </style>
    </head>
    <body>
        <h2 style="text-align: center;">Functional Groups</h2>
        <table>
            <thead>
                <tr>
                    <th>Group Name</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>
    </body>
    </html>
    """

    main_file = os.path.join(directory, "main_diagram.html")
    with open(main_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"Main diagram saved to {main_file}")

# Example usage:
def save_all_diagrams(grouped_files, selected_groups):
    directory = create_directory()

    mermaid_parts = break_down_diagram(grouped_files, selected_groups, max_groups_per_diagram=5)

    for i, part in enumerate(mermaid_parts):
        part_file = f"part_{i+1}.html"
        save_mermaid_to_html(part, part_file, directory=directory)
    
    create_main_html_with_table(selected_groups, directory=directory)

# Function to split the data into smaller chunks
def split_into_chunks(text, max_length=8000):
    chunks = []
    current_chunk = ""
    for line in text.split("\n"):
        if len(current_chunk) + len(line) + 1 > max_length:
            chunks.append(current_chunk)
            current_chunk = line
        else:
            current_chunk += "\n" + line
    if current_chunk:
        chunks.append(current_chunk)
    return chunks

# Function to start the conversation with ChatGPT for generating the Mermaid diagram
def start_conversation():
    prompt = "You are helping me build a Mermaid chart based on the descriptions of files in a project. Here's a summary of what we're working with:\n"
    
    # Example: Summarize the data or specific files to start with
    for i, item in enumerate(data[:5]):  # Limiting to the first 5 for the example
        prompt += f"{i+1}. Filename: {item['filename']}, Description: {item['description']}\n"

    prompt += "\nLet's start by building a basic structure. What nodes and relationships should we create first?"

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    
    log_box.insert(tk.END, response.choices[0].message['content'])
    log_box.see(tk.END)

# Function for modifying the Mermaid chart interactively
def modify_chart(instructions):
    prompt = f"You've given me these instructions to modify the Mermaid chart:\n{instructions}\nHow would you like to proceed?"

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    
    log_box.insert(tk.END, response.choices[0].message['content'])
    log_box.see(tk.END)

# Generate Mermaid text representation using OpenAI API with UI progress and debugging logs
def generate_mermaid_text(functionality_groups, selected_groups, progress_var, progress_label, log_box, total_files):
    global stop_processing
    mermaid_text = "graph TD\n"
    processed_files = 0

    groups_to_process = selected_groups

    # Create a node for each functionality group and track connections
    for group in groups_to_process:
        if stop_processing:
            log_box.insert(tk.END, "Processing stopped by user.\n")
            log_box.see(tk.END)
            break
        
        if group in functionality_groups:
            files = functionality_groups[group]
            log_box.insert(tk.END, f"Processing group: {group}\n")
            log_box.see(tk.END)
            
            # Create the node for the functionality group
            group_node = group.replace(' ', '_')  # Replace spaces for valid Mermaid syntax
            mermaid_text += f"    {group_node}[{group}]\n"
            
            # Determine relationships between functionality groups
            for file in files:
                description = file['description']
                
                # Example logic to determine relationships between groups
                for other_group in groups_to_process:
                    if other_group != group and other_group.lower() in description:
                        other_group_node = other_group.replace(' ', '_')
                        mermaid_text += f"    {group_node} --> {other_group_node}\n"

            # Update progress
            processed_files += len(files)
            progress_var.set(processed_files / total_files * 100)
            progress_bar.update_idletasks()  # Ensure the progress bar is updated

            log_box.insert(tk.END, f"Processed {len(files)} files in group: {group}\n")
            log_box.see(tk.END)
    
    if not stop_processing:
        progress_label.config(text="Completed!")
        log_box.insert(tk.END, "Completed processing the files!\n")
        log_box.see(tk.END)
    else:
        progress_label.config(text="Stopped")

    return mermaid_text

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

    # Determine total files based on selected groups
    total_files = sum(len(grouped_files.get(group, [])) for group in selected_groups)
    
    # Start initial conversation to build the Mermaid chart
    start_conversation()
    
    # Generate the initial Mermaid diagram based on selected groups
    mermaid_diagram_text = generate_mermaid_text(grouped_files, selected_groups, progress_var, progress_label, log_box, total_files)
    
    if not stop_processing:
        # Save Mermaid text to a file only if the processing wasn't stopped
        with open('mermaid_diagram.mmd', 'w', encoding='utf-8') as f:
            f.write(mermaid_diagram_text)
        
        save_all_diagrams(grouped_files, selected_groups)
    
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
root.title("Mermaid Diagram Generator")
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
