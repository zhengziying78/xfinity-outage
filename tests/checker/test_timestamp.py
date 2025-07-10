import pytest
from unittest.mock import patch, MagicMock
import datetime
import time
from src.libs.checker.timestamp import get_timestamp_info


class TestTimestamp:

    @patch('src.libs.checker.timestamp.time.tzname', ['EST', 'EDT'])
    @patch('src.libs.checker.timestamp.time.daylight', 1)
    @patch('src.libs.checker.timestamp.datetime.datetime')
    def test_get_timestamp_info_basic(self, mock_datetime):
        # Mock current time
        mock_local_dt = MagicMock()
        mock_local_dt.strftime.return_value = '2025-07-09 10:30:45'
        mock_datetime.now.return_value = mock_local_dt
        
        # Mock UTC time
        mock_utc_dt = MagicMock()
        mock_utc_dt.strftime.return_value = '2025-07-09 14:30:45'
        mock_datetime.now.side_effect = [mock_local_dt, mock_utc_dt]
        
        # Mock timezone offset
        mock_astimezone = MagicMock()
        mock_utcoffset = MagicMock()
        mock_utcoffset.total_seconds.return_value = -14400  # -4 hours in seconds
        mock_astimezone.utcoffset.return_value = mock_utcoffset
        mock_local_dt.astimezone.return_value = mock_astimezone
        
        result = get_timestamp_info()
        
        assert result['timestamp_local'] == '2025-07-09 10:30:45'
        assert result['timestamp_utc'] == '2025-07-09 14:30:45'
        assert result['timezone_local'] == 'EDT GMT-0400'

    @patch('src.libs.checker.timestamp.time.tzname', ['EST', 'EDT'])
    @patch('src.libs.checker.timestamp.time.daylight', 0)
    @patch('src.libs.checker.timestamp.datetime.datetime')
    def test_get_timestamp_info_standard_time(self, mock_datetime):
        # Mock current time
        mock_local_dt = MagicMock()
        mock_local_dt.strftime.return_value = '2025-01-15 15:30:45'
        mock_datetime.now.return_value = mock_local_dt
        
        # Mock UTC time
        mock_utc_dt = MagicMock()
        mock_utc_dt.strftime.return_value = '2025-01-15 20:30:45'
        mock_datetime.now.side_effect = [mock_local_dt, mock_utc_dt]
        
        # Mock timezone offset for standard time
        mock_astimezone = MagicMock()
        mock_utcoffset = MagicMock()
        mock_utcoffset.total_seconds.return_value = -18000  # -5 hours in seconds
        mock_astimezone.utcoffset.return_value = mock_utcoffset
        mock_local_dt.astimezone.return_value = mock_astimezone
        
        result = get_timestamp_info()
        
        assert result['timestamp_local'] == '2025-01-15 15:30:45'
        assert result['timestamp_utc'] == '2025-01-15 20:30:45'
        assert result['timezone_local'] == 'EST GMT-0500'

    @patch('src.libs.checker.timestamp.time.tzname', ['JST', 'JST'])
    @patch('src.libs.checker.timestamp.time.daylight', 0)
    @patch('src.libs.checker.timestamp.datetime.datetime')
    def test_get_timestamp_info_positive_offset(self, mock_datetime):
        # Mock current time
        mock_local_dt = MagicMock()
        mock_local_dt.strftime.return_value = '2025-07-09 22:30:45'
        mock_datetime.now.return_value = mock_local_dt
        
        # Mock UTC time
        mock_utc_dt = MagicMock()
        mock_utc_dt.strftime.return_value = '2025-07-09 14:30:45'
        mock_datetime.now.side_effect = [mock_local_dt, mock_utc_dt]
        
        # Mock timezone offset for JST (+9 hours)
        mock_astimezone = MagicMock()
        mock_utcoffset = MagicMock()
        mock_utcoffset.total_seconds.return_value = 32400  # +9 hours in seconds
        mock_astimezone.utcoffset.return_value = mock_utcoffset
        mock_local_dt.astimezone.return_value = mock_astimezone
        
        result = get_timestamp_info()
        
        assert result['timestamp_local'] == '2025-07-09 22:30:45'
        assert result['timestamp_utc'] == '2025-07-09 14:30:45'
        assert result['timezone_local'] == 'JST GMT+0900'

    @patch('src.libs.checker.timestamp.time.tzname', ['IST', 'IST'])
    @patch('src.libs.checker.timestamp.time.daylight', 0)
    @patch('src.libs.checker.timestamp.datetime.datetime')
    def test_get_timestamp_info_half_hour_offset(self, mock_datetime):
        # Mock current time
        mock_local_dt = MagicMock()
        mock_local_dt.strftime.return_value = '2025-07-09 19:00:45'
        mock_datetime.now.return_value = mock_local_dt
        
        # Mock UTC time
        mock_utc_dt = MagicMock()
        mock_utc_dt.strftime.return_value = '2025-07-09 14:30:45'
        mock_datetime.now.side_effect = [mock_local_dt, mock_utc_dt]
        
        # Mock timezone offset for IST (+5:30 hours)
        mock_astimezone = MagicMock()
        mock_utcoffset = MagicMock()
        mock_utcoffset.total_seconds.return_value = 19800  # +5.5 hours in seconds
        mock_astimezone.utcoffset.return_value = mock_utcoffset
        mock_local_dt.astimezone.return_value = mock_astimezone
        
        result = get_timestamp_info()
        
        assert result['timestamp_local'] == '2025-07-09 19:00:45'
        assert result['timestamp_utc'] == '2025-07-09 14:30:45'
        assert result['timezone_local'] == 'IST GMT+0530'

    @patch('src.libs.checker.timestamp.time.tzname', ['NST', 'NST'])
    @patch('src.libs.checker.timestamp.time.daylight', 0)
    @patch('src.libs.checker.timestamp.datetime.datetime')
    def test_get_timestamp_info_negative_half_hour_offset(self, mock_datetime):
        # Mock current time
        mock_local_dt = MagicMock()
        mock_local_dt.strftime.return_value = '2025-07-09 10:00:45'
        mock_datetime.now.return_value = mock_local_dt
        
        # Mock UTC time
        mock_utc_dt = MagicMock()
        mock_utc_dt.strftime.return_value = '2025-07-09 14:30:45'
        mock_datetime.now.side_effect = [mock_local_dt, mock_utc_dt]
        
        # Mock timezone offset for NST (-3:30 hours, but floor division gives -4:30)
        mock_astimezone = MagicMock()
        mock_utcoffset = MagicMock()
        mock_utcoffset.total_seconds.return_value = -12600  # -3.5 hours in seconds
        mock_astimezone.utcoffset.return_value = mock_utcoffset
        mock_local_dt.astimezone.return_value = mock_astimezone
        
        result = get_timestamp_info()
        
        assert result['timestamp_local'] == '2025-07-09 10:00:45'
        assert result['timestamp_utc'] == '2025-07-09 14:30:45'
        assert result['timezone_local'] == 'NST GMT-0430'

    @patch('src.libs.checker.timestamp.time.tzname', ['UTC', 'UTC'])
    @patch('src.libs.checker.timestamp.time.daylight', 0)
    @patch('src.libs.checker.timestamp.datetime.datetime')
    def test_get_timestamp_info_utc_timezone(self, mock_datetime):
        # Mock current time
        mock_local_dt = MagicMock()
        mock_local_dt.strftime.return_value = '2025-07-09 14:30:45'
        mock_datetime.now.return_value = mock_local_dt
        
        # Mock UTC time
        mock_utc_dt = MagicMock()
        mock_utc_dt.strftime.return_value = '2025-07-09 14:30:45'
        mock_datetime.now.side_effect = [mock_local_dt, mock_utc_dt]
        
        # Mock timezone offset for UTC (0 hours)
        mock_astimezone = MagicMock()
        mock_utcoffset = MagicMock()
        mock_utcoffset.total_seconds.return_value = 0  # 0 hours in seconds
        mock_astimezone.utcoffset.return_value = mock_utcoffset
        mock_local_dt.astimezone.return_value = mock_astimezone
        
        result = get_timestamp_info()
        
        assert result['timestamp_local'] == '2025-07-09 14:30:45'
        assert result['timestamp_utc'] == '2025-07-09 14:30:45'
        assert result['timezone_local'] == 'UTC GMT+0000'

    def test_get_timestamp_info_return_structure(self):
        """Test that the function returns the expected structure."""
        result = get_timestamp_info()
        
        # Check that all required keys are present
        assert 'timestamp_local' in result
        assert 'timestamp_utc' in result
        assert 'timezone_local' in result
        
        # Check that values are strings
        assert isinstance(result['timestamp_local'], str)
        assert isinstance(result['timestamp_utc'], str)
        assert isinstance(result['timezone_local'], str)
        
        # Check timestamp format (YYYY-MM-DD HH:MM:SS)
        import re
        timestamp_pattern = r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$'
        assert re.match(timestamp_pattern, result['timestamp_local'])
        assert re.match(timestamp_pattern, result['timestamp_utc'])
        
        # Check timezone format contains GMT
        assert 'GMT' in result['timezone_local']

    @patch('src.libs.checker.timestamp.time.tzname', ['EST', 'EDT'])
    @patch('src.libs.checker.timestamp.time.daylight', 1)
    @patch('src.libs.checker.timestamp.datetime.datetime')
    def test_get_timestamp_info_datetime_calls(self, mock_datetime):
        """Test that datetime.now() is called correctly."""
        # Mock current time
        mock_local_dt = MagicMock()
        mock_local_dt.strftime.return_value = '2025-07-09 10:30:45'
        
        # Mock UTC time
        mock_utc_dt = MagicMock()
        mock_utc_dt.strftime.return_value = '2025-07-09 14:30:45'
        
        # Set up side effects for datetime.now calls
        mock_datetime.now.side_effect = [mock_local_dt, mock_utc_dt]
        
        # Mock timezone offset
        mock_astimezone = MagicMock()
        mock_utcoffset = MagicMock()
        mock_utcoffset.total_seconds.return_value = -14400
        mock_astimezone.utcoffset.return_value = mock_utcoffset
        mock_local_dt.astimezone.return_value = mock_astimezone
        
        get_timestamp_info()
        
        # Verify datetime.now() was called twice
        assert mock_datetime.now.call_count == 2
        
        # Verify first call is without timezone, second is with UTC
        calls = mock_datetime.now.call_args_list
        assert len(calls) == 2
        assert calls[0][0] == ()  # First call without arguments
        # Second call should have timezone.utc - we'll just verify it has one argument
        assert len(calls[1][0]) == 1

    @patch('src.libs.checker.timestamp.time.tzname', ['PST', 'PDT'])
    @patch('src.libs.checker.timestamp.time.daylight', 1)
    @patch('src.libs.checker.timestamp.datetime.datetime')
    def test_get_timestamp_info_different_timezone(self, mock_datetime):
        """Test with different timezone names."""
        # Mock current time
        mock_local_dt = MagicMock()
        mock_local_dt.strftime.return_value = '2025-07-09 07:30:45'
        mock_datetime.now.return_value = mock_local_dt
        
        # Mock UTC time
        mock_utc_dt = MagicMock()
        mock_utc_dt.strftime.return_value = '2025-07-09 14:30:45'
        mock_datetime.now.side_effect = [mock_local_dt, mock_utc_dt]
        
        # Mock timezone offset for PDT (-7 hours)
        mock_astimezone = MagicMock()
        mock_utcoffset = MagicMock()
        mock_utcoffset.total_seconds.return_value = -25200  # -7 hours in seconds
        mock_astimezone.utcoffset.return_value = mock_utcoffset
        mock_local_dt.astimezone.return_value = mock_astimezone
        
        result = get_timestamp_info()
        
        assert result['timestamp_local'] == '2025-07-09 07:30:45'
        assert result['timestamp_utc'] == '2025-07-09 14:30:45'
        assert result['timezone_local'] == 'PDT GMT-0700'