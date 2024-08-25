import os
import json

# Set the directory path for the AWIPS project and the analysis files directory
project_directory_path = r'C:\Users\sdrau\code\awips\awips2'
analysis_directory_path = r'analysis_files'

# Load the analyzed files from the JSON file located in the analysis_files directory
analyzed_files_path = os.path.join(analysis_directory_path, 'analyzed_files.json')
with open(analyzed_files_path, 'r') as file:
    analyzed_files = json.load(file)

# Convert analyzed files to a set for easy comparison
analyzed_filenames = {entry['filename'] for entry in analyzed_files}

# Collect all Python files in the AWIPS project directory
all_python_files = set()
for root, dirs, files in os.walk(project_directory_path):
    for file_name in files:
        if file_name.endswith('.py'):
            full_path = os.path.join(root, file_name)
            all_python_files.add(full_path)

# Find files that have not been analyzed
untracked_files = all_python_files - analyzed_filenames
tracked_files = all_python_files & analyzed_filenames

# Print results
print(f"Total Python files in project: {len(all_python_files)}")
print(f"Analyzed files: {len(analyzed_filenames)}")
print(f"Unanalyzed files: {len(untracked_files)}")

if untracked_files:
    print("\nFiles that have not been analyzed:")
    for file in untracked_files:
        print(file)
else:
    print("\nAll files have been analyzed!")

# Optionally, save the list of untracked files to a JSON file in the analysis_files directory
untracked_files_path = os.path.join(analysis_directory_path, 'unanalyzed_files.json')
with open(untracked_files_path, 'w') as outfile:
    json.dump(list(untracked_files), outfile, indent=4)

print("\nVerification complete.")
