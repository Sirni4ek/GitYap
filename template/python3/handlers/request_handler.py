# begin template/python3/http/request_handler.py ; marker comment, please do not remove, including this message
import json
import urllib.parse
import os
from datetime import datetime
from typing import Optional, Union, Dict, Any
from http.server import BaseHTTPRequestHandler
from handlers.script_handler import ScriptHandler

# Cache classes remain unchanged
class PageCache:
	def __init__(self):
		self.cache = {}
	
	def invalidate(self, key: str) -> None:
		if key in self.cache:
			del self.cache[key]

class GitCache:
	def __init__(self):
		self.cache = {}
	
	def invalidate(self, key: str) -> None:
		if key in self.cache:
			del self.cache[key]

# Initialize cache objects
page_cache = PageCache()
git_cache = GitCache()

class ChatHandler:
	def __init__(self, request_handler):
		"""Initialize ChatHandler with a request handler instance"""
		if not isinstance(request_handler, BaseHTTPRequestHandler):
			raise TypeError("request_handler must be an instance of BaseHTTPRequestHandler")
			
		self.handler = request_handler
		self.script_handler = ScriptHandler(request_handler)  # Use ScriptHandler instead of ChatHandler
	
	@staticmethod
	def is_valid_channel_name(channel: str) -> bool:
		"""Validate channel name - only alphanumeric and underscores allowed"""
		return channel.isalnum() or all(c.isalnum() or c == '_' for c in channel)
	
	def run_script(self, filename: str) -> None:
		"""Run a script to regenerate files"""
		self.script_handler.run_script(filename)

