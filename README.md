# Python script to extract zip and rar files
## working on it - not for production

Here is a high-level summary of what this Python script does:

- It provides functionality to extract archive files (.rar, .zip) from a source folder to a destination folder.

- It has proper logging set up to log to a file app.log.

- The main() function ties together the helper functions in a workflow:

  1. Get list of archives in source folder
  2. Filter multi-part archives to only show first file
  3. Display list of archives with dates 
  4. Prompt user to select archives to extract
  5. Extract selected archives to destination folder
  
- Helper functions modularize the tasks:

  - get_archives(): finds all .rar files recursively
  - filter_multiparts(): filters to only first multi-part file
  - display_archives(): prints archive list nicely
  - get_user_selection(): gets user input on archives to extract
  - extract_archive(): extracts an archive, handles passwords

- Handles password protected archives by prompting for password

Some ways it could be improved further:

- Add support for more archive types (.7z, .tar, etc)
- Allow user to choose extract location instead of hardcoded
- More validation before extracting archives
- Use more specific exception handling
