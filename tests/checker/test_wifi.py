import pytest
from unittest.mock import patch, MagicMock
import subprocess
from src.libs.checker.wifi import (
    get_wifi_network_via_networksetup,
    get_wifi_network_via_system_profiler,
    get_wifi_network
)


class TestWiFi:

    @patch('src.libs.checker.wifi.subprocess.run')
    def test_get_wifi_network_via_networksetup_success(self, mock_run):
        """Test successful WiFi network detection via networksetup."""
        mock_result = MagicMock()
        mock_result.stdout = "Current Wi-Fi Network: HomeNetwork\n"
        mock_run.return_value = mock_result
        
        result = get_wifi_network_via_networksetup()
        
        assert result == "HomeNetwork"
        mock_run.assert_called_once_with(
            ['networksetup', '-getairportnetwork', 'en0'],
            capture_output=True, text=True, check=True
        )

    @patch('src.libs.checker.wifi.subprocess.run')
    def test_get_wifi_network_via_networksetup_with_spaces(self, mock_run):
        """Test WiFi network with spaces in name."""
        mock_result = MagicMock()
        mock_result.stdout = "Current Wi-Fi Network: My Home Network\n"
        mock_run.return_value = mock_result
        
        result = get_wifi_network_via_networksetup()
        
        assert result == "My Home Network"

    @patch('src.libs.checker.wifi.subprocess.run')
    def test_get_wifi_network_via_networksetup_no_network(self, mock_run):
        """Test when no WiFi network is connected."""
        mock_result = MagicMock()
        mock_result.stdout = "You are not associated with an AirPort network.\n"
        mock_run.return_value = mock_result
        
        result = get_wifi_network_via_networksetup()
        
        assert result is None

    @patch('src.libs.checker.wifi.subprocess.run')
    def test_get_wifi_network_via_networksetup_exception(self, mock_run):
        """Test exception handling in networksetup method."""
        mock_run.side_effect = subprocess.CalledProcessError(1, ['networksetup'])
        
        result = get_wifi_network_via_networksetup()
        
        assert result is None

    @patch('src.libs.checker.wifi.subprocess.run')
    def test_get_wifi_network_via_networksetup_empty_output(self, mock_run):
        """Test empty output from networksetup."""
        mock_result = MagicMock()
        mock_result.stdout = ""
        mock_run.return_value = mock_result
        
        result = get_wifi_network_via_networksetup()
        
        assert result is None

    @patch('src.libs.checker.wifi.subprocess.run')
    def test_get_wifi_network_via_system_profiler_success(self, mock_run):
        """Test successful WiFi network detection via system_profiler."""
        mock_result = MagicMock()
        mock_result.stdout = """
        AirPort:

          Software Versions:
              CoreWLAN: 13.0 (1380.1)
              CoreWLANKit: 13.0 (1380.1)
              Menu Extra: 14.0 (1400.1)
              System Information: 14.0 (1400.1)
              IO80211 Family: 12.0 (1200.12.2b1)
              Diagnostics: 11.0 (1100.32)
              AirPort Utility: 6.3.9 (639.15)

          Interfaces:

              en0:
                Card Type: AirPort Extreme  (0x14E4, 0x10F)
                Firmware Version: Broadcom BCM43xx 1.0 (7.15.166.50.8)
                MAC Address: aa:bb:cc:dd:ee:ff
                Locale: FCC
                Country Code: US
                Supported PHY Modes: 802.11 a/b/g/n/ac
                Supported Channels: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 36, 40, 44, 48, 52, 56, 60, 64, 100, 104, 108, 112, 116, 120, 124, 128, 132, 136, 140, 144, 149, 153, 157, 161, 165
                Wake On Wireless: Supported
                AirDrop: Supported
                Status: Connected
                Current Network Information:
                  TestNetwork:
                    PHY Mode: 802.11ac
                    Channel: 36
                    Country Code: US
                    Network Type: Infrastructure
                    Security: WPA2 Personal
                    Signal / Noise: -40 dBm / -92 dBm
                    Transmit Rate: 866
                    MCS Index: 9
        """
        mock_run.return_value = mock_result
        
        result = get_wifi_network_via_system_profiler()
        
        assert result == "TestNetwork"
        mock_run.assert_called_once_with(
            ['system_profiler', 'SPAirPortDataType'],
            capture_output=True, text=True, check=True
        )

    @patch('src.libs.checker.wifi.subprocess.run')
    def test_get_wifi_network_via_system_profiler_hotspot(self, mock_run):
        """Test WiFi network detection for hotspot connections."""
        mock_result = MagicMock()
        mock_result.stdout = """
        AirPort:
          Interfaces:
              en0:
                Status: Connected
                Current Network Information:
                  iPhone Hotspot:
                    PHY Mode: 802.11n
                    Channel: 6
                    Network Type: Infrastructure
                    Security: WPA2 Personal
        """
        mock_run.return_value = mock_result
        
        result = get_wifi_network_via_system_profiler()
        
        assert result == "iPhone Hotspot"

    @patch('src.libs.checker.wifi.subprocess.run')
    def test_get_wifi_network_via_system_profiler_network_with_spaces(self, mock_run):
        """Test WiFi network with spaces in name via system_profiler."""
        mock_result = MagicMock()
        mock_result.stdout = """
        AirPort:
          Interfaces:
              en0:
                Status: Connected
                Current Network Information:
                  My Home Network 5G:
                    PHY Mode: 802.11ac
                    Channel: 149
                    Network Type: Infrastructure
        """
        mock_run.return_value = mock_result
        
        result = get_wifi_network_via_system_profiler()
        
        assert result == "My Home Network 5G"

    @patch('src.libs.checker.wifi.subprocess.run')
    def test_get_wifi_network_via_system_profiler_no_current_network(self, mock_run):
        """Test when no current network information is available."""
        mock_result = MagicMock()
        mock_result.stdout = """
        AirPort:
          Interfaces:
              en0:
                Status: Off
                Card Type: AirPort Extreme
        """
        mock_run.return_value = mock_result
        
        result = get_wifi_network_via_system_profiler()
        
        assert result is None

    @patch('src.libs.checker.wifi.subprocess.run')
    def test_get_wifi_network_via_system_profiler_exception(self, mock_run):
        """Test exception handling in system_profiler method."""
        mock_run.side_effect = subprocess.CalledProcessError(1, ['system_profiler'])
        
        result = get_wifi_network_via_system_profiler()
        
        assert result is None

    @patch('src.libs.checker.wifi.subprocess.run')
    def test_get_wifi_network_via_system_profiler_empty_network_name(self, mock_run):
        """Test handling of empty network name in system_profiler output."""
        mock_result = MagicMock()
        mock_result.stdout = """
        AirPort:
          Interfaces:
              en0:
                Status: Connected
                Current Network Information:
                  :
                    PHY Mode: 802.11ac
                    Channel: 36
        """
        mock_run.return_value = mock_result
        
        result = get_wifi_network_via_system_profiler()
        
        assert result is None

    @patch('src.libs.checker.wifi.subprocess.run')
    def test_get_wifi_network_via_system_profiler_filtered_lines(self, mock_run):
        """Test that system_profiler filters out unwanted lines."""
        mock_result = MagicMock()
        mock_result.stdout = """
        AirPort:
          Interfaces:
              en0:
                Status: Connected
                Current Network Information:
                  PHY Mode: 802.11ac
                  Channel: 36
                  Country Code: US
                  Network Type: Infrastructure
                  TestNetwork:
                    PHY Mode: 802.11ac
                    Channel: 36
        """
        mock_run.return_value = mock_result
        
        result = get_wifi_network_via_system_profiler()
        
        assert result == "TestNetwork"

    @patch('src.libs.checker.wifi.get_wifi_network_via_system_profiler')
    @patch('src.libs.checker.wifi.get_wifi_network_via_networksetup')
    def test_get_wifi_network_networksetup_success(self, mock_networksetup, mock_system_profiler):
        """Test get_wifi_network when networksetup succeeds."""
        mock_networksetup.return_value = "HomeNetwork"
        mock_system_profiler.return_value = "BackupNetwork"
        
        result = get_wifi_network()
        
        assert result == "HomeNetwork"
        mock_networksetup.assert_called_once()
        mock_system_profiler.assert_not_called()

    @patch('src.libs.checker.wifi.get_wifi_network_via_system_profiler')
    @patch('src.libs.checker.wifi.get_wifi_network_via_networksetup')
    def test_get_wifi_network_fallback_to_system_profiler(self, mock_networksetup, mock_system_profiler):
        """Test get_wifi_network fallback to system_profiler when networksetup fails."""
        mock_networksetup.return_value = None
        mock_system_profiler.return_value = "HotspotNetwork"
        
        result = get_wifi_network()
        
        assert result == "HotspotNetwork"
        mock_networksetup.assert_called_once()
        mock_system_profiler.assert_called_once()

    @patch('src.libs.checker.wifi.get_wifi_network_via_system_profiler')
    @patch('src.libs.checker.wifi.get_wifi_network_via_networksetup')
    def test_get_wifi_network_both_methods_fail(self, mock_networksetup, mock_system_profiler):
        """Test get_wifi_network when both methods fail."""
        mock_networksetup.return_value = None
        mock_system_profiler.return_value = None
        
        result = get_wifi_network()
        
        assert result == "Not connected to WiFi"
        mock_networksetup.assert_called_once()
        mock_system_profiler.assert_called_once()

    @patch('src.libs.checker.wifi.get_wifi_network_via_system_profiler')
    @patch('src.libs.checker.wifi.get_wifi_network_via_networksetup')
    def test_get_wifi_network_networksetup_returns_empty_string(self, mock_networksetup, mock_system_profiler):
        """Test get_wifi_network when networksetup returns empty string."""
        mock_networksetup.return_value = ""
        mock_system_profiler.return_value = "SystemProfilerNetwork"
        
        result = get_wifi_network()
        
        assert result == "SystemProfilerNetwork"
        mock_networksetup.assert_called_once()
        mock_system_profiler.assert_called_once()

    @patch('src.libs.checker.wifi.subprocess.run')
    def test_get_wifi_network_via_system_profiler_malformed_output(self, mock_run):
        """Test handling of malformed system_profiler output."""
        mock_result = MagicMock()
        mock_result.stdout = """
        AirPort:
          Interfaces:
              en0:
                Status: Connected
                Current Network Information:
                  NoColonInThisLine
                  AnotherLineWithoutColon
        """
        mock_run.return_value = mock_result
        
        result = get_wifi_network_via_system_profiler()
        
        assert result is None

    @patch('src.libs.checker.wifi.subprocess.run')
    def test_get_wifi_network_via_system_profiler_with_special_characters(self, mock_run):
        """Test WiFi network name with special characters."""
        mock_result = MagicMock()
        mock_result.stdout = """
        AirPort:
          Interfaces:
              en0:
                Status: Connected
                Current Network Information:
                  Network-Name_With.Special@Chars:
                    PHY Mode: 802.11ac
                    Channel: 36
        """
        mock_run.return_value = mock_result
        
        result = get_wifi_network_via_system_profiler()
        
        assert result == "Network-Name_With.Special@Chars"

    @patch('src.libs.checker.wifi.subprocess.run')
    def test_get_wifi_network_via_networksetup_generic_exception(self, mock_run):
        """Test generic exception handling in networksetup method."""
        mock_run.side_effect = Exception("Generic error")
        
        result = get_wifi_network_via_networksetup()
        
        assert result is None

    @patch('src.libs.checker.wifi.subprocess.run')
    def test_get_wifi_network_via_system_profiler_generic_exception(self, mock_run):
        """Test generic exception handling in system_profiler method."""
        mock_run.side_effect = Exception("Generic error")
        
        result = get_wifi_network_via_system_profiler()
        
        assert result is None