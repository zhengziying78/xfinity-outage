"""
Dependency checking functionality for plotting scripts.
"""

import sys


def check_required_dependencies():
    """Check that all required packages are installed."""
    try:
        import matplotlib.pyplot
        return True
    except ImportError as e:
        print(f"Error: Required packages not installed. Please install: {e}")
        print("Try: pip install matplotlib")
        return False


def exit_if_dependencies_missing():
    """Check dependencies and exit if any are missing."""
    if not check_required_dependencies():
        sys.exit(1)