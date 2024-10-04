import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the JSON file path from the environment variable
json_file_path = os.getenv('JSON_FILE_PATH')

def validate_icon_paths_recursive(data, line_numbers, current_line, parent_key=""):

    results = []
    
    if isinstance(data, dict):
        if all(key in data for key in ["id", "version", "icon", "description"]):
            # Extract section type from parent_key (e.g., actionCards, modules)
            section_type = parent_key.rstrip('s').lower()  # Remove 's' if plural

            # Check if icon path starts with the section name
            icon_path = data.get("icon", "")
            expected_prefix = f"/icon/{section_type}"
            if icon_path.startswith(expected_prefix):
                # Store the result if the icon path is valid
                result = {
                    "id": data["id"],
                    "icon": icon_path,
                    "type": section_type,
                    "line": current_line
                }
                results.append(result)

        # Recursively go deeper into nested structures
        for key, value in data.items():
            nested_results = validate_icon_paths_recursive(value, line_numbers, line_numbers.get(key, current_line), key)
            results.extend(nested_results)

    elif isinstance(data, list):
        for i, item in enumerate(data):
            nested_results = validate_icon_paths_recursive(item, line_numbers, line_numbers.get(f"{parent_key}[{i}]", current_line), parent_key)
            results.extend(nested_results)

    return results

def get_line_numbers(json_file_path):
    """Helper function to map line numbers to keys in the JSON file."""
    line_numbers = {}
    with open(json_file_path, 'r') as f:
        for i, line in enumerate(f, 1):
            if ':' in line:
                key = line.split(':', 1)[0].strip().strip('"')
                line_numbers[key] = i
    return line_numbers

# Load line numbers and JSON data
line_numbers = get_line_numbers(json_file_path)

# Load the JSON file using the path from .env
with open(json_file_path, 'r') as file:
    data = json.load(file)

# Call the function and get the results
icon_check_results = validate_icon_paths_recursive(data, line_numbers, 1)

# Print the simplified output
for result in icon_check_results:
    print(f"ID: {result['id']}, Type: {result['type']}, Icon: {result['icon']}, Line: {result['line']}")
