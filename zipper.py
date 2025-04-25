import os
import zipfile


def zip_project_folder(output_filename):
    # Set the folder you want to zip
    folder_to_zip = '.'

    # Files to ignore (optional)
    ignore_files = {'.replit', '.config', 'venv', '__pycache__'}

    with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_to_zip):
            # Skip ignored folders
            dirs[:] = [d for d in dirs if d not in ignore_files]
            for file in files:
                if file not in ignore_files:
                    filepath = os.path.join(root, file)
                    # Keep the file structure clean
                    zipf.write(filepath,
                               os.path.relpath(filepath, folder_to_zip))


zip_project_folder('IndiaQuant_Project.zip')
print("✅ Project zipped successfully!")
