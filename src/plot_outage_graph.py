#!/usr/bin/env python3
"""
Connectivity Data Plotting Script

This script generates a dot line graph showing success rates over time
for connectivity logs from the current machine's hostname.
"""

import argparse
import datetime
import glob
import os
import re
import socket
import subprocess
import sys
from typing import List, Tuple
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def get_hostname() -> str:
    """Get the current machine's hostname."""
    return socket.gethostname()


def parse_log_files(logs_dir: str, hostname: str, wifi_filter: str = "GoTitansFC", time_range_hours: int = 72) -> List[Tuple[datetime.datetime, float]]:
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
    
    # Filter to specified time range if we have more data
    if data:
        latest_time = data[-1][0]
        cutoff_time = latest_time - datetime.timedelta(hours=time_range_hours)
        data = [(ts, rate) for ts, rate in data if ts >= cutoff_time]
    
    print(f"Found {len(data)} data points for WiFi network '{wifi_filter}'")
    return data


def aggregate_by_interval(data: List[Tuple[datetime.datetime, float]], interval_minutes: int = 15) -> List[Tuple[datetime.datetime, float]]:
    """Aggregate data into specified minute intervals."""
    if not data:
        return []
    
    # Group data by specified intervals
    intervals = {}
    
    for timestamp, success_rate in data:
        # Calculate the interval boundary (round down to nearest interval mark)
        minutes_since_hour = timestamp.minute
        interval_start_minute = (minutes_since_hour // interval_minutes) * interval_minutes
        interval_start = timestamp.replace(minute=interval_start_minute, second=0, microsecond=0)
        
        # The interval end is interval_minutes later
        interval_end = interval_start + datetime.timedelta(minutes=interval_minutes)
        
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
    
    print(f"Aggregated into {len(aggregated_data)} {interval_minutes}-minute intervals")
    return aggregated_data


def plot_success_rates(data: List[Tuple[datetime.datetime, float]], hostname: str, wifi_network: str, interval_minutes: int = 15, output_file: str = None):
    """Plot success rates as a dot line graph."""
    if not data:
        print("No data to plot")
        return None
    
    # Extract timestamps and success rates
    timestamps = [item[0] for item in data]
    success_rates = [item[1] * 100 for item in data]  # Convert to percentage
    failure_rates = [100 - rate for rate in success_rates]  # Calculate failure percentage
    
    # Create the plot
    plt.figure(figsize=(12, 6))
    
    # Calculate bar width based on interval
    bar_width = datetime.timedelta(minutes=interval_minutes * 0.8)  # 80% of interval for spacing
    
    # Create stacked bar chart
    # Bottom bars (failure) in orange-red (colorblind friendly)
    plt.bar(timestamps, failure_rates, width=bar_width, color='#FF6B35', alpha=0.8, 
           edgecolor='black', linewidth=0.5, label='Failure')
    # Top bars (success) in light green with tiny blue tone (colorblind friendly)
    plt.bar(timestamps, success_rates, width=bar_width, color='#66D9A6', alpha=0.8,
           bottom=failure_rates, edgecolor='black', linewidth=0.5, label='Success')
    
    # Set labels and title
    plt.title(f'Internet Connectivity Success/Failure Rate - {hostname} ({wifi_network})\n{interval_minutes}-minute intervals')
    plt.xlabel('Time', labelpad=20)  # Add more space above "Time" label
    plt.ylabel('Rate (%)')
    
    # Add legend at the bottom, with more space below "Time" label
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.35), ncol=2)
    
    # Set y-axis to 0-100%
    plt.ylim(0, 105)
    
    # Format x-axis with labels aligned to midnight
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
    # Set locator to align with midnight (byhour=0 means starting at midnight)
    plt.gca().xaxis.set_major_locator(mdates.HourLocator(byhour=range(0, 24, 6)))
    plt.xticks(rotation=45)
    
    # Add grid
    plt.grid(True, alpha=0.3)
    
    # Tight layout
    plt.tight_layout()
    
    # Save the plot
    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Plot saved to: {output_file}")
        plt.close()  # Close the figure to free memory
        return output_file
    else:
        plt.show()
        return None


