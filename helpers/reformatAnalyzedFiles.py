import json

# Load the current JSON file
with open('analyzed_files.json', 'r') as file:
    analyzed_files = json.load(file)

# Reformat the data
formatted_files = [{"filename": filename} for filename in analyzed_files]

# Save the reformatted JSON
with open('analyzed_files.json', 'w') as file:
    json.dump(formatted_files, file, indent=4)

print("Reformatting completed successfully.")
