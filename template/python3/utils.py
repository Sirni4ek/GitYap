# begin template/python3/utils.py ; marker comment, please do not remove

import socket
import random
import string
from datetime import datetime

def is_port_in_use(port: int) -> bool:
    """Check if a port is already in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def find_available_port(start_port: int) -> int:
    """Find an available port starting from the given port"""
    port = start_port
    while is_port_in_use(port):
        port += 1
    return port

def generate_title(message: str) -> str:
    """Generate a title for the message file"""
    if not message:
        return ''.join(random.choices(string.ascii_lowercase, k=10))

    words = message.split()[:5]
    title = '_'.join(words)
    safe_title = ''.join(c for c in title if c.isalnum() or c in ['_', '-'])
    return safe_title

# end utils.py ; marker comment, please do not remove