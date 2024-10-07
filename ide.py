import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

JSON_FILE_PATH = os.getenv('JSON_FILE_PATH', 'path/to/your/json_file.json')

def load_json_file(json_file_path):
    """Load JSON data from a file with line numbers."""
    try:
        with open(json_file_path, 'r') as file:
            data = file.readlines()
            json_data = json.loads(''.join(data))
            return json_data, data
    except FileNotFoundError:
        print("JSON file not found.")
        return {}, []
    except json.JSONDecodeError:
        print("Error decoding JSON.")
        return {}, []

def find_line_number(json_lines, search_str):
    """Find the line number of the given string in the JSON file."""
    for index, line in enumerate(json_lines, start=1):
        if search_str in line:
            return index
    return None

def check_icon_paths(json_data, json_lines, parent_key):
    """Recursively check the 'icon' paths and return line numbers with errors."""
    errors = []
    
    if isinstance(json_data, dict):
        for key, value in json_data.items():
            if key == 'icon' and isinstance(value, str):
                if not value.startswith('/'):  # Assuming valid paths must start with '/'
                    line_number = find_line_number(json_lines, f'"{key}": "{value}"')
                    errors.append((line_number, parent_key, value))
            elif isinstance(value, (dict, list)):
                errors.extend(check_icon_paths(value, json_lines, parent_key))
    elif isinstance(json_data, list):
        for idx, item in enumerate(json_data):
            errors.extend(check_icon_paths(item, json_lines, f"{parent_key}[{idx}]"))

    return errors

def validate_json_icons(json_data, json_lines):
    """Validate the 'icon' paths for specific objects."""
    fields_to_check = ['procedures', 'actioncards', 'modules', 'drugs', 'onboarding', 
                       'keylearningpoints', 'certificates']
    
    errors = []
    
    for field in fields_to_check:
        if field in json_data:
            errors.extend(check_icon_paths(json_data[field], json_lines, field))

    return errors

def main():
    # Load the JSON file
    json_data, json_lines = load_json_file(JSON_FILE_PATH)
    
    # Validate the JSON data for icon path errors
    errors = validate_json_icons(json_data, json_lines)
    
    if errors:
        print(f"Found {len(errors)} icon path errors:")
        for error in errors:
            line_number, field, icon_value = error
            print(f"Line {line_number}: Error in '{field}' -> Invalid icon path: {icon_value}")
    else:
        print("No errors found in icon paths.")

if __name__ == "__main__":
    main()
