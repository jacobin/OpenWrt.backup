###############################################################################
# https://www.google.com/search?q=python+compress+a+folder+best+rates
import shutil
import os

###############################################################################
def compress_folder_best_rate(source_dir, output_filename):
    """
    Compresses a folder to a .tar.xz archive using LZMA (best compression).

    Args:
        source_dir (str): The path to the folder to compress.
        output_filename (str): The name of the output archive (without extension).
    """
    # 'xztar' uses LZMA compression, which offers the best ratio
    try:
        output_path = shutil.make_archive(
            output_filename,
            'xztar', # Format: tar archive with xz compression
            root_dir=source_dir
        )
        print(f"Archive created at: {output_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage:
# Assuming a folder named 'my_data' in the current directory
# This will create an archive named 'my_data.tar.xz'
# compress_folder_best_rate('my_data', 'my_data')

###############################################################################
compress_folder_best_rate('/xyH.tmp/BackupEpodonios', '/xyH.tmp/tmptmp.zip')