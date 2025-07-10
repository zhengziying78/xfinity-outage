#!/usr/bin/env python3
import os
from src.site_checker import check_connectivity
from src.logging import log_to_file, print_summary
from src.git import push_logs_to_git


if __name__ == "__main__":
    results = check_connectivity()
    log_to_file(results)
    print_summary(results)
    
    # Push log changes to remote repository
    # Note: We use local log files (logs/{hostname}) instead of remote log services
    # since we can't emit logs externally when network connectivity fails.
    # The push_logs_to_git() function has internal logic to avoid excessive commits.
    push_logs_to_git()
    
