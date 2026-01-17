import os
import zipfile

###############################################################################
# https://www.google.com/search?q=python+compress+a+folder&pws=0&gl=us&gws_rd=cr
def create_zip_from_folder( folder_path, zip_name ):
    # Open the zip file in write mode with DEFLATED compression
    with zipfile.ZipFile( zip_name, "w", compression=zipfile.ZIP_LZMA, compresslevel=9 ) as zipf:
        # Walk through the directory tree
        for root, dirs, files in os.walk( folder_path ):
            for file in files:
                # Construct the full file path
                file_path = os.path.join( root, file )
                # Add the file to the zip, specifying the relative path
                # so the internal archive structure mirrors the folder structure
                zipf.write( file_path, os.path.relpath( file_path, start = folder_path ) )

# Example Usage:
source_directory = '/tmp/BackupEpodonios' # Replace with your folder path
output_archive = '/tmp/archive.zip'

# Create a dummy folder and files for testing (optional)
if not os.path.exists(source_directory):
    os.makedirs(source_directory)
    with open(os.path.join(source_directory, 'file1.txt'), 'w') as f:
        f.write("This is some data for file 1.")
    with open(os.path.join(source_directory, 'file2.txt'), 'w') as f:
        f.write("This is some data for file 2.")

create_zip_from_folder(source_directory, output_archive)