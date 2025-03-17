#Common Paths: Paths present in both content-bundle.json and the assets folder.
#Missed Paths: Paths in the assets folder but not referenced in the language’s content-bundle.json.
#Maintain a global set of all paths referenced in any content-bundle.json file.

import os
import json
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

load_dotenv()

def save_paths_to_file(directory, file_name, paths):
    os.makedirs(directory, exist_ok=True)
    full_path = os.path.join(directory, file_name)
    with open(full_path, 'w') as file:
        for path in paths:
            file.write(f"{path}\n")

def normalize_path(path):
    return path.replace("\\", "/").lower().strip()

def retrieve_image_files_from_blob_storage(container_name, image_prefix):
    connection_string = os.getenv("AZURE_CONNECTION_STRING")
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)
    blob_paths = []
    image_blobs = container_client.list_blobs(name_starts_with=image_prefix)
    for blob in image_blobs:
        blob_paths.append(normalize_path(f"/{blob.name}"))
    return blob_paths

def retrieve_language_json_files(container_name, languages_prefix):
    connection_string = os.getenv("AZURE_CONNECTION_STRING")
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)
    language_json_files = []
    blobs = container_client.list_blobs(name_starts_with=languages_prefix)
    for blob in blobs:
        if blob.name.endswith('content-bundle.json'):
            language_json_files.append(blob.name)
    return language_json_files

def process_language_json(blob_service_client, container_name, json_path):
    container_client = blob_service_client.get_container_client(container_name)
    blob_client = container_client.get_blob_client(json_path)
    json_content = blob_client.download_blob().readall()
    return json.loads(json_content)

def extract_src_values(json_data):
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

def compare_paths_per_language(language_id, json_src_values, assets_paths):
    language_results = {}
    json_set = set(normalize_path(path) for path in json_src_values)
    assets_set = set(normalize_path(path) for path in assets_paths)
    common_paths = json_set.intersection(assets_set)
    missed_paths = assets_set.difference(json_set)
    language_results["language_id"] = language_id
    language_results["common"] = list(common_paths)
    language_results["missed"] = list(missed_paths)
    return language_results

def main():
    assets_container = os.getenv("BLOB_CONTAINER_ASSETS")
    languages_container = os.getenv("BLOB_CONTAINER_JSON")
    assets_prefix = os.getenv("ASSETS_PREFIX", "assets/")
    languages_prefix = os.getenv("LANGUAGES_PREFIX", "languages/")
    output_dir = os.getenv("OUTPUT_DIR", "output")
    os.makedirs(output_dir, exist_ok=True)
    connection_string = os.getenv("AZURE_CONNECTION_STRING")
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    assets_paths = retrieve_image_files_from_blob_storage(assets_container, assets_prefix)
    language_json_files = retrieve_language_json_files(languages_container, languages_prefix)
    all_json_paths = set()
    global_missed_paths = set(assets_paths)
    for json_path in language_json_files:
        language_id = os.path.basename(os.path.dirname(json_path))
        json_data = process_language_json(blob_service_client, languages_container, json_path)
        json_src_values = extract_src_values(json_data)
        all_json_paths.update(json_src_values)
        results = compare_paths_per_language(language_id, json_src_values, assets_paths)
        save_paths_to_file(output_dir, f"{language_id}_common_paths.txt", results["common"])
        save_paths_to_file(output_dir, f"{language_id}_missed_paths.txt", results["missed"])
        global_missed_paths.intersection_update(results["missed"])
    global_missed_paths = global_missed_paths.difference(all_json_paths)
    save_paths_to_file(output_dir, "global_missed_paths.txt", list(global_missed_paths))

if __name__ == "__main__":
    main()

# ''''''
# import os
# import json
# from azure.storage.blob import BlobServiceClient
# from dotenv import load_dotenv

# # Load environment variables from .env file
# load_dotenv()

# # Directories and environment configurations
# output_dir = os.getenv("OUTPUT_DIR", "draft5")
# os.makedirs(output_dir, exist_ok=True)

# def save_paths_to_file(directory, file_name, paths):
#     os.makedirs(directory, exist_ok=True)  
#     full_path = os.path.join(directory, file_name)
             
#     with open(full_path, 'w') as file:
#         for path in paths:
#             file.write(f"{path}\n")
    
#     print(f"Paths saved to: {full_path}")

# def normalize_path(path):
#     """Normalizes paths to lowercase and replaces backslashes with forward slashes."""
#     return path.replace("\\", "/").lower().strip()

# def update_blob_paths(blob_paths):
#     """Update and normalize blob paths."""
#     updated_paths = []
#     for path in blob_paths:
#         updated_path = normalize_path(f"/content{path}".replace(' ', '%20'))
#         updated_paths.append(updated_path)
#     return updated_paths

# def retrieve_image_files_from_blob_storage(container_name, image_prefix):
#     """Find all .png file paths from Azure Blob Storage."""
#     connection_string = os.getenv("AZURE_CONNECTION_STRING")
#     blob_service_client = BlobServiceClient.from_connection_string(connection_string)
#     container_client = blob_service_client.get_container_client(container_name)

#     blob_paths = []
    
#     # Retrieve image files
#     image_blobs = container_client.list_blobs(name_starts_with=image_prefix)
#     for blob in image_blobs:
#         if blob.name.endswith('.png'):
#             blob_path = normalize_path(f"/{blob.name}" if not blob.name.startswith('/') else blob.name)
#             blob_paths.append(blob_path)
    
#     return blob_paths

