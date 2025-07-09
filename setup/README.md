# Setup Instructions

Complete setup guide for the Internet Connectivity Checker.

## Quick Start

1. **Manual Run** (for testing):
   ```bash
   python3 connectivity_checker.py
   ```

2. **Automated Setup** (choose one):
   - [User-level LaunchAgent](#user-level-launchagent) - Runs when user is logged in
   - [System-level LaunchDaemon](#system-level-launchdaemon) - Runs continuously

## Automated Scheduling

### User-level (LaunchAgent)
Runs when user is logged in, pauses during sleep:

```bash
# Install
cp com.connectivity.checker.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.connectivity.checker.plist

# Stop
launchctl unload ~/Library/LaunchAgents/com.connectivity.checker.plist
```

### System-level (LaunchDaemon)
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

## Log Rotation Setup

To prevent log files from growing indefinitely, configure automatic log rotation:

```bash
# Install the newsyslog configuration
sudo cp connectivity_checker.newsyslog.conf /etc/newsyslog.d/
```

This will automatically rotate the `connectivity_checker.log` and `connectivity_checker.error` files when they exceed 1MB, keeping 7 rotated files.

## Remote Logging Setup (Optional)

Set up centralized logging with Logtail (Better Stack):

### 1. Create Better Stack Account
Sign up at https://betterstack.com

### 2. Add HTTP Source
- Go to Logs → Sources → Add source
- Choose "HTTP" in "Logs + Metrics"
- Copy the source token (starts with `st_`)
- Note your unique endpoint URL (e.g., `https://s1374986.eu-nbg-2.betterstackdata.com/`)

### 3. Set Environment Variable

⚠️ **Security Note**: The LOGTAIL_TOKEN is a secret authentication token. Never commit it to git or share it publicly.

#### If Token is Accidentally Leaked

If your LOGTAIL_TOKEN is accidentally exposed (in git history, shared publicly, etc.):

1. **Immediately regenerate the token**:
   - Go to Better Stack → Logs → Sources
   - Find your HTTP source
   - Click "Regenerate token" or delete and recreate the source

2. **Update your configuration**:
   - Update the token in your environment variables
   - Update any plist files with the new token
   - Restart any running services

3. **Clean up exposure**:
   - If committed to git: Consider rewriting git history or rotating the token
   - If shared publicly: Regenerate immediately and update documentation

4. **Monitor your Better Stack account** for any unusual activity

**For manual testing:**
```bash
export LOGTAIL_TOKEN="your_actual_token_here"
```

**For LaunchAgent:**
Add to your shell profile (~/.zshrc or ~/.bash_profile):
```bash
export LOGTAIL_TOKEN="your_actual_token_here"
```

**For LaunchDaemon:**
Add to your plist file:
```xml
<key>EnvironmentVariables</key>
<dict>
    <key>LOGTAIL_TOKEN</key>
    <string>your_actual_token_here</string>
</dict>
```

### 4. Verify Setup
Run the script manually to verify logs are being sent:
```bash
python3 connectivity_checker.py
```

Check your logs at: https://telemetry.betterstack.com/team/387653/tail

## Troubleshooting

### LaunchAgent/LaunchDaemon Issues
- Check logs: `tail -f logs/connectivity_checker.log`
- Verify plist syntax: `plutil -lint your_plist_file.plist`
- Check if loaded: `launchctl list | grep connectivity`

### Remote Logging Issues
- Ensure `LOGTAIL_TOKEN` is set: `echo $LOGTAIL_TOKEN`
- Check for errors in `logs/connectivity_checker.error`
- Verify network connectivity to Better Stack endpoint

### Log Rotation Issues
- Check newsyslog configuration: `sudo cat /etc/newsyslog.d/connectivity_checker.newsyslog.conf`
- Test rotation: `sudo newsyslog -v`

## Requirements

### System Requirements
- Python 3 (built-in modules only, no external dependencies)
- macOS with launchctl for scheduling

### Python Modules Used
The script uses only built-in Python modules:
- `urllib.request` - HTTP requests for connectivity testing
- `urllib.error` - HTTP error handling
- `datetime` - Timestamp generation
- `time` - Response time measurement and timezone handling
- `subprocess` - WiFi network detection and git operations
- `socket` - Hostname detection
- `os` - Environment variable access
- `json` - JSON serialization for remote logging
- `concurrent.futures` - Parallel connectivity testing

**No external dependencies or pip installs required.**