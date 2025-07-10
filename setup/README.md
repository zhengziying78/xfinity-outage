# Setup Instructions

Complete setup guide for the Internet Connectivity Checker.

## Quick Start

### Manual Run

For testing or one-time checks:

```bash
python3 src/xfinity_outage_checker.py
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
tail -f logs/xfinity_outage_checker.log
```


## Automated Setup

### System-level (LaunchDaemon)
Runs continuously, even during sleep/wake cycles:

```bash
# First, customize the plist file with your paths and username
# Replace placeholders with actual values (run from project directory):
sed -i '' "s|/PATH/TO/PROJECT|$(pwd)|g" setup/com.zhengziying.xfinity-outage.checker.system.plist
sed -i '' "s|YOUR_USERNAME|$(whoami)|g" setup/com.zhengziying.xfinity-outage.checker.system.plist

# Install (requires sudo)
sudo cp setup/com.zhengziying.xfinity-outage.checker.system.plist /Library/LaunchDaemons/
sudo chown root:wheel /Library/LaunchDaemons/com.zhengziying.xfinity-outage.checker.system.plist
sudo chmod 644 /Library/LaunchDaemons/com.zhengziying.xfinity-outage.checker.system.plist
sudo launchctl load /Library/LaunchDaemons/com.zhengziying.xfinity-outage.checker.system.plist

# Stop
sudo launchctl unload /Library/LaunchDaemons/com.zhengziying.xfinity-outage.checker.system.plist
```

### Updating Configuration

After modifying the plist file, reload the service:

```bash
sudo launchctl unload /Library/LaunchDaemons/com.zhengziying.xfinity-outage.checker.system.plist
sudo cp setup/com.zhengziying.xfinity-outage.checker.system.plist /Library/LaunchDaemons/
sudo launchctl load /Library/LaunchDaemons/com.zhengziying.xfinity-outage.checker.system.plist
```

## Log Rotation Setup

To prevent log files from growing indefinitely, configure automatic log rotation:

```bash
# First, customize the newsyslog configuration file
# Replace placeholders with actual values (run from project directory):
sed -i '' "s|/PATH/TO/PROJECT|$(pwd)|g" setup/zhengziying.xfinity-outage.checker.newsyslog.conf
sed -i '' "s|YOUR_USERNAME|$(whoami)|g" setup/zhengziying.xfinity-outage.checker.newsyslog.conf

# Install the newsyslog configuration
sudo cp setup/zhengziying.xfinity-outage.checker.newsyslog.conf /etc/newsyslog.d/
```

This will automatically rotate the `xfinity_outage_checker.log` and `xfinity_outage_checker.error` files when they exceed 1MB, keeping 7 rotated files.


## Troubleshooting

### LaunchDaemon Issues
- Check logs: `tail -f logs/xfinity_outage_checker.log`
- Verify plist syntax: `plutil -lint your_plist_file.plist`
- Check if loaded: `launchctl list | grep xfinity-outage`


### Log Rotation Issues
- Check newsyslog configuration: `sudo cat /etc/newsyslog.d/zhengziying.xfinity-outage.checker.newsyslog.conf`
- Test rotation: `sudo newsyslog -v`


## Cleanup and Removal

To completely remove the connectivity checker and all its components:

### Remove LaunchDaemon Service

```bash
# Stop and unload the service
sudo launchctl unload /Library/LaunchDaemons/com.zhengziying.xfinity-outage.checker.system.plist

# Remove the plist file
sudo rm /Library/LaunchDaemons/com.zhengziying.xfinity-outage.checker.system.plist

# Verify removal
launchctl list | grep xfinity-outage  # Should return nothing
```

### Remove Log Rotation Configuration

```bash
# Remove the newsyslog configuration
sudo rm /etc/newsyslog.d/zhengziying.xfinity-outage.checker.newsyslog.conf

# Verify removal
ls /etc/newsyslog.d/ | grep xfinity-outage  # Should return nothing
```

### Remove Log Files (Optional)

```bash
# Remove runtime logs (these are not tracked in git)
rm -f logs/xfinity_outage_checker.log*
rm -f logs/xfinity_outage_checker.error*

# Note: Daily connectivity logs in logs/{hostname}/ are tracked in git
# Remove them only if you want to delete historical data:
# rm -rf logs/{hostname}/
```

### Verify Complete Removal

```bash
# Check that no launchctl services are running
launchctl list | grep xfinity-outage

# Check that no configuration files remain
ls /Library/LaunchDaemons/ | grep xfinity-outage
ls /etc/newsyslog.d/ | grep xfinity-outage

# Check for any remaining processes (exclude the grep command itself)
ps aux | grep xfinity_outage_checker | grep -v grep
```

### Kill Remaining Processes (If Any)

If you find any running xfinity_outage_checker processes, kill them:

```bash
# Find running xfinity_outage_checker processes (excluding grep)
PIDS=$(ps aux | grep xfinity_outage_checker | grep -v grep | awk '{print $2}')

# Kill the processes if any are found
if [ ! -z "$PIDS" ]; then
    echo "Found running processes: $PIDS"
    echo "Killing processes..."
    kill $PIDS
    
    # If processes don't terminate gracefully, force kill them
    sleep 2
    REMAINING=$(ps aux | grep xfinity_outage_checker | grep -v grep | awk '{print $2}')
    if [ ! -z "$REMAINING" ]; then
        echo "Force killing remaining processes: $REMAINING"
        kill -9 $REMAINING
    fi
else
    echo "No xfinity_outage_checker processes found running"
fi

# Verify all processes are gone
ps aux | grep xfinity_outage_checker | grep -v grep
```

**Note**: The `grep xfinity_outage_checker` command itself will appear in the process list, which is normal. The above commands filter out the grep process to show only actual xfinity_outage_checker instances.

After running these commands, the connectivity checker will be completely removed from your system. You can safely delete the project directory if desired.

