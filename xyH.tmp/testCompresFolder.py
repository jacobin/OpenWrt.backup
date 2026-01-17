###############################################################################
import os
import shutil
import zipfile
import tarfile

###############################################################################
# https://www.google.com/search?q=python+compress+a+folder&pws=0&gl=us&gws_rd=cr
def zipfile_compress_folder( folder_path, zip_name ):
    with zipfile.ZipFile( zip_name, "w", compression=zipfile.ZIP_LZMA, compresslevel=9 ) as zipf:
        for root, dirs, files in os.walk( folder_path ):
            for file in files:
                file_path = os.path.join( root, file )
                zipf.write( file_path, os.path.relpath( file_path, start = folder_path ) )

###############################################################################
# https://www.google.com/search?q=python+compress+a+folder+best+rates
def shutil_compress_folder( source_dir, output_filename ):
    # 'xztar' uses LZMA compression, which offers the best ratio
    output_filename = output_filename.removesuffix( '.tar.xz' )
    try:
        output_path = shutil.make_archive(
            output_filename,
            'xztar', # Format: tar archive with xz compression
            root_dir=source_dir
        )
    except Exception as e:
        print(f"An error occurred: {e}")

###############################################################################
def tarfile_compress_folder( folder_to_compress, output_filename ):
    with tarfile.open(output_filename, "w:xz") as tar:
        tar.add( folder_to_compress,  arcname=os.path.basename(folder_to_compress))


###############################################################################
shutil_compress_folder( '/tmp/BackupEpodonios', '/tmp/shutil_archive' )
zipfile_compress_folder( '/tmp/BackupEpodonios', '/tmp/zipfile_archive.zip' )
tarfile_compress_folder( '/tmp/BackupEpodonios', '/tmp/tarfile_archive.tar.xz' )
