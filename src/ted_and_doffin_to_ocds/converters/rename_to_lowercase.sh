#!/bin/bash

# Rename all files to lowercase in the current directory
for file in *; do
    if [ -f "$file" ]; then
        lowercase_name=$(echo "$file" | tr '[:upper:]' '[:lower:]')
        if [ "$file" != "$lowercase_name" ]; then
            mv "$file" "$lowercase_name"
            echo "Renamed: $file -> $lowercase_name"
        fi
    fi
done

echo "All files have been renamed to lowercase."
