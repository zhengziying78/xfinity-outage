import pytest
from unittest.mock import patch, MagicMock
import argparse
import os
from src.libs.plotter.arg_parser import create_plot_argument_parser, print_configuration


class TestCreatePlotArgumentParser:
    """Test cases for create_plot_argument_parser function."""
    
    @patch('src.libs.plotter.arg_parser.get_hostname')
    def test_create_parser_returns_argument_parser(self, mock_hostname):
        mock_hostname.return_value = 'test-hostname'
        
        parser = create_plot_argument_parser()
        
        assert isinstance(parser, argparse.ArgumentParser)
        assert parser.description == 'Generate connectivity success rate plots'
    
    @patch('src.libs.plotter.arg_parser.get_hostname')
    def test_parser_default_values(self, mock_hostname):
        mock_hostname.return_value = 'test-hostname'
        
        parser = create_plot_argument_parser()
        args = parser.parse_args([])
        
        assert args.hostname == 'test-hostname'
        assert args.wifi_network == 'GoTitansFC'
        assert args.time_range == 72
        assert args.interval == 15
        assert args.output_dir == os.path.expanduser('~/Desktop')
        assert args.output is None
    
    @patch('src.libs.plotter.arg_parser.get_hostname')
    def test_parser_custom_hostname(self, mock_hostname):
        mock_hostname.return_value = 'default-hostname'
        
        parser = create_plot_argument_parser()
        args = parser.parse_args(['--hostname', 'custom-hostname'])
        
        assert args.hostname == 'custom-hostname'
    
    @patch('src.libs.plotter.arg_parser.get_hostname')
    def test_parser_custom_wifi_network(self, mock_hostname):
        mock_hostname.return_value = 'test-hostname'
        
        parser = create_plot_argument_parser()
        args = parser.parse_args(['--wifi-network', 'MyNetwork'])
        
        assert args.wifi_network == 'MyNetwork'
    
    @patch('src.libs.plotter.arg_parser.get_hostname')
    def test_parser_custom_time_range(self, mock_hostname):
        mock_hostname.return_value = 'test-hostname'
        
        parser = create_plot_argument_parser()
        args = parser.parse_args(['--time-range', '24'])
        
        assert args.time_range == 24
    
    @patch('src.libs.plotter.arg_parser.get_hostname')
    def test_parser_custom_interval(self, mock_hostname):
        mock_hostname.return_value = 'test-hostname'
        
        parser = create_plot_argument_parser()
        args = parser.parse_args(['--interval', '30'])
        
        assert args.interval == 30
    
    @patch('src.libs.plotter.arg_parser.get_hostname')
    def test_parser_custom_output_dir(self, mock_hostname):
        mock_hostname.return_value = 'test-hostname'
        
        parser = create_plot_argument_parser()
        args = parser.parse_args(['--output-dir', '/tmp'])
        
        assert args.output_dir == '/tmp'
    
    @patch('src.libs.plotter.arg_parser.get_hostname')
    def test_parser_custom_output_file(self, mock_hostname):
        mock_hostname.return_value = 'test-hostname'
        
        parser = create_plot_argument_parser()
        args = parser.parse_args(['--output', '/tmp/custom.png'])
        
        assert args.output == '/tmp/custom.png'
    
    @patch('src.libs.plotter.arg_parser.get_hostname')
    def test_parser_all_custom_args(self, mock_hostname):
        mock_hostname.return_value = 'default-hostname'
        
        parser = create_plot_argument_parser()
        args = parser.parse_args([
            '--hostname', 'my-host',
            '--wifi-network', 'HomeWiFi', 
            '--time-range', '48',
            '--interval', '5',
            '--output-dir', '/home/user',
            '--output', '/home/user/plot.png'
        ])
        
        assert args.hostname == 'my-host'
        assert args.wifi_network == 'HomeWiFi'
        assert args.time_range == 48
        assert args.interval == 5
        assert args.output_dir == '/home/user'
        assert args.output == '/home/user/plot.png'
    
    @patch('src.libs.plotter.arg_parser.get_hostname')
    def test_parser_invalid_time_range_type(self, mock_hostname):
        mock_hostname.return_value = 'test-hostname'
        
        parser = create_plot_argument_parser()
        
        with pytest.raises(SystemExit):
            parser.parse_args(['--time-range', 'invalid'])
    
    @patch('src.libs.plotter.arg_parser.get_hostname')
    def test_parser_invalid_interval_type(self, mock_hostname):
        mock_hostname.return_value = 'test-hostname'
        
        parser = create_plot_argument_parser()
        
        with pytest.raises(SystemExit):
            parser.parse_args(['--interval', 'invalid'])
    
    @patch('src.libs.plotter.arg_parser.get_hostname')
    def test_parser_help_message(self, mock_hostname):
        mock_hostname.return_value = 'test-hostname'
        
        parser = create_plot_argument_parser()
        
        with pytest.raises(SystemExit):
            parser.parse_args(['--help'])


class TestPrintConfiguration:
    """Test cases for print_configuration function."""
    
    @patch('builtins.print')
    def test_print_configuration_basic(self, mock_print):
        args = MagicMock()
        args.hostname = 'test-hostname'
        args.wifi_network = 'TestNetwork'
        args.time_range = 24
        args.interval = 10
        args.output_dir = '/tmp'
        
        print_configuration(args)
        
        expected_calls = [
            ('Hostname: test-hostname',),
            ('WiFi network filter: TestNetwork',),
            ('Time range: 24 hours',),
            ('Aggregation interval: 10 minutes',),
            ('Output directory: /tmp',)
        ]
        
        assert mock_print.call_count == 5
        actual_calls = [call[0] for call in mock_print.call_args_list]
        assert actual_calls == expected_calls
    
    @patch('builtins.print')
    def test_print_configuration_with_special_characters(self, mock_print):
        args = MagicMock()
        args.hostname = 'host-with-dashes'
        args.wifi_network = 'Network With Spaces'
        args.time_range = 72
        args.interval = 15
        args.output_dir = '/path/with spaces/output'
        
        print_configuration(args)
        
        expected_calls = [
            ('Hostname: host-with-dashes',),
            ('WiFi network filter: Network With Spaces',),
            ('Time range: 72 hours',),
            ('Aggregation interval: 15 minutes',),
            ('Output directory: /path/with spaces/output',)
        ]
        
        assert mock_print.call_count == 5
        actual_calls = [call[0] for call in mock_print.call_args_list]
        assert actual_calls == expected_calls
    
    @patch('builtins.print')
    def test_print_configuration_edge_values(self, mock_print):
        args = MagicMock()
        args.hostname = ''
        args.wifi_network = ''
        args.time_range = 0
        args.interval = 1
        args.output_dir = '.'
        
        print_configuration(args)
        
        expected_calls = [
            ('Hostname: ',),
            ('WiFi network filter: ',),
            ('Time range: 0 hours',),
            ('Aggregation interval: 1 minutes',),
            ('Output directory: .',)
        ]
        
        assert mock_print.call_count == 5
        actual_calls = [call[0] for call in mock_print.call_args_list]
        assert actual_calls == expected_calls