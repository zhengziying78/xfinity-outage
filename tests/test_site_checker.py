import pytest
from unittest.mock import patch, MagicMock
import urllib.error
import time
from concurrent.futures import Future
from src.site_checker import check_single_site, check_connectivity, DEFAULT_WEBSITES


class TestSiteChecker:

    @patch('src.site_checker.time.time')
    @patch('src.site_checker.urllib.request.urlopen')
    def test_check_single_site_success(self, mock_urlopen, mock_time):
        mock_time.side_effect = [1000.0, 1000.5]  # Start and end times
        mock_response = MagicMock()
        mock_response.getcode.return_value = 200
        mock_urlopen.return_value = mock_response
        
        result = check_single_site('https://example.com')
        
        assert result == {
            'url': 'https://example.com',
            'status': 'SUCCESS',
            'duration': 0.5
        }
        mock_urlopen.assert_called_once_with('https://example.com', timeout=5)

    @patch('src.site_checker.time.time')
    @patch('src.site_checker.urllib.request.urlopen')
    def test_check_single_site_http_error(self, mock_urlopen, mock_time):
        mock_time.side_effect = [1000.0, 1000.3]
        mock_response = MagicMock()
        mock_response.getcode.return_value = 404
        mock_urlopen.return_value = mock_response
        
        result = check_single_site('https://example.com')
        
        assert result['url'] == 'https://example.com'
        assert result['status'] == 'HTTP_404'
        assert abs(result['duration'] - 0.3) < 0.001  # Allow for floating point precision

    @patch('src.site_checker.time.time')
    @patch('src.site_checker.urllib.request.urlopen')
    def test_check_single_site_url_error(self, mock_urlopen, mock_time):
        mock_time.side_effect = [1000.0, 1005.0]
        mock_urlopen.side_effect = urllib.error.URLError("Name or service not known")
        
        result = check_single_site('https://nonexistent.com')
        
        assert result['url'] == 'https://nonexistent.com'
        assert result['status'].startswith('FAILED: ')
        assert 'Name or service not known' in result['status']
        assert result['duration'] == 5.0

    @patch('src.site_checker.time.time')
    @patch('src.site_checker.urllib.request.urlopen')
    def test_check_single_site_generic_exception(self, mock_urlopen, mock_time):
        mock_time.side_effect = [1000.0, 1002.0]
        mock_urlopen.side_effect = Exception("Connection timeout")
        
        result = check_single_site('https://example.com')
        
        assert result['url'] == 'https://example.com'
        assert result['status'] == 'FAILED: Connection timeout'
        assert result['duration'] == 2.0

    @patch('src.site_checker.get_wifi_network')
    @patch('src.site_checker.get_timestamp_info')
    @patch('src.site_checker.ThreadPoolExecutor')
    def test_check_connectivity_default_websites(self, mock_executor, mock_timestamp, mock_wifi):
        # Mock dependencies
        mock_timestamp.return_value = {
            'timestamp_local': '2025-07-09 10:30:45',
            'timestamp_utc': '2025-07-09 14:30:45',
            'timezone_local': 'America/New_York'
        }
        mock_wifi.return_value = 'TestNetwork'
        
        # Mock thread pool executor
        mock_executor_instance = MagicMock()
        mock_executor.return_value.__enter__.return_value = mock_executor_instance
        
        # Mock futures
        mock_futures = []
        for i, url in enumerate(DEFAULT_WEBSITES):
            future = MagicMock()
            future.result.return_value = {
                'url': url,
                'status': 'SUCCESS',
                'duration': 0.1 + i * 0.1
            }
            mock_futures.append(future)
        
        mock_executor_instance.submit.side_effect = mock_futures
        
        result = check_connectivity()
        
        assert result['timestamp'] == '2025-07-09 10:30:45'
        assert result['timestamp_utc'] == '2025-07-09 14:30:45'
        assert result['timezone_local'] == 'America/New_York'
        assert result['wifi_network'] == 'TestNetwork'
        assert len(result['checks']) == len(DEFAULT_WEBSITES)
        
        # Verify all default websites were checked
        for i, check in enumerate(result['checks']):
            assert check['url'] == DEFAULT_WEBSITES[i]
            assert check['status'] == 'SUCCESS'

    @patch('src.site_checker.get_wifi_network')
    @patch('src.site_checker.get_timestamp_info')
    @patch('src.site_checker.ThreadPoolExecutor')
    def test_check_connectivity_custom_websites(self, mock_executor, mock_timestamp, mock_wifi):
        custom_websites = ['https://test1.com', 'https://test2.com']
        
        mock_timestamp.return_value = {
            'timestamp_local': '2025-07-09 10:30:45',
            'timestamp_utc': '2025-07-09 14:30:45',
            'timezone_local': 'America/New_York'
        }
        mock_wifi.return_value = 'TestNetwork'
        
        mock_executor_instance = MagicMock()
        mock_executor.return_value.__enter__.return_value = mock_executor_instance
        
        mock_futures = []
        for i, url in enumerate(custom_websites):
            future = MagicMock()
            future.result.return_value = {
                'url': url,
                'status': 'SUCCESS',
                'duration': 0.2
            }
            mock_futures.append(future)
        
        mock_executor_instance.submit.side_effect = mock_futures
        
        result = check_connectivity(custom_websites)
        
        assert len(result['checks']) == 2
        assert result['checks'][0]['url'] == 'https://test1.com'
        assert result['checks'][1]['url'] == 'https://test2.com'

    @patch('src.site_checker.get_wifi_network')
    @patch('src.site_checker.get_timestamp_info')
    @patch('src.site_checker.ThreadPoolExecutor')
    def test_check_connectivity_with_failed_checks(self, mock_executor, mock_timestamp, mock_wifi):
        websites = ['https://good.com', 'https://bad.com']
        
        mock_timestamp.return_value = {
            'timestamp_local': '2025-07-09 10:30:45',
            'timestamp_utc': '2025-07-09 14:30:45',
            'timezone_local': 'America/New_York'
        }
        mock_wifi.return_value = 'TestNetwork'
        
        mock_executor_instance = MagicMock()
        mock_executor.return_value.__enter__.return_value = mock_executor_instance
        
        # Mock one successful and one failed check
        future_success = MagicMock()
        future_success.result.return_value = {
            'url': 'https://good.com',
            'status': 'SUCCESS',
            'duration': 0.1
        }
        
        future_failed = MagicMock()
        future_failed.result.return_value = {
            'url': 'https://bad.com',
            'status': 'FAILED: Connection timeout',
            'duration': 5.0
        }
        
        mock_executor_instance.submit.side_effect = [future_success, future_failed]
        
        result = check_connectivity(websites)
        
        assert len(result['checks']) == 2
        assert result['checks'][0]['status'] == 'SUCCESS'
        assert result['checks'][1]['status'] == 'FAILED: Connection timeout'

    @patch('src.site_checker.get_wifi_network')
    @patch('src.site_checker.get_timestamp_info')
    @patch('src.site_checker.ThreadPoolExecutor')
    def test_check_connectivity_thread_exception(self, mock_executor, mock_timestamp, mock_wifi):
        websites = ['https://example.com']
        
        mock_timestamp.return_value = {
            'timestamp_local': '2025-07-09 10:30:45',
            'timestamp_utc': '2025-07-09 14:30:45',
            'timezone_local': 'America/New_York'
        }
        mock_wifi.return_value = 'TestNetwork'
        
        mock_executor_instance = MagicMock()
        mock_executor.return_value.__enter__.return_value = mock_executor_instance
        
        # Mock future that raises exception
        future = MagicMock()
        future.result.side_effect = Exception("Thread execution failed")
        mock_executor_instance.submit.return_value = future
        
        result = check_connectivity(websites)
        
        assert len(result['checks']) == 1
        assert result['checks'][0]['url'] == 'https://example.com'
        assert result['checks'][0]['status'] == 'FAILED: Thread execution failed'
        assert result['checks'][0]['duration'] == 0.0

    @patch('src.site_checker.get_wifi_network')
    @patch('src.site_checker.get_timestamp_info')
    @patch('src.site_checker.ThreadPoolExecutor')
    def test_check_connectivity_result_ordering(self, mock_executor, mock_timestamp, mock_wifi):
        websites = ['https://z.com', 'https://a.com', 'https://m.com']
        
        mock_timestamp.return_value = {
            'timestamp_local': '2025-07-09 10:30:45',
            'timestamp_utc': '2025-07-09 14:30:45',
            'timezone_local': 'America/New_York'
        }
        mock_wifi.return_value = 'TestNetwork'
        
        mock_executor_instance = MagicMock()
        mock_executor.return_value.__enter__.return_value = mock_executor_instance
        
        # Create futures that return results in different order than submitted
        futures = []
        for url in websites:
            future = MagicMock()
            future.result.return_value = {
                'url': url,
                'status': 'SUCCESS',
                'duration': 0.1
            }
            futures.append(future)
        
        mock_executor_instance.submit.side_effect = futures
        
        result = check_connectivity(websites)
        
        # Results should be ordered by original website order
        assert len(result['checks']) == 3
        assert result['checks'][0]['url'] == 'https://z.com'
        assert result['checks'][1]['url'] == 'https://a.com'
        assert result['checks'][2]['url'] == 'https://m.com'

    def test_default_websites_constant(self):
        """Test that DEFAULT_WEBSITES contains expected values."""
        assert isinstance(DEFAULT_WEBSITES, list)
        assert len(DEFAULT_WEBSITES) > 0
        assert 'https://github.com' in DEFAULT_WEBSITES
        assert 'https://google.com' in DEFAULT_WEBSITES
        assert 'https://apple.com' in DEFAULT_WEBSITES
        assert 'https://reddit.com' in DEFAULT_WEBSITES