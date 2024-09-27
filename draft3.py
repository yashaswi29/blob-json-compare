import os
import json
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

load_dotenv()

def save_paths_to_file(directory, file_name, paths):
    """Save the paths to a file within a specified directory."""
    os.makedirs(directory, exist_ok=True)  # Create directory if it doesn't exist
    full_path = os.path.join(directory, file_name)
    
    with open(full_path, 'w') as file:
        for path in paths:
            file.write(f"{path}\n")
    
    print(f"Paths saved to: {full_path}")

def retrieve_image_video_files_from_blob_storage(container_name, directory_prefix):
    """Retrieves all .png and .mp4 file paths from Azure Blob Storage container."""
    connection_string = os.getenv("AZURE_CONNECTION_STRING")
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)

    blob_paths = []
    blobs = container_client.list_blobs(name_starts_with=directory_prefix)

    for blob in blobs:
        if blob.name.endswith('.png') or blob.name.endswith('.mp4'):
            blob_path = f"/{blob.name}" if not blob.name.startswith('/') else blob.name
            blob_paths.append(blob_path.strip())  # Case-sensitive comparison, no lowercase
    
    return blob_paths

def load_json_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def extract_src_values(json_data):
    src_values = []
    if isinstance(json_data, list):
        for item in json_data:
            src_values.extend(extract_src_values(item))
    elif isinstance(json_data, dict):
        for key, value in json_data.items():
            if key == 'src' and isinstance(value, str):
                src_values.append(value.strip())  # Case-sensitive comparison, no lowercase
            else:
                src_values.extend(extract_src_values(value))
    return src_values

def count_lines_in_file(file_path):
    """Count the number of lines in a text file."""
    with open(file_path, 'r') as file:
        return sum(1 for line in file)

def count_lines_twice(file_path):
    """Check line count twice to ensure accurate results."""
    first_count = count_lines_in_file(file_path)
    second_count = count_lines_in_file(file_path)
    
    if first_count != second_count:
        print(f"Warning: Inconsistent line count in {file_path} (first count: {first_count}, second count: {second_count})")
    else:
        print(f"{file_path} consistently has {first_count} lines.")
    
    return first_count
        
def find_duplicates(paths):
    """Return a set of duplicate paths."""
    from collections import Counter
    return {path for path, count in Counter(paths).items() if count > 1}

def verify_counts(blob_files, json_src_values, common_paths, missed_paths, json_only_paths):
    """Check the consistency of common, missed, and total paths."""
    blob_total = len(blob_files)
    json_total = len(json_src_values)
    common_total = len(common_paths)
    missed_total = len(missed_paths)
    json_only_total = len(json_only_paths)
    
    # Verify if the sum of common + missed = total blob paths
    if common_total + missed_total == blob_total:
        print(f"✔ Common ({common_total}) + Missed ({missed_total}) = Total Blob Paths ({blob_total})")
    else:
        print(f"✘ Common ({common_total}) + Missed ({missed_total}) != Total Blob Paths ({blob_total})")
        print(f"Missing paths in blob set: {blob_total - (common_total + missed_total)}")

    # Verify if the sum of common + json-only = total JSON paths
    if common_total + json_only_total == json_total:
        print(f"✔ Common ({common_total}) + JSON-only ({json_only_total}) = Total JSON Paths ({json_total})")
    else:
        print(f"✘ Common ({common_total}) + JSON-only ({json_only_total}) != Total JSON Paths ({json_total})")
        print(f"Missing paths in JSON set: {json_total - (common_total + json_only_total)}")

def main():
    container_name = os.getenv("BLOB_CONTAINER")
    directory_prefix = "content/assets/"
    
    output_dir = "draft3_output"  # Directory where all text files will be saved
    blob_output_file = "blob_src.txt"
    json_output_file = "json_src.txt"
    common_output_file = "common_path_src.txt"
    missed_output_file = "missed_path_src.txt"
    json_only_output_file = "json_only_path_src.txt"

    # Retrieve blob files and save them to the blob_src.txt file
    blob_files = retrieve_image_video_files_from_blob_storage(container_name, directory_prefix)
    save_paths_to_file(output_dir, blob_output_file, blob_files)

    # Load JSON file and extract paths, save them to the json_src.txt file
    json_file_path = os.getenv("JSON_FILE_PATH")
    json_data = load_json_file(json_file_path)
    json_src_values = extract_src_values(json_data)
    save_paths_to_file(output_dir, json_output_file, json_src_values)

    # Convert paths to sets for comparison
    blob_set = set(blob_files)
    json_set = set(json_src_values)

    # Find common paths, missed paths, and JSON-only paths
    common_paths = blob_set.intersection(json_set)  # Common in both
    missed_paths = blob_set.difference(json_set)    # Present in Blob but not in JSON
    json_only_paths = json_set.difference(blob_set) # Present in JSON but not in Blob

    # Save common and missed paths
    save_paths_to_file(output_dir, common_output_file, common_paths)
    save_paths_to_file(output_dir, missed_output_file, missed_paths)
    save_paths_to_file(output_dir, json_only_output_file, json_only_paths)

    # Check for duplicates
    blob_duplicates = find_duplicates(blob_files)
    json_duplicates = find_duplicates(json_src_values)
    
    if blob_duplicates:
        print(f"Warning: Duplicates found in Blob paths: {blob_duplicates}")
    if json_duplicates:
        print(f"Warning: Duplicates found in JSON paths: {json_duplicates}")

    # Check the line count twice for all files
    print("\nChecking file line counts twice:")
    blob_lines = count_lines_twice(os.path.join(output_dir, blob_output_file))
    json_lines = count_lines_twice(os.path.join(output_dir, json_output_file))
    common_lines = count_lines_twice(os.path.join(output_dir, common_output_file))
    missed_lines = count_lines_twice(os.path.join(output_dir, missed_output_file))
    json_only_lines = count_lines_twice(os.path.join(output_dir, json_only_output_file))

    # Final results and consistency checks
    print(f"\nFinal line counts:\n"
          f"- blob_src.txt: {blob_lines}\n"
          f"- json_src.txt: {json_lines}\n"
          f"- common_path_src.txt: {common_lines}\n"
          f"- missed_path_src.txt: {missed_lines}\n"
          f"- json_only_path_src.txt: {json_only_lines}")
    
    # Verify the sums for consistency
    verify_counts(blob_files, json_src_values, common_paths, missed_paths, json_only_paths)

if __name__ == "__main__":
    main()
