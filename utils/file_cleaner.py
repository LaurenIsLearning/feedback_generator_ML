import os

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
