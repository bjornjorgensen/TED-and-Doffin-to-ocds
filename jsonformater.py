import json
from pathlib import Path


def format_json_files(folder_path) -> None:
    # Iterate through all files in the specified folder
    for file_path in Path(folder_path).iterdir():
        if file_path.name.endswith(".json"):
            # Read the JSON file with UTF-8 encoding
            with file_path.open(encoding="utf-8") as file:
                try:
                    data = json.load(file)
                except json.JSONDecodeError:
                    print(  # noqa: T201
                        f"Error: {file_path.name} is not a valid JSON file. Skipping."
                    )
                    continue

            # Write the formatted JSON back to the same file with UTF-8 encoding
            with file_path.open("w", encoding="utf-8") as file:
                json.dump(data, file, indent=2, ensure_ascii=False)

            print(f"Formatted: {file_path.name}")  # noqa: T201


# Specify the folder path containing JSON files
folder_path = "outputjsonfiles"

# Call the function to format JSON files
format_json_files(folder_path)
