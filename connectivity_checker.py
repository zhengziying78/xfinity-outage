#!/usr/bin/env python3
import os
from src.site_checker import check_connectivity
from src.logging import log_results, send_to_logtail


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
    
