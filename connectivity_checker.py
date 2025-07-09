#!/usr/bin/env python3
import urllib.request
import urllib.error
import datetime
import time

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
        f.write(f"Internet: {success_count}/{total_count} sites accessible\n")
        
        for check in results['checks']:
            status_info = f"{check['status']}"
            if check['response_time']:
                status_info += f" ({check['response_time']:.2f}s)"
            f.write(f"  {check['url']}: {status_info}\n")
        f.write("\n")

if __name__ == "__main__":
    results = check_connectivity()
    log_results(results)
    success_count = sum(1 for check in results['checks'] if check['status'] == 'SUCCESS')
    total_count = len(results['checks'])
    status = "success" if success_count == total_count else "failed"
    print(f"Connectivity check completed at {results['timestamp']} - {status}, {success_count}/{total_count} sites accessible")