def open_file_non_blocking(file_path: str):
    """Open a file in the default application in a non-blocking way."""
    try:
        if sys.platform == 'darwin':  # macOS
            subprocess.Popen(['open', file_path])
        elif sys.platform == 'linux':  # Linux
            subprocess.Popen(['xdg-open', file_path])
        elif sys.platform == 'win32':  # Windows
            subprocess.Popen(['start', file_path], shell=True)
        else:
            print(f"Unsupported platform: {sys.platform}. Please open the file manually: {file_path}")
            return False
        return True
    except Exception as e:
        print(f"Could not open file automatically: {e}")
        print(f"Please open manually: {file_path}")
        return False


def main():
    """Main function."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Generate connectivity success rate plots')
    parser.add_argument('--hostname', default=get_hostname(), 
                       help='Hostname to plot data for (default: current machine)')
    parser.add_argument('--wifi-network', default='GoTitansFC',
                       help='WiFi network to filter by (default: GoTitansFC)')
    parser.add_argument('--time-range', type=int, default=72,
                       help='Time range in hours to plot (default: 72)')
    parser.add_argument('--interval', type=int, default=15,
                       help='Aggregation interval in minutes (default: 15)')
    parser.add_argument('--output-dir', default=os.path.expanduser('~/Desktop'),
                       help='Output directory for PNG files (default: ~/Desktop)')
    parser.add_argument('--output', help='Specific output file path (overrides --output-dir)')
    
    args = parser.parse_args()
    
    # Check for required packages
    try:
        import matplotlib.pyplot
    except ImportError as e:
        print(f"Error: Required packages not installed. Please install: {e}")
        print("Try: pip install matplotlib")
        sys.exit(1)
    
    print(f"Hostname: {args.hostname}")
    print(f"WiFi network filter: {args.wifi_network}")
    print(f"Time range: {args.time_range} hours")
    print(f"Aggregation interval: {args.interval} minutes")
    print(f"Output directory: {args.output_dir}")
    
    # Set up paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    logs_dir = os.path.join(script_dir, "..", "logs")
    
    if not os.path.exists(logs_dir):
        print(f"Error: Logs directory not found: {logs_dir}")
        sys.exit(1)
    
    # Parse log files
    data = parse_log_files(logs_dir, args.hostname, args.wifi_network, args.time_range)
    
    if not data:
        print("No data found to plot")
        sys.exit(1)
    
    # Aggregate data by specified intervals
    aggregated_data = aggregate_by_interval(data, args.interval)
    
    # Generate output filename if not specified
    if args.output:
        output_file = args.output
    else:
        # Create automatic filename
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"connectivity_plot_{args.hostname}_{args.wifi_network}_{args.time_range}h_{args.interval}m_{timestamp}.png"
        output_file = os.path.join(args.output_dir, filename)
        
        # Ensure output directory exists
        os.makedirs(args.output_dir, exist_ok=True)
    
    # Plot the data
    saved_file = plot_success_rates(aggregated_data, args.hostname, args.wifi_network, args.interval, output_file)
    
    # Open the file in a non-blocking way
    if saved_file and os.path.exists(saved_file):
        try:
            # Use subprocess to open the file non-blocking
            if sys.platform == 'darwin':  # macOS
                subprocess.Popen(['open', saved_file])
            elif sys.platform == 'linux':  # Linux
                subprocess.Popen(['xdg-open', saved_file])
            elif sys.platform == 'win32':  # Windows
                subprocess.Popen(['start', saved_file], shell=True)
            else:
                print(f"Unsupported platform: {sys.platform}. Please open the file manually: {saved_file}")
            
            print(f"Opening plot file: {saved_file}")
        except Exception as e:
            print(f"Could not open file automatically: {e}")
            print(f"Please open manually: {saved_file}")


if __name__ == '__main__':
    main()