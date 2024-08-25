import os
import openai
import json
import signal
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Event
import subprocess

# Set the OpenAI API key using an environment variable
def load_api_key():
    with open('apikey.json', 'r') as f:
        api_key_data = json.load(f)
    return api_key_data['key']

openai.api_key = load_api_key()

CHECKPOINT_FILE = 'analyzed_files.json'
FAILED_FILES_FILE = 'failed_files.json'
OUTPUT_FILE = 'combined_descriptions.json'
OUTPUT_DIR = 'analysis_files'

stop_event = Event()  # Event to handle graceful shutdown
file_lock = threading.Lock()  # Lock to manage concurrent access to the JSON file

def ensure_output_directory():
    """Ensure the output directory exists."""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

def load_analyzed_files():
    """Load the list of already analyzed files from the checkpoint file."""
    checkpoint_path = os.path.join(OUTPUT_DIR, CHECKPOINT_FILE)
    if os.path.exists(checkpoint_path):
        with open(checkpoint_path, 'r') as file:
            return json.load(file)
    return []

def save_analyzed_file(file_path):
    """Save the file path of the analyzed file to the checkpoint file."""
    analyzed_files = load_analyzed_files()
    analyzed_files.append({"filename": file_path})
    checkpoint_path = os.path.join(OUTPUT_DIR, CHECKPOINT_FILE)
    with open(checkpoint_path, 'w') as file:
        json.dump(analyzed_files, file, indent=4)

def log_failed_file(file_path, reason):
    """Log the file path of a failed file to the failed files JSON."""
    failed_files_path = os.path.join(OUTPUT_DIR, FAILED_FILES_FILE)
    with file_lock:
        if os.path.exists(failed_files_path):
            with open(failed_files_path, 'r') as file:
                failed_files = json.load(file)
        else:
            failed_files = []
        
        failed_files.append({"filename": file_path, "reason": reason})
        
        with open(failed_files_path, 'w') as file:
            json.dump(failed_files, file, indent=4)

def split_into_chunks(text, chunk_size=6000):
    """Split the text into smaller chunks that fit within the token limit."""
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

def analyze_file(file_path):
    """Analyze a file using GPT and return a description of what the file is doing."""
    with open(file_path, 'r') as file:
        file_content = file.read()

    chunks = split_into_chunks(file_content)

    descriptions = []
    for chunk in chunks:
        if stop_event.is_set():
            print(f"Stopping analysis of {file_path} due to interrupt.")
            break
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Use gpt-4 or gpt-3.5-turbo-16k model
            messages=[
                {"role": "system", "content": "You are a helpful assistant that analyzes code files."},
                {"role": "user", "content": f"Analyze the following code and describe what this part of the file is doing:\n\n{chunk}"}
            ],
            max_tokens=1000,  # Increased max tokens for more detailed responses
            temperature=0.3
        )
        descriptions.append(response['choices'][0]['message']['content'].strip())

    return "\n\n".join(descriptions)

def process_file(file_path, output_file):
    """Process a single file and save its description to the JSON output file."""
    try:
        if stop_event.is_set():
            print(f"Skipping {file_path} due to interrupt.")
            return
        print(f"Analyzing {file_path}...")
        description = analyze_file(file_path)

        with file_lock:
            # Load existing descriptions if the file already exists
            if os.path.exists(output_file):
                with open(output_file, 'r') as f:
                    all_descriptions = json.load(f)
            else:
                all_descriptions = []

            # Add the new description
            all_descriptions.append({"filename": file_path, "description": description})

            # Write the updated descriptions atomically
            temp_output_file = output_file + ".tmp"
            with open(temp_output_file, 'w') as output:
                json.dump(all_descriptions, output, indent=4)
            os.replace(temp_output_file, output_file)

        print(f"Description of {file_path} written to {output_file}")
        save_analyzed_file(file_path)  # Save the file as analyzed
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        log_failed_file(file_path, str(e))  # Log the failed file

def process_directory(directory_path, output_file):
    """Process all files in the given directory using multiple threads."""
    analyzed_files = {entry['filename'] for entry in load_analyzed_files()}
    files_to_analyze = []

    # Collect files to analyze
    for root, dirs, files in os.walk(directory_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            if file_name.endswith('.py') and file_path not in analyzed_files:
                files_to_analyze.append(file_path)

    # Use a thread pool to analyze files concurrently
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(process_file, file_path, output_file): file_path for file_path in files_to_analyze}

        for future in as_completed(futures):
            if stop_event.is_set():
                print("Stopping processing of remaining files due to interrupt.")
                break
            file_path = futures[future]
            try:
                future.result()
            except Exception as e:
                print(f"Unhandled error processing {file_path}: {e}")
                log_failed_file(file_path, str(e))

def handle_interrupt(signal_num, frame):
    """Handle an interrupt signal by setting the stop event."""
    print("Interrupt received. Stopping new file processing...")
    stop_event.set()

def verify_files():
    """Call the file verification script after analysis is complete."""
    print("Verifying that all files have been analyzed...")
    verification_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'file_verification.py')
    subprocess.run(['python', verification_script])
    print("Verification complete.")

if __name__ == "__main__":
    # Register the interrupt handler for graceful shutdown
    signal.signal(signal.SIGINT, handle_interrupt)
    signal.signal(signal.SIGTERM, handle_interrupt)

    # Ensure the output directory exists
    ensure_output_directory()

    # Automatically set the directory path
    directory_path = r'C:\Users\sdrau\code\awips\awips2'
    # Set the output file path to the analysis_files directory
    output_file = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
    print(f"Analyzing all Python files in the directory: {directory_path}")
    process_directory(directory_path, output_file)
    print(f"All descriptions have been written to {output_file}")

    # Call the file verification script
    verify_files()
