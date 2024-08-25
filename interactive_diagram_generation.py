import json
import openai

# Load API key
with open('apikey.json') as f:
    api_data = json.load(f)
api_key = api_data['key']

# Set up OpenAI API key
openai.api_key = api_key

# Load combined descriptions JSON
with open('analysis_files/combined_descriptions.json') as f:
    data = json.load(f)

# Start conversation with ChatGPT
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
    
    print(response.choices[0].message['content'])

# Interactive modification function
def modify_chart(instructions):
    prompt = f"You've given me these instructions to modify the Mermaid chart:\n{instructions}\nHow would you like to proceed?"

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    
    print(response.choices[0].message['content'])

# Example usage
start_conversation()
# Now you would interact with ChatGPT, providing more instructions through the modify_chart function as needed.
