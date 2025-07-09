#!/usr/bin/env python3
import urllib.request
import urllib.error
import datetime
import time
import subprocess

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

def check_connectivity():
    """Check internet connectivity by testing multiple well-known websites."""
    websites = [
        'https://github.com',
        'https://google.com',
        'https://apple.com',
        'https://reddit.com'
    ]
    
    results = {
        'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'wifi_network': get_wifi_network(),
        'checks': []
    }
    
    for url in websites:
        try:
            start_time = time.time()
            response = urllib.request.urlopen(url, timeout=5)
            response_time = time.time() - start_time
            status = 'SUCCESS' if response.getcode() == 200 else f'HTTP_{response.getcode()}'
        except urllib.error.URLError as e:
            status = f'FAILED: {str(e)}'
            response_time = None
        except Exception as e:
            status = f'FAILED: {str(e)}'
            response_time = None
        
        results['checks'].append({
            'url': url,
            'status': status,
            'response_time': response_time
        })
    
    return results

def log_results(results, log_file=None):
    """Append results to log file."""
    if log_file is None:
        date_str = datetime.datetime.now().strftime('%Y%m%d')
        log_file = f'connectivity_log_{date_str}.txt'
    
    with open(log_file, 'a') as f:
        f.write(f"{results['timestamp']} - ")
        success_count = sum(1 for check in results['checks'] if check['status'] == 'SUCCESS')
        total_count = len(results['checks'])
        f.write(f"WiFi: {results['wifi_network']} - Internet: {success_count}/{total_count} sites accessible\n")
        
        for check in results['checks']:
            status_info = f"{check['status']}"
            if check['response_time']:
                status_info += f" ({check['response_time']:.2f}s)"
            f.write(f"  {results['timestamp']} - {check['url']}: {status_info}\n")
        f.write("\n")

if __name__ == "__main__":
    results = check_connectivity()
    log_results(results)
    success_count = sum(1 for check in results['checks'] if check['status'] == 'SUCCESS')
    total_count = len(results['checks'])
    status = "success" if success_count == total_count else "failed"
    print(f"{results['timestamp']} - WiFi: {results['wifi_network']} - {status}, {success_count}/{total_count} sites accessible")