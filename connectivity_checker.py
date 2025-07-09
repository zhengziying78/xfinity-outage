#!/usr/bin/env python3
import urllib.request
import urllib.error
import datetime
import time
import subprocess
import socket
import os
import json
from concurrent.futures import ThreadPoolExecutor

def get_wifi_network():
    """Get the currently connected WiFi network name."""
    # Try method 1: networksetup (works for regular WiFi)
    try:
        result = subprocess.run(['networksetup', '-getairportnetwork', 'en0'], 
                              capture_output=True, text=True, check=True)
        output = result.stdout.strip()
        if "Current Wi-Fi Network:" in output:
            return output.replace("Current Wi-Fi Network: ", "")
    except:
        pass
    
    # Try method 2: system_profiler (works for hotspots and regular WiFi)
    try:
        result = subprocess.run(['system_profiler', 'SPAirPortDataType'], 
                              capture_output=True, text=True, check=True)
        lines = result.stdout.split('\n')
        for i, line in enumerate(lines):
            if "Current Network Information:" in line:
                # Look for the network name in the next few lines
                for j in range(i+1, min(i+10, len(lines))):
                    next_line = lines[j].strip()
                    if next_line and ':' in next_line and not next_line.startswith('PHY Mode') and not next_line.startswith('Channel') and not next_line.startswith('Country Code') and not next_line.startswith('Network Type'):
                        network_name = next_line.split(':')[0].strip()
                        if network_name:
                            return network_name
    except:
        pass
    
    return "Not connected to WiFi"

def check_single_site(url):
    """Check connectivity to a single website."""
    start_time = time.time()
    try:
        response = urllib.request.urlopen(url, timeout=5)
        duration = time.time() - start_time
        status = 'SUCCESS' if response.getcode() == 200 else f'HTTP_{response.getcode()}'
    except urllib.error.URLError as e:
        duration = time.time() - start_time
        status = f'FAILED: {str(e)}'
    except Exception as e:
        duration = time.time() - start_time
        status = f'FAILED: {str(e)}'
    
    return {
        'url': url,
        'status': status,
        'duration': duration
    }

def check_connectivity():
    """Check internet connectivity by testing multiple well-known websites."""
    websites = [
        'https://github.com',
        'https://google.com',
        'https://apple.com',
        'https://reddit.com'
    ]
    
    # Get timezone info
    local_tz = time.tzname[time.daylight]
    # Map common timezone abbreviations to full names
    timezone_map = {
        'PST': 'Pacific Standard Time',
        'PDT': 'Pacific Daylight Time',
        'EST': 'Eastern Standard Time',
        'EDT': 'Eastern Daylight Time',
        'MST': 'Mountain Standard Time',
        'MDT': 'Mountain Daylight Time',
        'CST': 'Central Standard Time',
        'CDT': 'Central Daylight Time',
        'HST': 'Hawaii Standard Time',
        'HDT': 'Hawaii Daylight Time',
        'AKST': 'Alaska Standard Time',
        'AKDT': 'Alaska Daylight Time'
    }
    timezone_full = timezone_map.get(local_tz, local_tz)
    
    # Get GMT offset
    local_time = time.localtime()
    offset_seconds = -time.timezone + (time.daylight * 3600)
    offset_hours = offset_seconds // 3600
    offset_minutes = abs(offset_seconds % 3600) // 60
    gmt_offset = f"GMT{offset_hours:+03d}{offset_minutes:02d}"
    
    # Create comprehensive timezone info
    timezone_info = f"{local_tz} ({timezone_full}) {gmt_offset}"
    
    results = {
        'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'timestamp_utc': datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
        'timezone_local': timezone_info,  # Comprehensive timezone info
        'wifi_network': get_wifi_network(),
        'checks': []
    }
    
    # Use ThreadPoolExecutor to check all websites in parallel
    with ThreadPoolExecutor(max_workers=len(websites)) as executor:
        future_to_url = {executor.submit(check_single_site, url): url for url in websites}
        
        for future in future_to_url:
            try:
                check_result = future.result()
                results['checks'].append(check_result)
            except Exception as e:
                # Handle any unexpected errors from the thread
                url = future_to_url[future]
                results['checks'].append({
                    'url': url,
                    'status': f'FAILED: {str(e)}',
                    'duration': 0.0
                })
    
    # Sort results by original URL order to maintain consistency
    url_order = {url: i for i, url in enumerate(websites)}
    results['checks'].sort(key=lambda x: url_order[x['url']])
    
    return results

