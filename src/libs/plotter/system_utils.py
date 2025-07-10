"""
System utility functions for getting system information.
"""

import socket


def get_hostname() -> str:
    """Get the current machine's hostname."""
    return socket.gethostname()