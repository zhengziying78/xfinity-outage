import subprocess
import socket
import datetime


def _get_git_status(hostname):
    """Get git status for hostname log directory."""
    try:
        result = subprocess.run(['git', 'status', '--porcelain', f'logs/{hostname}/'], 
                              check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"DEBUG: Git status check failed: {e}")
        return None
    except FileNotFoundError:
        print("DEBUG: Git command not found - skipping log push")
        return None


def _find_past_day_log_files(git_status_output, hostname, today_file):
    """Find log files from past days that have changes."""
    files_to_add = []
    
    for line in git_status_output.split('\n'):
        if line.strip():
            # Parse git status output (format: " M filename" or "?? filename")
            # Split on whitespace and take the last part as the filename
            parts = line.split()
            if len(parts) < 2:
                continue
            file_path = parts[-1]
            
            # Only process connectivity log files, not today's file
            if (file_path.startswith(f'logs/{hostname}/connectivity_log_') and 
                file_path.endswith('.txt') and 
                file_path != today_file):
                files_to_add.append(file_path)
    
    return files_to_add


def _add_files_to_git(files_to_add):
    """Add files to git staging area."""
    try:
        for file_path in files_to_add:
            subprocess.run(['git', 'add', file_path], check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"DEBUG: Git add failed: {e}")
        return False


def _commit_files(hostname):
    """Commit staged files."""
    try:
        commit_message = f"Add connectivity log entries for past days - {hostname}"
        subprocess.run(['git', 'commit', '-m', commit_message], check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"DEBUG: Git commit failed (possibly no changes): {e}")
        return False


def _pull_and_push(files_count):
    """Pull with rebase and push to remote."""
    # Pull with rebase to avoid merge conflicts
    try:
        subprocess.run(['git', 'pull', '--rebase'], check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print(f"DEBUG: Git pull failed (possibly network issue): {e}")
        # Continue anyway - we'll try to push
    
    # Push to remote
    try:
        subprocess.run(['git', 'push'], check=True, capture_output=True)
        print(f"DEBUG: Successfully pushed {files_count} past day log files")
        return True
    except subprocess.CalledProcessError as e:
        print(f"DEBUG: Git push failed (possibly network issue): {e}")
        return False


def push_logs_to_git():
    """Push log changes to remote repository for past days only (not today's file)."""
    try:
        hostname = socket.gethostname()
        today_date = datetime.datetime.now().strftime('%Y%m%d')
        today_file = f"logs/{hostname}/connectivity_log_{today_date}.txt"
        
        # Get git status for hostname log directory
        git_status_output = _get_git_status(hostname)
        if not git_status_output:
            return
        
        # Find past day log files with changes
        files_to_add = _find_past_day_log_files(git_status_output, hostname, today_file)
        if not files_to_add:
            return
        
        print(f"DEBUG: Found {len(files_to_add)} past day log files to push: {files_to_add}")
        
        # Add files to git
        if not _add_files_to_git(files_to_add):
            return
        
        # Commit files
        if not _commit_files(hostname):
            return
        
        # Pull and push
        _pull_and_push(len(files_to_add))
        
    except Exception as e:
        # Catch any other unexpected errors
        print(f"DEBUG: Unexpected error in push_logs_to_git(): {e}")
        # Never let this function crash the main script