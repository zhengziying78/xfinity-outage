"""
Argument parsing functionality for plotting scripts.
"""

import argparse
import os
from .system_utils import get_hostname


def create_plot_argument_parser():
    """Create and configure argument parser for plotting scripts."""
    parser = argparse.ArgumentParser(description='Generate connectivity success rate plots')
    parser.add_argument('--hostname', default=get_hostname(), 
                       help='Hostname to plot data for (default: current machine)')
    parser.add_argument('--wifi-network', default='GoTitansFC',
                       help='WiFi network to filter by (default: GoTitansFC)')
    parser.add_argument('--time-range', type=int, default=72,
                       help='Time range in hours to plot (default: 72)')
    parser.add_argument('--interval', type=int, default=15,
                       help='Aggregation interval in minutes (default: 15)')
    parser.add_argument('--output-dir', default=os.path.expanduser('~/Desktop'),
                       help='Output directory for PNG files (default: ~/Desktop)')
    parser.add_argument('--output', help='Specific output file path (overrides --output-dir)')
    
    return parser


def print_configuration(args):
    """Print the configuration settings to console."""
    print(f"Hostname: {args.hostname}")
    print(f"WiFi network filter: {args.wifi_network}")
    print(f"Time range: {args.time_range} hours")
    print(f"Aggregation interval: {args.interval} minutes")
    print(f"Output directory: {args.output_dir}")