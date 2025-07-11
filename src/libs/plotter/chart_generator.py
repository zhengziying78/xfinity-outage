"""
Chart generation functionality for connectivity data visualization.
"""

import datetime
from typing import List, Tuple
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def plot_success_rates(data: List[Tuple[datetime.datetime, float, str]], hostname: str, wifi_network: str, interval_minutes: int = 15, output_file: str = None):
    """Plot success rates as a dot line graph."""
    if not data:
        print("No data to plot")
        return None
    
    # Separate data by status
    measured_data = [(item[0], item[1]) for item in data if item[2] == "measured"]
    missing_data = [(item[0], item[1]) for item in data if item[2] == "missing"]
    
    # Create the plot
    plt.figure(figsize=(12, 6))
    
    # Calculate bar width based on interval
    bar_width = datetime.timedelta(minutes=interval_minutes * 0.8)  # 80% of interval for spacing
    
    # Plot measured data with normal colors
    if measured_data:
        timestamps = [item[0] for item in measured_data]
        success_rates = [item[1] * 100 for item in measured_data]  # Convert to percentage
        failure_rates = [100 - rate for rate in success_rates]  # Calculate failure percentage
        
        # Create stacked bar chart for measured data
        # Bottom bars (failure) in orange-red (colorblind friendly)
        plt.bar(timestamps, failure_rates, width=bar_width, color='#FF6B35', alpha=0.8, 
               edgecolor='black', linewidth=0.5, label='Connection Failed')
        # Top bars (success) in light green with tiny blue tone (colorblind friendly)
        plt.bar(timestamps, success_rates, width=bar_width, color='#66D9A6', alpha=0.8,
               bottom=failure_rates, edgecolor='black', linewidth=0.5, label='Connection Success')
    
    # Plot missing data with distinctive styling
    if missing_data:
        missing_timestamps = [item[0] for item in missing_data]
        missing_heights = [100 for _ in missing_data]  # Full height bars
        
        # Create bars for missing data with dotted border and no fill
        plt.bar(missing_timestamps, missing_heights, width=bar_width, 
               color='none', edgecolor='black', linewidth=0.5, 
               linestyle=':', label='No Data Recorded')
    
    # Set labels and title
    plt.title(f'Internet Connectivity Success/Failure Rate - {hostname} ({wifi_network})\n{interval_minutes}-minute intervals')
    plt.xlabel('Time', labelpad=20)  # Add more space above "Time" label
    plt.ylabel('Rate (%)')
    
    # Add legend at the bottom, with more space below "Time" label
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.35), ncol=3)
    
    # Set y-axis to 0-100%
    plt.ylim(0, 105)
    
    # Custom x-axis formatting: show date for 00:00, leftmost, rightmost labels; only time for others
    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.HourLocator(byhour=range(0, 24, 3)))
    
    # Custom formatter function
    def custom_date_formatter(x, pos):
        date = mdates.num2date(x)
        # Get all tick locations to determine leftmost and rightmost
        tick_locs = ax.get_xticks()
        is_leftmost = (pos == 0)
        is_rightmost = (pos == len(tick_locs) - 1)
        is_midnight = (date.hour == 0 and date.minute == 0)
        
        if is_leftmost or is_rightmost or is_midnight:
            return date.strftime('%m/%d %H:%M')
        else:
            return date.strftime('%H:%M')
    
    ax.xaxis.set_major_formatter(plt.FuncFormatter(custom_date_formatter))
    plt.xticks(rotation=45)
    
    # Add grid
    plt.grid(True, alpha=0.3)
    
    # Tight layout
    plt.tight_layout()
    
    # Save the plot
    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Plot saved to: {output_file}")
        plt.close()  # Close the figure to free memory
        return output_file
    else:
        plt.show()
        return None