import pytest
from unittest.mock import patch, mock_open, MagicMock
import datetime
import tempfile
import os
from src.libs.plotter.log_parser import parse_log_files


class TestParseLogFiles:
    """Test cases for parse_log_files function."""
    
    @patch('src.libs.plotter.log_parser.os.path.exists')
    @patch('builtins.print')
    def test_parse_log_files_hostname_directory_not_found(self, mock_print, mock_exists):
        mock_exists.return_value = False
        
        result = parse_log_files('/logs', 'nonexistent-host')
        
        assert result == []
        mock_print.assert_called_once_with("Error: Hostname directory not found: /logs/nonexistent-host")
    
    @patch('src.libs.plotter.log_parser.glob.glob')
    @patch('src.libs.plotter.log_parser.os.path.exists')
    @patch('builtins.print')
    def test_parse_log_files_no_log_files_found(self, mock_print, mock_exists, mock_glob):
        mock_exists.return_value = True
        mock_glob.return_value = []
        
        result = parse_log_files('/logs', 'test-host')
        
        assert result == []
        mock_print.assert_called_once_with("Error: No log files found in /logs/test-host")
    
    @patch('src.libs.plotter.log_parser.glob.glob')
    @patch('src.libs.plotter.log_parser.os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data="")
    @patch('builtins.print')
    def test_parse_log_files_empty_log_file(self, mock_print, mock_file, mock_exists, mock_glob):
        mock_exists.return_value = True
        mock_glob.return_value = ['/logs/test-host/connectivity_log_20250710.txt']
        
        result = parse_log_files('/logs', 'test-host')
        
        assert result == []
        mock_print.assert_any_call("Parsing 1 log files...")
        mock_print.assert_any_call("Processing: connectivity_log_20250710.txt")
        mock_print.assert_any_call("Found 0 data points for WiFi network 'GoTitansFC'")
    
    @patch('src.libs.plotter.log_parser.glob.glob')
    @patch('src.libs.plotter.log_parser.os.path.exists')
    @patch('builtins.print')
    def test_parse_log_files_valid_log_data(self, mock_print, mock_exists, mock_glob):
        mock_exists.return_value = True
        mock_glob.return_value = ['/logs/test-host/connectivity_log_20250710.txt']
        
        log_content = """2025-07-10 12:00:00 - WiFi: GoTitansFC - Internet: 8/10 sites accessible
2025-07-10 12:15:00 - WiFi: GoTitansFC - Internet: 10/10 sites accessible
2025-07-10 12:30:00 - WiFi: GoTitansFC - Internet: 6/10 sites accessible"""
        
        with patch('builtins.open', mock_open(read_data=log_content)):
            result = parse_log_files('/logs', 'test-host')
        
        assert len(result) == 3
        assert result[0] == (datetime.datetime(2025, 7, 10, 12, 0, 0), 0.8)
        assert result[1] == (datetime.datetime(2025, 7, 10, 12, 15, 0), 1.0)
        assert result[2] == (datetime.datetime(2025, 7, 10, 12, 30, 0), 0.6)
        mock_print.assert_any_call("Found 3 data points for WiFi network 'GoTitansFC'")
    
    @patch('src.libs.plotter.log_parser.glob.glob')
    @patch('src.libs.plotter.log_parser.os.path.exists')
    @patch('builtins.print')
    def test_parse_log_files_custom_wifi_filter(self, mock_print, mock_exists, mock_glob):
        mock_exists.return_value = True
        mock_glob.return_value = ['/logs/test-host/connectivity_log_20250710.txt']
        
        log_content = """2025-07-10 12:00:00 - WiFi: MyWiFi - Internet: 8/10 sites accessible
2025-07-10 12:15:00 - WiFi: GoTitansFC - Internet: 10/10 sites accessible
2025-07-10 12:30:00 - WiFi: MyWiFi - Internet: 6/10 sites accessible"""
        
        with patch('builtins.open', mock_open(read_data=log_content)):
            result = parse_log_files('/logs', 'test-host', wifi_filter='MyWiFi')
        
        assert len(result) == 2
        assert result[0] == (datetime.datetime(2025, 7, 10, 12, 0, 0), 0.8)
        assert result[1] == (datetime.datetime(2025, 7, 10, 12, 30, 0), 0.6)
        mock_print.assert_any_call("Found 2 data points for WiFi network 'MyWiFi'")
    
    @patch('src.libs.plotter.log_parser.glob.glob')
    @patch('src.libs.plotter.log_parser.os.path.exists')
    @patch('builtins.print')
    def test_parse_log_files_mixed_wifi_networks(self, mock_print, mock_exists, mock_glob):
        mock_exists.return_value = True
        mock_glob.return_value = ['/logs/test-host/connectivity_log_20250710.txt']
        
        log_content = """2025-07-10 12:00:00 - WiFi: GoTitansFC - Internet: 8/10 sites accessible
2025-07-10 12:15:00 - WiFi: OtherNetwork - Internet: 5/10 sites accessible
2025-07-10 12:30:00 - WiFi: GoTitansFC - Internet: 9/10 sites accessible"""
        
        with patch('builtins.open', mock_open(read_data=log_content)):
            result = parse_log_files('/logs', 'test-host')
        
        # Should only include GoTitansFC entries
        assert len(result) == 2
        assert result[0] == (datetime.datetime(2025, 7, 10, 12, 0, 0), 0.8)
        assert result[1] == (datetime.datetime(2025, 7, 10, 12, 30, 0), 0.9)
    
    @patch('src.libs.plotter.log_parser.glob.glob')
    @patch('src.libs.plotter.log_parser.os.path.exists')
    @patch('builtins.print')
    def test_parse_log_files_zero_total_sites(self, mock_print, mock_exists, mock_glob):
        mock_exists.return_value = True
        mock_glob.return_value = ['/logs/test-host/connectivity_log_20250710.txt']
        
        log_content = """2025-07-10 12:00:00 - WiFi: GoTitansFC - Internet: 0/0 sites accessible
2025-07-10 12:15:00 - WiFi: GoTitansFC - Internet: 8/10 sites accessible"""
        
        with patch('builtins.open', mock_open(read_data=log_content)):
            result = parse_log_files('/logs', 'test-host')
        
        assert len(result) == 2
        assert result[0] == (datetime.datetime(2025, 7, 10, 12, 0, 0), 0.0)  # 0/0 = 0
        assert result[1] == (datetime.datetime(2025, 7, 10, 12, 15, 0), 0.8)
    
    @patch('src.libs.plotter.log_parser.glob.glob')
    @patch('src.libs.plotter.log_parser.os.path.exists')
    @patch('builtins.print')
    def test_parse_log_files_invalid_log_lines(self, mock_print, mock_exists, mock_glob):
        mock_exists.return_value = True
        mock_glob.return_value = ['/logs/test-host/connectivity_log_20250710.txt']
        
        log_content = """Invalid log line
2025-07-10 12:00:00 - WiFi: GoTitansFC - Internet: 8/10 sites accessible
Another invalid line
2025-07-10 12:15:00 - WiFi: GoTitansFC - Internet: 10/10 sites accessible
Yet another invalid format"""
        
        with patch('builtins.open', mock_open(read_data=log_content)):
            result = parse_log_files('/logs', 'test-host')
        
        # Should only parse valid lines
        assert len(result) == 2
        assert result[0] == (datetime.datetime(2025, 7, 10, 12, 0, 0), 0.8)
        assert result[1] == (datetime.datetime(2025, 7, 10, 12, 15, 0), 1.0)
    
    @patch('src.libs.plotter.log_parser.glob.glob')
    @patch('src.libs.plotter.log_parser.os.path.exists')
    @patch('builtins.print')
    def test_parse_log_files_multiple_log_files(self, mock_print, mock_exists, mock_glob):
        mock_exists.return_value = True
        mock_glob.return_value = [
            '/logs/test-host/connectivity_log_20250709.txt',
            '/logs/test-host/connectivity_log_20250710.txt'
        ]
        
        log_content_1 = "2025-07-09 23:45:00 - WiFi: GoTitansFC - Internet: 8/10 sites accessible"
        log_content_2 = "2025-07-10 12:15:00 - WiFi: GoTitansFC - Internet: 10/10 sites accessible"
        
        def side_effect(file_path, mode='r', encoding='utf-8'):
            if 'connectivity_log_20250709.txt' in file_path:
                return mock_open(read_data=log_content_1).return_value
            elif 'connectivity_log_20250710.txt' in file_path:
                return mock_open(read_data=log_content_2).return_value
            return mock_open().return_value
        
        with patch('builtins.open', side_effect=side_effect):
            result = parse_log_files('/logs', 'test-host')
        
        assert len(result) == 2
        # Results should be sorted by timestamp
        assert result[0] == (datetime.datetime(2025, 7, 9, 23, 45, 0), 0.8)
        assert result[1] == (datetime.datetime(2025, 7, 10, 12, 15, 0), 1.0)
        mock_print.assert_any_call("Parsing 2 log files...")
    
    @patch('src.libs.plotter.log_parser.glob.glob')
    @patch('src.libs.plotter.log_parser.os.path.exists')
    @patch('builtins.print')
    def test_parse_log_files_time_range_filtering(self, mock_print, mock_exists, mock_glob):
        mock_exists.return_value = True
        mock_glob.return_value = ['/logs/test-host/connectivity_log_20250710.txt']
        
        # Data spanning more than the time range
        log_content = """2025-07-08 12:00:00 - WiFi: GoTitansFC - Internet: 8/10 sites accessible
2025-07-09 12:00:00 - WiFi: GoTitansFC - Internet: 9/10 sites accessible
2025-07-10 12:00:00 - WiFi: GoTitansFC - Internet: 10/10 sites accessible"""
        
        with patch('builtins.open', mock_open(read_data=log_content)):
            result = parse_log_files('/logs', 'test-host', time_range_hours=24)
        
        # Should only include data from last 24 hours (from 2025-07-10 12:00:00)
        assert len(result) == 2  # 2025-07-09 12:00:00 and 2025-07-10 12:00:00
        assert result[0] == (datetime.datetime(2025, 7, 9, 12, 0, 0), 0.9)
        assert result[1] == (datetime.datetime(2025, 7, 10, 12, 0, 0), 1.0)
    
    @patch('src.libs.plotter.log_parser.glob.glob')
    @patch('src.libs.plotter.log_parser.os.path.exists')
    @patch('builtins.print')
    def test_parse_log_files_file_exception_handling(self, mock_print, mock_exists, mock_glob):
        mock_exists.return_value = True
        mock_glob.return_value = ['/logs/test-host/connectivity_log_20250710.txt']
        
        # Mock file open to raise an exception
        with patch('builtins.open', side_effect=IOError("Permission denied")):
            result = parse_log_files('/logs', 'test-host')
        
        assert result == []
        mock_print.assert_any_call("Error parsing /logs/test-host/connectivity_log_20250710.txt: Permission denied")
        mock_print.assert_any_call("Found 0 data points for WiFi network 'GoTitansFC'")
    
    @patch('src.libs.plotter.log_parser.glob.glob')
    @patch('src.libs.plotter.log_parser.os.path.exists')
    @patch('builtins.print')
    def test_parse_log_files_unsorted_timestamps(self, mock_print, mock_exists, mock_glob):
        mock_exists.return_value = True
        mock_glob.return_value = ['/logs/test-host/connectivity_log_20250710.txt']
        
        # Timestamps in non-chronological order
        log_content = """2025-07-10 12:30:00 - WiFi: GoTitansFC - Internet: 6/10 sites accessible
2025-07-10 12:00:00 - WiFi: GoTitansFC - Internet: 8/10 sites accessible
2025-07-10 12:15:00 - WiFi: GoTitansFC - Internet: 10/10 sites accessible"""
        
        with patch('builtins.open', mock_open(read_data=log_content)):
            result = parse_log_files('/logs', 'test-host')
        
        # Results should be sorted by timestamp
        assert len(result) == 3
        assert result[0] == (datetime.datetime(2025, 7, 10, 12, 0, 0), 0.8)
        assert result[1] == (datetime.datetime(2025, 7, 10, 12, 15, 0), 1.0)
        assert result[2] == (datetime.datetime(2025, 7, 10, 12, 30, 0), 0.6)
    
    @patch('src.libs.plotter.log_parser.glob.glob')
    @patch('src.libs.plotter.log_parser.os.path.exists')
    @patch('builtins.print')
    def test_parse_log_files_wifi_network_with_spaces(self, mock_print, mock_exists, mock_glob):
        mock_exists.return_value = True
        mock_glob.return_value = ['/logs/test-host/connectivity_log_20250710.txt']
        
        log_content = """2025-07-10 12:00:00 - WiFi: My Home WiFi - Internet: 8/10 sites accessible
2025-07-10 12:15:00 - WiFi: My Home WiFi - Internet: 10/10 sites accessible"""
        
        with patch('builtins.open', mock_open(read_data=log_content)):
            result = parse_log_files('/logs', 'test-host', wifi_filter='My Home WiFi')
        
        assert len(result) == 2
        assert result[0] == (datetime.datetime(2025, 7, 10, 12, 0, 0), 0.8)
        assert result[1] == (datetime.datetime(2025, 7, 10, 12, 15, 0), 1.0)
    
    @patch('src.libs.plotter.log_parser.glob.glob')
    @patch('src.libs.plotter.log_parser.os.path.exists')
    @patch('builtins.print')
    def test_parse_log_files_edge_case_success_rates(self, mock_print, mock_exists, mock_glob):
        mock_exists.return_value = True
        mock_glob.return_value = ['/logs/test-host/connectivity_log_20250710.txt']
        
        log_content = """2025-07-10 12:00:00 - WiFi: GoTitansFC - Internet: 0/10 sites accessible
2025-07-10 12:15:00 - WiFi: GoTitansFC - Internet: 10/10 sites accessible
2025-07-10 12:30:00 - WiFi: GoTitansFC - Internet: 1/1 sites accessible"""
        
        with patch('builtins.open', mock_open(read_data=log_content)):
            result = parse_log_files('/logs', 'test-host')
        
        assert len(result) == 3
        assert result[0] == (datetime.datetime(2025, 7, 10, 12, 0, 0), 0.0)   # 0% success
        assert result[1] == (datetime.datetime(2025, 7, 10, 12, 15, 0), 1.0)  # 100% success
        assert result[2] == (datetime.datetime(2025, 7, 10, 12, 30, 0), 1.0)  # 100% success (1/1)
    
    @patch('src.libs.plotter.log_parser.glob.glob')
    @patch('src.libs.plotter.log_parser.os.path.exists')
    @patch('builtins.print')
    def test_parse_log_files_path_construction(self, mock_print, mock_exists, mock_glob):
        """Test that paths are constructed correctly."""
        mock_exists.return_value = True
        mock_glob.return_value = []
        
        parse_log_files('/custom/logs', 'my-hostname')
        
        # Verify os.path.exists was called with correct path
        mock_exists.assert_called_once_with('/custom/logs/my-hostname')
        # Verify glob.glob was called with correct pattern
        mock_glob.assert_called_once_with('/custom/logs/my-hostname/connectivity_log_*.txt')
    
    @patch('src.libs.plotter.log_parser.glob.glob')
    @patch('src.libs.plotter.log_parser.os.path.exists')
    @patch('builtins.print')
    def test_parse_log_files_large_numbers(self, mock_print, mock_exists, mock_glob):
        """Test with large site numbers."""
        mock_exists.return_value = True
        mock_glob.return_value = ['/logs/test-host/connectivity_log_20250710.txt']
        
        log_content = "2025-07-10 12:00:00 - WiFi: GoTitansFC - Internet: 999/1000 sites accessible"
        
        with patch('builtins.open', mock_open(read_data=log_content)):
            result = parse_log_files('/logs', 'test-host')
        
        assert len(result) == 1
        assert result[0] == (datetime.datetime(2025, 7, 10, 12, 0, 0), 0.999)