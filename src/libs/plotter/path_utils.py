"""
Path and file setup utilities for plotting scripts.
"""

import datetime
import os
import sys


def setup_logs_directory(script_path: str) -> str:
    """Set up and validate the logs directory path."""
    script_dir = os.path.dirname(os.path.abspath(script_path))
    logs_dir = os.path.join(script_dir, "..", "logs")
    
    if not os.path.exists(logs_dir):
        print(f"Error: Logs directory not found: {logs_dir}")
        sys.exit(1)
    
    return logs_dir


def generate_output_filename(hostname: str, wifi_network: str, time_range_hours: int, interval_minutes: int, output_dir: str) -> str:
    """Generate an automatic output filename with timestamp."""
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"connectivity_plot_{hostname}_{wifi_network}_{time_range_hours}h_{interval_minutes}m_{timestamp}.png"
    output_file = os.path.join(output_dir, filename)
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    return output_file


def resolve_output_path(args) -> str:
    """Resolve the final output file path based on arguments."""
    if args.output:
        return args.output
    else:
        return generate_output_filename(
            args.hostname, 
            args.wifi_network, 
            args.time_range, 
            args.interval, 
            args.output_dir
        )