import os
import shutil

def clear_directory_if_exists(directory_path):
  #if directory exists
  if os.path.exists(directory_path):
    # Delete all files (not folders) in the directory
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)

    print("✅ All files deleted from generated_output.")
  else:
    print("✅ The generated_output directory does not exist. No worries!")