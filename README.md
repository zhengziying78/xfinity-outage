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

You can change the time range by modifying the URL parameter (e.g., `?rf=now-30m` for 30 minutes, `?rf=now-24h` for 24 hours) or by using the time range selector in the Logtail web UI.

For manual testing and local log viewing, see [`setup/README.md`](setup/README.md).

## Setup & Configuration

📋 **Setup Guide**: [`setup/README.md`](setup/README.md) - Complete installation and configuration instructions

📊 **Log Details**: [`logs/README.md`](logs/README.md) - Log organization and remote logging setup

## Requirements

- Python 3 (uses built-in `urllib` and `concurrent.futures` modules, no external dependencies)
- macOS with launchctl for scheduling