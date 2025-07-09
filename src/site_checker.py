import urllib.request
import urllib.error
import time
from concurrent.futures import ThreadPoolExecutor
from .wifi import get_wifi_network
from .timestamp import get_timestamp_info


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
    
    # Get timestamp and timezone info
    timestamp_info = get_timestamp_info()
    
    results = {
        'timestamp': timestamp_info['timestamp'],
        'timestamp_utc': timestamp_info['timestamp_utc'],
        'timezone_local': timestamp_info['timezone_local'],
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