import pytest
from unittest.mock import patch, MagicMock, call
import datetime
import tempfile
import os
from src.libs.plotter.chart_generator import plot_success_rates


class TestPlotSuccessRates:
    """Test cases for plot_success_rates function."""
    
    @patch('builtins.print')
    def test_plot_success_rates_empty_data(self, mock_print):
        result = plot_success_rates([], 'test-host', 'TestNetwork')
        
        assert result is None
        mock_print.assert_called_once_with("No data to plot")
    
    @patch('src.libs.plotter.chart_generator.plt')
    @patch('builtins.print')
    def test_plot_success_rates_basic_functionality(self, mock_print, mock_plt):
        # Mock plt methods
        mock_figure = MagicMock()
        mock_plt.figure.return_value = mock_figure
        mock_gca = MagicMock()
        mock_plt.gca.return_value = mock_gca
        
        # Test data
        test_data = [
            (datetime.datetime(2025, 7, 10, 12, 0), 1.0, "measured"),  # 100% success
            (datetime.datetime(2025, 7, 10, 12, 15), 0.75, "measured"),  # 75% success
            (datetime.datetime(2025, 7, 10, 12, 30), 0.5, "measured"),   # 50% success
        ]
        
        result = plot_success_rates(test_data, 'test-host', 'TestNetwork', 15)
        
        # Verify matplotlib calls
        mock_plt.figure.assert_called_once_with(figsize=(12, 6))
        assert mock_plt.bar.call_count == 2  # Two bar calls (failure and success)
        mock_plt.title.assert_called_once()
        mock_plt.xlabel.assert_called_once_with('Time', labelpad=20)
        mock_plt.ylabel.assert_called_once_with('Rate (%)')
        mock_plt.legend.assert_called_once()
        mock_plt.ylim.assert_called_once_with(0, 105)
        mock_plt.xticks.assert_called_once_with(rotation=45)
        mock_plt.grid.assert_called_once_with(True, alpha=0.3)
        mock_plt.tight_layout.assert_called_once()
        mock_plt.show.assert_called_once()
        
        assert result is None
    
    @patch('src.libs.plotter.chart_generator.plt')
    @patch('builtins.print')
    def test_plot_success_rates_with_output_file(self, mock_print, mock_plt):
        # Mock plt methods
        mock_figure = MagicMock()
        mock_plt.figure.return_value = mock_figure
        mock_gca = MagicMock()
        mock_plt.gca.return_value = mock_gca
        
        # Test data
        test_data = [
            (datetime.datetime(2025, 7, 10, 12, 0), 0.8, "measured"),
        ]
        
        output_file = '/tmp/test_plot.png'
        result = plot_success_rates(test_data, 'test-host', 'TestNetwork', 15, output_file)
        
        # Verify file operations
        mock_plt.savefig.assert_called_once_with(output_file, dpi=300, bbox_inches='tight')
        mock_plt.close.assert_called_once()
        mock_plt.show.assert_not_called()
        mock_print.assert_called_once_with(f"Plot saved to: {output_file}")
        
        assert result == output_file
    
    @patch('src.libs.plotter.chart_generator.plt')
    def test_plot_success_rates_data_processing(self, mock_plt):
        # Mock plt methods
        mock_figure = MagicMock()
        mock_plt.figure.return_value = mock_figure
        mock_gca = MagicMock()
        mock_plt.gca.return_value = mock_gca
        
        # Test data with specific success rates
        test_data = [
            (datetime.datetime(2025, 7, 10, 12, 0), 1.0, "measured"),    # 100% success
            (datetime.datetime(2025, 7, 10, 12, 15), 0.75, "measured"),  # 75% success  
            (datetime.datetime(2025, 7, 10, 12, 30), 0.0, "measured"),   # 0% success
        ]
        
        plot_success_rates(test_data, 'test-host', 'TestNetwork', 15)
        
        # Verify bar chart calls with correct data
        bar_calls = mock_plt.bar.call_args_list
        assert len(bar_calls) == 2
        
        # First call should be for failure rates
        failure_call = bar_calls[0]
        failure_rates = failure_call[0][1]  # Second argument (y values)
        expected_failure_rates = [0.0, 25.0, 100.0]  # 100-success_rate*100
        assert failure_rates == expected_failure_rates
        
        # Second call should be for success rates
        success_call = bar_calls[1]
        success_rates = success_call[0][1]  # Second argument (y values)
        expected_success_rates = [100.0, 75.0, 0.0]  # success_rate*100
        assert success_rates == expected_success_rates
    
    @patch('src.libs.plotter.chart_generator.plt')
    def test_plot_success_rates_title_formatting(self, mock_plt):
        # Mock plt methods
        mock_figure = MagicMock()
        mock_plt.figure.return_value = mock_figure
        mock_gca = MagicMock()
        mock_plt.gca.return_value = mock_gca
        
        test_data = [
            (datetime.datetime(2025, 7, 10, 12, 0), 1.0, "measured"),
        ]
        
        plot_success_rates(test_data, 'my-hostname', 'MyWiFiNetwork', 30)
        
        # Verify title contains expected information
        title_call = mock_plt.title.call_args
        title_text = title_call[0][0]
        
        assert 'my-hostname' in title_text
        assert 'MyWiFiNetwork' in title_text
        assert '30-minute intervals' in title_text
        assert 'Internet Connectivity Success/Failure Rate' in title_text
    
    @patch('src.libs.plotter.chart_generator.plt')
    def test_plot_success_rates_bar_width_calculation(self, mock_plt):
        # Mock plt methods
        mock_figure = MagicMock()
        mock_plt.figure.return_value = mock_figure
        mock_gca = MagicMock()
        mock_plt.gca.return_value = mock_gca
        
        test_data = [
            (datetime.datetime(2025, 7, 10, 12, 0), 1.0, "measured"),
        ]
        
        interval_minutes = 20
        plot_success_rates(test_data, 'test-host', 'TestNetwork', interval_minutes)
        
        # Verify bar width calculation
        bar_calls = mock_plt.bar.call_args_list
        first_bar_call = bar_calls[0]
        bar_width = first_bar_call[1]['width']  # width keyword argument
        
        expected_width = datetime.timedelta(minutes=interval_minutes * 0.8)
        assert bar_width == expected_width
    
    @patch('src.libs.plotter.chart_generator.plt')
    def test_plot_success_rates_color_scheme(self, mock_plt):
        # Mock plt methods
        mock_figure = MagicMock()
        mock_plt.figure.return_value = mock_figure
        mock_gca = MagicMock()
        mock_plt.gca.return_value = mock_gca
        
        test_data = [
            (datetime.datetime(2025, 7, 10, 12, 0), 0.5, "measured"),
        ]
        
        plot_success_rates(test_data, 'test-host', 'TestNetwork', 15)
        
        # Verify color scheme
        bar_calls = mock_plt.bar.call_args_list
        
        # Failure bars (first call)
        failure_call = bar_calls[0]
        assert failure_call[1]['color'] == '#FF6B35'  # Orange-red
        assert failure_call[1]['label'] == 'Connection Failed'
        
        # Success bars (second call)
        success_call = bar_calls[1]
        assert success_call[1]['color'] == '#66D9A6'  # Light green
        assert success_call[1]['label'] == 'Connection Success'
    
    @patch('src.libs.plotter.chart_generator.plt')
    def test_plot_success_rates_axis_formatting(self, mock_plt):
        # Mock plt methods
        mock_figure = MagicMock()
        mock_plt.figure.return_value = mock_figure
        mock_gca = MagicMock()
        mock_plt.gca.return_value = mock_gca
        mock_xaxis = MagicMock()
        mock_gca.xaxis = mock_xaxis
        
        test_data = [
            (datetime.datetime(2025, 7, 10, 12, 0), 1.0, "measured"),
        ]
        
        plot_success_rates(test_data, 'test-host', 'TestNetwork', 15)
        
        # Verify axis formatting
        mock_xaxis.set_major_formatter.assert_called_once()
        mock_xaxis.set_major_locator.assert_called_once()
        mock_plt.ylim.assert_called_once_with(0, 105)
    
    @patch('src.libs.plotter.chart_generator.plt')
    def test_plot_success_rates_single_data_point(self, mock_plt):
        # Mock plt methods
        mock_figure = MagicMock()
        mock_plt.figure.return_value = mock_figure
        mock_gca = MagicMock()
        mock_plt.gca.return_value = mock_gca
        
        # Single data point
        test_data = [
            (datetime.datetime(2025, 7, 10, 12, 0), 0.9, "measured"),  # 90% success
        ]
        
        result = plot_success_rates(test_data, 'test-host', 'TestNetwork')
        
        # Should still work with single data point
        mock_plt.figure.assert_called_once()
        assert mock_plt.bar.call_count == 2
        assert result is None
    
    @patch('src.libs.plotter.chart_generator.plt')
    def test_plot_success_rates_edge_case_values(self, mock_plt):
        # Mock plt methods
        mock_figure = MagicMock()
        mock_plt.figure.return_value = mock_figure
        mock_gca = MagicMock()
        mock_plt.gca.return_value = mock_gca
        
        # Test with edge case values
        test_data = [
            (datetime.datetime(2025, 7, 10, 12, 0), 0.0, "measured"),   # 0% success
            (datetime.datetime(2025, 7, 10, 12, 15), 1.0, "measured"),  # 100% success
        ]
        
        plot_success_rates(test_data, '', '', 1)  # Edge case parameters
        
        # Should handle edge cases without error
        mock_plt.figure.assert_called_once()
        assert mock_plt.bar.call_count == 2
    
    def test_plot_success_rates_with_real_file(self):
        """Test with actual file creation (integration test)."""
        test_data = [
            (datetime.datetime(2025, 7, 10, 12, 0), 0.8, "measured"),
        ]
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            output_file = tmp_file.name
        
        try:
            result = plot_success_rates(test_data, 'test-host', 'TestNetwork', 15, output_file)
            
            # Verify file was created
            assert result == output_file
            assert os.path.exists(output_file)
            assert os.path.getsize(output_file) > 0  # File should not be empty
            
        finally:
            # Clean up
            if os.path.exists(output_file):
                os.unlink(output_file)