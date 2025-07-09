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

- `connectivity_log_YYYYMMDD.txt` - Daily connectivity results
- `connectivity_checker.log` - Script output/status messages
- `connectivity_checker.error` - Error messages

## Requirements

- Python 3 (uses built-in `urllib` module, no external dependencies)
- macOS with launchctl for scheduling