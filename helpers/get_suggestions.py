import openai
import json
import threading
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

# Set the OpenAI API key using an environment variable
def load_api_key():
    with open('apikey.json', 'r') as f:
        api_key_data = json.load(f)
    return api_key_data['key']

openai.api_key = load_api_key()

# Set up logging
logging.basicConfig(
    filename='analysis_files/progress.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

# Load the combined descriptions from JSON
with open('analysis_files/combined_descriptions.json', 'r') as file:
    descriptions = json.load(file)

# Function to estimate the number of tokens in the text
def estimate_tokens(text):
    return int(len(text.split()) * 1.5)  # Conservative estimate

# Function to generate GPT suggestions for a batch
def get_gpt_suggestions(description_batch, batch_num):
    prompt = f"""
    You are an expert in software architecture and system design. Below are descriptions of various components in a software system:

    {description_batch}

    Based on these descriptions, suggest the most suitable diagrams to represent the entire system. Provide ideas for:
    1. A high-level system architecture diagram.
    2. A data flow diagram.
    3. Service interaction diagrams.
    4. Any other relevant diagrams that would help visualize and understand this system.
    """

    logging.info(f"Processing batch {batch_num}")
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        logging.info(f"Batch {batch_num} completed successfully")
        return response['choices'][0]['message']['content']
    except Exception as e:
        logging.error(f"Error processing batch {batch_num}: {e}")
        return f"Error processing batch {batch_num}: {e}"

# Process descriptions in smaller batches based on token estimates
max_tokens_per_request = 7500
current_batch_tokens = 0
description_batch = []
batch_num = 0
suggestions = []
batches = []

# Prepare batches
for entry in descriptions:
    filename = entry['filename']
    description = entry['description']
    description_text = f"Filename: {filename}\nDescription: {description}"
    
    estimated_tokens = estimate_tokens(description_text)
    
    if current_batch_tokens + estimated_tokens > max_tokens_per_request:
        batch_num += 1
        batches.append((description_batch, batch_num))
        description_batch = []
        current_batch_tokens = 0
    
    description_batch.append(description_text)
    current_batch_tokens += estimated_tokens

# Add any remaining descriptions as a final batch
if description_batch:
    batch_num += 1
    batches.append((description_batch, batch_num))

# Multithreading to process batches
with ThreadPoolExecutor(max_workers=4) as executor:  # Adjust max_workers based on your system's capabilities
    future_to_batch = {executor.submit(get_gpt_suggestions, "\n\n".join(batch), num): num for batch, num in batches}

    for future in as_completed(future_to_batch):
        batch_num = future_to_batch[future]
        try:
            result = future.result()
            suggestions.append(result)
        except Exception as e:
            logging.error(f"Batch {batch_num} generated an exception: {e}")

# Combine all suggestions
all_suggestions = "\n\n".join(suggestions)

# Print and save the suggestions
print("GPT's Diagram Suggestions:")
print(all_suggestions)

with open('analysis_files/diagram_suggestions.txt', 'w') as file:
    file.write(all_suggestions)

logging.info("Processing complete. Suggestions saved.")
