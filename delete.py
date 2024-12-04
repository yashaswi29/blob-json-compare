# vim .env 
import os
from azure.storage.blob import BlobServiceClient, ContainerClient
from dotenv import load_dotenv

load_dotenv()

AZURE_CONNECTION_STRING = os.getenv("AZURE_CONNECTION_STRING")
BLOB_CONTAINER = os.getenv("BLOB_CONTAINER")

def delete_blob_directory(container_client, directory_path):
    
    blobs = container_client.list_blobs(name_starts_with=directory_path)
    for blob in blobs:
        print(f"Deleting blob: {blob.name}")
        container_client.delete_blob(blob.name)

def delete_directory(path):
    
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
    container_client = blob_service_client.get_container_client(BLOB_CONTAINER)

    delete_blob_directory(container_client, path)

def list_blobs_in_container(container_name):
    connection_string = os.getenv("AZURE_CONNECTION_STRING")
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)
    
    blobs = container_client.list_blobs()
    for blob in blobs:
        print(blob.name)

list_blobs_in_container("localcontent")


if __name__ == "__main__":
    paths_to_delete = [ 
    # provide a list of directory paths or followed by ' , ' [comma]
        "content/assets/images/india/Delete/DL2",  
    ]

    for path in paths_to_delete:
        delete_directory(path)