# Logs Directory

This directory contains log files organized by hostname.

## Structure

```
logs/
├── {hostname}/
│   └── connectivity_log_YYYYMMDD.txt  # Daily connectivity test results
├── connectivity_checker.log           # Script stdout (local only)
├── connectivity_checker.error         # Script stderr (local only)
└── README.md
```

## Log Files

- **Daily connectivity logs** (`{hostname}/connectivity_log_YYYYMMDD.txt`) - Tracked in git
  - Contains timestamped connectivity test results
  - Shows response times for each website tested
  - Includes hostname for identification

- **Runtime logs** (`connectivity_checker.log`, `connectivity_checker.error`) - Local only
  - Located directly under `logs/` folder
  - Contains script output and error messages
  - Rotated automatically when they exceed 1MB
  - Not tracked in git (ignored by .gitignore)

## Example

For hostname `Ziyings-MacBook-Pro.local`:
- `logs/Ziyings-MacBook-Pro.local/connectivity_log_20250709.txt` (tracked in git)
- `logs/connectivity_checker.log` (local only)
- `logs/connectivity_checker.error` (local only)