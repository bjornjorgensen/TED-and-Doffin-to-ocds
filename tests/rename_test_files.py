import os
import re


def rename_test_files(directory="."):
    for filename in os.listdir(directory):
        if filename.startswith("test_") and filename.endswith(".py"):
            # Convert the filename to lowercase
            new_filename = filename.lower()

            # Replace 'bt_' with 'bt_' (in case it was already lowercase)
            new_filename = re.sub(r"bt_", "bt_", new_filename)

            # Replace 'opp_' with 'opp_' (in case it was already lowercase)
            new_filename = re.sub(r"opp_", "opp_", new_filename)

            # Replace 'opt_' with 'opt_' (in case it was already lowercase)
            new_filename = re.sub(r"opt_", "opt_", new_filename)

            # Special handling for 'LotsGroup'
            new_filename = new_filename.replace("lotsgroup", "lotsgroup")

            if new_filename != filename:
                old_path = os.path.join(directory, filename)
                new_path = os.path.join(directory, new_filename)
                os.rename(old_path, new_path)
                print(f"Renamed: {filename} -> {new_filename}")


# Usage
rename_test_files()
