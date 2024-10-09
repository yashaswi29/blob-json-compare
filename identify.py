import json

# Function to validate icon and image paths for specific parent keys
def validate_icon_and_image_paths(data, line_info):
    mismatched_paths = []

    def traverse(obj, parent_key="", current_line=0):
        if isinstance(obj, dict):
            for key, value in obj.items():
                # Check for icon path in "procedures" and "actionCards"
                if parent_key in ['procedures', 'actionCards'] and key == 'icon':
                    expected_path_prefix = f"/icon/{parent_key.lower()}"
                    if not value.startswith(expected_path_prefix):
                        # Append mismatch info along with the line number
                        mismatched_paths.append((parent_key, key, value, expected_path_prefix, line_info[current_line]))
                
                # Check for image path in "keyLearningPoints"
                elif parent_key == 'keyLearningPoints' and key == 'image':
                    expected_path_prefix = f"/image/{parent_key.lower()}"
                    if not value.startswith(expected_path_prefix):
                        # Append mismatch info along with the line number
                        mismatched_paths.append((parent_key, key, value, expected_path_prefix, line_info[current_line]))

                elif isinstance(value, (dict, list)):
                    traverse(value, parent_key=key if key in ['procedures', 'actionCards', 'keyLearningPoints'] else parent_key, current_line=current_line)
                current_line += 1
        elif isinstance(obj, list):
            for index, item in enumerate(obj):
                traverse(item, parent_key=parent_key, current_line=current_line)
                current_line += 1

    traverse(data)
    return mismatched_paths

# Load the new JSON data from a file and track line numbers
json_file_path = '/home/nitish/Downloads/new-idea/content-bundle.json'  # Replace with the path to your new JSON file

with open(json_file_path, 'r') as json_file:
    json_data = json.load(json_file)
    json_file.seek(0)  # Reset file pointer to the beginning
    line_info = {i: line.strip() for i, line in enumerate(json_file.readlines())}  # Track line numbers

# Validate the icon and image paths against the original JSON data
mismatched_paths = validate_icon_and_image_paths(json_data, line_info)

# Save the mismatched paths to a new text file
output_file_path = 'mismatched_paths.txt'  # Path for the output text file
with open(output_file_path, 'w') as output_file:
    if mismatched_paths:
        output_file.write("Mismatched Paths:\n")
        for parent, key, path, expected, line in mismatched_paths:
            output_file.write(f"Parent Key: {parent}, Key: {key}, Path: {path}, Expected Prefix: {expected}, Line: {line}\n")
        print(f"All mismatched paths have been saved to {output_file_path}.")
    else:
        output_file.write("All paths are valid!\n")
        print("All paths are valid!")