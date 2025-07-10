import pytest
from unittest.mock import patch, MagicMock
import subprocess
from src.git import (
    _get_git_status,
    _find_past_day_log_files,
    _add_files_to_git,
    _commit_files,
    _pull_and_push,
    push_logs_to_git
)


class TestGetGitStatus:
    """Test cases for _get_git_status function."""
    
    @patch('src.git.subprocess.run')
    def test_get_git_status_success(self, mock_run):
        mock_result = MagicMock()
        mock_result.stdout = " M logs/test-hostname/connectivity_log_20250708.txt\n?? logs/test-hostname/connectivity_log_20250707.txt\n"
        mock_run.return_value = mock_result
        
        result = _get_git_status("test-hostname")
        
        assert result == "M logs/test-hostname/connectivity_log_20250708.txt\n?? logs/test-hostname/connectivity_log_20250707.txt"
        mock_run.assert_called_once_with(
            ['git', 'status', '--porcelain', 'logs/test-hostname/'],
            check=True, capture_output=True, text=True
        )
    
    @patch('src.git.subprocess.run')
    @patch('builtins.print')
    def test_get_git_status_called_process_error(self, mock_print, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(1, 'git')
        
        result = _get_git_status("test-hostname")
        
        assert result is None
        mock_print.assert_called_once()
        assert "Git status check failed" in mock_print.call_args[0][0]
    
    @patch('src.git.subprocess.run')
    @patch('builtins.print')
    def test_get_git_status_file_not_found(self, mock_print, mock_run):
        mock_run.side_effect = FileNotFoundError()
        
        result = _get_git_status("test-hostname")
        
        assert result is None
        mock_print.assert_called_once_with("DEBUG: Git command not found - skipping log push")
    
    @patch('src.git.subprocess.run')
    def test_get_git_status_empty_output(self, mock_run):
        mock_result = MagicMock()
        mock_result.stdout = "   \n  \n"
        mock_run.return_value = mock_result
        
        result = _get_git_status("test-hostname")
        
        assert result == ""


class TestFindPastDayLogFiles:
    """Test cases for _find_past_day_log_files function."""
    
    def test_find_past_day_log_files_success(self):
        git_output = " M logs/test-hostname/connectivity_log_20250708.txt\n?? logs/test-hostname/connectivity_log_20250707.txt\n M logs/test-hostname/connectivity_log_20250709.txt"
        hostname = "test-hostname"
        today_file = "logs/test-hostname/connectivity_log_20250709.txt"
        
        result = _find_past_day_log_files(git_output, hostname, today_file)
        
        expected = [
            "logs/test-hostname/connectivity_log_20250708.txt",
            "logs/test-hostname/connectivity_log_20250707.txt"
        ]
        assert result == expected
    
    def test_find_past_day_log_files_excludes_today(self):
        git_output = " M logs/test-hostname/connectivity_log_20250709.txt"
        hostname = "test-hostname"
        today_file = "logs/test-hostname/connectivity_log_20250709.txt"
        
        result = _find_past_day_log_files(git_output, hostname, today_file)
        
        assert result == []
    
    def test_find_past_day_log_files_excludes_non_log_files(self):
        git_output = " M logs/test-hostname/connectivity_log_20250708.txt\n M logs/test-hostname/other_file.txt\n M README.md"
        hostname = "test-hostname"
        today_file = "logs/test-hostname/connectivity_log_20250709.txt"
        
        result = _find_past_day_log_files(git_output, hostname, today_file)
        
        assert result == ["logs/test-hostname/connectivity_log_20250708.txt"]
    
    def test_find_past_day_log_files_empty_input(self):
        result = _find_past_day_log_files("", "test-hostname", "logs/test-hostname/connectivity_log_20250709.txt")
        assert result == []
    
    def test_find_past_day_log_files_different_hostname(self):
        git_output = " M logs/other-hostname/connectivity_log_20250708.txt"
        hostname = "test-hostname"
        today_file = "logs/test-hostname/connectivity_log_20250709.txt"
        
        result = _find_past_day_log_files(git_output, hostname, today_file)
        
        assert result == []


class TestAddFilesToGit:
    """Test cases for _add_files_to_git function."""
    
    @patch('src.git.subprocess.run')
    def test_add_files_to_git_success(self, mock_run):
        files = ["logs/test-hostname/connectivity_log_20250708.txt", "logs/test-hostname/connectivity_log_20250707.txt"]
        
        result = _add_files_to_git(files)
        
        assert result is True
        assert mock_run.call_count == 2
        mock_run.assert_any_call(['git', 'add', 'logs/test-hostname/connectivity_log_20250708.txt'], check=True, capture_output=True)
        mock_run.assert_any_call(['git', 'add', 'logs/test-hostname/connectivity_log_20250707.txt'], check=True, capture_output=True)
    
    @patch('src.git.subprocess.run')
    @patch('builtins.print')
    def test_add_files_to_git_failure(self, mock_print, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(1, 'git')
        files = ["logs/test-hostname/connectivity_log_20250708.txt"]
        
        result = _add_files_to_git(files)
        
        assert result is False
        mock_print.assert_called_once()
        assert "Git add failed" in mock_print.call_args[0][0]
    
    @patch('src.git.subprocess.run')
    def test_add_files_to_git_empty_list(self, mock_run):
        result = _add_files_to_git([])
        
        assert result is True
        mock_run.assert_not_called()


class TestCommitFiles:
    """Test cases for _commit_files function."""
    
    @patch('src.git.subprocess.run')
    def test_commit_files_success(self, mock_run):
        hostname = "test-hostname"
        
        result = _commit_files(hostname)
        
        assert result is True
        mock_run.assert_called_once_with(
            ['git', 'commit', '-m', 'Add connectivity log entries for past days - test-hostname'],
            check=True, capture_output=True
        )
    
    @patch('src.git.subprocess.run')
    @patch('builtins.print')
    def test_commit_files_failure(self, mock_print, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(1, 'git')
        hostname = "test-hostname"
        
        result = _commit_files(hostname)
        
        assert result is False
        mock_print.assert_called_once()
        assert "Git commit failed" in mock_print.call_args[0][0]


class TestPullAndPush:
    """Test cases for _pull_and_push function."""
    
    @patch('src.git.subprocess.run')
    @patch('builtins.print')
    def test_pull_and_push_success(self, mock_print, mock_run):
        files_count = 2
        
        result = _pull_and_push(files_count)
        
        assert result is True
        assert mock_run.call_count == 2
        mock_run.assert_any_call(['git', 'pull', '--rebase'], check=True, capture_output=True)
        mock_run.assert_any_call(['git', 'push'], check=True, capture_output=True)
        mock_print.assert_called_once_with("DEBUG: Successfully pushed 2 past day log files")
    
    @patch('src.git.subprocess.run')
    @patch('builtins.print')
    def test_pull_and_push_pull_fails_push_succeeds(self, mock_print, mock_run):
        # First call (pull) fails, second call (push) succeeds
        mock_run.side_effect = [subprocess.CalledProcessError(1, 'git'), None]
        files_count = 1
        
        result = _pull_and_push(files_count)
        
        assert result is True
        assert mock_run.call_count == 2
        assert mock_print.call_count == 2
        assert "Git pull failed" in mock_print.call_args_list[0][0][0]
        assert "Successfully pushed 1 past day log files" in mock_print.call_args_list[1][0][0]
    
    @patch('src.git.subprocess.run')
    @patch('builtins.print')
    def test_pull_and_push_push_fails(self, mock_print, mock_run):
        # First call (pull) succeeds, second call (push) fails
        mock_run.side_effect = [None, subprocess.CalledProcessError(1, 'git')]
        files_count = 1
        
        result = _pull_and_push(files_count)
        
        assert result is False
        assert mock_run.call_count == 2
        mock_print.assert_called_once()
        assert "Git push failed" in mock_print.call_args[0][0]


class TestPushLogsToGit:
    """Test cases for push_logs_to_git function."""
    
    @patch('src.git.socket.gethostname')
    @patch('src.git.datetime.datetime')
    @patch('src.git._get_git_status')
    @patch('src.git._find_past_day_log_files')
    @patch('src.git._add_files_to_git')
    @patch('src.git._commit_files')
    @patch('src.git._pull_and_push')
    @patch('builtins.print')
    def test_push_logs_to_git_full_success(self, mock_print, mock_pull_push, mock_commit, 
                                          mock_add, mock_find, mock_git_status, 
                                          mock_datetime, mock_hostname):
        # Setup mocks
        mock_hostname.return_value = "test-hostname"
        mock_datetime.now.return_value.strftime.return_value = "20250709"
        mock_git_status.return_value = " M logs/test-hostname/connectivity_log_20250708.txt"
        mock_find.return_value = ["logs/test-hostname/connectivity_log_20250708.txt"]
        mock_add.return_value = True
        mock_commit.return_value = True
        mock_pull_push.return_value = True
        
        push_logs_to_git()
        
        # Verify all functions were called
        mock_git_status.assert_called_once_with("test-hostname")
        mock_find.assert_called_once_with(
            " M logs/test-hostname/connectivity_log_20250708.txt",
            "test-hostname",
            "logs/test-hostname/connectivity_log_20250709.txt"
        )
        mock_add.assert_called_once_with(["logs/test-hostname/connectivity_log_20250708.txt"])
        mock_commit.assert_called_once_with("test-hostname")
        mock_pull_push.assert_called_once_with(1)
        mock_print.assert_called_once()
        assert "Found 1 past day log files to push" in mock_print.call_args[0][0]
    
    @patch('src.git._get_git_status')
    def test_push_logs_to_git_no_git_status(self, mock_git_status):
        mock_git_status.return_value = None
        
        # Should return early without doing anything
        push_logs_to_git()
        
        mock_git_status.assert_called_once()
    
    @patch('src.git.socket.gethostname')
    @patch('src.git.datetime.datetime')
    @patch('src.git._get_git_status')
    @patch('src.git._find_past_day_log_files')
    def test_push_logs_to_git_no_files_to_add(self, mock_find, mock_git_status, 
                                             mock_datetime, mock_hostname):
        mock_hostname.return_value = "test-hostname"
        mock_datetime.now.return_value.strftime.return_value = "20250709"
        mock_git_status.return_value = " M some_output"
        mock_find.return_value = []
        
        # Should return early when no files to add
        push_logs_to_git()
        
        mock_find.assert_called_once()
    
    @patch('src.git.socket.gethostname')
    @patch('src.git.datetime.datetime')
    @patch('src.git._get_git_status')
    @patch('src.git._find_past_day_log_files')
    @patch('src.git._add_files_to_git')
    @patch('builtins.print')
    def test_push_logs_to_git_add_fails(self, mock_print, mock_add, mock_find, 
                                       mock_git_status, mock_datetime, mock_hostname):
        mock_hostname.return_value = "test-hostname"
        mock_datetime.now.return_value.strftime.return_value = "20250709"
        mock_git_status.return_value = " M logs/test-hostname/connectivity_log_20250708.txt"
        mock_find.return_value = ["logs/test-hostname/connectivity_log_20250708.txt"]
        mock_add.return_value = False
        
        # Should return early when add fails
        push_logs_to_git()
        
        mock_add.assert_called_once()
    
    @patch('src.git.socket.gethostname')
    @patch('builtins.print')
    def test_push_logs_to_git_unexpected_exception(self, mock_print, mock_hostname):
        mock_hostname.side_effect = Exception("Unexpected error")
        
        push_logs_to_git()
        
        mock_print.assert_called_once()
        assert "Unexpected error in push_logs_to_git()" in mock_print.call_args[0][0]