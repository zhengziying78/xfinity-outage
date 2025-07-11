"""
Data aggregation functionality for time-series connectivity data.
"""

import datetime
from typing import List, Tuple


def aggregate_by_interval(data: List[Tuple[datetime.datetime, float]], interval_minutes: int = 15) -> List[Tuple[datetime.datetime, float, str]]:
    """Aggregate data into specified minute intervals with data status."""
    if not data:
        return []
    
    # Group data by specified intervals
    intervals = {}
    
    for timestamp, success_rate in data:
        # Calculate the interval boundary (round down to nearest interval mark)
        minutes_since_hour = timestamp.minute
        interval_start_minute = (minutes_since_hour // interval_minutes) * interval_minutes
        interval_start = timestamp.replace(minute=interval_start_minute, second=0, microsecond=0)
        
        # The interval end is interval_minutes later
        interval_end = interval_start + datetime.timedelta(minutes=interval_minutes)
        
        # Use interval_end as the key (the dot position)
        if interval_end not in intervals:
            intervals[interval_end] = []
        
        intervals[interval_end].append(success_rate)
    
    # Fill in missing intervals and calculate average success rate
    if not intervals:
        return []
    
    # Get the full time range
    first_time = min(intervals.keys())
    last_time = max(intervals.keys())
    
    # Generate all expected intervals
    aggregated_data = []
    current_time = first_time
    
    while current_time <= last_time:
        if current_time in intervals:
            # Data available - calculate average
            success_rates = intervals[current_time]
            avg_success_rate = sum(success_rates) / len(success_rates)
            aggregated_data.append((current_time, avg_success_rate, "measured"))
        else:
            # No data available - mark as missing
            aggregated_data.append((current_time, 0.0, "missing"))
        
        current_time += datetime.timedelta(minutes=interval_minutes)
    
    print(f"Aggregated into {len(aggregated_data)} {interval_minutes}-minute intervals")
    return aggregated_data