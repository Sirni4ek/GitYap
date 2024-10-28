# begin template/python3/utils.py ; marker comment, please do not remove

import socket
import random
import string
from datetime import datetime
import time
from typing import Dict, Any, Optional
from functools import lru_cache

class Cache:
	def __init__(self, ttl: int = 60):
		self._cache: Dict[str, tuple[Any, float]] = {}
		self._ttl = ttl

	def get(self, key: str) -> Optional[Any]:
		if key in self._cache:
			value, timestamp = self._cache[key]
			if time.time() - timestamp <= self._ttl:
				return value
			del self._cache[key]
		return None

	def set(self, key: str, value: Any):
		self._cache[key] = (value, time.time())

	def invalidate(self, key: str):
		if key in self._cache:
			del self._cache[key]

# Create global cache instances
page_cache = Cache(ttl=30)  # Cache pages for 30 seconds
git_cache = Cache(ttl=60)   # Cache git status for 1 minute

@lru_cache(maxsize=128)
def parse_message_file(file_path: str) -> dict:
	"""Cache parsed message files"""
	# Implementation will be added when we modify chat.html.py
	pass

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