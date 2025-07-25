# Logging Documentation

Technical details about log organization and formats.

## Log Structure

```
logs/
├── {hostname}/
│   └── connectivity_log_YYYYMMDD.txt  # Daily connectivity test results
├── xfinity_outage_checker.log           # Script stdout
├── xfinity_outage_checker.error         # Script stderr
└── README.md
```

## Log Types

### Daily Connectivity Logs
**Location**: `logs/{hostname}/connectivity_log_YYYYMMDD.txt`  
**Git Tracking**: Yes (committed to repository)  
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
**Location**: `logs/xfinity_outage_checker.log` and `logs/xfinity_outage_checker.error`  
**Git Tracking**: No (ignored by .gitignore)  
**Purpose**: Script execution output and error messages  
**Rotation**: Automatic when files exceed 1MB (keeps 7 rotated files)

## Example Files

For hostname `Ziyings-MacBook-Pro.local`:
- `logs/Ziyings-MacBook-Pro.local/connectivity_log_20250709.txt` (committed to repository)
- `logs/xfinity_outage_checker.log` (local only)
- `logs/xfinity_outage_checker.error` (local only)


