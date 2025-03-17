import os
import json
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

load_dotenv()

output_dir = os.getenv("OUTPUT_DIR", "draft5")
os.makedirs(output_dir, exist_ok=True)
container_name = os.getenv("BLOB_CONTAINER_ASSETS")

def save_paths_to_file(directory, file_name, paths):
    os.makedirs(directory, exist_ok=True)  
    full_path = os.path.join(directory, file_name)
    with open(full_path, 'w') as file:
        for path in paths:
            file.write(f"{path}\n")
    
    print(f"Paths saved to: {full_path}")

def normalize_path(path):
    """Normalizes paths to lowercase and replaces backslashes with forward slashes."""
    return path.replace("\\", "/").lower().strip()

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
            blob_path = normalize_path(f"/{blob.name}" if not blob.name.startswith('/') else blob.name)
            blob_paths.append(blob_path)
    
    return blob_paths

def retrieve_video_files_from_blob_storage(container_name, video_prefix):
    """Find all video file paths from Azure Blob Storage."""
    connection_string = os.getenv("AZURE_CONNECTION_STRING")
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)

    blob_paths = []
    
    # Retrieve video files (consider supported video extensions here)
    video_blobs = container_client.list_blobs(name_starts_with=video_prefix)
    for blob in video_blobs:
        # Check for video extensions (e.g., .mp4, .mkv)
        if blob.name.endswith(('.mp4', '.mkv', '.avi', ...)):  # Add relevant extensions
            blob_path = normalize_path(f"/{blob.name}" if not blob.name.startswith('/') else blob.name)
            blob_paths.append(blob_path)
    
    return blob_paths

def retrieve_json_file_from_blob(container_client, blob_name):
    """Fetches a JSON file from a specific path in the Azure Blob Storage container."""
    blob_client = container_client.get_blob_client(blob_name)
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
                src_values.append(normalize_path(value.strip()))
            else:
                src_values.extend(extract_src_values(value))
    return src_values

def analyze_language(language_id, language_info, container_client):
    # Retrieve content-bundle.json for the language
    json_blob_path = f"{language_id}/content-bundle.json"
    json_data = retrieve_json_file_from_blob(container_client, json_blob_path)
    json_src_values = extract_src_values(json_data)

    # Retrieve image and video paths from the asset version
    image_paths = retrieve_image_files_from_blob_storage(container_name, language_info["asset_version"][0])
    video_paths = retrieve_video_files_from_blob_storage(container_name, language_info["asset_version"][1])

    # Compare JSON paths with asset paths
    common_paths = set(json_src_values).intersection(set(image_paths + video_paths))
    missing_paths = set(json_src_values).difference(set(image_paths + video_paths))
    extra_paths = set(image_paths + video_paths).difference(set(json_src_values))

    # Save comparison results for the language
    save_paths_to_file(output_dir, f"{language_id}_common_paths.txt", common_paths)
    save_paths_to_file(output_dir, f"{language_id}_missing_paths.txt", missing_paths)
    save_paths_to_file(output_dir, f"{language_id}_extra_paths.txt", extra_paths)

    # Add JSON paths to the global set of used paths
    global_used_paths.update(json_src_values)

def main():
    # Load language mapping
    with open("language_mapping.json", "r") as f:
        language_mapping = json.load(f)

    global_used_paths = set()

    # Connect to Azure Blob Storage
    connection_string = os.getenv("AZURE_CONNECTION_STRING")
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)

    # Iterate over languages
    for language_id, language_info in language_mapping.items():
        analyze_language(language_id, language_info, container_client)

    # Identify globally unused files
    globally_unused_files = []
    for image_path in image_paths:
        if image_path not in global_used_paths:
            globally_unused_files.append(image_path)
    for video_path in video_paths:
        if video_path not in global_used_paths:
            globally_unused_files.append(video_path)

    # Save globally unused files to a file
    save_paths_to_file(output_dir, "globally_unused.txt", globally_unused_files)

if __name__ == "__main__":
    main()