class RequestHandler:
	DEBUG = False

	def __init__(self, request_handler):
		"""
		Initialize the RequestHandler with a BaseHTTPRequestHandler instance
		"""
		if not isinstance(request_handler, BaseHTTPRequestHandler):
			raise TypeError("request_handler must be an instance of BaseHTTPRequestHandler")
			
		self.handler = request_handler
		self.directory = os.getenv('CHAT_DIRECTORY', './chat')
		self.chat_handler = ChatHandler(request_handler)
		
		# These attributes will be set during request handling
		self._headers = None
		self._rfile = None
		self._wfile = None

	@property
	def headers(self):
		if self._headers is None and hasattr(self.handler, 'headers'):
			self._headers = self.handler.headers
		return self._headers

	@property
	def rfile(self):
		if self._rfile is None and hasattr(self.handler, 'rfile'):
			self._rfile = self.handler.rfile
		return self._rfile

	@property
	def wfile(self):
		if self._wfile is None and hasattr(self.handler, 'wfile'):
			self._wfile = self.handler.wfile
		return self._wfile

	@staticmethod
	def debug_print(*args, **kwargs):
		if RequestHandler.DEBUG:
			print(*args, **kwargs)

	def handle_chat_post(self):
		"""Handle POST request for chat messages"""
		try:
			self.debug_print("\n=== Starting chat post handling ===")
			
			# Check initial conditions
			if not self.headers or not self.rfile:
				self.debug_print("Error: Headers or request body not initialized")
				return self.send_json_response({
					'error': 'Request not properly initialized',
					'debug_info': {
						'headers_present': bool(self.headers),
						'rfile_present': bool(self.rfile)
					}
				}, 400)

			# Get and decode request data
			content_length = int(self.headers.get('Content-Length', 0))
			self.debug_print(f"Content Length: {content_length}")
			post_data = self.rfile.read(content_length).decode('utf-8')
			self.debug_print(f"Raw POST data: {post_data}")

			# Parse JSON data
			try:
				data = json.loads(post_data)
				self.debug_print(f"Parsed data: {json.dumps(data, indent=2)}")
			except json.JSONDecodeError as e:
				self.debug_print(f"JSON decode error: {str(e)}")
				return self.send_json_response({
					'error': 'Invalid JSON format',
					'debug_info': {
						'error_message': str(e),
						'error_position': e.pos,
						'raw_data': post_data,
						'error_line': e.lineno,
						'error_column': e.colno
					}
				}, 400)

			# Extract fields
			author = data.get('author', '')
			content = data.get('content', '')
			tags = data.get('tags', [])
			channel = data.get('channel', 'general')
			
			self.debug_print(f"Extracted fields:")
			self.debug_print(f"- Author: {author}")
			self.debug_print(f"- Content: {content}")
			self.debug_print(f"- Tags: {tags}")
			self.debug_print(f"- Channel: {channel}")

			if not author:
				author = 'Guest'
				self.debug_print("Using default author: Guest")

			if not content:
				self.debug_print("Error: Missing content")
				return self.send_json_response({
					'error': 'Missing content',
					'debug_info': {'received_data': data}
				}, 400)

			if not self.chat_handler.is_valid_channel_name(channel):
				self.debug_print(f"Error: Invalid channel name: {channel}")
				return self.send_json_response({
					'error': 'Invalid channel name',
					'debug_info': {'channel': channel}
				}, 400)

			# Create message directory with correct path
			message_dir = os.path.join('./message', channel)  # Changed path
			self.debug_print(f"Message directory path: {message_dir}")
			
			try:
				os.makedirs(message_dir, exist_ok=True)
				self.debug_print(f"Created/verified directory at: {message_dir}")
			except OSError as e:
				self.debug_print(f"Error creating directory: {str(e)}")
				return self.send_json_response({
					'error': 'Failed to create message directory',
					'debug_info': {'error': str(e)}
				}, 500)

			# Generate timestamp and filename
			timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
			filename = f"{timestamp}.txt"
			filepath = os.path.join(message_dir, filename)
			self.debug_print(f"Will save message to: {filepath}")

			# Write message to file
			try:
				self.debug_print("Writing message to file...")
				with open(filepath, 'w', encoding='utf-8') as f:
					f.write(f"Author: {author}\n")
					f.write(f"Channel: {channel}\n")
					# f.write(f"Timestamp: {timestamp}\n\n") #todo
					f.write(content)
					if tags:
						f.write(f"\n\nTags: {' '.join(tags)}")
				
				# Verify file was written
				if os.path.exists(filepath):
					self.debug_print(f"Successfully wrote file. Size: {os.path.getsize(filepath)} bytes")
					with open(filepath, 'r', encoding='utf-8') as f:
						self.debug_print(f"File content verification:\n{f.read()}")
				else:
					self.debug_print("Warning: File not found after writing!")
					
			except IOError as e:
				self.debug_print(f"Error writing file: {str(e)}")
				return self.send_json_response({
					'error': 'Failed to write message',
					'debug_info': {'error': str(e)}
				}, 500)

			# Regenerate chat.html
			self.debug_print("Attempting to regenerate chat.html...")
			try:
				if hasattr(self.chat_handler, 'run_script'):
					self.chat_handler.run_script('chat.html')
					self.debug_print("Successfully regenerated chat.html")
				else:
					self.debug_print("Warning: chat_handler.run_script method not found")
			except Exception as e:
				self.debug_print(f"Error regenerating chat.html: {str(e)}")
				# Continue anyway as the message was saved

			# Invalidate cache
			self.debug_print("Invalidating caches...")
			page_cache.invalidate(f'chat/{channel}')
			git_cache.invalidate(channel)
			self.debug_print("Cache invalidation complete")

			self.debug_print("=== Chat post handling complete ===\n")
			return self.send_json_response({
				'status': 'success',
					'timestamp': timestamp,
					'debug_info': {
						'filepath': filepath,
						'channel': channel,
						'message_length': len(content)
					}
			})

		except Exception as e:
			import traceback
			trace = traceback.format_exc()
			self.debug_print(f"Unexpected error: {str(e)}")
			self.debug_print(f"Traceback:\n{trace}")
			return self.send_json_response({
				'error': str(e),
				'debug_info': {
					'traceback': trace,
					'error_type': type(e).__name__
				}
			}, 500)
			
	def handle_post_request(self, path: str):
		"""Route POST requests to appropriate handlers"""
		parsed_path = urllib.parse.urlparse(path)
		path = parsed_path.path

		if path == '/sync':
			return self.handle_sync_request()
		elif path in ['/post', '/chat.html']:
			return self.handle_chat_post()
		else:
			return self.send_json_response({'error': 'Method not allowed'}, 405)

	def handle_sync_request(self):
		"""Handle manual sync request"""
		try:
			content_length = int(self.headers.get('Content-Length', 0))
			post_data = self.rfile.read(content_length).decode('utf-8')
			data = json.loads(post_data)

			channel = data.get('channel', 'general')
			if not self.chat_handler.is_valid_channel_name(channel):
				return self.send_json_response({'error': 'Invalid channel name'}, 400)

			channel_repo_path = os.path.join(self.directory, 'message', channel)
			if not os.path.exists(channel_repo_path):
				return self.send_json_response({'error': 'Channel not found'}, 404)

			from commit_files import pull_changes
			if pull_changes(channel_repo_path):
				# Invalidate cache after successful sync
				page_cache.invalidate(f'chat/{channel}')
				git_cache.invalidate(channel)
				return self.send_json_response({'status': 'success'})
			else:
				return self.send_json_response({'error': 'Sync failed'}, 500)

		except json.JSONDecodeError as e:
			return self.send_json_response({'error': f'Invalid JSON: {str(e)}'}, 400)
		except Exception as e:
			return self.send_json_response({'error': str(e)}, 500)

	def send_json_response(self, data: Dict[str, Any], status: int = 200) -> None:
		"""Send a JSON response with the specified status code"""
		if not self.wfile:
			raise RuntimeError("Response writer not properly initialized")

		response = json.dumps(data)
		response_bytes = response.encode('utf-8')

		self.handler.send_response(status)
		self.handler.send_header('Content-Type', 'application/json')
		self.handler.send_header('Content-Length', len(response_bytes))
		self.handler.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
		self.handler.send_header('Pragma', 'no-cache')
		self.handler.send_header('Expires', '0')
		self.handler.end_headers()
		self.handler.wfile.write(response_bytes)

	def send_error(self, code: int, message: str):
		"""Send an error as JSON response"""
		return self.send_json_response({'error': message}, code)
	
# end request_handler.py ; marker comment, please do not remove, including this message