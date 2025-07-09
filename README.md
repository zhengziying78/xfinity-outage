# Internet Connectivity Checker

A Python script that monitors internet connectivity by testing access to popular websites and logs results to daily files.

## Features

- Tests connectivity to GitHub, Google, Apple, and Reddit in parallel
- Logs results with timestamps to daily log files organized by hostname
- Measures response times for each website tested
- Remote logging to Logtail (Better Stack) for centralized monitoring
- Automated scheduling via macOS LaunchAgent/LaunchDaemon

## Usage

For manual testing and local log viewing, see [`setup/README.md`](setup/README.md).

### Remote Logs

View remote logs at:
**Live Tail**: https://telemetry.betterstack.com/team/387653/tail?rf=now-60m

You can change the time range by modifying the URL parameter (e.g., `?rf=now-30m` for 30 minutes, `?rf=now-24h` for 24 hours) or by using the time range selector in the Logtail web UI.

## Setup & Configuration

📋 **Setup Guide**: [`setup/README.md`](setup/README.md) - Complete installation and configuration instructions

📊 **Log Details**: [`logs/README.md`](logs/README.md) - Log organization and remote logging setup

## Requirements

- Python 3 (uses built-in `urllib` and `concurrent.futures` modules, no external dependencies)
- macOS with launchctl for scheduling