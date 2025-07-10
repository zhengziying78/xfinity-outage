#!/usr/bin/env python3
"""
Connectivity Data Plotting Script

This script generates a dot line graph showing success rates over time
for connectivity logs from the current machine's hostname.
"""

import os
import sys
from libs.plotter.arg_parser import create_plot_argument_parser, print_configuration
from libs.plotter.dependencies import exit_if_dependencies_missing
from libs.plotter.path_utils import setup_logs_directory, resolve_output_path
from libs.plotter.log_parser import parse_log_files
from libs.plotter.data_aggregator import aggregate_by_interval
from libs.plotter.chart_generator import plot_success_rates
from libs.plotter.file_utils import open_file_non_blocking




def main():
    """Main function."""
    # Parse command line arguments
    parser = create_plot_argument_parser()
    args = parser.parse_args()
    
    # Check for required dependencies
    exit_if_dependencies_missing()
    
    # Print configuration
    print_configuration(args)
    
    # Set up paths
    logs_dir = setup_logs_directory(__file__)
    
    # Parse log files
    data = parse_log_files(logs_dir, args.hostname, args.wifi_network, args.time_range)
    
    if not data:
        print("No data found to plot")
        sys.exit(1)
    
    # Aggregate data by specified intervals
    aggregated_data = aggregate_by_interval(data, args.interval)
    
    # Resolve output file path
    output_file = resolve_output_path(args)
    
    # Plot the data
    saved_file = plot_success_rates(aggregated_data, args.hostname, args.wifi_network, args.interval, output_file)
    
    # Open the file in a non-blocking way
    if saved_file and os.path.exists(saved_file):
        if open_file_non_blocking(saved_file):
            print(f"Opening plot file: {saved_file}")


if __name__ == '__main__':
    main()