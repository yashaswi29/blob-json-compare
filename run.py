import os
import json
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

output_dir = "draft5"
os.makedirs(output_dir, exist_ok=True)

def save_paths_to_file(directory, file_name, paths):

    os.makedirs(directory, exist_ok=True)  
    full_path = os.path.join(directory, file_name)
    
    with open(full_path, 'w') as file:
        for path in paths:
            file.write(f"{path}\n")
    
    print(f"Paths saved to: {full_path}")

def retrieve_image_video_files_from_blob_storage(container_name, directory_prefix):
    """Find all .png and .mp4 file paths from Azure Blob Storage."""
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

def retrieve_json_file_from_blob(container_name, blob_name):
    """Fetches a JSON file from the Azure Blob Storage container."""
    connection_string = os.getenv("AZURE_CONNECTION_STRING")
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)
    
    blob_client = container_client.get_blob_client(blob_name)
    json_content = blob_client.download_blob().readall()
    return json.loads(json_content)

def extract_src_values(json_data):
    """ extract 'src' values from JSON data using recursion."""
    # Case-sensitive comparison, no lowercase
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
    from collections import Counter
    return {path for path, count in Counter(paths).items() if count > 1}

def verify_counts(blob_files, json_src_values, common_paths, missed_paths, json_only_paths):
    blob_total = len(blob_files)
    json_total = len(json_src_values)
    common_total = len(common_paths)
    missed_total = len(missed_paths)
    json_only_total = len(json_only_paths)
    
    #logic of fetched, sum of common + missed = total blob paths
    if common_total + missed_total == blob_total:
        print(f"✔ Common ({common_total}) + Missed ({missed_total}) = Total Blob Paths ({blob_total})")
    else:
        print(f"✘ Common ({common_total}) + Missed ({missed_total}) != Total Blob Paths ({blob_total})")
        print(f"Missing paths in blob set: {blob_total - (common_total + missed_total)}")

    #logic of fetched, sum of common + json-only = total JSON paths
    if common_total + json_only_total == json_total:
        print(f"✔ Common ({common_total}) + JSON-only ({json_only_total}) = Total JSON Paths ({json_total})")
    else:
        print(f"✘ Common ({common_total}) + JSON-only ({json_only_total}) != Total JSON Paths ({json_total})")
        print(f"Missing paths in JSON set: {json_total - (common_total + json_only_total)}")

def main():
    container_name = os.getenv("BLOB_CONTAINER")
    directory_prefix = os.getenv("BLOB_PREFIX")
    json_blob_name = os.getenv("JSON_BLOB_NAME")

    blob_output_file = "blob_src.txt"
    json_output_file = "json_src.txt"
    common_output_file = "common_path_src.txt"
    missed_output_file = "missed_path_src.txt"
    json_only_output_file = "json_only_path_src.txt"

    # fetchesblob files and save them to the blob_src.txt file
    blob_files = retrieve_image_video_files_from_blob_storage(container_name, directory_prefix)
    save_paths_to_file(output_dir, blob_output_file, blob_files)

    # fetches JSON file from Azure Blob Storage and extract paths
    json_data = retrieve_json_file_from_blob(container_name, json_blob_name)
    json_src_values = extract_src_values(json_data)
    save_paths_to_file(output_dir, json_output_file, json_src_values)

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

    # Check the line count: twice 
    print("\nChecking file line counts twice:")
    blob_lines = count_lines_twice(os.path.join(output_dir, blob_output_file))
    json_lines = count_lines_twice(os.path.join(output_dir, json_output_file))
    common_lines = count_lines_twice(os.path.join(output_dir, common_output_file))
    missed_lines = count_lines_twice(os.path.join(output_dir, missed_output_file))
    json_only_lines = count_lines_twice(os.path.join(output_dir, json_only_output_file))

    print(f"\nFinal line counts:\n"
          f"- blob_src.txt: {blob_lines}\n"
          f"- json_src.txt: {json_lines}\n"
          f"- common_path_src.txt: {common_lines}\n"
          f"- missed_path_src.txt: {missed_lines}\n"
          f"- json_only_path_src.txt: {json_only_lines}")

    verify_counts(blob_files, json_src_values, common_paths, missed_paths, json_only_paths)

if __name__ == "__main__":
    main()
