import os
import shutil
import google.colab import files

def rename_files_in_folder(root_folder):
    for dirpath, dirnames, filenames in os.walk(root_folder, topdown=False):
        for filename in filenames:
            if " " in filename:
                old_path = os.path.join(dirpath, filename)
                new_path = os.path.join(dirpath, filename.replace(" ", "_"))
                os.rename(old_path, new_path)
        
        for dirname in dirnames:
            if " " in dirname:
                old_path = os.path.join(dirpath, dirname)
                new_path = os.path.join(dirpath, dirname.replace(" ", "_"))
                os.rename(old_path, new_path)

def zip_and_download_folder(folder_path: str, zip_name: str = "downloaded_folder"):
    """
    Zips a folder and downloads it to your local machine.
    
    Parameters:
    - folder_path: Full path to the folder (e.g., "/content/project/data")
    - zip_name: Base name for the output zip file (default: "downloaded_folder")
    """
    zip_path = f"{zip_name}.zip"
    print(f"Zipping folder: {folder_path} → {zip_path}")
    shutil.make_archive(zip_name, 'zip', folder_path)
    files.download(zip_path)