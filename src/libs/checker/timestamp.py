import datetime
import time


def get_timestamp_info():
    """Get comprehensive timestamp and timezone information."""
    now = datetime.datetime.now()
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    
    # Get timezone name and offset
    local_tz_name = time.tzname[time.daylight]
    
    # Get UTC offset in a more reliable way
    offset_seconds = now.astimezone().utcoffset().total_seconds()
    offset_hours = int(offset_seconds // 3600)
    offset_minutes = int(abs(offset_seconds % 3600) // 60)
    gmt_offset = f"GMT{offset_hours:+03d}{offset_minutes:02d}"
    
    # Create timezone info string
    timezone_info = f"{local_tz_name} {gmt_offset}"
    
    return {
        'timestamp_local': now.strftime('%Y-%m-%d %H:%M:%S'),
        'timestamp_utc': now_utc.strftime('%Y-%m-%d %H:%M:%S'),
        'timezone_local': timezone_info
    }