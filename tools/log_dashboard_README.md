# Log Dashboard

A web-based dashboard for visualizing and analyzing log files from the pAIssive_income project.

## Features

- Real-time log viewing with automatic refresh
- Filtering by log level, module, and time range
- Log statistics and visualizations
- Search functionality
- Support for multiple log files

## Installation

Install the required dependencies:

```bash
pip install -r tools/log_dashboard_requirements.txt
```

## Usage

Run the dashboard:

```bash
python tools/log_dashboard.py [--port PORT] [--log-dir LOG_DIR]
```

Arguments:
- `--port PORT`: Port to run the dashboard on (default: 8050)
- `--log-dir LOG_DIR`: Directory containing log files (default: current directory)

Then open your web browser and navigate to `http://localhost:8050` (or the port you specified).

## Dashboard Sections

### Log Files

Select the log file you want to analyze from the dropdown menu. The dashboard will display information about the selected file, including:
- Number of log entries
- File size
- Last modified timestamp

### Filters

Filter log entries by:
- Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Module
- Date range

### Visualizations

The dashboard provides several visualizations:

1. **Log Level Distribution**: Pie chart showing the distribution of log entries by log level
2. **Logs by Module**: Bar chart showing the number of log entries per module
3. **Logs by Time**: Line chart showing log activity over time, broken down by log level

### Log Entries

View the actual log entries, filtered according to your selections. The log entries are displayed in reverse chronological order (newest first) and include:
- Timestamp
- Log level (color-coded)
- Module name
- Log message

Use the search box to find specific log entries by their content.

## Customization

You can customize the dashboard by modifying the `tools/log_dashboard.py` file:

- Change the log pattern regex to match your log format
- Adjust the color scheme
- Add additional visualizations
- Modify the refresh interval (default: 30 seconds)

## Troubleshooting

If you encounter any issues:

1. Make sure your log files follow the expected format:
   ```
   YYYY-MM-DD HH:MM:SS - MODULE_NAME - LEVEL - MESSAGE
   ```

2. Check that you have the required dependencies installed.

3. Verify that the log directory contains valid log files with the `.log` extension.

4. If the dashboard is slow, try filtering the logs or using smaller log files.

## Contributing

Contributions to improve the log dashboard are welcome! Please feel free to submit pull requests or open issues with suggestions.
