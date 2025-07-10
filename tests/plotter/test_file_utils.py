import pytest
from unittest.mock import patch, MagicMock, call
import sys
from src.libs.plotter.file_utils import open_file_non_blocking


class TestOpenFileNonBlocking:
    """Test cases for open_file_non_blocking function."""
    
    @patch('src.libs.plotter.file_utils.subprocess.Popen')
    @patch('src.libs.plotter.file_utils.sys.platform', 'darwin')
    @patch('builtins.print')
    def test_open_file_non_blocking_macos_success(self, mock_print, mock_popen):
        mock_process = MagicMock()
        mock_popen.return_value = mock_process
        
        result = open_file_non_blocking('/path/to/test.png')
        
        assert result is True
        mock_popen.assert_called_once_with(['open', '/path/to/test.png'])
        mock_print.assert_not_called()
    
    @patch('src.libs.plotter.file_utils.subprocess.Popen')
    @patch('src.libs.plotter.file_utils.sys.platform', 'linux')
    @patch('builtins.print')
    def test_open_file_non_blocking_linux_success(self, mock_print, mock_popen):
        mock_process = MagicMock()
        mock_popen.return_value = mock_process
        
        result = open_file_non_blocking('/path/to/test.png')
        
        assert result is True
        mock_popen.assert_called_once_with(['xdg-open', '/path/to/test.png'])
        mock_print.assert_not_called()
    
    @patch('src.libs.plotter.file_utils.subprocess.Popen')
    @patch('src.libs.plotter.file_utils.sys.platform', 'win32')
    @patch('builtins.print')
    def test_open_file_non_blocking_windows_success(self, mock_print, mock_popen):
        mock_process = MagicMock()
        mock_popen.return_value = mock_process
        
        result = open_file_non_blocking('/path/to/test.png')
        
        assert result is True
        mock_popen.assert_called_once_with(['start', '/path/to/test.png'], shell=True)
        mock_print.assert_not_called()
    
    @patch('src.libs.plotter.file_utils.sys.platform', 'freebsd')
    @patch('builtins.print')
    def test_open_file_non_blocking_unsupported_platform(self, mock_print):
        result = open_file_non_blocking('/path/to/test.png')
        
        assert result is False
        expected_calls = [
            call("Unsupported platform: freebsd. Please open the file manually: /path/to/test.png")
        ]
        mock_print.assert_has_calls(expected_calls)
    
    @patch('src.libs.plotter.file_utils.subprocess.Popen')
    @patch('src.libs.plotter.file_utils.sys.platform', 'darwin')
    @patch('builtins.print')
    def test_open_file_non_blocking_exception_handling(self, mock_print, mock_popen):
        # Mock Popen to raise an exception
        mock_popen.side_effect = FileNotFoundError("Command not found")
        
        result = open_file_non_blocking('/path/to/test.png')
        
        assert result is False
        mock_popen.assert_called_once_with(['open', '/path/to/test.png'])
        expected_calls = [
            call("Could not open file automatically: Command not found"),
            call("Please open manually: /path/to/test.png")
        ]
        mock_print.assert_has_calls(expected_calls)
    
    @patch('src.libs.plotter.file_utils.subprocess.Popen')
    @patch('src.libs.plotter.file_utils.sys.platform', 'linux')
    @patch('builtins.print')
    def test_open_file_non_blocking_permission_error(self, mock_print, mock_popen):
        # Mock Popen to raise a permission error
        mock_popen.side_effect = PermissionError("Permission denied")
        
        result = open_file_non_blocking('/path/to/restricted.png')
        
        assert result is False
        expected_calls = [
            call("Could not open file automatically: Permission denied"),
            call("Please open manually: /path/to/restricted.png")
        ]
        mock_print.assert_has_calls(expected_calls)
    
    @patch('src.libs.plotter.file_utils.subprocess.Popen')
    @patch('src.libs.plotter.file_utils.sys.platform', 'darwin')
    def test_open_file_non_blocking_with_spaces_in_path(self, mock_popen):
        mock_process = MagicMock()
        mock_popen.return_value = mock_process
        
        file_path = '/path/to/file with spaces.png'
        result = open_file_non_blocking(file_path)
        
        assert result is True
        mock_popen.assert_called_once_with(['open', file_path])
    
    @patch('src.libs.plotter.file_utils.subprocess.Popen')
    @patch('src.libs.plotter.file_utils.sys.platform', 'win32')
    def test_open_file_non_blocking_windows_shell_true(self, mock_popen):
        """Test that Windows command uses shell=True."""
        mock_process = MagicMock()
        mock_popen.return_value = mock_process
        
        result = open_file_non_blocking('/path/to/test.png')
        
        assert result is True
        # Verify shell=True is passed for Windows
        call_args = mock_popen.call_args
        assert call_args[1]['shell'] is True
    
    @patch('src.libs.plotter.file_utils.subprocess.Popen')
    @patch('src.libs.plotter.file_utils.sys.platform', 'darwin')
    def test_open_file_non_blocking_macos_no_shell(self, mock_popen):
        """Test that macOS command doesn't use shell=True."""
        mock_process = MagicMock()
        mock_popen.return_value = mock_process
        
        result = open_file_non_blocking('/path/to/test.png')
        
        assert result is True
        # Verify shell=True is not passed for macOS
        call_args = mock_popen.call_args
        assert 'shell' not in call_args[1] or call_args[1].get('shell') is False
    
    @patch('src.libs.plotter.file_utils.subprocess.Popen')
    @patch('src.libs.plotter.file_utils.sys.platform', 'linux')
    def test_open_file_non_blocking_linux_no_shell(self, mock_popen):
        """Test that Linux command doesn't use shell=True."""
        mock_process = MagicMock()
        mock_popen.return_value = mock_process
        
        result = open_file_non_blocking('/path/to/test.png')
        
        assert result is True
        # Verify shell=True is not passed for Linux
        call_args = mock_popen.call_args
        assert 'shell' not in call_args[1] or call_args[1].get('shell') is False
    
    @patch('src.libs.plotter.file_utils.subprocess.Popen')
    @patch('src.libs.plotter.file_utils.sys.platform', 'darwin')
    def test_open_file_non_blocking_empty_path(self, mock_popen):
        """Test with empty file path."""
        mock_process = MagicMock()
        mock_popen.return_value = mock_process
        
        result = open_file_non_blocking('')
        
        assert result is True
        mock_popen.assert_called_once_with(['open', ''])
    
    @patch('src.libs.plotter.file_utils.subprocess.Popen')
    @patch('src.libs.plotter.file_utils.sys.platform', 'linux')
    def test_open_file_non_blocking_absolute_path(self, mock_popen):
        """Test with absolute file path."""
        mock_process = MagicMock()
        mock_popen.return_value = mock_process
        
        absolute_path = '/home/user/documents/report.pdf'
        result = open_file_non_blocking(absolute_path)
        
        assert result is True
        mock_popen.assert_called_once_with(['xdg-open', absolute_path])
    
    @patch('src.libs.plotter.file_utils.subprocess.Popen')
    @patch('src.libs.plotter.file_utils.sys.platform', 'win32')
    @patch('builtins.print')
    def test_open_file_non_blocking_windows_oserror(self, mock_print, mock_popen):
        """Test Windows-specific OSError handling."""
        mock_popen.side_effect = OSError("The system cannot find the file specified")
        
        result = open_file_non_blocking('C:\\path\\to\\file.png')
        
        assert result is False
        expected_calls = [
            call("Could not open file automatically: The system cannot find the file specified"),
            call("Please open manually: C:\\path\\to\\file.png")
        ]
        mock_print.assert_has_calls(expected_calls)