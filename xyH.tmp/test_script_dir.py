from pathlib import Path
import os # os is still needed if you want to perform further OS interaction

script_dir = Path(__file__).resolve().parent
print(f"Script directory: {script_dir}")

# Example of accessing a file relative to the script's directory
data_file_path = script_dir / "data" / "my_file.txt"
# or
data_file_path_os = os.path.join(script_dir, "data", "my_file.txt")

print(data_file_path)
print(data_file_path_os)
