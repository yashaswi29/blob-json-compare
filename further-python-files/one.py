import os
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def retrieve_image_video_files_from_blob_storage(container_name, directory_prefix):
    """
    Retrieves all .png and .mp4 file paths from the specified Azure Blob Storage container 
    and saves the paths into a list. This searches recursively inside nested directories.
    
    Args:
        container_name (str): The name of the Azure Blob Storage container.
        directory_prefix (str): The directory inside the container to search for files.
    
    Returns:
        list: A list of paths to the .png and .mp4 files found in the blob storage.
    """
    # Step 1: Connect to the Azure Blob Storage using the connection string from the environment variables.
    connection_string = os.getenv("AZURE_CONNECTION_STRING")
    if not connection_string:
        print("Error: Connection string not found in environment variables.")
        return []

    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)

    # Step 2: Initialize an empty list to store the blob paths of .png and .mp4 files.
    blob_paths = []

    # Step 3: Use `list_blobs` to recursively list all blobs (files) starting from the given prefix (directory).
    blobs = container_client.list_blobs(name_starts_with=directory_prefix)

    # Step 4: Filter and collect the .png and .mp4 file paths found in the nested directories.
    print(f"Searching for .png and .mp4 files in the nested directory: '{directory_prefix}'")
    for blob in blobs:
        if blob.name.endswith('.png') or blob.name.endswith('.mp4'):
            # Print the full path of the image or video file
            # print(f"Found file: {blob.name}")
            blob_paths.append(blob.name)

    return blob_paths

def save_paths_to_file(file_name, paths):
    """
    Saves the list of file paths to a specified text file.
    
    Args:
        file_name (str): The name of the output text file.
        paths (list): The list of paths to save into the file.
    """
    with open(file_name, 'w') as file:
        for path in paths:
            file.write(f"{path}\n")

    print(f"File paths saved to: {file_name}")

def main():
    """
    Main function that triggers the search for image and video files inside the nested directories 
    of the Azure Blob Storage and saves them to a text file.
    """
    # Step 1: Get the blob container name and directory to search from environment variables.
    container_name = os.getenv("BLOB_CONTAINER")  # e.g., "storagev1"
    directory_prefix = "content/assets/"  # This is the directory inside the blob storage

    # Output text file where the found paths will be saved
    output_file = "found_paths.txt"

    if not container_name:
        print("Error: Blob container name not found in environment variables.")
        return

    # Step 2: Retrieve the .png and .mp4 files from the blob storage and save the paths.
    blob_files = retrieve_image_video_files_from_blob_storage(container_name, directory_prefix)

    if not blob_files:
        print("No .png or .mp4 files found in the specified directory.")
    else:
        # Step 3: Save the file paths to a text file.
        save_paths_to_file(output_file, blob_files)
        print(f"Total number of .png and .mp4 files found: {len(blob_files)}")

if __name__ == "__main__":
    # Execute the main function when the script is run.
    main()
