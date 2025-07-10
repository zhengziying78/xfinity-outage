# Setup Instructions

Complete setup guide for the Internet Connectivity Checker.

## Quick Start

### Manual Run

For testing or one-time checks:

```bash
python3 src/connectivity_checker.py
```

Output example:
```
2025-07-09 11:03:43 - WiFi: GoTitansFC - success, 4/4 sites accessible
```

### Check Logs

View detailed connectivity results:

```bash
# View today's connectivity log
cat logs/$(hostname)/connectivity_log_$(date +%Y%m%d).txt

# View recent entries
tail -f logs/$(hostname)/connectivity_log_$(date +%Y%m%d).txt

# View script output
tail -f logs/connectivity_checker.log
```


## Automated Setup

### System-level (LaunchDaemon)
Runs continuously, even during sleep/wake cycles:

```bash
# First, customize the plist file with your paths and username
# Replace placeholders with actual values (run from project directory):
sed -i '' "s|/PATH/TO/PROJECT|$(pwd)|g" setup/com.connectivity.checker.system.plist
sed -i '' "s|YOUR_USERNAME|$(whoami)|g" setup/com.connectivity.checker.system.plist

# Install (requires sudo)
sudo cp setup/com.connectivity.checker.system.plist /Library/LaunchDaemons/
sudo chown root:wheel /Library/LaunchDaemons/com.connectivity.checker.system.plist
sudo chmod 644 /Library/LaunchDaemons/com.connectivity.checker.system.plist
sudo launchctl load /Library/LaunchDaemons/com.connectivity.checker.system.plist

# Stop
sudo launchctl unload /Library/LaunchDaemons/com.connectivity.checker.system.plist
```

### Updating Configuration

After modifying the plist file, reload the service:

```bash
sudo launchctl unload /Library/LaunchDaemons/com.connectivity.checker.system.plist
sudo cp setup/com.connectivity.checker.system.plist /Library/LaunchDaemons/
sudo launchctl load /Library/LaunchDaemons/com.connectivity.checker.system.plist
```

## Log Rotation Setup

To prevent log files from growing indefinitely, configure automatic log rotation:

```bash
# First, customize the newsyslog configuration file
# Replace placeholders with actual values (run from project directory):
sed -i '' "s|/PATH/TO/PROJECT|$(pwd)|g" setup/connectivity_checker.newsyslog.conf
sed -i '' "s|YOUR_USERNAME|$(whoami)|g" setup/connectivity_checker.newsyslog.conf

# Install the newsyslog configuration
sudo cp setup/connectivity_checker.newsyslog.conf /etc/newsyslog.d/
```

This will automatically rotate the `connectivity_checker.log` and `connectivity_checker.error` files when they exceed 1MB, keeping 7 rotated files.


## Troubleshooting

### LaunchDaemon Issues
- Check logs: `tail -f logs/connectivity_checker.log`
- Verify plist syntax: `plutil -lint your_plist_file.plist`
- Check if loaded: `launchctl list | grep connectivity`


### Log Rotation Issues
- Check newsyslog configuration: `sudo cat /etc/newsyslog.d/connectivity_checker.newsyslog.conf`
- Test rotation: `sudo newsyslog -v`

