import pytest
from unittest.mock import patch, MagicMock
import socket
from src.libs.plotter.system_utils import get_hostname


class TestGetHostname:
    """Test cases for get_hostname function."""
    
    @patch('src.libs.plotter.system_utils.socket.gethostname')
    def test_get_hostname_success(self, mock_gethostname):
        mock_gethostname.return_value = 'test-machine.local'
        
        result = get_hostname()
        
        assert result == 'test-machine.local'
        mock_gethostname.assert_called_once()
    
    @patch('src.libs.plotter.system_utils.socket.gethostname')
    def test_get_hostname_different_formats(self, mock_gethostname):
        # Test various hostname formats
        test_hostnames = [
            'localhost',
            'my-computer',
            'desktop-abc123',
            'server01.example.com',
            'MacBook-Pro.local',
            'ubuntu-vm',
            '192.168.1.100',
            'host_with_underscores',
            'UPPERCASE-HOST',
            'mixed-Case.Domain.Com'
        ]
        
        for hostname in test_hostnames:
            mock_gethostname.return_value = hostname
            result = get_hostname()
            assert result == hostname
    
    @patch('src.libs.plotter.system_utils.socket.gethostname')
    def test_get_hostname_empty_string(self, mock_gethostname):
        mock_gethostname.return_value = ''
        
        result = get_hostname()
        
        assert result == ''
        mock_gethostname.assert_called_once()
    
    @patch('src.libs.plotter.system_utils.socket.gethostname')
    def test_get_hostname_with_special_characters(self, mock_gethostname):
        # Test hostnames with various special characters
        special_hostnames = [
            'host-with-dashes',
            'host.with.dots',
            'host_with_underscores',
            'host123',
            'host-123.local',
            'a' * 63,  # Maximum hostname length
        ]
        
        for hostname in special_hostnames:
            mock_gethostname.return_value = hostname
            result = get_hostname()
            assert result == hostname
    
    @patch('src.libs.plotter.system_utils.socket.gethostname')
    def test_get_hostname_exception_handling(self, mock_gethostname):
        # Test that exceptions are propagated (function doesn't handle them)
        mock_gethostname.side_effect = OSError("Unable to get hostname")
        
        with pytest.raises(OSError, match="Unable to get hostname"):
            get_hostname()
        
        mock_gethostname.assert_called_once()
    
    @patch('src.libs.plotter.system_utils.socket.gethostname')
    def test_get_hostname_socket_error(self, mock_gethostname):
        # Test socket-specific errors
        mock_gethostname.side_effect = socket.error("Socket error")
        
        with pytest.raises(socket.error, match="Socket error"):
            get_hostname()
        
        mock_gethostname.assert_called_once()
    
    def test_get_hostname_real_system_call(self):
        """Test with actual system call (integration test)."""
        result = get_hostname()
        
        # The result should be a string (hostname)
        assert isinstance(result, str)
        # Real hostnames are typically not empty
        assert len(result) > 0
        # Should match what socket.gethostname() returns directly
        assert result == socket.gethostname()
    
    @patch('src.libs.plotter.system_utils.socket.gethostname')
    def test_get_hostname_multiple_calls(self, mock_gethostname):
        """Test multiple consecutive calls."""
        mock_gethostname.return_value = 'consistent-hostname'
        
        # Call the function multiple times
        results = [get_hostname() for _ in range(5)]
        
        # All results should be the same
        assert all(result == 'consistent-hostname' for result in results)
        # socket.gethostname should be called each time
        assert mock_gethostname.call_count == 5
    
    @patch('src.libs.plotter.system_utils.socket.gethostname')
    def test_get_hostname_unicode_characters(self, mock_gethostname):
        """Test with Unicode characters in hostname."""
        unicode_hostname = 'host-ñáéíóú'
        mock_gethostname.return_value = unicode_hostname
        
        result = get_hostname()
        
        assert result == unicode_hostname
        assert isinstance(result, str)
    
    @patch('src.libs.plotter.system_utils.socket.gethostname')
    def test_get_hostname_numeric_hostname(self, mock_gethostname):
        """Test with purely numeric hostname."""
        mock_gethostname.return_value = '12345'
        
        result = get_hostname()
        
        assert result == '12345'
        assert isinstance(result, str)
    
    @patch('src.libs.plotter.system_utils.socket')
    def test_get_hostname_socket_module_access(self, mock_socket_module):
        """Test that the function accesses socket.gethostname correctly."""
        mock_socket_module.gethostname.return_value = 'module-test-host'
        
        result = get_hostname()
        
        assert result == 'module-test-host'
        mock_socket_module.gethostname.assert_called_once()
    
    @patch('src.libs.plotter.system_utils.socket.gethostname')
    def test_get_hostname_return_type(self, mock_gethostname):
        """Test that return type is always string."""
        mock_gethostname.return_value = 'type-test-host'
        
        result = get_hostname()
        
        assert isinstance(result, str)
        assert result == 'type-test-host'