# Internet Connectivity Checker

A Python script that monitors internet connectivity by testing access to popular websites and logs results to daily files.

## Features

- Tests connectivity to GitHub, Google, Apple, and Reddit
- Logs results with timestamps to daily log files (`connectivity_log_YYYYMMDD.txt`)
- Measures response times for successful connections
- Automated scheduling via macOS LaunchAgent/LaunchDaemon

## Usage

### Manual Run
```bash
python3 connectivity_checker.py
```

### Automated Scheduling

#### Option 1: User-level (LaunchAgent)
Runs when user is logged in, pauses during sleep:

```bash
# Install
cp com.connectivity.checker.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.connectivity.checker.plist

# Stop
launchctl unload ~/Library/LaunchAgents/com.connectivity.checker.plist
```

#### Option 2: System-level (LaunchDaemon)
Runs continuously, even during sleep/wake cycles:

```bash
# Install (requires sudo)
sudo cp com.connectivity.checker.system.plist /Library/LaunchDaemons/
sudo chown root:wheel /Library/LaunchDaemons/com.connectivity.checker.system.plist
sudo chmod 644 /Library/LaunchDaemons/com.connectivity.checker.system.plist
sudo launchctl load /Library/LaunchDaemons/com.connectivity.checker.system.plist

# Stop
sudo launchctl unload /Library/LaunchDaemons/com.connectivity.checker.system.plist
```

### Updating Configuration

After modifying plist files, reload the service:

**For LaunchAgent:**
```bash
launchctl unload ~/Library/LaunchAgents/com.connectivity.checker.plist
launchctl load ~/Library/LaunchAgents/com.connectivity.checker.plist
```

**For LaunchDaemon:**
```bash
sudo launchctl unload /Library/LaunchDaemons/com.connectivity.checker.system.plist
sudo cp com.connectivity.checker.system.plist /Library/LaunchDaemons/
sudo launchctl load /Library/LaunchDaemons/com.connectivity.checker.system.plist
```

## Log Files

Log files are organized by hostname under the `logs/` directory:

- `logs/{hostname}/connectivity_log_YYYYMMDD.txt` - Daily connectivity results with response times and hostname
- `logs/{hostname}/connectivity_checker.log` - Script output/status messages  
- `logs/{hostname}/connectivity_checker.error` - Error messages

For example, on a machine named `Ziyings-MacBook-Pro.local`, logs would be stored in:
- `logs/Ziyings-MacBook-Pro.local/connectivity_log_20250709.txt`
- `logs/Ziyings-MacBook-Pro.local/connectivity_checker.log`
- `logs/Ziyings-MacBook-Pro.local/connectivity_checker.error`

### Log Rotation

To prevent log files from growing indefinitely, configure automatic log rotation using newsyslog:

```bash
# Install the newsyslog configuration
sudo cp connectivity_checker.newsyslog.conf /etc/newsyslog.d/
```

This will automatically rotate the `connectivity_checker.log` and `connectivity_checker.error` files when they exceed 1MB, keeping 7 rotated files.

## Requirements

- Python 3 (uses built-in `urllib` module, no external dependencies)
- macOS with launchctl for scheduling