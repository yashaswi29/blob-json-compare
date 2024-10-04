import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# File paths from .env
json_file_path = os.getenv('JSON_FILE_PATH')

def get_line_numbers(json_file):
    line_number_dict = {}
    with open(json_file, 'r') as f:
        for i, line in enumerate(f, 1):
            if ':' in line:
                key = line.split(':')[0].strip().replace('"', '')
                line_number_dict[key] = i
    return line_number_dict

def validate_icons_in_functions(data, line_numbers, expected_prefix, parent_key=None):
    if isinstance(data, dict):
        # Check for functions with id, version, icon, description, and chapters
        if all(k in data for k in ['id', 'version', 'icon', 'description', 'chapters']):
            function_id = data['id']
            function_icon = data['icon']
            function_desc = data['description']
            line = line_numbers.get('id', 'Unknown')

            # Validate the icon path
            if not function_icon.startswith(expected_prefix):
                print(f"ID: {function_id}, Type: {parent_key}, Invalid Icon Path: {function_icon}, Line: {line}")
            
            # Validate chapters consistency
            for chapter in data.get('chapters', []):
                if chapter.get('id') != function_id or chapter.get('description') != function_desc:
                    chapter_id = chapter.get('id')
                    chapter_desc = chapter.get('description')
                    print(f"ID: {function_id}, Type: {parent_key}, Mismatch in Chapters - Chapter ID: {chapter_id}, Chapter Description: {chapter_desc}, Line: {line}")

        # Recursively check nested dictionaries or lists
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                validate_icons_in_functions(value, line_numbers, expected_prefix, parent_key=key)

    elif isinstance(data, list):
        for item in data:
            validate_icons_in_functions(item, line_numbers, expected_prefix, parent_key)

# Load the JSON file
with open(json_file_path, 'r') as f:
    json_data = json.load(f)

# Get the line numbers for all keys
line_numbers = get_line_numbers(json_file_path)

# Validate icons in the 'procedures' section (or any function)
validate_icons_in_functions(json_data, line_numbers, '/icon/procedures/', parent_key='procedures')
