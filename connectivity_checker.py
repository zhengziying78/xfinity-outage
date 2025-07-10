#!/usr/bin/env python3
import os
from src.site_checker import check_connectivity
from src.logging import log_to_file


if __name__ == "__main__":
    results = check_connectivity()
    log_to_file(results)
    success_count = sum(1 for check in results['checks'] if check['status'] == 'SUCCESS')
    total_count = len(results['checks'])
    status = "success" if success_count == total_count else "failed"
    print(f"{results['timestamp']} - WiFi: {results['wifi_network']} - {status}, {success_count}/{total_count} sites accessible")
    
    
