"""
Chart generation functionality for connectivity data visualization.
"""

import datetime
from typing import List, Tuple
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def plot_success_rates(data: List[Tuple[datetime.datetime, float]], hostname: str, wifi_network: str, interval_minutes: int = 15, output_file: str = None):
    """Plot success rates as a dot line graph."""
    if not data:
        print("No data to plot")
        return None
    
    # Extract timestamps and success rates
    timestamps = [item[0] for item in data]
    success_rates = [item[1] * 100 for item in data]  # Convert to percentage
    failure_rates = [100 - rate for rate in success_rates]  # Calculate failure percentage
    
    # Create the plot
    plt.figure(figsize=(12, 6))
    
    # Calculate bar width based on interval
    bar_width = datetime.timedelta(minutes=interval_minutes * 0.8)  # 80% of interval for spacing
    
    # Create stacked bar chart
    # Bottom bars (failure) in orange-red (colorblind friendly)
    plt.bar(timestamps, failure_rates, width=bar_width, color='#FF6B35', alpha=0.8, 
           edgecolor='black', linewidth=0.5, label='Failure')
    # Top bars (success) in light green with tiny blue tone (colorblind friendly)
    plt.bar(timestamps, success_rates, width=bar_width, color='#66D9A6', alpha=0.8,
           bottom=failure_rates, edgecolor='black', linewidth=0.5, label='Success')
    
    # Set labels and title
    plt.title(f'Internet Connectivity Success/Failure Rate - {hostname} ({wifi_network})\n{interval_minutes}-minute intervals')
    plt.xlabel('Time', labelpad=20)  # Add more space above "Time" label
    plt.ylabel('Rate (%)')
    
    # Add legend at the bottom, with more space below "Time" label
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.35), ncol=2)
    
    # Set y-axis to 0-100%
    plt.ylim(0, 105)
    
    # Format x-axis with labels aligned to midnight, at least every 3 hours
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
    # Set locator to align with midnight (every 3 hours: 00:00, 03:00, 06:00, 09:00, etc.)
    plt.gca().xaxis.set_major_locator(mdates.HourLocator(byhour=range(0, 24, 3)))
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