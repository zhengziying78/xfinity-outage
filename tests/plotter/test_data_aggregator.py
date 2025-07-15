import pytest
from unittest.mock import patch
import datetime
from src.libs.plotter.data_aggregator import aggregate_by_interval


class TestAggregateByInterval:
    """Test cases for aggregate_by_interval function."""
    
    @patch('builtins.print')
    def test_aggregate_by_interval_empty_data(self, mock_print):
        result = aggregate_by_interval([])
        
        assert result == []
        mock_print.assert_not_called()
    
    @patch('builtins.print')
    def test_aggregate_by_interval_single_data_point(self, mock_print):
        data = [
            (datetime.datetime(2025, 7, 10, 12, 5), 0.8)
        ]
        
        result = aggregate_by_interval(data, 15)
        
        assert len(result) == 1
        # Should round down to 12:00 and add 15 minutes = 12:15
        expected_time = datetime.datetime(2025, 7, 10, 12, 15)
        assert result[0] == (expected_time, 0.8, "measured")
        mock_print.assert_called_once_with("Aggregated into 1 15-minute intervals")
    
    @patch('builtins.print')
    def test_aggregate_by_interval_multiple_same_interval(self, mock_print):
        data = [
            (datetime.datetime(2025, 7, 10, 12, 5), 0.8),
            (datetime.datetime(2025, 7, 10, 12, 10), 0.6),
            (datetime.datetime(2025, 7, 10, 12, 14), 1.0)
        ]
        
        result = aggregate_by_interval(data, 15)
        
        assert len(result) == 1
        expected_time = datetime.datetime(2025, 7, 10, 12, 15)
        expected_avg = (0.8 + 0.6 + 1.0) / 3
        assert result[0] == (expected_time, expected_avg, "measured")
        mock_print.assert_called_once_with("Aggregated into 1 15-minute intervals")
    
    @patch('builtins.print')
    def test_aggregate_by_interval_multiple_intervals(self, mock_print):
        data = [
            (datetime.datetime(2025, 7, 10, 12, 5), 0.8),    # 12:00-12:15 interval
            (datetime.datetime(2025, 7, 10, 12, 20), 0.6),   # 12:15-12:30 interval
            (datetime.datetime(2025, 7, 10, 12, 35), 1.0)    # 12:30-12:45 interval
        ]
        
        result = aggregate_by_interval(data, 15)
        
        assert len(result) == 3
        # Results should be sorted by time
        assert result[0] == (datetime.datetime(2025, 7, 10, 12, 15), 0.8, "measured")
        assert result[1] == (datetime.datetime(2025, 7, 10, 12, 30), 0.6, "measured")
        assert result[2] == (datetime.datetime(2025, 7, 10, 12, 45), 1.0, "measured")
        mock_print.assert_called_once_with("Aggregated into 3 15-minute intervals")
    
    @patch('builtins.print')
    def test_aggregate_by_interval_custom_interval(self, mock_print):
        data = [
            (datetime.datetime(2025, 7, 10, 12, 5), 0.8),    # 12:00-12:10 interval
            (datetime.datetime(2025, 7, 10, 12, 15), 0.6),   # 12:10-12:20 interval
            (datetime.datetime(2025, 7, 10, 12, 25), 1.0)    # 12:20-12:30 interval
        ]
        
        result = aggregate_by_interval(data, 10)  # 10-minute intervals
        
        assert len(result) == 3
        assert result[0] == (datetime.datetime(2025, 7, 10, 12, 10), 0.8, "measured")
        assert result[1] == (datetime.datetime(2025, 7, 10, 12, 20), 0.6, "measured")
        assert result[2] == (datetime.datetime(2025, 7, 10, 12, 30), 1.0, "measured")
        mock_print.assert_called_once_with("Aggregated into 3 10-minute intervals")
    
    @patch('builtins.print')
    def test_aggregate_by_interval_hour_boundaries(self, mock_print):
        data = [
            (datetime.datetime(2025, 7, 10, 11, 55), 0.8),   # 11:45-12:00 interval
            (datetime.datetime(2025, 7, 10, 12, 5), 0.6),    # 12:00-12:15 interval
            (datetime.datetime(2025, 7, 10, 12, 35), 1.0)    # 12:30-12:45 interval
        ]
        
        result = aggregate_by_interval(data, 15)
        
        assert len(result) == 4
        # Should handle hour boundaries correctly
        assert result[0] == (datetime.datetime(2025, 7, 10, 12, 0), 0.8, "measured")   # 11:55 rounds to 11:45, +15 = 12:00
        assert result[1] == (datetime.datetime(2025, 7, 10, 12, 15), 0.6, "measured")  # 12:05 rounds to 12:00, +15 = 12:15
        assert result[2] == (datetime.datetime(2025, 7, 10, 12, 30), 0.0, "missing")   # Missing interval filled in
        assert result[3] == (datetime.datetime(2025, 7, 10, 12, 45), 1.0, "measured")  # 12:35 rounds to 12:30, +15 = 12:45
    
    @patch('builtins.print')
    def test_aggregate_by_interval_exact_boundaries(self, mock_print):
        data = [
            (datetime.datetime(2025, 7, 10, 12, 0), 0.8),    # Exactly on 15-minute boundary
            (datetime.datetime(2025, 7, 10, 12, 15), 0.6),   # Exactly on 15-minute boundary
            (datetime.datetime(2025, 7, 10, 12, 30), 1.0)    # Exactly on 15-minute boundary
        ]
        
        result = aggregate_by_interval(data, 15)
        
        assert len(result) == 3
        assert result[0] == (datetime.datetime(2025, 7, 10, 12, 15), 0.8, "measured")
        assert result[1] == (datetime.datetime(2025, 7, 10, 12, 30), 0.6, "measured")
        assert result[2] == (datetime.datetime(2025, 7, 10, 12, 45), 1.0, "measured")
    
    @patch('builtins.print')
    def test_aggregate_by_interval_seconds_microseconds_ignored(self, mock_print):
        data = [
            (datetime.datetime(2025, 7, 10, 12, 5, 30, 123456), 0.8),  # 12:05:30.123456
            (datetime.datetime(2025, 7, 10, 12, 10, 45, 789012), 0.6)  # 12:10:45.789012
        ]
        
        result = aggregate_by_interval(data, 15)
        
        assert len(result) == 1
        expected_time = datetime.datetime(2025, 7, 10, 12, 15)  # Clean time without seconds/microseconds
        expected_avg = (0.8 + 0.6) / 2
        assert result[0] == (expected_time, expected_avg, "measured")
    
    @patch('builtins.print')
    def test_aggregate_by_interval_unsorted_input(self, mock_print):
        # Input data not in chronological order
        data = [
            (datetime.datetime(2025, 7, 10, 12, 35), 1.0),   # Latest
            (datetime.datetime(2025, 7, 10, 12, 5), 0.8),    # Earliest
            (datetime.datetime(2025, 7, 10, 12, 20), 0.6)    # Middle
        ]
        
        result = aggregate_by_interval(data, 15)
        
        assert len(result) == 3
        # Results should be sorted by time regardless of input order
        assert result[0] == (datetime.datetime(2025, 7, 10, 12, 15), 0.8, "measured")
        assert result[1] == (datetime.datetime(2025, 7, 10, 12, 30), 0.6, "measured")
        assert result[2] == (datetime.datetime(2025, 7, 10, 12, 45), 1.0, "measured")
    
    @patch('builtins.print')
    def test_aggregate_by_interval_mixed_intervals_same_bucket(self, mock_print):
        data = [
            (datetime.datetime(2025, 7, 10, 12, 1), 0.2),
            (datetime.datetime(2025, 7, 10, 12, 3), 0.4),
            (datetime.datetime(2025, 7, 10, 12, 7), 0.6),
            (datetime.datetime(2025, 7, 10, 12, 14), 0.8)
        ]
        
        result = aggregate_by_interval(data, 15)
        
        assert len(result) == 1
        expected_time = datetime.datetime(2025, 7, 10, 12, 15)
        expected_avg = (0.2 + 0.4 + 0.6 + 0.8) / 4
        assert result[0] == (expected_time, expected_avg, "measured")
    
    @patch('builtins.print')
    def test_aggregate_by_interval_edge_case_values(self, mock_print):
        data = [
            (datetime.datetime(2025, 7, 10, 12, 5), 0.0),    # 0% success
            (datetime.datetime(2025, 7, 10, 12, 10), 1.0),   # 100% success
            (datetime.datetime(2025, 7, 10, 12, 20), 0.5)    # 50% success
        ]
        
        result = aggregate_by_interval(data, 15)
        
        assert len(result) == 2
        # First interval: average of 0.0 and 1.0
        assert result[0] == (datetime.datetime(2025, 7, 10, 12, 15), 0.5, "measured")
        # Second interval: just 0.5
        assert result[1] == (datetime.datetime(2025, 7, 10, 12, 30), 0.5, "measured")
    
    @patch('builtins.print')
    def test_aggregate_by_interval_large_interval(self, mock_print):
        data = [
            (datetime.datetime(2025, 7, 10, 12, 5), 0.8),
            (datetime.datetime(2025, 7, 10, 12, 35), 0.6),
            (datetime.datetime(2025, 7, 10, 13, 5), 1.0)
        ]
        
        result = aggregate_by_interval(data, 60)  # 60-minute intervals
        
        assert len(result) == 2
        # 12:05 rounds to 12:00, +60 = 13:00
        # 12:35 rounds to 12:00, +60 = 13:00 (same interval)
        # 13:05 rounds to 13:00, +60 = 14:00
        expected_avg_first = (0.8 + 0.6) / 2
        assert result[0] == (datetime.datetime(2025, 7, 10, 13, 0), expected_avg_first, "measured")
        assert result[1] == (datetime.datetime(2025, 7, 10, 14, 0), 1.0, "measured")
        mock_print.assert_called_once_with("Aggregated into 2 60-minute intervals")
    
    @patch('builtins.print')
    def test_aggregate_by_interval_one_minute_interval(self, mock_print):
        data = [
            (datetime.datetime(2025, 7, 10, 12, 5, 10), 0.8),
            (datetime.datetime(2025, 7, 10, 12, 5, 30), 0.6),
            (datetime.datetime(2025, 7, 10, 12, 6, 45), 1.0)
        ]
        
        result = aggregate_by_interval(data, 1)  # 1-minute intervals
        
        assert len(result) == 2
        # Both 12:05:10 and 12:05:30 should be in the 12:05-12:06 interval
        expected_avg_first = (0.8 + 0.6) / 2
        assert result[0] == (datetime.datetime(2025, 7, 10, 12, 6), expected_avg_first, "measured")
        assert result[1] == (datetime.datetime(2025, 7, 10, 12, 7), 1.0, "measured")
        mock_print.assert_called_once_with("Aggregated into 2 1-minute intervals")