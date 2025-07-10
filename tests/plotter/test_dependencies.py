import pytest
from unittest.mock import patch, MagicMock
import sys
from src.libs.plotter.dependencies import check_required_dependencies, exit_if_dependencies_missing


class TestCheckRequiredDependencies:
    """Test cases for check_required_dependencies function."""
    
    @patch('builtins.print')
    def test_check_required_dependencies_success(self, mock_print):
        # Test the real function - matplotlib should be available
        result = check_required_dependencies()
        
        assert result is True
        # Should not print anything on success
        mock_print.assert_not_called()
    
    def test_check_required_dependencies_real_import(self):
        """Test with real matplotlib import (should pass if matplotlib is installed)."""
        result = check_required_dependencies()
        
        # This should be True since matplotlib should be available in the test environment
        assert result is True


class TestExitIfDependenciesMissing:
    """Test cases for exit_if_dependencies_missing function."""
    
    @patch('src.libs.plotter.dependencies.check_required_dependencies')
    def test_exit_if_dependencies_missing_success(self, mock_check):
        # Mock successful dependency check
        mock_check.return_value = True
        
        # Should not raise SystemExit
        exit_if_dependencies_missing()
        
        mock_check.assert_called_once()
    
    @patch('src.libs.plotter.dependencies.check_required_dependencies')
    @patch('sys.exit')
    def test_exit_if_dependencies_missing_failure(self, mock_exit, mock_check):
        # Mock failed dependency check
        mock_check.return_value = False
        
        exit_if_dependencies_missing()
        
        mock_check.assert_called_once()
        mock_exit.assert_called_once_with(1)
    
    @patch('src.libs.plotter.dependencies.check_required_dependencies')
    def test_exit_if_dependencies_missing_with_real_exit(self, mock_check):
        # Mock failed dependency check
        mock_check.return_value = False
        
        # Should raise SystemExit
        with pytest.raises(SystemExit) as exc_info:
            exit_if_dependencies_missing()
        
        assert exc_info.value.code == 1
        mock_check.assert_called_once()
    
    @patch('src.libs.plotter.dependencies.check_required_dependencies')
    @patch('builtins.print')
    def test_exit_if_dependencies_missing_prints_error_before_exit(self, mock_print, mock_check):
        # Mock failed dependency check that prints error messages
        def side_effect():
            print("Error: Required packages not installed. Please install: No module named 'matplotlib'")
            print("Try: pip install matplotlib")
            return False
        
        mock_check.side_effect = side_effect
        
        with pytest.raises(SystemExit):
            exit_if_dependencies_missing()
        
        # Verify error messages were printed
        assert mock_print.call_count == 2