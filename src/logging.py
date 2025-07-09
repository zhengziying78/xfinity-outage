import datetime
import socket
import os
import json
import urllib.request


def log_to_file(results, log_file=None):
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


def prepare_logtail_data(results):
    """Prepare log data structure for remote logging."""
    success_count = sum(1 for check in results['checks'] if check['status'] == 'SUCCESS')
    total_count = len(results['checks'])
    failed_count = total_count - success_count
    success_percentage = round((success_count / total_count) * 100, 1) if total_count > 0 else 0
    failed_percentage = round((failed_count / total_count) * 100, 1) if total_count > 0 else 0
    status = "success" if success_count == total_count else "failed"
    
    # Create one-line summary message
    message = f"{results['timestamp']} - WiFi: {results['wifi_network']} - {status}, {success_count}/{total_count} sites accessible"
    
    # Prepare log data with hostname as separate field for querying
    return {
        'message': message,
        'hostname': socket.gethostname(),
        'timestamp_utc': results['timestamp_utc'],
        'timestamp_local': results['timestamp'],
        'timezone_local': results['timezone_local'],
        'wifi_network': results['wifi_network'],
        'status': status,
        'success_count': success_count,
        'failed_count': failed_count,
        'total_count': total_count,
        'success_percentage': success_percentage,
        'failed_percentage': failed_percentage
    }


def send_to_logtail(results, source_token=None):
    """Send connectivity results to Logtail."""
    if not source_token:
        print("DEBUG: No LOGTAIL_TOKEN provided, skipping remote logging")
        return
    
    try:
        log_data = prepare_logtail_data(results)
        
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
        pass