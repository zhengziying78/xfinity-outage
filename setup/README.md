# Setup Instructions

Complete setup guide for the Internet Connectivity Checker.

## Quick Start

### Manual Run

For testing or one-time checks:

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

For remote log viewing and search examples, see [`../logs/README.md`](../logs/README.md).

## Automated Setup

### System-level (LaunchDaemon)
Runs continuously, even during sleep/wake cycles:

```bash
# First, customize the plist file with your paths and username
# Replace placeholders with actual values (run from project directory):
sed -i '' "s|/PATH/TO/PROJECT|$(pwd)|g" com.connectivity.checker.system.plist
sed -i '' "s|YOUR_USERNAME|$(whoami)|g" com.connectivity.checker.system.plist
sed -i '' "s|fake_token_12345|YOUR_ACTUAL_LOGTAIL_TOKEN|g" com.connectivity.checker.system.plist

# Install (requires sudo)
sudo cp com.connectivity.checker.system.plist /Library/LaunchDaemons/
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
sudo cp com.connectivity.checker.system.plist /Library/LaunchDaemons/
sudo launchctl load /Library/LaunchDaemons/com.connectivity.checker.system.plist
```

## Log Rotation Setup

To prevent log files from growing indefinitely, configure automatic log rotation:

```bash
# First, customize the newsyslog configuration file
# Replace placeholders with actual values (run from project directory):
sed -i '' "s|/PATH/TO/PROJECT|$(pwd)|g" connectivity_checker.newsyslog.conf
sed -i '' "s|YOUR_USERNAME|$(whoami)|g" connectivity_checker.newsyslog.conf

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

Check your logs using the URLs in [`../logs/README.md`](../logs/README.md)

## Troubleshooting

### LaunchDaemon Issues
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

