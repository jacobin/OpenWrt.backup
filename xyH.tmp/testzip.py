import os
import zipfile

def create_zip_from_folder(folder_path, zip_name):
    # Open the zip file in write mode with DEFLATED compression
    with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as zipf:
        # Walk through the directory tree
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                # Construct the full file path
                file_path = os.path.join(root, file)
                # Add the file to the zip, specifying the relative path
                # so the internal archive structure mirrors the folder structure
                zipf.write(file_path, os.path.relpath(file_path, start=folder_path))

# Example usage:
create_zip_from_folder("/xyH.tmp/Epodonios", "backup88888888.zip")
print("Folder zipped using zipfile module.")