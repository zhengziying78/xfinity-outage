# Internet Connectivity Checker

A Python script that monitors internet connectivity by testing access to popular websites and logs results to daily files.

## Features

- Tests connectivity to multiple websites every minute
- Runs automatically in background, even when laptop is closed
- Creates bar charts from log data to show when internet was working vs broken

## Usage

### Connectivity Monitoring

You can run the connectivity checker in two ways:

- **Manual run**: Execute the script directly to test connectivity immediately
- **Scheduled run**: Configure it to run automatically at regular intervals

All connectivity results are logged to files organized by date and hostname (e.g., `logs/hostname/connectivity_log_20250709.txt`) and committed to the repository. Each log entry includes timestamp, WiFi network name, and connectivity status for each tested website. 

You can view the log files directly on GitHub: [all logs](https://github.com/zhengziying78/xfinity-outage/tree/main/logs) or [logs from specific hostname](https://github.com/zhengziying78/xfinity-outage/tree/main/logs/Ziyings-MacBook-Pro.local).

### Plotting Charts

Make bar charts from your log data:

```bash
# Generate plot with default settings (72 hours, 15-minute intervals)
python3 src/plot_outage_graph.py

# Customize time range and interval
python3 src/plot_outage_graph.py --time-range 24 --interval 30

# Specify different hostname or WiFi network
python3 src/plot_outage_graph.py --hostname other-machine --wifi-network "MyWiFi"

# Save to specific location
python3 src/plot_outage_graph.py --output-dir ~/Documents --output my_plot.png
```

**Example**

<img width="3553" height="1634" alt="image" src="https://github.com/user-attachments/assets/64d3ec7f-cf87-4a3a-86a4-f6f47fbd046e" />

For detailed setup instructions and configuration options, see [`setup/README.md`](setup/README.md).

## Setup & Configuration

📋 **Setup Guide**: [`setup/README.md`](setup/README.md) - Complete installation and configuration instructions

📊 **Log Details**: [`logs/README.md`](logs/README.md) - Log organization and file structure

## Requirements

- Python 3 (uses built-in `urllib` and `concurrent.futures` modules, no external dependencies)
- macOS with launchctl for scheduling
- For plotting: `matplotlib` (install with `pip install matplotlib`)

## Testing

This project includes comprehensive unit tests for all modules. The test suite covers:

- **Logging functionality**: File logging and data preparation
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
