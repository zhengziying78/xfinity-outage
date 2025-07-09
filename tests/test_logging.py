import pytest
from unittest.mock import patch, mock_open, MagicMock, call
import json
from src.logging import log_to_file, prepare_logtail_data, send_to_logtail


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

@patch('src.logging.socket.gethostname')
@patch('src.logging.datetime.datetime')
@patch('src.logging.os.makedirs')
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


@patch('src.logging.socket.gethostname')
def test_prepare_logtail_data(mock_hostname, sample_results):
    mock_hostname.return_value = 'test-hostname'
    
    result = prepare_logtail_data(sample_results)
    
    expected = {
        'message': '2025-07-09 10:30:45 - WiFi: TestNetwork - failed, 2/3 sites accessible',
        'hostname': 'test-hostname',
        'timestamp_utc': '2025-07-09 14:30:45',
        'timestamp_local': '2025-07-09 10:30:45',
        'timezone_local': 'America/New_York',
        'wifi_network': 'TestNetwork',
        'status': 'failed',
        'success_count': 2,
        'failed_count': 1,
        'total_count': 3,
        'success_percentage': 66.7,
        'failed_percentage': 33.3
    }
    
    assert result == expected

@patch('src.logging.socket.gethostname')
def test_prepare_logtail_data_all_success(mock_hostname):
    mock_hostname.return_value = 'test-hostname'
    
    all_success_results = {
        'timestamp': '2025-07-09 10:30:45',
        'timestamp_utc': '2025-07-09 14:30:45',
        'timezone_local': 'America/New_York',
        'wifi_network': 'TestNetwork',
        'checks': [
            {'url': 'https://google.com', 'status': 'SUCCESS', 'duration': 0.25},
            {'url': 'https://github.com', 'status': 'SUCCESS', 'duration': 0.18}
        ]
    }
    
    result = prepare_logtail_data(all_success_results)
    
    assert result['status'] == 'success'
    assert result['success_count'] == 2
    assert result['failed_count'] == 0
    assert result['success_percentage'] == 100.0
    assert result['failed_percentage'] == 0.0

@patch('src.logging.socket.gethostname')
def test_prepare_logtail_data_empty_checks(mock_hostname):
    mock_hostname.return_value = 'test-hostname'
    
    empty_results = {
        'timestamp': '2025-07-09 10:30:45',
        'timestamp_utc': '2025-07-09 14:30:45',
        'timezone_local': 'America/New_York',
        'wifi_network': 'TestNetwork',
        'checks': []
    }
    
    result = prepare_logtail_data(empty_results)
    
    assert result['success_percentage'] == 0
    assert result['failed_percentage'] == 0


def test_send_to_logtail_no_token(sample_results):
    with patch('builtins.print') as mock_print:
        send_to_logtail(sample_results)
        mock_print.assert_called_once_with("DEBUG: No LOGTAIL_TOKEN provided, skipping remote logging")

@patch('src.logging.urllib.request.urlopen')
@patch('src.logging.urllib.request.Request')
@patch('src.logging.prepare_logtail_data')
def test_send_to_logtail_success(mock_prepare, mock_request, mock_urlopen, sample_results):
    mock_prepare.return_value = {'test': 'data'}
    mock_response = MagicMock()
    mock_urlopen.return_value = mock_response
    
    send_to_logtail(sample_results, 'test-token')
    
    mock_prepare.assert_called_once_with(sample_results)
    mock_request.assert_called_once_with(
        'https://s1374986.eu-nbg-2.betterstackdata.com/',
        data=json.dumps({'test': 'data'}).encode('utf-8'),
        headers={
            'Authorization': 'Bearer test-token',
            'Content-Type': 'application/json'
        }
    )
    mock_urlopen.assert_called_once()


@patch('src.logging.urllib.request.urlopen')
@patch('src.logging.prepare_logtail_data')
def test_send_to_logtail_exception_handled(mock_prepare, mock_urlopen, sample_results):
    mock_prepare.return_value = {'test': 'data'}
    mock_urlopen.side_effect = Exception("Network error")
    
    # Should not raise exception
    send_to_logtail(sample_results, 'test-token')
    
    mock_prepare.assert_called_once_with(sample_results)