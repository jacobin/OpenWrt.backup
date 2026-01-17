import tarfile
import os

folder_to_compress = '/tmp/BackupEpodonios' # The folder you want to archive
output_filename = "/tmp/archive.tar.gz" # Output name with .gz for gzip

# Ensure the folder exists (optional, but good practice)
if not os.path.exists(folder_to_compress):
    os.makedirs(folder_to_compress)
    # Add some dummy files for testing
    with open(os.path.join(folder_to_compress, "file1.txt"), "w") as f:
        f.write("Hello World")
    with open(os.path.join(folder_to_compress, "file2.txt"), "w") as f:
        f.write("Another file")

# Open the tar file in write mode with gzip compression ('w:gz')
with tarfile.open(output_filename, "w:xz") as tar:
    # Add the entire folder, including subdirectories and files
    # arcname sets the name inside the archive (removes the top folder name if needed)
    tar.add(folder_to_compress, arcname=os.path.basename(folder_to_compress))

print(f"Successfully created {output_filename}")