import os
import urllib.parse

def load_paths_from_file(file_path):
    """
    Loads all file paths from a text file into a list, decoding URL-encoded characters.
    
    Args:
        file_path (str): The path to the text file to read.
    
    Returns:
        list: A list of file paths from the text file, with URL-encoded characters decoded.
    """
    with open(file_path, 'r') as file:
        return [urllib.parse.unquote(line.strip()) for line in file]

def compare_paths(src_paths, found_paths):
    """
    Compares two lists of file paths to find missing and extra paths, after decoding URL-encoded characters.
    
    Args:
        src_paths (list): The list of expected paths (from src_path.txt).
        found_paths (list): The list of actual paths found (from found_image_video_paths.txt).
    
    Returns:
        tuple: Two lists - missing_paths and extra_paths.
    """
    # Decode URL-encoded characters for both sets of paths
    src_paths_set = set([urllib.parse.unquote(path.lower()) for path in src_paths])
    found_paths_set = set([urllib.parse.unquote(path.lower()) for path in found_paths])

    # Find missing paths (in src_paths but not in found_paths)
    missing_paths = list(src_paths_set - found_paths_set)

    # Find extra paths (in found_paths but not in src_paths)
    extra_paths = list(found_paths_set - src_paths_set)

    return missing_paths, extra_paths

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

    print(f"Paths saved to: {file_name}")

def main():
    """
    Main function that loads paths from the src_path and found_image_video_paths files,
    compares them, and saves missing and extra paths to separate files.
    """
    # File paths for comparison
    src_path_file = "src_path.txt"  # This file contains the total expected paths
    found_paths_file = "found_paths.txt"  # This file contains the paths found in Blob storage

    # Output files for the comparison results
    missing_output_file = "missing_paths.txt"
    extra_output_file = "extra_paths.txt"

    # Step 1: Load the paths from both files
    src_paths = load_paths_from_file(src_path_file)
    found_paths = load_paths_from_file(found_paths_file)

    # Step 2: Compare the lists to find missing and extra paths
    missing_paths, extra_paths = compare_paths(src_paths, found_paths)

    # Step 3: Save the missing and extra paths to text files
    save_paths_to_file(missing_output_file, missing_paths)
    save_paths_to_file(extra_output_file, extra_paths)

    print(f"Comparison complete. Missing paths saved to '{missing_output_file}', and extra paths saved to '{extra_output_file}'.")

if __name__ == "__main__":
    # Execute the main function when the script is run
    main()
