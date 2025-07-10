import pytest
from unittest.mock import patch, mock_open, MagicMock, call
import json
from src.libs.checker.logging import log_to_file


@pytest.fixture
def sample_results():
    return {
        'timestamp': '2025-07-09 10:30:45',
        'timestamp_utc': '2025-07-09 14:30:45',
        'timezone_local': 'America/New_York',
        'wifi_network': 'TestNetwork',
        'checks': [
            {'url': 'https://google.com', 'status': 'SUCCESS', 'duration': 0.25},
            {'url': 'https://github.com', 'status': 'SUCCESS', 'duration': 0.18},
            {'url': 'https://example.com', 'status': 'FAILED', 'duration': 5.0}
        ]
    }

@patch('src.libs.checker.logging.socket.gethostname')
@patch('src.libs.checker.logging.datetime.datetime')
@patch('src.libs.checker.logging.os.makedirs')
@patch('builtins.open', new_callable=mock_open)
def test_log_to_file_default_path(mock_file, mock_makedirs, mock_datetime, mock_hostname, sample_results):
    mock_hostname.return_value = 'test-hostname'
    mock_datetime.now.return_value.strftime.return_value = '20250709'
    
    log_to_file(sample_results)
    
    mock_makedirs.assert_called_once_with('logs/test-hostname', exist_ok=True)
    mock_file.assert_called_once_with('logs/test-hostname/connectivity_log_20250709.txt', 'a')
    
    handle = mock_file()
    expected_calls = [
        call('2025-07-09 10:30:45 - '),
        call('WiFi: TestNetwork - Internet: 2/3 sites accessible\n'),
        call('  (0.25s) - https://google.com: SUCCESS\n'),
        call('  (0.18s) - https://github.com: SUCCESS\n'),
        call('  (5.00s) - https://example.com: FAILED\n'),
        call('Hostname: test-hostname\n\n')
    ]
    handle.write.assert_has_calls(expected_calls)

@patch('builtins.open', new_callable=mock_open)
def test_log_to_file_custom_path(mock_file, sample_results):
    custom_log_file = '/tmp/test_log.txt'
    
    log_to_file(sample_results, custom_log_file)
    
    mock_file.assert_called_once_with(custom_log_file, 'a')


