#!/usr/bin/env python3
"""
Connectivity Data Plotting Script

This script generates a dot line graph showing success rates over time
for connectivity logs from the current machine's hostname.
"""

import datetime
import glob
import os
import re
import socket
import sys
from typing import List, Tuple
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd


def get_hostname() -> str:
    """Get the current machine's hostname."""
    return socket.gethostname()


def parse_log_files(logs_dir: str, hostname: str, wifi_filter: str = "GoTitansFC") -> List[Tuple[datetime.datetime, float]]:
    """Parse log files and extract success rate data for specified WiFi network."""
    data = []
    
    # Find all log files for this hostname
    hostname_dir = os.path.join(logs_dir, hostname)
    if not os.path.exists(hostname_dir):
        print(f"Error: Hostname directory not found: {hostname_dir}")
        return data
    
    log_files = glob.glob(os.path.join(hostname_dir, "connectivity_log_*.txt"))
    if not log_files:
        print(f"Error: No log files found in {hostname_dir}")
        return data
    
    # Sort log files by date
    log_files.sort()
    
    # Pattern to match summary lines
    summary_pattern = re.compile(
        r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) - WiFi: ([^-]+) - Internet: (\d+)/(\d+) sites accessible'
    )
    
    print(f"Parsing {len(log_files)} log files...")
    
    for log_file in log_files:
        print(f"Processing: {os.path.basename(log_file)}")
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    match = summary_pattern.match(line)
                    
                    if match:
                        timestamp_str = match.group(1)
                        wifi_network = match.group(2).strip()
                        accessible_sites = int(match.group(3))
                        total_sites = int(match.group(4))
                        
                        # Filter by WiFi network
                        if wifi_network == wifi_filter:
                            timestamp = datetime.datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                            success_rate = accessible_sites / total_sites if total_sites > 0 else 0
                            data.append((timestamp, success_rate))
        
        except Exception as e:
            print(f"Error parsing {log_file}: {e}")
    
    # Sort by timestamp
    data.sort(key=lambda x: x[0])
    
    # Filter to last 72 hours if we have more data
    if data:
        latest_time = data[-1][0]
        cutoff_time = latest_time - datetime.timedelta(hours=72)
        data = [(ts, rate) for ts, rate in data if ts >= cutoff_time]
    
    print(f"Found {len(data)} data points for WiFi network '{wifi_filter}'")
    return data


def aggregate_by_half_hour(data: List[Tuple[datetime.datetime, float]]) -> List[Tuple[datetime.datetime, float]]:
    """Aggregate data into 30-minute intervals."""
    if not data:
        return []
    
    # Group data by 30-minute intervals
    intervals = {}
    
    for timestamp, success_rate in data:
        # Calculate the interval boundary (round down to nearest 30-minute mark)
        minute = timestamp.minute
        if minute < 30:
            interval_start = timestamp.replace(minute=0, second=0, microsecond=0)
        else:
            interval_start = timestamp.replace(minute=30, second=0, microsecond=0)
        
        # The interval end is 30 minutes later
        interval_end = interval_start + datetime.timedelta(minutes=30)
        
        # Use interval_end as the key (the dot position)
        if interval_end not in intervals:
            intervals[interval_end] = []
        
        intervals[interval_end].append(success_rate)
    
    # Calculate average success rate for each interval
    aggregated_data = []
    for interval_end in sorted(intervals.keys()):
        success_rates = intervals[interval_end]
        avg_success_rate = sum(success_rates) / len(success_rates)
        aggregated_data.append((interval_end, avg_success_rate))
    
    print(f"Aggregated into {len(aggregated_data)} 30-minute intervals")
    return aggregated_data


def plot_success_rates(data: List[Tuple[datetime.datetime, float]], hostname: str, wifi_network: str, output_file: str = None):
    """Plot success rates as a dot line graph."""
    if not data:
        print("No data to plot")
        return
    
    # Extract timestamps and success rates
    timestamps = [item[0] for item in data]
    success_rates = [item[1] * 100 for item in data]  # Convert to percentage
    
    # Create the plot
    plt.figure(figsize=(12, 6))
    
    # Plot dots
    plt.plot(timestamps, success_rates, 'o-', markersize=6, linewidth=1, alpha=0.7)
    
    # Set labels and title
    plt.title(f'Internet Connectivity Success Rate - {hostname} ({wifi_network})')
    plt.xlabel('Time')
    plt.ylabel('Success Rate (%)')
    
    # Set y-axis to 0-100%
    plt.ylim(0, 105)
    
    # Format x-axis
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
    plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=6))
    plt.xticks(rotation=45)
    
    # Add grid
    plt.grid(True, alpha=0.3)
    
    # Tight layout
    plt.tight_layout()
    
    # Save or show
    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Plot saved to: {output_file}")
    else:
        plt.show()


def main():
    """Main function."""
    # Check for required packages
    try:
        import matplotlib.pyplot as plt
        import pandas as pd
    except ImportError as e:
        print(f"Error: Required packages not installed. Please install: {e}")
        print("Try: pip install matplotlib pandas")
        sys.exit(1)
    
    # Get current hostname
    hostname = get_hostname()
    print(f"Current hostname: {hostname}")
    
    # Set up paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    logs_dir = os.path.join(script_dir, "..", "logs")
    
    if not os.path.exists(logs_dir):
        print(f"Error: Logs directory not found: {logs_dir}")
        sys.exit(1)
    
    # Parse log files
    wifi_filter = "GoTitansFC"
    data = parse_log_files(logs_dir, hostname, wifi_filter)
    
    if not data:
        print("No data found to plot")
        sys.exit(1)
    
    # Aggregate data by 30-minute intervals
    aggregated_data = aggregate_by_half_hour(data)
    
    # Plot the data
    plot_success_rates(aggregated_data, hostname, wifi_filter)


if __name__ == '__main__':
    main()