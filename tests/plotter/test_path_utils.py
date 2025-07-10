import pytest
from unittest.mock import patch, MagicMock
import datetime
import os
import tempfile
from src.libs.plotter.path_utils import setup_logs_directory, generate_output_filename, resolve_output_path


class TestSetupLogsDirectory:
    """Test cases for setup_logs_directory function."""
    
    @patch('src.libs.plotter.path_utils.os.path.exists')
    def test_setup_logs_directory_exists(self, mock_exists):
        mock_exists.return_value = True
        
        # Mock the path operations
        with patch('src.libs.plotter.path_utils.os.path.dirname') as mock_dirname, \
             patch('src.libs.plotter.path_utils.os.path.abspath') as mock_abspath, \
             patch('src.libs.plotter.path_utils.os.path.join') as mock_join:
            
            mock_abspath.return_value = '/home/user/project/src/plot_script.py'
            mock_dirname.return_value = '/home/user/project/src'
            mock_join.return_value = '/home/user/project/logs'
            
            result = setup_logs_directory('/home/user/project/src/plot_script.py')
            
            assert result == '/home/user/project/logs'
            mock_abspath.assert_called_once_with('/home/user/project/src/plot_script.py')
            mock_dirname.assert_called_once_with('/home/user/project/src/plot_script.py')
            mock_join.assert_called_once_with('/home/user/project/src', '..', 'logs')
            mock_exists.assert_called_once_with('/home/user/project/logs')
    
    @patch('src.libs.plotter.path_utils.os.path.exists')
    @patch('src.libs.plotter.path_utils.sys.exit')
    @patch('builtins.print')
    def test_setup_logs_directory_not_exists(self, mock_print, mock_exit, mock_exists):
        mock_exists.return_value = False
        
        with patch('src.libs.plotter.path_utils.os.path.dirname') as mock_dirname, \
             patch('src.libs.plotter.path_utils.os.path.abspath') as mock_abspath, \
             patch('src.libs.plotter.path_utils.os.path.join') as mock_join:
            
            mock_abspath.return_value = '/home/user/project/src/plot_script.py'
            mock_dirname.return_value = '/home/user/project/src'
            mock_join.return_value = '/home/user/project/logs'
            
            setup_logs_directory('/home/user/project/src/plot_script.py')
            
            mock_print.assert_called_once_with("Error: Logs directory not found: /home/user/project/logs")
            mock_exit.assert_called_once_with(1)
    
    def test_setup_logs_directory_real_integration(self):
        """Integration test with real filesystem operations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a script path and logs directory
            script_path = os.path.join(temp_dir, 'src', 'script.py')
            logs_dir = os.path.join(temp_dir, 'logs')
            
            # Create the directories
            os.makedirs(os.path.dirname(script_path))
            os.makedirs(logs_dir)
            
            result = setup_logs_directory(script_path)
            
            # The result should be the logs directory
            assert os.path.basename(result) == 'logs'
            assert os.path.exists(result)


class TestGenerateOutputFilename:
    """Test cases for generate_output_filename function."""
    
    @patch('src.libs.plotter.path_utils.datetime.datetime')
    @patch('src.libs.plotter.path_utils.os.makedirs')
    def test_generate_output_filename_basic(self, mock_makedirs, mock_datetime):
        # Mock datetime.now()
        mock_now = MagicMock()
        mock_now.strftime.return_value = '20250710_143025'
        mock_datetime.now.return_value = mock_now
        
        result = generate_output_filename(
            'test-host', 
            'MyWiFi', 
            24, 
            15, 
            '/output'
        )
        
        expected = '/output/connectivity_plot_test-host_MyWiFi_24h_15m_20250710_143025.png'
        assert result == expected
        mock_makedirs.assert_called_once_with('/output', exist_ok=True)
    
    @patch('src.libs.plotter.path_utils.datetime.datetime')
    @patch('src.libs.plotter.path_utils.os.makedirs')
    def test_generate_output_filename_special_characters(self, mock_makedirs, mock_datetime):
        # Mock datetime.now()
        mock_now = MagicMock()
        mock_now.strftime.return_value = '20250710_143025'
        mock_datetime.now.return_value = mock_now
        
        result = generate_output_filename(
            'my-host.local', 
            'My WiFi Network', 
            72, 
            30, 
            '/tmp/plots'
        )
        
        expected = '/tmp/plots/connectivity_plot_my-host.local_My WiFi Network_72h_30m_20250710_143025.png'
        assert result == expected
        mock_makedirs.assert_called_once_with('/tmp/plots', exist_ok=True)
    
    @patch('src.libs.plotter.path_utils.datetime.datetime')
    @patch('src.libs.plotter.path_utils.os.makedirs')
    def test_generate_output_filename_edge_case_values(self, mock_makedirs, mock_datetime):
        # Mock datetime.now()
        mock_now = MagicMock()
        mock_now.strftime.return_value = '20250710_000000'
        mock_datetime.now.return_value = mock_now
        
        result = generate_output_filename(
            '', 
            '', 
            1, 
            1, 
            '.'
        )
        
        expected = './connectivity_plot___1h_1m_20250710_000000.png'
        assert result == expected
        mock_makedirs.assert_called_once_with('.', exist_ok=True)
    
    def test_generate_output_filename_real_integration(self):
        """Integration test with real filesystem operations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = generate_output_filename(
                'test-host', 
                'TestWiFi', 
                24, 
                15, 
                temp_dir
            )
            
            # Verify the file path structure
            assert result.startswith(temp_dir)
            assert 'connectivity_plot_test-host_TestWiFi_24h_15m_' in result
            assert result.endswith('.png')
            
            # Verify directory exists
            assert os.path.exists(temp_dir)
    
    @patch('src.libs.plotter.path_utils.datetime.datetime')
    @patch('src.libs.plotter.path_utils.os.makedirs')
    def test_generate_output_filename_path_join(self, mock_makedirs, mock_datetime):
        """Test that os.path.join is used correctly."""
        mock_now = MagicMock()
        mock_now.strftime.return_value = '20250710_120000'
        mock_datetime.now.return_value = mock_now
        
        with patch('src.libs.plotter.path_utils.os.path.join') as mock_join:
            mock_join.return_value = '/custom/path/file.png'
            
            result = generate_output_filename('host', 'wifi', 24, 15, '/custom')
            
            assert result == '/custom/path/file.png'
            # Verify os.path.join was called with correct arguments
            expected_filename = 'connectivity_plot_host_wifi_24h_15m_20250710_120000.png'
            mock_join.assert_called_once_with('/custom', expected_filename)


