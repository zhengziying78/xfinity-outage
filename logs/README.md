# Logging Documentation

Technical details about log organization, formats, and remote logging configuration.

## Log Structure

```
logs/
├── {hostname}/
│   └── connectivity_log_YYYYMMDD.txt  # Daily connectivity test results
├── connectivity_checker.log           # Script stdout (local only)
├── connectivity_checker.error         # Script stderr (local only)
└── README.md
```

## Log Types

### Daily Connectivity Logs
**Location**: `logs/{hostname}/connectivity_log_YYYYMMDD.txt`
**Git Tracking**: No (local only)
**Purpose**: Historical record of connectivity test results

**Format**:
```
2025-07-09 11:03:43 - WiFi: GoTitansFC - Internet: 4/4 sites accessible
  (0.24s) - https://github.com: SUCCESS
  (0.47s) - https://google.com: SUCCESS
  (0.37s) - https://apple.com: SUCCESS
  (0.50s) - https://reddit.com: SUCCESS
Hostname: Ziyings-MacBook-Pro.local
```

### Runtime Logs
**Location**: `logs/connectivity_checker.log` and `logs/connectivity_checker.error`
**Git Tracking**: No (ignored by .gitignore)
**Purpose**: Script execution output and error messages
**Rotation**: Automatic when files exceed 1MB (keeps 7 rotated files)

## Example Files

For hostname `Ziyings-MacBook-Pro.local`:
- `logs/Ziyings-MacBook-Pro.local/connectivity_log_20250709.txt` (local only)
- `logs/connectivity_checker.log` (local only)
- `logs/connectivity_checker.error` (local only)

## Remote Logging (Logtail)

The script can optionally send connectivity summaries to Logtail (Better Stack) for centralized monitoring.

### Data Transmission

**What Gets Sent**: Only one-line summaries are transmitted as structured JSON:
- **Main message**: `"2025-07-09 11:03:43 - WiFi: GoTitansFC - success, 4/4 sites accessible"` (uses local time)
- **Structured fields**: hostname, timestamp_utc, timestamp_local, timezone_local, wifi_network, status, success_count, failed_count, total_count, success_percentage, failed_percentage

**What Stays Local**: Detailed individual site results (response times, specific errors) remain in local logs only.

**Timezone Handling**: 
- Local logs use local system timezone for user readability
- Remote logs use UTC in the `timestamp_utc` field for cross-platform consistency
- `timestamp_local` field preserves local time for reference
- `timezone_local` field provides comprehensive timezone info: short name, full name, and GMT offset (e.g., "PDT (Pacific Daylight Time) GMT-0700")

### Remote Log Format

```json
{
  "message": "2025-07-09 11:03:43 - WiFi: GoTitansFC - success, 4/4 sites accessible",
  "hostname": "Ziyings-MacBook-Pro.local",
  "timestamp_utc": "2025-07-09 18:03:43",
  "timestamp_local": "2025-07-09 11:03:43",
  "timezone_local": "PDT (Pacific Daylight Time) GMT-0700",
  "wifi_network": "GoTitansFC",
  "status": "success",
  "success_count": 4,
  "failed_count": 0,
  "total_count": 4,
  "success_percentage": 100.0,
  "failed_percentage": 0.0
}
```

### Viewing Remote Logs

**Live Tail**: https://telemetry.betterstack.com/team/387653/tail?rf=now-60m

You can change the time range by modifying the URL parameter (e.g., `?rf=now-30m` for 30 minutes, `?rf=now-24h` for 24 hours) or by using the time range selector in the Logtail web UI.

**Search Examples**:
- `hostname:"Ziyings-MacBook-Pro.local"` - Filter by specific machine
- `status:"failed"` - Show only failed connectivity attempts
- `wifi_network:"GoTitansFC"` - Filter by WiFi network
- `success_count:<4` - Show when not all sites were accessible
- `success_percentage:<100` - Show partial connectivity issues
- `failed_count:>0` - Show entries with any failures
- `timezone_local:"Pacific Daylight Time"` - Filter by timezone

### Configuration

See [`../setup/README.md`](../setup/README.md) for complete remote logging setup instructions.

