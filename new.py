import json

# Function to validate icon paths based on parent key values
def validate_icon_paths(data, line_numbers):
    mismatched_icons = []

    def traverse(obj, parent_key="", current_line=0):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key == 'icon':
                    expected_path_prefix = f"/icon/{parent_key.lower()}"
                    if not value.startswith(expected_path_prefix):
                        # Get the actual line number from line_numbers
                        line_number = line_numbers.get(current_line, 'Unknown')
                        # Append mismatch info along with the line number
                        mismatched_icons.append((parent_key, value, expected_path_prefix, line_number))
                elif isinstance(value, (dict, list)):
                    # Traverse nested structures, keep track of current line index
                    traverse(value, parent_key=key, current_line=current_line)
                current_line += 1
        elif isinstance(obj, list):
            for index, item in enumerate(obj):
                traverse(item, parent_key=parent_key, current_line=current_line)
                current_line += 1

    traverse(data)
    return mismatched_icons

# Load the new JSON data from a file and track line numbers
json_file_path = '/home/yashaswi/Developer/Understanding-JSON/new-idea/content-bundle.json'  # Replace with your JSON file path

with open(json_file_path, 'r') as json_file:
    json_data = json.load(json_file)
    json_file.seek(0)  # Reset file pointer to the beginning
    line_info = {i: line.strip() for i, line in enumerate(json_file.readlines())}  # Track line numbers

# Get line numbers from the file for the 'icon' key
line_numbers = {}
with open(json_file_path, 'r') as json_file:
    for line_num, line in enumerate(json_file, 1):
        if '"icon"' in line:
            line_numbers[line_num] = line.strip()

# Validate the icon paths against the original JSON data
mismatched_icons = validate_icon_paths(json_data, line_numbers)

# Save the mismatched icons to a new text file
output_file_path = 'mismatched_icons_with_lines.txt'  # Path for the output text file
with open(output_file_path, 'w') as output_file:
    if mismatched_icons:
        for _, _, _, line_num in mismatched_icons:
            output_file.write(f"LINE ON ERROR {line_num}\n")  # Only print the line number error message
        print
