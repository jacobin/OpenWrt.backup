from pathlib import Path

# Specify the directory path
directory_path = '/tmp/BackupEpodonios' # '.' refers to the current directory

# Use Path.iterdir() to list items, convert to a list, and sort using sorted()
# This creates a new sorted list of Path objects
sorted_files_and_dirs = sorted(list(Path(directory_path).iterdir()))

# To get just the names as strings:
sorted_names = sorted([item.name for item in Path(directory_path).iterdir()])

print("Sorted list of files and directories (Path objects):")
for item in sorted_files_and_dirs:
    print(item)

print("\nSorted list of names (strings):")
print(sorted_names)
