CopyGuard
Overview
CopyGuard is a Python script designed to copy files from a source directory to a destination directory while logging any errors encountered during the process. It continues execution even if errors occur, making it useful for handling large file transfers with potential issues.
Features

Copies files while preserving metadata (e.g., timestamps).
Ignores directories and logs only file-related errors.
Creates a log file (copy_errors.log) with detailed error messages.
Provides console feedback on the copying process.

Prerequisites

Python 3.x
No additional libraries required (uses built-in shutil, os, and logging modules)

Installation

Clone the repository or download the copy_files_with_log.py script.
Ensure Python is installed on your system.

Usage

Edit the script to set your source_dir and dest_dir paths.
Example: Replace "path/to/source/folder" and "path/to/dest/folder" with actual paths.


Run the script:python copy_files_with_log.py


Check the console for progress and copy_errors.log for any errors.

Logging

Errors are logged to copy_errors.log in the script's directory.
Log format: YYYY-MM-DD HH:MM:SS - Error message

Contributing
Feel free to fork this project and submit pull requests for improvements.
License
This project is open-source. See the LICENSE file for details (if applicable).