def log_results(results, log_file=None):
    """Append results to log file."""
    if log_file is None:
        hostname = socket.gethostname()
        date_str = datetime.datetime.now().strftime('%Y%m%d')
        log_dir = f'logs/{hostname}'
        
        # Create hostname directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = f'{log_dir}/connectivity_log_{date_str}.txt'
    
    with open(log_file, 'a') as f:
        f.write(f"{results['timestamp']} - ")
        success_count = sum(1 for check in results['checks'] if check['status'] == 'SUCCESS')
        total_count = len(results['checks'])
        f.write(f"WiFi: {results['wifi_network']} - Internet: {success_count}/{total_count} sites accessible\n")
        
        for check in results['checks']:
            duration_str = f"({check['duration']:.2f}s)"
            f.write(f"  {duration_str} - {check['url']}: {check['status']}\n")
        
        # Add hostname at the end
        hostname = socket.gethostname()
        f.write(f"Hostname: {hostname}\n\n")

def send_to_logtail(results, source_token=None):
    """Send connectivity results to Logtail."""
    if not source_token:
        print("DEBUG: No LOGTAIL_TOKEN provided, skipping remote logging")
        return  # Skip if no token provided
    
    try:
        success_count = sum(1 for check in results['checks'] if check['status'] == 'SUCCESS')
        total_count = len(results['checks'])
        failed_count = total_count - success_count
        success_percentage = round((success_count / total_count) * 100, 1) if total_count > 0 else 0
        failed_percentage = round((failed_count / total_count) * 100, 1) if total_count > 0 else 0
        status = "success" if success_count == total_count else "failed"
        
        # Create one-line summary message
        message = f"{results['timestamp']} - WiFi: {results['wifi_network']} - {status}, {success_count}/{total_count} sites accessible"
        
        # Prepare log data with hostname as separate field for querying
        log_data = {
            'message': message,
            'hostname': socket.gethostname(),
            'timestamp_utc': results['timestamp_utc'],  # Use UTC for remote logs
            'timestamp_local': results['timestamp'],  # Include local time for reference
            'timezone_local': results['timezone_local'],  # Include timezone info
            'wifi_network': results['wifi_network'],
            'status': status,
            'success_count': success_count,
            'failed_count': failed_count,
            'total_count': total_count,
            'success_percentage': success_percentage,
            'failed_percentage': failed_percentage
        }
        
        # Send to Logtail
        headers = {
            'Authorization': f'Bearer {source_token}',
            'Content-Type': 'application/json'
        }
        
        response = urllib.request.Request(
            'https://s1374986.eu-nbg-2.betterstackdata.com/',
            data=json.dumps(log_data).encode('utf-8'),
            headers=headers
        )
        
        urllib.request.urlopen(response, timeout=10)
        
    except Exception as e:
        # Ignore logging errors to prevent script failure
        # Note: Removed debug print to avoid exposing sensitive token info
        pass

def push_logs_to_git(timestamp):
    """Push log changes to remote repository."""
    try:
        # Add log files to git
        subprocess.run(['git', 'add', 'logs/'], check=True, capture_output=True)
        
        # Commit changes
        commit_message = f"Add connectivity log entry - {timestamp}"
        subprocess.run(['git', 'commit', '-m', commit_message], check=True, capture_output=True)
        
        # Pull with rebase to avoid merge conflicts
        subprocess.run(['git', 'pull', '--rebase'], check=True, capture_output=True)
        
        # Push to remote
        subprocess.run(['git', 'push'], check=True, capture_output=True)
        
    except subprocess.CalledProcessError:
        # Ignore git errors (e.g., no changes to commit, network issues)
        pass

if __name__ == "__main__":
    results = check_connectivity()
    log_results(results)
    success_count = sum(1 for check in results['checks'] if check['status'] == 'SUCCESS')
    total_count = len(results['checks'])
    status = "success" if success_count == total_count else "failed"
    print(f"{results['timestamp']} - WiFi: {results['wifi_network']} - {status}, {success_count}/{total_count} sites accessible")
    
    # Send to Logtail (set your source token here)
    logtail_token = os.environ.get('LOGTAIL_TOKEN')  # Set via environment variable
    send_to_logtail(results, logtail_token)
    
    # Push log changes to remote repository
    # push_logs_to_git(results['timestamp'])  # Disabled - too frequent