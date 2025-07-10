"""
Log parsing functionality for connectivity data.
"""

import datetime
import glob
import os
import re
from typing import List, Tuple


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