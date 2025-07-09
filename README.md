# Internet Connectivity Checker

A Python script that monitors internet connectivity by testing access to popular websites and logs results to daily files.

## Features

- Tests connectivity to multiple websites in parallel
- Remote logging (Logtail)
- Runs automatically in background, even when laptop is closed

## Usage

### Remote Logs

View remote logs at:
**Live Tail**: https://telemetry.betterstack.com/team/387653/tail?rf=now-60m

<img width="1708" alt="image" src="https://github.com/user-attachments/assets/f1725f13-28d5-4779-b8bd-61cfa36cfe91" />

You can change the time range by modifying the URL parameter (e.g., `?rf=now-30m` for 30 minutes, `?rf=now-24h` for 24 hours) or by using the time range selector in the Logtail web UI.

For manual testing and local log viewing, see [`setup/README.md`](setup/README.md).

## Setup & Configuration

📋 **Setup Guide**: [`setup/README.md`](setup/README.md) - Complete installation and configuration instructions

📊 **Log Details**: [`logs/README.md`](logs/README.md) - Log organization and remote logging setup

## Requirements

- Python 3 (uses built-in `urllib` and `concurrent.futures` modules, no external dependencies)
- macOS with launchctl for scheduling

## Testing

This project includes comprehensive unit tests for all modules. The test suite covers:

- **Logging functionality**: File logging, remote logging (Logtail), and data preparation
- **Site checking**: HTTP requests, error handling, and concurrent execution
- **Timestamp handling**: Timezone calculations and formatting
- **WiFi detection**: Network name detection via multiple methods

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest tests/ -v

# Run tests with coverage
pytest tests/ -v --cov=src --cov-report=term-missing
```

### Continuous Integration

GitHub Actions automatically runs all tests on every commit to ensure code quality and functionality.
