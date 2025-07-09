import subprocess


def get_wifi_network():
    """Get the currently connected WiFi network name."""
    # Try method 1: networksetup (works for regular WiFi)
    try:
        result = subprocess.run(['networksetup', '-getairportnetwork', 'en0'], 
                              capture_output=True, text=True, check=True)
        output = result.stdout.strip()
        if "Current Wi-Fi Network:" in output:
            return output.replace("Current Wi-Fi Network: ", "")
    except:
        pass
    
    # Try method 2: system_profiler (works for hotspots and regular WiFi)
    try:
        result = subprocess.run(['system_profiler', 'SPAirPortDataType'], 
                              capture_output=True, text=True, check=True)
        lines = result.stdout.split('\n')
        for i, line in enumerate(lines):
            if "Current Network Information:" in line:
                # Look for the network name in the next few lines
                for j in range(i+1, min(i+10, len(lines))):
                    next_line = lines[j].strip()
                    if next_line and ':' in next_line and not next_line.startswith('PHY Mode') and not next_line.startswith('Channel') and not next_line.startswith('Country Code') and not next_line.startswith('Network Type'):
                        network_name = next_line.split(':')[0].strip()
                        if network_name:
                            return network_name
    except:
        pass
    
    return "Not connected to WiFi"