import datetime
import time


def get_timestamp_info():
    """Get comprehensive timestamp and timezone information."""
    # Get timezone info
    local_tz = time.tzname[time.daylight]
    # Map common timezone abbreviations to full names
    timezone_map = {
        'PST': 'Pacific Standard Time',
        'PDT': 'Pacific Daylight Time',
        'EST': 'Eastern Standard Time',
        'EDT': 'Eastern Daylight Time',
        'MST': 'Mountain Standard Time',
        'MDT': 'Mountain Daylight Time',
        'CST': 'Central Standard Time',
        'CDT': 'Central Daylight Time',
        'HST': 'Hawaii Standard Time',
        'HDT': 'Hawaii Daylight Time',
        'AKST': 'Alaska Standard Time',
        'AKDT': 'Alaska Daylight Time'
    }
    timezone_full = timezone_map.get(local_tz, local_tz)
    
    # Get GMT offset
    local_time = time.localtime()
    offset_seconds = -time.timezone + (time.daylight * 3600)
    offset_hours = offset_seconds // 3600
    offset_minutes = abs(offset_seconds % 3600) // 60
    gmt_offset = f"GMT{offset_hours:+03d}{offset_minutes:02d}"
    
    # Create comprehensive timezone info
    timezone_info = f"{local_tz} ({timezone_full}) {gmt_offset}"
    
    return {
        'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'timestamp_utc': datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
        'timezone_local': timezone_info
    }