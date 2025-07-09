# BetterStack Dashboard Configuration

## Chart 1: Success vs Failed Pie Chart

### Chart Type: Pie Chart
### Query Configuration:
```sql
-- Group by status for the last N hours (using dashboard time picker)
SELECT 
  status,
  COUNT(*) as count
FROM logs 
WHERE timestamp >= $__timeFrom()
  AND timestamp <= $__timeTo()
GROUP BY status
```

**Alternative with variable:**
```sql
-- Using a dashboard variable for hours
SELECT 
  status,
  COUNT(*) as count
FROM logs 
WHERE timestamp >= NOW() - INTERVAL $hours HOUR
GROUP BY status
```

### Chart Settings:
- **Time Range**: Last 3 hours (configurable)
- **Group By**: status field
- **Metric**: Count of records
- **Chart Type**: Pie
- **Legend**: Show percentage and count
- **Colors**: 
  - Success: Green (#28a745)
  - Failed: Red (#dc3545)

### BetterStack UI Configuration:
1. Go to your BetterStack dashboard
2. Click "Add Chart" → "Pie Chart"
3. Set the query to group by `status` field
4. Set time range to "Last 3 hours"
5. Enable percentage display in legend

---

## Chart 2: Failed Count Over Time Bar Chart

### Chart Type: Bar Chart
### Query Configuration:
```sql
-- Show failed_count over time (using dashboard time picker)
SELECT 
  DATE_TRUNC('minute', timestamp) as time_bucket,
  failed_count
FROM logs 
WHERE timestamp >= $__timeFrom()
  AND timestamp <= $__timeTo()
ORDER BY time_bucket
```

**Alternative with variable:**
```sql
-- Using a dashboard variable for hours
SELECT 
  DATE_TRUNC('minute', timestamp) as time_bucket,
  failed_count
FROM logs 
WHERE timestamp >= NOW() - INTERVAL $hours HOUR
ORDER BY time_bucket
```

### Chart Settings:
- **Time Range**: Last 3 hours (configurable)
- **X-Axis**: Time (timestamp field)
- **Y-Axis**: failed_count field
- **Chart Type**: Bar Chart
- **Aggregation**: None (show raw failed_count values)
- **Time Bucket**: 1 minute intervals
- **Color**: Red (#dc3545) for failed counts

### BetterStack UI Configuration:
1. Go to your BetterStack dashboard
2. Click "Add Chart" → "Bar Chart"
3. Set X-axis to timestamp field
4. Set Y-axis to failed_count field
5. Set time range to "Last 3 hours"
6. Set time bucket to 1 minute for granular view

---

## Making Time Range Dynamic:

### Method 1: Dashboard Time Picker (Recommended)
- Use `$__timeFrom()` and `$__timeTo()` macros
- BetterStack automatically provides these based on the dashboard time picker
- Users can select "Last 3 hours", "Last 24 hours", etc. from dropdown

### Method 2: Dashboard Variables
1. Create a dashboard variable called `hours`
2. Set default value to `3`
3. Add options: 1, 3, 6, 12, 24
4. Use `$hours` in your queries

### Method 3: Template Variables
```sql
-- Create a template variable in dashboard settings
-- Variable name: time_range
-- Options: "1 HOUR", "3 HOUR", "6 HOUR", "12 HOUR", "24 HOUR"
WHERE timestamp >= NOW() - INTERVAL $time_range
```

## Dashboard Layout Suggestions:

1. **Row 1**: Place the pie chart (Success vs Failed percentage)
2. **Row 2**: Place the bar chart (Failed count timeline)
3. **Time Range Control**: Add a global time picker or variable dropdown

## Available Fields in Your Data:
Based on your logging code, these fields are available:
- `status`: "success" or "failed"
- `failed_count`: Number of failed site checks
- `success_count`: Number of successful site checks  
- `total_count`: Total number of sites checked
- `success_percentage`: Calculated success percentage
- `failed_percentage`: Calculated failed percentage
- `timestamp_utc`: UTC timestamp
- `timestamp_local`: Local timestamp
- `hostname`: Machine hostname
- `wifi_network`: WiFi network name

## Alternative Chart Ideas:
- **Success Rate Trend**: Line chart showing success_percentage over time
- **Response Time**: Chart showing average duration from site checks
- **Network Analysis**: Group by wifi_network to see connectivity by network
- **Host Comparison**: Compare connectivity across different hostnames