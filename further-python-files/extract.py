import os
import urllib.parse
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
import json

# Load environment variables from .env file
load_dotenv()

# Utility function to save paths to text file
def save_paths_to_file(file_name, paths):
    """Saves the list of file paths to a specified text file."""
    with open(file_name, 'w') as file:
        for path in paths:
            # Decode any URL-encoded characters (e.g., %20 for space)
            decoded_path = urllib.parse.unquote(path)
            file.write(f"{decoded_path}\n")
    print(f"Paths saved to: {file_name}")

# Retrieve .png and .mp4 files from Azure Blob Storage
def retrieve_image_video_files_from_blob_storage(container_name, directory_prefix):
    """Retrieves all .png and .mp4 file paths from Azure Blob Storage container."""
    connection_string = os.getenv("AZURE_CONNECTION_STRING")
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)

    blob_paths = []
    blobs = container_client.list_blobs(name_starts_with=directory_prefix)

    for blob in blobs:
        if blob.name.endswith('.png') or blob.name.endswith('.mp4'):
            # Decode the blob name (file path)
            blob_paths.append(urllib.parse.unquote(blob.name))
    
    return blob_paths

# Load file paths from JSON
def load_json_file(file_path):
    """Loads the JSON data from the specified file."""
    with open(file_path, 'r') as file:
        return json.load(file)

def extract_src_values(json_data):
    """Recursively extracts all 'src' values from the JSON structure."""
    src_values = []
    if isinstance(json_data, list):
        for item in json_data:
            src_values.extend(extract_src_values(item))
    elif isinstance(json_data, dict):
        for key, value in json_data.items():
            if key == 'src' and isinstance(value, str):
                # Decode the src value
                src_values.append(urllib.parse.unquote(value))
            else:
                src_values.extend(extract_src_values(value))
    return src_values

# Load paths from text file
def load_paths_from_file(file_path):
    """Loads all file paths from a text file into a list, decoding URL-encoded characters."""
    with open(file_path, 'r') as file:
        return [urllib.parse.unquote(line.strip()) for line in file]

# Compare the blob and JSON src paths
def compare_paths(json_src_paths, blob_src_paths):
    """Compares two lists of file paths to find missing and common paths."""
    json_src_paths_set = set([urllib.parse.unquote(path.lower()) for path in json_src_paths])
    blob_src_paths_set = set([urllib.parse.unquote(path.lower()) for path in blob_src_paths])

    # Find missing paths in blob storage and common paths
    missing_paths = list(json_src_paths_set - blob_src_paths_set)
    common_paths = list(json_src_paths_set & blob_src_paths_set)

    return missing_paths, common_paths

# Main function
def main():
    # Set up environment variables and paths
    container_name = os.getenv("BLOB_CONTAINER")
    directory_prefix = "content/assets/"
    
    # Output text files
    blob_output_file = "blob_src.txt"
    json_output_file = "json_src.txt"
    missing_output_file = "missed_path_src.txt"
    common_output_file = "common_path_src.txt"

    # Step 1: Recheck and retrieve file paths from Azure Blob Storage
    blob_files = retrieve_image_video_files_from_blob_storage(container_name, directory_prefix)
    save_paths_to_file(blob_output_file, blob_files)

    # Step 2: Recheck and retrieve file paths from JSON
    json_file_path = os.getenv("JSON_FILE_PATH")
    json_data = load_json_file(json_file_path)
    json_src_values = extract_src_values(json_data)
    save_paths_to_file(json_output_file, json_src_values)

    # Step 3: Compare the file paths between the JSON and Blob storage
    json_src_paths = load_paths_from_file(json_output_file)
    blob_src_paths = load_paths_from_file(blob_output_file)
    
    missing_paths, common_paths = compare_paths(json_src_paths, blob_src_paths)

    # Step 4: Save missing and common paths to text files
    save_paths_to_file(missing_output_file, missing_paths)
    save_paths_to_file(common_output_file, common_paths)

    print(f"Comparison complete. Missing paths saved to '{missing_output_file}', and common paths saved to '{common_output_file}'.")

if __name__ == "__main__":
    main()