class TestResolveOutputPath:
    """Test cases for resolve_output_path function."""
    
    def test_resolve_output_path_with_explicit_output(self):
        # Create a mock args object with output specified
        args = MagicMock()
        args.output = '/explicit/path/output.png'
        
        result = resolve_output_path(args)
        
        assert result == '/explicit/path/output.png'
    
    def test_resolve_output_path_without_output(self):
        # Create a mock args object without output specified
        args = MagicMock()
        args.output = None
        args.hostname = 'test-host'
        args.wifi_network = 'TestWiFi'
        args.time_range = 48
        args.interval = 20
        args.output_dir = '/auto/output'
        
        with patch('src.libs.plotter.path_utils.generate_output_filename') as mock_generate:
            mock_generate.return_value = '/auto/output/generated_file.png'
            
            result = resolve_output_path(args)
            
            assert result == '/auto/output/generated_file.png'
            mock_generate.assert_called_once_with(
                'test-host', 
                'TestWiFi', 
                48, 
                20, 
                '/auto/output'
            )
    
    def test_resolve_output_path_empty_output(self):
        # Create a mock args object with empty output
        args = MagicMock()
        args.output = ''
        args.hostname = 'test-host'
        args.wifi_network = 'TestWiFi'
        args.time_range = 24
        args.interval = 15
        args.output_dir = '/default/output'
        
        with patch('src.libs.plotter.path_utils.generate_output_filename') as mock_generate:
            mock_generate.return_value = '/default/output/auto_file.png'
            
            result = resolve_output_path(args)
            
            # Empty string should be treated as falsy, so should generate filename
            assert result == '/default/output/auto_file.png'
            mock_generate.assert_called_once()
    
    def test_resolve_output_path_false_output(self):
        # Create a mock args object with False output
        args = MagicMock()
        args.output = False
        args.hostname = 'my-host'
        args.wifi_network = 'MyNetwork'
        args.time_range = 72
        args.interval = 30
        args.output_dir = '/generated/output'
        
        with patch('src.libs.plotter.path_utils.generate_output_filename') as mock_generate:
            mock_generate.return_value = '/generated/output/false_file.png'
            
            result = resolve_output_path(args)
            
            assert result == '/generated/output/false_file.png'
            mock_generate.assert_called_once_with(
                'my-host', 
                'MyNetwork', 
                72, 
                30, 
                '/generated/output'
            )
    
    def test_resolve_output_path_integration_with_real_args(self):
        """Integration test with real argument-like object."""
        # Create a simple namespace object similar to argparse.Namespace
        class Args:
            def __init__(self):
                self.output = None
                self.hostname = 'integration-host'
                self.wifi_network = 'IntegrationWiFi'
                self.time_range = 36
                self.interval = 10
                self.output_dir = '/integration/test'
        
        args = Args()
        
        with patch('src.libs.plotter.path_utils.generate_output_filename') as mock_generate:
            mock_generate.return_value = '/integration/test/integration_result.png'
            
            result = resolve_output_path(args)
            
            assert result == '/integration/test/integration_result.png'
            mock_generate.assert_called_once_with(
                'integration-host',
                'IntegrationWiFi',
                36,
                10,
                '/integration/test'
            )
    
    def test_resolve_output_path_with_complex_output_path(self):
        """Test with complex output path including directories."""
        args = MagicMock()
        args.output = '/very/long/path/to/output/directory/complex_filename_with_timestamp.png'
        
        result = resolve_output_path(args)
        
        assert result == '/very/long/path/to/output/directory/complex_filename_with_timestamp.png'