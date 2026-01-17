import os
import tarfile
import zstandard

def compress_folder_to_zstd_tar(source_dir, output_filename):
    # Ensure the output filename has the correct extension
    if not output_filename.endswith('.tar.zst'):
        output_filename += '.tar.zst'

    # Create a Zstandard compressor
    cctx = zstandard.ZstdCompressor(level=3) # Level 3 is the default

    # Open the output file for writing in binary mode
    with open(output_filename, 'wb') as ofh:
        # Create a stream writer for the compressor
        with cctx.stream_writer(ofh) as compressor_writer:
            # Open a tar file and write to the compressor's stream
            with tarfile.open(fileobj=compressor_writer, mode='w|') as tar:
                # Add the entire source directory to the tar archive
                # arcname=os.path.basename(source_dir) ensures the root folder name is kept inside the archive
                tar.add(source_dir, arcname=os.path.basename(source_dir))

    print(f"Folder '{source_dir}' successfully compressed to '{output_filename}'")

# Example Usage:
source_directory = '/tmp/BackupEpodonios' # Replace with your folder path
output_archive = '/tmp/compressed_archive.tar.zst'

# Create a dummy folder and files for testing (optional)
if not os.path.exists(source_directory):
    os.makedirs(source_directory)
    with open(os.path.join(source_directory, 'file1.txt'), 'w') as f:
        f.write("This is some data for file 1.")
    with open(os.path.join(source_directory, 'file2.txt'), 'w') as f:
        f.write("This is some data for file 2.")

compress_folder_to_zstd_tar(source_directory, output_archive)