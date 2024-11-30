import json
import os
from pathlib import Path


def format_json_files(folder_path) -> None:
    # Iterate through all files in the specified folder
    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            file_path = Path(folder_path) / filename

            # Read the JSON file with UTF-8 encoding
            with file_path.open(encoding="utf-8") as file:
                try:
                    data = json.load(file)
                except json.JSONDecodeError:
                    print(f"Error: {filename} is not a valid JSON file. Skipping.")  # noqa: T201
                    continue

            # Write the formatted JSON back to the same file with UTF-8 encoding
            with file_path.open("w", encoding="utf-8") as file:
                json.dump(data, file, indent=2, ensure_ascii=False)

            print(f"Formatted: {filename}")  # noqa: T201


# Specify the folder path containing JSON files
folder_path = "outputjsonfiles"

# Call the function to format JSON files
format_json_files(folder_path)
