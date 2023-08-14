import os
import logging
from datetime import datetime
import subprocess

# Logging setup
logging.basicConfig(filename='app.log', level=logging.DEBUG)

# Helper functions

def get_archives(folder, recursive=False):
    archives = []
    if not archives:
        print("No archives found in the folder")
    elif recursive:
        for root, dirs, files in os.walk(folder):
            for file in files:
                if file.endswith('.rar') or file.endswith('.zip'):
                    archive = os.path.join(root, file)
                    archives.append(archive)
    else:
        for file in os.listdir(folder):
            if file.endswith(('.rar', '.zip')): 
                archive = os.path.join(folder, file)
                archives.append(archive)

    return archives

def get_modified_time(archive):
    return os.path.getmtime(archive)

def filter_multiparts(archives):
    filtered = [] 
    seen = set()
    for archive in archives:
        name = os.path.basename(archive)
        base = ''
        if '.r' in name:
            base = name.split('.r')[0]
        if base not in seen:
            seen.add(base)
            # Check if it's the first file
            if name.endswith('.r01') or name.endswith('.r001'):
                filtered.append(archive)
        else:
            filtered.append(archive)
    return filtered

def display_archives(archives):
    archives.sort(key=get_modified_time)
    print("Archives:")
    for i, archive in enumerate(archives):
        date = datetime.fromtimestamp(get_modified_time(archive))
        print(f"{i + 1}. {archive} ({date.strftime('%Y-%m-%d')})")
    print("0. exit")


def get_user_selection(archives):
    while True:
        input_str = input("Enter archive numbers (comma separated) or 0 to exit: ")
        if input_str == '0':
            print("Exiting program")
            return []
        
        selections = input_str.split(',')

        try:
            indexes = [int(x) - 1 for x in selections]
            selected = [archives[i] for i in indexes]
            return selected
        except ValueError:
            print("Invalid input, please enter numbers")

def is_archive_password_protected(archive):
    """Check if an archive file is password protected."""
    if archive.endswith('.rar'):
        result = subprocess.run(['unrar', 'lt', archive], stdout=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        return "Password protected" in output
    return False

def extract_archive(archive, output):
    """
    Extract the provided archive file to the specified output directory.
    Supports .rar and .zip archive formats. Prompt for password if needed.
    """
    
    total_size = os.path.getsize(archive)
    extracted_size = 0

    with open(archive, 'rb') as f:

        print("Extracting...", end='')

        while True:
            chunk = f.read(1048576)
            if not chunk:
                break

            extracted_size += len(chunk)

            percent = extracted_size / total_size * 100
            print("\r[%-20s] %.2f%%" % ('='*int(percent/5), percent), end='')
    if archive.endswith('.rar') and is_archive_password_protected(archive):
        password = input(f"Enter password for {archive}: ")
        extraction_command = ['unrar', 'x', '-p' + password, archive, output]
    if archive.endswith('.rar'):
        extraction_command = ['unrar', 'x', archive, output]
    elif archive.endswith('.zip'):
        extraction_command = ['unzip', archive, '-d', output]
    else:
        print(f"Unsupported archive format: {archive}")
        return

    try:
        subprocess.run(extraction_command, check=True)
        logging.info(f'Extracted {archive} to {output}')
    except subprocess.CalledProcessError as e:
        logging.error(f"Error extracting {archive}: {e}")
    print("\nDone!")

def main():
    folder = input("Enter the path to the folder containing archives: ")
    print("Folder path:", folder)
    recursive = input("Search subdirectories? (y/n): ")
    if recursive.lower() == 'y':
        recursive = True
    else:
        recursive = False
    
    archives = get_archives(folder, recursive)
    if len(archives) == 0:
        exit() 

    output = input("Enter the path to the output directory: ")
    print("Output path:", output)

    if not os.path.exists(folder) or not os.path.exists(output):
        print("Invalid folder or output path.")
        return

    archives = get_archives(folder)
    archives = filter_multiparts(archives)

    display_archives(archives)

    selected = get_user_selection(archives)

    for archive in selected:
        try:
            extract_archive(archive, output)
        except Exception as e:
            logging.error(f"Error extracting {archive}: {e}")

if __name__ == '__main__':
    main()
