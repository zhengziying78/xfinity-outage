# Internet Connectivity Checker

A Python script that monitors internet connectivity by testing access to popular websites and logs results to daily files.

## Features

- Tests connectivity to GitHub, Google, Apple, and Reddit in parallel
- Logs results with timestamps to daily log files organized by hostname
- Measures response times for each website tested
- Optional remote logging to Logtail (Better Stack) for centralized monitoring
- Automated scheduling via macOS LaunchAgent/LaunchDaemon

## Usage

### Manual Run

```bash
python3 connectivity_checker.py
```

Output example:
```
2025-07-09 11:03:43 - WiFi: GoTitansFC - success, 4/4 sites accessible
```

### Check Local Logs

View detailed connectivity results:

```bash
# View today's connectivity log
cat logs/$(hostname)/connectivity_log_$(date +%Y%m%d).txt

# View recent entries
tail -f logs/$(hostname)/connectivity_log_$(date +%Y%m%d).txt

# View script output
tail -f logs/connectivity_checker.log
```

### Check Remote Logs

If remote logging is enabled, view logs at:
**Live Tail**: https://telemetry.betterstack.com/team/387653/tail

Search examples:
- `hostname:"Ziyings-MacBook-Pro.local"` - Filter by machine
- `status:"failed"` - Show only failures
- `wifi_network:"GoTitansFC"` - Filter by WiFi network
- `success_percentage:<100` - Show partial connectivity issues
- `failed_count:>0` - Show entries with any failures

## Setup & Configuration

📋 **Setup Guide**: [`setup/README.md`](setup/README.md) - Complete installation and configuration instructions

📊 **Log Details**: [`logs/README.md`](logs/README.md) - Log organization and remote logging setup

## Requirements

- Python 3 (uses built-in `urllib` and `concurrent.futures` modules, no external dependencies)
- macOS with launchctl for scheduling