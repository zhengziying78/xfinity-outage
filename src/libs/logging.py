import datetime
import socket
import os


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


def print_summary(results):
    """Print connectivity summary to console."""
    success_count = sum(1 for check in results['checks'] if check['status'] == 'SUCCESS')
    total_count = len(results['checks'])
    status = "success" if success_count == total_count else "failed"
    print(f"{results['timestamp']} - WiFi: {results['wifi_network']} - {status}, {success_count}/{total_count} sites accessible")


