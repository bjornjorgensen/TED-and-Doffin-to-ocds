import os
import json

def format_json_files(folder_path):
    # Iterate through all files in the specified folder
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            file_path = os.path.join(folder_path, filename)
            
            # Read the JSON file with UTF-8 encoding
            with open(file_path, 'r', encoding='utf-8') as file:
                try:
                    data = json.load(file)
                except json.JSONDecodeError:
                    print(f"Error: {filename} is not a valid JSON file. Skipping.")
                    continue
            
            # Write the formatted JSON back to the same file with UTF-8 encoding
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=2, ensure_ascii=False)
            
            print(f"Formatted: {filename}")

# Specify the folder path containing JSON files
folder_path = 'outputjsonfiles'

# Call the function to format JSON files
format_json_files(folder_path)