"""
File utility functions for cross-platform file operations.
"""

import subprocess
import sys


def open_file_non_blocking(file_path: str):
    """Open a file in the default application in a non-blocking way."""
    try:
        if sys.platform == 'darwin':  # macOS
            subprocess.Popen(['open', file_path])
        elif sys.platform == 'linux':  # Linux
            subprocess.Popen(['xdg-open', file_path])
        elif sys.platform == 'win32':  # Windows
            subprocess.Popen(['start', file_path], shell=True)
        else:
            print(f"Unsupported platform: {sys.platform}. Please open the file manually: {file_path}")
            return False
        return True
    except Exception as e:
        print(f"Could not open file automatically: {e}")
        print(f"Please open manually: {file_path}")
        return False