# def retrieve_json_file_from_blob(container_name, json_blob_path):
#     """Fetches a JSON file from a specific path in the Azure Blob Storage container."""
#     connection_string = os.getenv("AZURE_CONNECTION_STRING")
#     blob_service_client = BlobServiceClient.from_connection_string(connection_string)
#     container_client = blob_service_client.get_container_client(container_name)
    
#     blob_client = container_client.get_blob_client(json_blob_path)
#     json_content = blob_client.download_blob().readall()
#     return json.loads(json_content)

# def extract_src_values(json_data):
#     """Extract 'src' values from JSON data using recursion."""
#     src_values = []
#     if isinstance(json_data, list):
#         for item in json_data:
#             src_values.extend(extract_src_values(item))
#     elif isinstance(json_data, dict):
#         for key, value in json_data.items():
#             if key == 'src' and isinstance(value, str):
#                 src_values.append(normalize_path(value.strip()))
#             else:
#                 src_values.extend(extract_src_values(value))
#     return src_values

# def count_lines_twice(file_path):
#     """Check line count twice to ensure accurate results."""
#     def count_lines_in_file(fp):
#         with open(fp, 'r') as file:
#             return sum(1 for line in file)

#     first_count = count_lines_in_file(file_path)
#     second_count = count_lines_in_file(file_path)
    
#     if first_count != second_count:
#         print(f"Warning: Inconsistent line count in {file_path} (first: {first_count}, second: {second_count})")
#     else:
#         print(f"{file_path} consistently has {first_count} lines.")
#     return first_count

# def find_duplicates(paths):
#     from collections import Counter
#     return {path for path, count in Counter(paths).items() if count > 1}

# def verify_counts(blob_files, json_src_values, common_paths, missed_paths, json_only_paths):
#     blob_total = len(blob_files)
#     json_total = len(json_src_values)
#     common_total = len(common_paths)
#     missed_total = len(missed_paths)
#     json_only_total = len(json_only_paths)
    
#     if common_total + missed_total == blob_total:
#         print(f"✔ Common ({common_total}) + Missed ({missed_total}) = Total Blob Paths ({blob_total})")
#     else:
#         print(f"✘ Common ({common_total}) + Missed ({missed_total}) != Total Blob Paths ({blob_total})")
#         # print(f"Missing paths in blob set: {blob_total - (common_total + missed_total)}")

#     if common_total + json_only_total == json_total:
#         print(f"✔ Common ({common_total}) + JSON-only ({json_only_total}) = Total JSON Paths ({json_total})")
#     else:
#         print(f"✘ Common ({common_total}) + JSON-only ({json_only_total}) != Total JSON Paths ({json_total})")
#         # print(f"Missing paths in JSON set: {json_total - (common_total + json_only_total)}")

# def main():
#     # Container and blob configurations from environment variables
#     assets_container = os.getenv("BLOB_CONTAINER_ASSETS")
#     image_prefix = os.getenv("BLOB_IMAGES_PREFIX")
#     json_container = os.getenv("BLOB_CONTAINER_JSON")
#     json_blob_path = os.getenv("JSON_BLOB_PATH")

#     blob_output_file = "blob_src.txt"
#     json_output_file = "json_src.txt"
#     common_output_file = "common_path_src.txt"
#     missed_output_file = "missed_path_src.txt"
#     json_only_output_file = "json_only_path_src.txt"

#     # Retrieve Blob files (images) and save to blob_src.txt
#     blob_files = retrieve_image_files_from_blob_storage(assets_container, image_prefix)
#     updated_blob_files = update_blob_paths(blob_files)  # Update blob paths
#     save_paths_to_file(output_dir, blob_output_file, updated_blob_files)  # Save updated paths

#     # Retrieve JSON file and extract src values
#     json_data = retrieve_json_file_from_blob(json_container, json_blob_path)
#     json_src_values = extract_src_values(json_data)
#     save_paths_to_file(output_dir, json_output_file, json_src_values)

#     # Compare Blob and JSON paths
#     blob_set = set(normalize_path(path) for path in updated_blob_files)
#     json_set = set(normalize_path(path) for path in json_src_values)

#     common_paths = blob_set.intersection(json_set)
#     missed_paths = blob_set.difference(json_set)
#     json_only_paths = json_set.difference(blob_set)

#     # Save comparison results
#     save_paths_to_file(output_dir, common_output_file, common_paths)
#     save_paths_to_file(output_dir, missed_output_file, missed_paths)
#     save_paths_to_file(output_dir, json_only_output_file, json_only_paths)

#     # Check for duplicates
#     blob_duplicates = find_duplicates(updated_blob_files)
#     json_duplicates = find_duplicates(json_src_values)
    
#     if blob_duplicates:
#         print(f"Warning: Duplicates found in Blob paths: {blob_duplicates}")
#     if json_duplicates:
#         print(f"Warning: Duplicates found in JSON paths: {json_duplicates}")

#     # Validate file counts
#     print("\nChecking file line counts twice:")
#     count_lines_twice(os.path.join(output_dir, blob_output_file))
#     count_lines_twice(os.path.join(output_dir, json_output_file))
#     count_lines_twice(os.path.join(output_dir, common_output_file))
#     count_lines_twice(os.path.join(output_dir, missed_output_file))
#     count_lines_twice(os.path.join(output_dir, json_only_output_file))

#     verify_counts(updated_blob_files, json_src_values, common_paths, missed_paths, json_only_paths)

# if __name__ == "__main__":
#     main()
# ''''''