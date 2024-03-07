import os
import zipfile
import tkinter as tk
from tkinter import filedialog
from tkinter import simpledialog
import contextlib
import tempfile

@contextlib.contextmanager
def open_zip_file(file_path, mode='r'):
    with zipfile.ZipFile(file_path, mode) as zip_file:
        yield zip_file

def create_dtx(dtx_filename):
    with zipfile.ZipFile(dtx_filename, 'w') as zip_file:
        # Create an empty .ids file
        ids_filename = '.ids'
        zip_file.writestr(ids_filename, '')

def update_ids(zip_file_path):
    ids_filename = '.ids'
    temp_zip_path = ""

    try:
        # Use zipfile.ZipFile directly for clarity and avoid potential issues
        with open_zip_file(zip_file_path, 'r') as original_zip:
            original_contents = {item.filename: original_zip.read(item.filename) for item in original_zip.infolist()}

        updated_contents = {}
        for i, filename in enumerate(original_contents.keys()):
            if filename != ids_filename:
                updated_contents[f"{i + 1}: {filename}"] = original_contents[filename]

        # Create a temporary file using tempfile for safer management
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_zip_path = temp_file.name
            with zipfile.ZipFile(temp_zip_path, 'w') as temp_zip:
                for filename, data in updated_contents.items():
                    temp_zip.writestr(filename, data)

        # Replace the original zip with the temporary one atomically
        try:
            os.replace(temp_zip_path, zip_file_path)
        except FileNotFoundError:
            print("Error: Original file not found. Skipping replacement.")
        except PermissionError:
            print("Error: Permission denied. File may be in use. Try closing other applications that might be accessing the file.")
            return

    except Exception as e:
        print(f"Error updating IDs: {e}")

        # Ensure temporary file is deleted even if exceptions occur
        if os.path.exists(temp_zip_path):
            os.remove(temp_zip_path)

    # Open the zip file again in write mode before returning
    with open_zip_file(zip_file_path, 'a'):
        pass

def remove_file(zip_file_path, file_name):
    temp_zip_path = 'temp_data.dtx'
    ZIP_FILE_PATH = 'data.dtx'

    with open_zip_file(ZIP_FILE_PATH, 'r') as zip_file, zipfile.ZipFile(temp_zip_path, 'w') as temp_zip:
        duplicate_warning_shown = False

        for item in zip_file.infolist():
            if item.filename != file_name and item.filename != '.ids':
                data = zip_file.read(item.filename)
                temp_zip.writestr(item, data)

                if item.filename == os.path.basename(file_name) and not duplicate_warning_shown:
                    print(f"Warning: Duplicate name found ('{item.filename}') in the zip file.")
                    duplicate_warning_shown = True

    os.remove(ZIP_FILE_PATH)
    os.rename(temp_zip_path, ZIP_FILE_PATH)

    # Update the .ids file
    update_ids(ZIP_FILE_PATH)

def add_file(zip_file_path):
    file_path = filedialog.askopenfilename(title="Select a file to add")

    if file_path:
        file_name = os.path.basename(file_path)
        with open_zip_file(zip_file_path, 'a') as zip_file:
            zip_file.write(file_path, file_name)

        # Update the .ids file
        update_ids(zip_file_path)

def save_file(zip_file_path, file_id):
    file_name = simpledialog.askstring("Save File", "Enter the file name to save as (including extension):")

    if file_name:
        with open_zip_file(zip_file_path, 'r') as zip_file:
            file_data = zip_file.read(file_id).decode('utf-8')

        with open(file_name, 'w') as save_file:
            save_file.write(file_data)

def print_files(zip_file_path):
    with open_zip_file(zip_file_path, 'r') as zip_file:
        print("\nFiles inside the archive:")
        for item in zip_file.infolist():
            if item.filename != '.ids':
                print(f"{item.filename} ({item.file_size} bytes)")

def main():
    DTX_FILE_PATH = 'data.dtx'

    if not os.path.exists(DTX_FILE_PATH):
        create_dtx(DTX_FILE_PATH)

    root = tk.Tk()
    root.withdraw()  # Hide the main window

    with open_zip_file(DTX_FILE_PATH, 'a') as zip_file:
        while True:
            print("\nOptions:")
            print("1. Add File")
            print("2. Remove File")
            print("3. Save File")
            print("4. Print Files")
            print("5. Exit")

            choice = input("Enter your choice (1/2/3/4/5): ")

            if choice == '1':
                add_file(DTX_FILE_PATH)
            elif choice == '2':
                file_name = simpledialog.askstring("Remove File", "Enter the file name to remove (case-sensitive):")
                if file_name:
                    remove_file(DTX_FILE_PATH, file_name)
                    print(f"File '{file_name}' removed successfully.")
            elif choice == '3':
                file_id = simpledialog.askinteger("Save File", "Enter the file ID to save:")
                if file_id:
                    save_file(DTX_FILE_PATH, file_id)
                    print(f"File saved successfully.")
            elif choice == '4':
                print_files(DTX_FILE_PATH)
            elif choice == '5':
                break
            else:
                print("Invalid choice. Please enter a valid option.")

if __name__ == "__main__":
    main()
