import os
import json
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Directories and environment configurations
output_dir = os.getenv("OUTPUT_DIR", "draft5")
os.makedirs(output_dir, exist_ok=True)

def save_paths_to_file(directory, file_name, paths):
    """Save the paths to a file."""
    os.makedirs(directory, exist_ok=True)  
    full_path = os.path.join(directory, file_name)
    
    with open(full_path, 'w') as file:
        for path in paths:
            file.write(f"{path}\n")
    
    print(f"Paths saved to: {full_path}")

def update_blob_paths(blob_paths):
    """Update blob paths by adding 'content' and replacing spaces with '%', returning updated paths."""
    updated_paths = []
    for path in blob_paths:
        # Here we replace spaces with '%'
        updated_path = f"/content{path}".replace(' ', '%20')
        updated_paths.append(updated_path)
    return updated_paths

def retrieve_image_files_from_blob_storage(container_name, image_prefix):
    """Find all .png file paths from Azure Blob Storage."""
    connection_string = os.getenv("AZURE_CONNECTION_STRING")
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)

    blob_paths = []
    
    # Retrieve image files
    image_blobs = container_client.list_blobs(name_starts_with=image_prefix)
    for blob in image_blobs:
        if blob.name.endswith('.png'):
            blob_path = f"/{blob.name}" if not blob.name.startswith('/') else blob.name
            blob_paths.append(blob_path.strip())
    
    return blob_paths

def retrieve_json_file_from_blob(container_name, json_blob_path):
    """Fetches a JSON file from a specific path in the Azure Blob Storage container."""
    connection_string = os.getenv("AZURE_CONNECTION_STRING")
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)
    
    blob_client = container_client.get_blob_client(json_blob_path)
    json_content = blob_client.download_blob().readall()
    return json.loads(json_content)

def extract_src_values(json_data):
    """Extract 'src' values from JSON data using recursion."""
    src_values = []
    if isinstance(json_data, list):
        for item in json_data:
            src_values.extend(extract_src_values(item))
    elif isinstance(json_data, dict):
        for key, value in json_data.items():
            if key == 'src' and isinstance(value, str):
                src_values.append(value.strip())  
            else:
                src_values.extend(extract_src_values(value))
    return src_values

def count_lines_twice(file_path):
    """Check line count twice to ensure accurate results."""
    def count_lines_in_file(fp):
        with open(fp, 'r') as file:
            return sum(1 for line in file)

    first_count = count_lines_in_file(file_path)
    second_count = count_lines_in_file(file_path)
    
    if first_count != second_count:
        print(f"Warning: Inconsistent line count in {file_path} (first: {first_count}, second: {second_count})")
    else:
        print(f"{file_path} consistently has {first_count} lines.")
    return first_count

def find_duplicates(paths):
    from collections import Counter
    return {path for path, count in Counter(paths).items() if count > 1}

def verify_counts(blob_files, json_src_values, common_paths, missed_paths, json_only_paths):
    blob_total = len(blob_files)
    json_total = len(json_src_values)
    common_total = len(common_paths)
    missed_total = len(missed_paths)
    json_only_total = len(json_only_paths)
    
    if common_total + missed_total == blob_total:
        print(f"✔ Common ({common_total}) + Missed ({missed_total}) = Total Blob Paths ({blob_total})")
    else:
        print(f"✘ Common ({common_total}) + Missed ({missed_total}) != Total Blob Paths ({blob_total})")
        print(f"Missing paths in blob set: {blob_total - (common_total + missed_total)}")

    if common_total + json_only_total == json_total:
        print(f"✔ Common ({common_total}) + JSON-only ({json_only_total}) = Total JSON Paths ({json_total})")
    else:
        print(f"✘ Common ({common_total}) + JSON-only ({json_only_total}) != Total JSON Paths ({json_total})")
        print(f"Missing paths in JSON set: {json_total - (common_total + json_only_total)}")

def main():
    # Container and blob configurations from environment variables
    assets_container = os.getenv("BLOB_CONTAINER_ASSETS")
    image_prefix = os.getenv("BLOB_IMAGES_PREFIX")
    json_container = os.getenv("BLOB_CONTAINER_JSON")
    json_blob_path = os.getenv("JSON_BLOB_PATH")

    blob_output_file = "blob_src.txt"
    json_output_file = "json_src.txt"
    common_output_file = "common_path_src.txt"
    missed_output_file = "missed_path_src.txt"
    json_only_output_file = "json_only_path_src.txt"

    # Retrieve Blob files (images) and save to blob_src.txt
    blob_files = retrieve_image_files_from_blob_storage(assets_container, image_prefix)
    updated_blob_files = update_blob_paths(blob_files)  # Update blob paths
    save_paths_to_file(output_dir, blob_output_file, updated_blob_files)  # Save updated paths

    # Retrieve JSON file and extract src values
    json_data = retrieve_json_file_from_blob(json_container, json_blob_path)
    json_src_values = extract_src_values(json_data)
    save_paths_to_file(output_dir, json_output_file, json_src_values)

    # Compare Blob and JSON paths
    blob_set = set(updated_blob_files)
    json_set = set(json_src_values)

    common_paths = blob_set.intersection(json_set)
    missed_paths = blob_set.difference(json_set)
    json_only_paths = json_set.difference(blob_set)

    # Save comparison results
    save_paths_to_file(output_dir, common_output_file, common_paths)
    save_paths_to_file(output_dir, missed_output_file, missed_paths)
    save_paths_to_file(output_dir, json_only_output_file, json_only_paths)

    # Check for duplicates
    blob_duplicates = find_duplicates(updated_blob_files)
    json_duplicates = find_duplicates(json_src_values)
    
    if blob_duplicates:
        print(f"Warning: Duplicates found in Blob paths: {blob_duplicates}")
    if json_duplicates:
        print(f"Warning: Duplicates found in JSON paths: {json_duplicates}")

    # Validate file counts
    print("\nChecking file line counts twice:")
    count_lines_twice(os.path.join(output_dir, blob_output_file))
    count_lines_twice(os.path.join(output_dir, json_output_file))
    count_lines_twice(os.path.join(output_dir, common_output_file))
    count_lines_twice(os.path.join(output_dir, missed_output_file))
    count_lines_twice(os.path.join(output_dir, json_only_output_file))

    verify_counts(updated_blob_files, json_src_values, common_paths, missed_paths, json_only_paths)

if __name__ == "__main__":
    main()
