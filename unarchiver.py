import os
import logging
from datetime import datetime
import subprocess

NUM_PER_PAGE = 10

# Logging setup
logging.basicConfig(filename='app.log', level=logging.DEBUG)

# Helper functions

# Recursively walk folder tree to find archives
def get_archives(folder, recursive, archive_type):
    archives = []   
    if archive_type == 'rar':
        exts = ['.rar']
    elif archive_type == 'zip':
        exts = ['.zip']
    else:
        exts = ['.rar', '.zip']
    
    if recursive:
        for root, dirs, files in os.walk(folder):
            # Check each file
            for file in files:
                if file.endswith(tuple(exts)):
                    # Append matching files to list
                    archive = os.path.join(root, file)
                    archives.append(archive)
    elif not recursive:
        for file in os.listdir(folder):
            if file.endswith(tuple(exts)): 
                archive = os.path.join(folder, file)
                archives.append(archive)
    # Return empty list if no archives found
    elif not archives:
        print("No archives found in the folder")
        exit()

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
    page = 0
    num_archives = len(archives)
    
    while True:

        start = page * NUM_PER_PAGE
        if start + NUM_PER_PAGE > num_archives:
            end = num_archives
        else:
            end = start + NUM_PER_PAGE

        for i, archive in enumerate(archives[start:end], start=start):
            date = datetime.fromtimestamp(get_modified_time(archive))
            print(f"{i + 1}. {archive} ({date.strftime('%Y-%m-%d')})")
        print()
        page += 1
        if end == num_archives:
            break
        input("Enter to continue...")
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
    elif archive.endswith('.rar'):
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
    archive_type = input("Find only .rar, only .zip, or both? (rar/zip/both): ")
    folder = input("Enter the path to the folder containing archives: ")
    if not os.path.exists(folder):
        print("Invalid folder.")
        main()
    print("Folder path:", folder)
    recursive = input("Search subdirectories? (y/n): ")
    if recursive.lower() == 'y':
        recursive = True
    else:
        recursive = False
    
    # Get archives
    archives = get_archives(folder, recursive, archive_type)
    
    # Filter multipart rars
    # if archive_type == 'rar':
    #    archives = filter_multiparts(archives)

    if len(archives) == 0:
        print("No archives found in the folder")
        print("Exiting program")
        logging.info("No archives found in the folder")
        logging.info("Exiting program")
        exit() 

    for archive in archives:
        archive_dir = os.path.dirname(archive)
        print("Extracting to: {} ".format(archive_dir))
        output = input("Enter alternative directory (or press enter):")

    if not output:
        output = archive_dir

    print("Output path:", output)

    if not os.path.exists(output):
        print("Invalid output path.")
        return
 
    display_archives(archives)

    selected = get_user_selection(archives)

    for archive in selected:
        try:
            extract_archive(archive, output)
        except Exception as e:
            logging.error(f"Error extracting {archive}: {e}")

if __name__ == '__main__':
    main()
